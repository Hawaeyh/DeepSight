import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

const manifest = JSON.parse(fs.readFileSync(new URL("../manifest.json", import.meta.url), "utf8"));
const content = fs.readFileSync(new URL("../content-script.js", import.meta.url), "utf8");
const worker = fs.readFileSync(new URL("../service-worker.js", import.meta.url), "utf8");
const config = fs.readFileSync(new URL("../config.js", import.meta.url), "utf8");

test("extension permissions remain minimal for active-page capture", () => {
  assert.deepEqual(manifest.permissions.sort(), ["activeTab", "storage"]);
  assert.deepEqual(manifest.host_permissions, ["<all_urls>"]);
});

test("video scan is user controlled and uses the protected session frame endpoint", () => {
  for (const action of ["DEEPSIGHT_VIDEO_START", "DEEPSIGHT_VIDEO_PAUSE", "DEEPSIGHT_VIDEO_STOP"]) assert.match(content, new RegExp(action));
  assert.match(worker, /extension\/video-sessions/);
  assert.match(worker, /sessionId.*frames/);
  assert.match(worker, /Authorization: `Bearer \$\{accessToken\}`/);
});

test("capture stops safely on browser security failures and navigation", () => {
  assert.match(content, /SecurityError/);
  assert.match(content, /stopVideoScan\(false\)/);
  assert.match(content, /pagehide/);
});

test("extension source contains no private integration credentials", () => {
  const source = `${content}\n${worker}\n${config}`;
  assert.doesNotMatch(source, /STRIPE_SECRET|FIREBASE_PRIVATE_KEY|BEGIN PRIVATE KEY|service_account/);
});
