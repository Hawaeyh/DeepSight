import { cp, mkdir, rm } from "node:fs/promises";
import path from "node:path";

import { extensionRoot, validateExtension } from "./validate-extension.mjs";


await validateExtension();
const outputDirectory = path.resolve(extensionRoot, "dist");
if (path.dirname(outputDirectory) !== extensionRoot || path.basename(outputDirectory) !== "dist") {
  throw new Error("Refusing to build outside extension/dist");
}

await rm(outputDirectory, { recursive: true, force: true });
await mkdir(outputDirectory, { recursive: true });
const runtimeFiles = [
  "manifest.json",
  "config.js",
  "popup.html",
  "popup.css",
  "popup.js",
  "content-script.js",
  "service-worker.js",
  "logo.png"
];
await Promise.all(runtimeFiles.map(file => cp(path.join(extensionRoot, file), path.join(outputDirectory, file))));
console.log(`Extension build complete: ${outputDirectory}`);
