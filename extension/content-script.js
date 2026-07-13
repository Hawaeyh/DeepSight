const labels = new WeakMap();
const analyzedSources = new Set();
let observer = null;
let proEnabled = false;

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === "DEEPSIGHT_SCAN") {
    scanPage(Boolean(message.pro)).then(sendResponse);
    return true;
  }
  if (message.type === "DEEPSIGHT_PRO") {
    setProMode(Boolean(message.enabled));
    sendResponse({ ok: true });
  }
  return false;
});

chrome.storage.local.get("proEnabled").then(({ proEnabled: enabled }) => setProMode(Boolean(enabled)));
chrome.storage.onChanged.addListener(changes => {
  if (changes.proEnabled) setProMode(Boolean(changes.proEnabled.newValue));
});

async function scanPage(pro) {
  const images = [...document.images]
    .filter(image => image.currentSrc && image.naturalWidth >= 120 && image.naturalHeight >= 80)
    .filter(image => !analyzedSources.has(image.currentSrc))
    .slice(0, 16);
  let completed = 0;
  for (const image of images) {
    analyzedSources.add(image.currentSrc);
    showLabel(image, "Checking", "pending");
    const response = await chrome.runtime.sendMessage({ type: "ANALYZE_IMAGE", url: image.currentSrc, pro });
    if (response?.ok) {
      const result = response.result;
      showLabel(image, `${result.prediction} ${Number(result.confidence).toFixed(1)}%`, result.prediction.toLowerCase());
      completed += 1;
    } else {
      removeLabel(image);
    }
  }
  return { ok: true, completed, found: images.length };
}

function setProMode(enabled) {
  proEnabled = enabled;
  if (observer) observer.disconnect();
  observer = null;
  if (!enabled) return;
  scanPage(true);
  observer = new MutationObserver(() => window.setTimeout(() => scanPage(true), 500));
  observer.observe(document.documentElement, { childList: true, subtree: true });
}

function showLabel(image, text, state) {
  let label = labels.get(image);
  if (!label) {
    label = document.createElement("div");
    label.dataset.deepsightLabel = "true";
    Object.assign(label.style, {
      position: "fixed",
      zIndex: "2147483647",
      padding: "5px 9px",
      borderRadius: "6px",
      color: "white",
      font: "600 12px/1.2 system-ui, sans-serif",
      boxShadow: "0 2px 10px rgba(0,0,0,.35)",
      pointerEvents: "none"
    });
    document.documentElement.appendChild(label);
    labels.set(image, label);
  }
  label.textContent = `DeepSight: ${text}`;
  label.style.background = state === "fake" ? "#dc2626" : state === "real" ? "#059669" : "#0369a1";
  positionLabel(image, label);
}

function positionLabel(image, label) {
  const rect = image.getBoundingClientRect();
  label.style.left = `${Math.max(4, rect.left + 6)}px`;
  label.style.top = `${Math.max(4, rect.top + 6)}px`;
  label.style.display = rect.bottom < 0 || rect.top > innerHeight ? "none" : "block";
}

function removeLabel(image) {
  labels.get(image)?.remove();
  labels.delete(image);
}

function refreshLabels() {
  document.querySelectorAll("[data-deepsight-label]").forEach(label => {
    for (const image of document.images) if (labels.get(image) === label) positionLabel(image, label);
  });
}
addEventListener("scroll", refreshLabels, true);
addEventListener("resize", refreshLabels);
