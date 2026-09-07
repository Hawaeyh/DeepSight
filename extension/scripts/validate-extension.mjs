import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";


export const extensionRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

export async function validateExtension(root = extensionRoot) {
  const manifestPath = path.join(root, "manifest.json");
  const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
  if (manifest.manifest_version !== 3) throw new Error("manifest_version must be 3");

  const requiredFiles = [
    manifest.action?.default_popup,
    manifest.background?.service_worker,
    ...(manifest.content_scripts ?? []).flatMap(item => item.js ?? []),
    "config.js"
  ].filter(Boolean);

  for (const relativePath of requiredFiles) {
    const target = path.resolve(root, relativePath);
    if (!target.startsWith(`${path.resolve(root)}${path.sep}`)) {
      throw new Error(`Manifest path escapes extension root: ${relativePath}`);
    }
    if (!(await stat(target)).isFile()) throw new Error(`Required extension file is missing: ${relativePath}`);
  }

  const sourceFiles = ["config.js", "popup.js", "content-script.js", "service-worker.js"];
  const source = (await Promise.all(sourceFiles.map(file => readFile(path.join(root, file), "utf8")))).join("\n");
  const secretPatterns = [
    /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/,
    /(?:stripe|sk)_(?:live|test)_[A-Za-z0-9]{16,}/,
    /private_key\s*[:=]/i,
    /serviceAccountKey\.json/i
  ];
  if (secretPatterns.some(pattern => pattern.test(source))) {
    throw new Error("Possible production credential embedded in extension source");
  }
  if (!source.includes("DEEPSIGHT_CONFIG")) throw new Error("API URL is not read from extension config");
  return { manifest, requiredFiles };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const result = await validateExtension();
  console.log(`Extension validation passed (${result.requiredFiles.length} required entries).`);
}
