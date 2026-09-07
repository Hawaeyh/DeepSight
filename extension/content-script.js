const labels = new WeakMap();
const analysedSources = new Set();
let scanGeneration = 0;
let session = null;

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === "DEEPSIGHT_SCAN") { scanPage(message).then(sendResponse); return true; }
  if (message.type === "DEEPSIGHT_VIDEO_START") { startVideoScan(message).then(sendResponse); return true; }
  if (message.type === "DEEPSIGHT_VIDEO_PAUSE") { pauseOrResume().then(sendResponse); return true; }
  if (message.type === "DEEPSIGHT_VIDEO_STOP") { stopVideoScan(true).then(sendResponse); return true; }
  if (message.type === "DEEPSIGHT_LOGOUT") { stopVideoScan(false); clearLabels(); sendResponse({ message: "Signed out." }); }
  return false;
});

async function scanPage({ modelId = "efficientnet" } = {}) {
  const generation = ++scanGeneration;
  const seen = new Set();
  const images = [...document.images].filter(image => {
    const rect = image.getBoundingClientRect();
    const source = image.currentSrc;
    if (!source || seen.has(source) || analysedSources.has(source)) return false;
    seen.add(source);
    return image.naturalWidth >= 120 && image.naturalHeight >= 80 && rect.width >= 80 && rect.height >= 60 && rect.bottom > 0 && rect.top < innerHeight && getComputedStyle(image).visibility !== "hidden";
  }).slice(0, 16);
  let completed = 0;
  const queue = [...images];
  async function worker() {
    while (queue.length && generation === scanGeneration) {
      const image = queue.shift();
      analysedSources.add(image.currentSrc); showLabel(image, "Checking", "pending");
      const response = await chrome.runtime.sendMessage({ type: "ANALYZE_IMAGE", url: image.currentSrc, modelId });
      if (response?.ok) { const result = response.result; showLabel(image, `${result.prediction} ${Number(result.confidence).toFixed(1)}%`, result.prediction.toLowerCase()); completed += 1; }
      else removeLabel(image);
    }
  }
  await Promise.all(Array.from({ length: Math.min(3, images.length) }, worker));
  return { ok: true, completed, found: images.length };
}

async function startVideoScan(options = {}) {
  await stopVideoScan(false);
  const videos = [...document.querySelectorAll("video")].filter(video => {
    const rect = video.getBoundingClientRect();
    return rect.width >= 240 && rect.height >= 120 && rect.bottom > 0 && rect.top < innerHeight && video.readyState >= 1;
  });
  if (!videos.length) return { message: "No visible playable video was found." };
  const index = Math.max(0, Math.min(Number(options.videoIndex || 0), videos.length - 1));
  const video = videos.sort((a, b) => b.clientWidth * b.clientHeight - a.clientWidth * a.clientHeight)[index];
  video.dataset.deepsightSelected = "true";
  video.style.outline = "3px solid #22d3ee";
  const created = await chrome.runtime.sendMessage({ type: "DEEPSIGHT_SESSION_CREATE", pageDomain: location.hostname, modelId: options.modelId || "efficientnet" });
  if (!created?.ok) { cleanupSelected(video); return { message: created?.error || "Could not start detection." }; }
  const overlay = createOverlay();
  const intervalMs = Math.max(1000, Math.min(5000, Number(options.intervalMs || 1500)));
  const maxDurationMs = Math.max(30_000, Math.min(300_000, Number(options.maxDurationSeconds || 180) * 1000));
  session = { id: created.result.sessionId, video, source: video.currentSrc || video.src, overlay, state: "analysing", busy: false, timer: null, started: Date.now(), frames: 0, failures: 0, previousSignature: null, intervalMs, maxDurationMs, options };
  renderOverlay(session, created.result);
  scheduleCapture(0);
  return { message: `Continuous detection started on video ${index + 1} of ${videos.length}.`, videoCount: videos.length };
}

function scheduleCapture(delay) {
  if (!session || session.state !== "analysing") return;
  clearTimeout(session.timer);
  session.timer = setTimeout(captureVideoFrame, delay);
}

async function captureVideoFrame() {
  const current = session;
  if (!current || current.state !== "analysing" || current.busy) return;
  if (Date.now() - current.started >= current.maxDurationMs || current.frames >= 120) return stopVideoScan(true);
  if (current.video.currentSrc !== current.source || !document.contains(current.video)) return stopVideoScan(false, "Video source changed. Detection stopped.");
  if (document.hidden || current.video.paused || current.video.readyState < 2) { scheduleCapture(current.intervalMs); return; }
  current.busy = true;
  try {
    const canvas = document.createElement("canvas");
    canvas.width = Math.min(current.video.videoWidth, 960); canvas.height = Math.round(canvas.width * current.video.videoHeight / current.video.videoWidth);
    const context = canvas.getContext("2d", { willReadFrequently: true });
    context.drawImage(current.video, 0, 0, canvas.width, canvas.height);
    const pixels = context.getImageData(0, 0, Math.min(32, canvas.width), Math.min(18, canvas.height)).data;
    let signature = 0; for (let i = 0; i < pixels.length; i += 32) signature = (signature + pixels[i] + pixels[i + 1] + pixels[i + 2]) % 1000003;
    if (current.previousSignature !== null && Math.abs(signature - current.previousSignature) < 30) { renderOverlay(current, { status: "analysing", framesAnalysed: current.frames, overallResult: "analysing" }); return; }
    current.previousSignature = signature;
    const dataUrl = canvas.toDataURL("image/jpeg", 0.82);
    if (dataUrl.length < 500) throw Object.assign(new Error("VIDEO_CAPTURE_RESTRICTED"), { name: "SecurityError" });
    const response = await chrome.runtime.sendMessage({ type: "DEEPSIGHT_SESSION_FRAME", sessionId: current.id, dataUrl });
    if (!response?.ok) throw new Error(response?.error || "Frame analysis failed.");
    current.frames = response.result.framesAnalysed; current.failures = 0; renderOverlay(current, response.result);
  } catch (error) {
    current.failures += 1;
    if (error?.name === "SecurityError" || /taint|capture/i.test(error?.message || "")) return stopVideoScan(false, "Browser security prevents this video from being captured. Upload it to DeepSight instead.");
    if (current.failures >= 3) return stopVideoScan(false, error.message || "DeepSight is unavailable.");
  } finally {
    if (session === current) { current.busy = false; scheduleCapture(current.intervalMs); }
  }
}

async function pauseOrResume() {
  if (!session) return { message: "No video scan is running." };
  const action = session.state === "paused" ? "resume" : "pause";
  const response = await chrome.runtime.sendMessage({ type: "DEEPSIGHT_SESSION_ACTION", sessionId: session.id, action });
  if (!response?.ok) return { message: response?.error || "Session could not be updated." };
  session.state = action === "pause" ? "paused" : "analysing";
  renderOverlay(session, response.result); if (session.state === "analysing") scheduleCapture(0);
  return { message: session.state === "paused" ? "Video scan paused." : "Video scan resumed." };
}

async function stopVideoScan(complete, message = "Video scan stopped.") {
  const current = session; if (!current) return { message };
  session = null; clearTimeout(current.timer); current.state = "stopping";
  const action = complete && current.frames > 0 ? "complete" : "cancel";
  const response = await chrome.runtime.sendMessage({ type: "DEEPSIGHT_SESSION_ACTION", sessionId: current.id, action }).catch(() => null);
  current.overlay.remove(); cleanupSelected(current.video);
  return { message, result: response?.result };
}

function createOverlay() {
  document.querySelector("[data-deepsight-video-overlay]")?.remove();
  const overlay = document.createElement("aside"); overlay.dataset.deepsightVideoOverlay = "true";
  Object.assign(overlay.style, { position: "fixed", right: "18px", top: "18px", width: "280px", zIndex: "2147483647", padding: "12px", border: "1px solid #22d3ee", borderRadius: "12px", background: "#071426ee", color: "#f8fafc", font: "12px/1.5 system-ui", boxShadow: "0 12px 35px #0008" });
  overlay.innerHTML = `<div data-drag style="display:flex;justify-content:space-between;cursor:move;font-weight:700"><span>DeepSight Live Detection</span><span><button data-min aria-label="Minimise">-</button> <button data-close aria-label="Close">x</button></span></div><div data-body><p data-state>Analysing</p><strong data-result style="display:block;font-size:16px">Collecting evidence...</strong><div data-metrics></div><div style="display:flex;gap:6px;margin-top:9px"><button data-pause>Pause</button><button data-stop>Stop</button></div></div>`;
  overlay.querySelectorAll("button").forEach(button => Object.assign(button.style, { background: "#164e63", color: "white", border: 0, borderRadius: "5px", padding: "4px 7px", cursor: "pointer" }));
  overlay.querySelector("[data-pause]").onclick = () => pauseOrResume(); overlay.querySelector("[data-stop]").onclick = () => stopVideoScan(true); overlay.querySelector("[data-close]").onclick = () => stopVideoScan(false);
  overlay.querySelector("[data-min]").onclick = () => { const body = overlay.querySelector("[data-body]"); body.hidden = !body.hidden; };
  let drag = null; overlay.querySelector("[data-drag]").addEventListener("pointerdown", event => { drag = { x: event.clientX - overlay.offsetLeft, y: event.clientY - overlay.offsetTop }; });
  addEventListener("pointermove", event => { if (drag) { overlay.style.left = `${Math.max(0, event.clientX-drag.x)}px`; overlay.style.top = `${Math.max(0, event.clientY-drag.y)}px`; overlay.style.right = "auto"; } }); addEventListener("pointerup", () => { drag = null; });
  document.documentElement.appendChild(overlay); return overlay;
}

function renderOverlay(current, result) {
  if (!current?.overlay.isConnected) return;
  const label = String(result.overallResult || result.status || "analysing").replaceAll("_", " ");
  current.overlay.querySelector("[data-state]").textContent = `Status: ${current.state === "paused" ? "Paused" : "Analysing"}`;
  current.overlay.querySelector("[data-result]").textContent = label === "analysing" ? "Collecting consistent evidence..." : label.replace(/\b\w/g, c => c.toUpperCase());
  current.overlay.querySelector("[data-metrics]").innerHTML = `Rolling confidence: ${result.overallConfidence == null ? "--" : Number(result.overallConfidence).toFixed(1)+"%"}<br>Frames analysed: ${result.framesAnalysed || 0}<br>Suspicious frames: ${result.suspiciousFrames || 0}<br>Model: ${result.actualModelId || current.options.modelId || "default"}`;
  current.overlay.querySelector("[data-pause]").textContent = current.state === "paused" ? "Resume" : "Pause";
}

function cleanupSelected(video) { if (video) { delete video.dataset.deepsightSelected; video.style.outline = ""; } }
function showLabel(image, text, state) { let label=labels.get(image); if (!label) { label=document.createElement("div"); label.dataset.deepsightLabel="true"; Object.assign(label.style,{position:"fixed",zIndex:"2147483647",padding:"5px 9px",borderRadius:"6px",color:"white",font:"600 12px system-ui",boxShadow:"0 2px 10px #0008",pointerEvents:"none"}); document.documentElement.appendChild(label); labels.set(image,label); } label.textContent=`DeepSight: ${text}`; label.style.background=state==="fake"?"#b91c1c":state==="real"?"#047857":"#0369a1"; positionLabel(image,label); }
function positionLabel(image,label){const rect=image.getBoundingClientRect();label.style.left=`${Math.max(4,rect.left+6)}px`;label.style.top=`${Math.max(4,rect.top+6)}px`;label.style.display=rect.bottom<0||rect.top>innerHeight?"none":"block";}
function removeLabel(image){labels.get(image)?.remove();labels.delete(image);}
function clearLabels(){scanGeneration+=1;document.querySelectorAll("[data-deepsight-label]").forEach(item=>item.remove());}
addEventListener("scroll",()=>{for(const image of document.images){const label=labels.get(image);if(label)positionLabel(image,label);}},true);
addEventListener("resize",()=>{for(const image of document.images){const label=labels.get(image);if(label)positionLabel(image,label);}});
document.addEventListener("visibilitychange",()=>{if(session&&document.hidden&&session.state==="analysing")pauseOrResume();});
addEventListener("pagehide",()=>{stopVideoScan(false);clearLabels();});
