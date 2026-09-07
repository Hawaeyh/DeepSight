import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

const popup = fs.readFileSync(new URL("../popup.html", import.meta.url), "utf8");
const popupScript = fs.readFileSync(new URL("../popup.js", import.meta.url), "utf8");
const content = fs.readFileSync(new URL("../content-script.js", import.meta.url), "utf8");
const worker = fs.readFileSync(new URL("../service-worker.js", import.meta.url), "utf8");

test("popup exposes authenticated tabs, account, plan, usage, models and bounded settings", () => {
  for (const value of ["image", "page", "video", "history", "settings"]) assert.match(popup, new RegExp(`data-tab="${value}"`));
  for (const id of ["account", "plan", "usage", "model", "interval", "duration"]) assert.match(popup, new RegExp(`id="${id}"`));
  assert.match(popup, /min="1" max="5"/);
  assert.match(popupScript, /DEEPSIGHT_MODELS/);
  assert.match(popupScript, /DEEPSIGHT_HISTORY/);
});

test("continuous capture is explicit, sequential and bounded", () => {
  assert.match(content, /current\.busy = true/);
  assert.match(content, /finally[\s\S]*current\.busy = false/);
  assert.match(content, /current\.frames >= 120/);
  assert.match(content, /Math\.min\(5000/);
  assert.match(content, /Math\.min\(300_000/);
  assert.match(content, /previousSignature/);
  assert.doesNotMatch(content, /setInterval\(captureVideoFrame/);
});

test("video lifecycle supports server sessions, pause, resume, complete and cancel", () => {
  for (const action of ["pause", "resume", "complete", "cancel"]) assert.match(content, new RegExp(`"${action}"`));
  assert.match(worker, /AbortController/);
  assert.match(worker, /response\.status === 401/);
  assert.match(content, /visibilitychange/);
  assert.match(content, /current\.video\.currentSrc !== current\.source/);
});

test("overlay is draggable, minimisable and removable without colour-only status", () => {
  assert.match(content, /data-drag/);
  assert.match(content, /data-min/);
  assert.match(content, /data-close/);
  assert.match(content, /Frames analysed:/);
  assert.match(content, /Rolling confidence:/);
});
