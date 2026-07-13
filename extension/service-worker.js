const API_URL = "http://127.0.0.1:8000/api/v1";

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type !== "ANALYZE_IMAGE") return false;
  analyzeImage(message.url, Boolean(message.pro))
    .then(result => sendResponse({ ok: true, result }))
    .catch(error => sendResponse({ ok: false, error: error.message }));
  return true;
});

async function analyzeImage(url, pro) {
  const { accessToken } = await chrome.storage.local.get("accessToken");
  if (!accessToken) throw new Error("Sign in to DeepSight first.");

  const sourceResponse = await fetch(url, { credentials: "omit" });
  if (!sourceResponse.ok) throw new Error("The image could not be downloaded.");
  const blob = await sourceResponse.blob();
  if (!blob.type.startsWith("image/")) throw new Error("Unsupported image source.");

  const form = new FormData();
  form.append("file", blob, `web-image.${blob.type.split("/")[1] || "jpg"}`);
  form.append("model", "efficientnet");
  const response = await fetch(`${API_URL}/analysis/image`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "X-DeepSight-Client": pro ? "extension-pro" : "extension"
    },
    body: form
  });
  const payload = await response.json();
  if (!response.ok) {
    const detail = payload.detail;
    throw new Error(typeof detail === "string" ? detail : detail?.message || "Detection failed.");
  }
  return payload;
}
