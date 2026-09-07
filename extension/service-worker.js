importScripts("config.js");

const API_URL = globalThis.DEEPSIGHT_CONFIG.apiBaseUrl;
const TIMEOUT_MS = 25_000;

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  dispatch(message).then(sendResponse).catch(error => sendResponse({ ok: false, error: safeError(error) }));
  return true;
});

async function dispatch(message) {
  switch (message.type) {
    case "ANALYZE_IMAGE": return { ok: true, result: await analyzeImage(message.url, message.modelId || "efficientnet", Boolean(message.pro)) };
    case "DEEPSIGHT_MODELS": return { ok: true, result: await api("/models/available") };
    case "DEEPSIGHT_ACCOUNT": return { ok: true, result: await api("/subscriptions/status") };
    case "DEEPSIGHT_HISTORY": return { ok: true, result: await api("/extension/video-sessions") };
    case "DEEPSIGHT_SESSION_CREATE": return { ok: true, result: await api("/extension/video-sessions", { method: "POST", json: { page_domain: message.pageDomain, model_id: message.modelId } }) };
    case "DEEPSIGHT_SESSION_FRAME": return { ok: true, result: await sendFrame(message.sessionId, message.dataUrl) };
    case "DEEPSIGHT_SESSION_ACTION": return { ok: true, result: await api(`/extension/video-sessions/${encodeURIComponent(message.sessionId)}/${message.action}`, { method: "POST" }) };
    case "DEEPSIGHT_LOGOUT": await chrome.storage.local.remove(["accessToken", "user", "proEnabled"]); return { ok: true };
    default: return { ok: false, error: "Unsupported extension request." };
  }
}

async function api(path, options = {}) {
  const { accessToken } = await chrome.storage.local.get("accessToken");
  if (!accessToken) throw new Error("SESSION_EXPIRED");
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const headers = { Authorization: `Bearer ${accessToken}`, ...(options.headers || {}) };
    let body = options.body;
    if (options.json) { headers["Content-Type"] = "application/json"; body = JSON.stringify(options.json); }
    const response = await fetch(`${API_URL}${path}`, { method: options.method || "GET", headers, body, signal: controller.signal });
    if (response.status === 401) {
      await chrome.storage.local.remove(["accessToken", "user", "proEnabled"]);
      throw new Error("SESSION_EXPIRED");
    }
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = payload.detail;
      const code = typeof detail === "object" ? detail.code : undefined;
      throw new Error(code || (typeof detail === "string" ? detail : "BACKEND_UNAVAILABLE"));
    }
    return payload;
  } catch (error) {
    if (error?.name === "AbortError") throw new Error("BACKEND_UNAVAILABLE");
    throw error;
  } finally { clearTimeout(timer); }
}

async function analyzeImage(url, modelId, pro) {
  const sourceResponse = await fetch(url, { credentials: "omit" });
  if (!sourceResponse.ok) throw new Error("The image could not be downloaded.");
  const blob = await sourceResponse.blob();
  if (!blob.type.startsWith("image/")) throw new Error("Unsupported image source.");
  const form = new FormData();
  form.append("file", blob, `web-image.${blob.type.split("/")[1] || "jpg"}`);
  form.append("model", modelId);
  return api("/analysis/image", { method: "POST", headers: { "X-DeepSight-Client": pro ? "extension-pro" : "extension" }, body: form });
}

async function sendFrame(sessionId, dataUrl) {
  const response = await fetch(dataUrl);
  const blob = await response.blob();
  const form = new FormData();
  form.append("file", blob, "web-video-frame.jpg");
  return api(`/extension/video-sessions/${encodeURIComponent(sessionId)}/frames`, { method: "POST", body: form });
}

function safeError(error) {
  const messages = {
    SESSION_EXPIRED: "Your session has expired. Please log in again.",
    MODEL_UNAVAILABLE: "The selected model is currently unavailable.",
    PLAN_REQUIRED: "Your current plan does not include continuous video detection.",
    USAGE_LIMIT_REACHED: "You have reached your current usage limit.",
    BACKEND_UNAVAILABLE: "DeepSight is currently unavailable."
  };
  return messages[error?.message] || error?.message || messages.BACKEND_UNAVAILABLE;
}
