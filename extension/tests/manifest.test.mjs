import assert from "node:assert/strict";
import test from "node:test";

import { validateExtension } from "../scripts/validate-extension.mjs";


test("manifest is MV3 and every declared entry exists", async () => {
  const { manifest, requiredFiles } = await validateExtension();
  assert.equal(manifest.manifest_version, 3);
  assert.ok(requiredFiles.includes("popup.html"));
  assert.ok(requiredFiles.includes("content-script.js"));
  assert.ok(requiredFiles.includes("service-worker.js"));
});

test("development API URL is isolated in config", async () => {
  const { requiredFiles } = await validateExtension();
  assert.ok(requiredFiles.includes("config.js"));
});
