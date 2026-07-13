const API_URL = "http://127.0.0.1:8000/api/v1";
const form = document.querySelector("#login-form");
const controls = document.querySelector("#controls");
const account = document.querySelector("#account");
const status = document.querySelector("#status");
const pro = document.querySelector("#pro");

initialize();

async function initialize() {
  const state = await chrome.storage.local.get(["accessToken", "user", "proEnabled"]);
  if (state.accessToken && state.user) showAccount(state.user, state.proEnabled);
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  setStatus("Signing in...");
  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: document.querySelector("#email").value, password: document.querySelector("#password").value })
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "Sign in failed.");
    await chrome.storage.local.set({ accessToken: payload.access_token, user: payload.user, proEnabled: false });
    showAccount(payload.user, false);
    setStatus("Signed in.");
  } catch (error) { setStatus(error.message); }
});

document.querySelector("#scan").addEventListener("click", async () => {
  setStatus("Scanning visible images...");
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) return setStatus("No active webpage.");
  try {
    const response = await chrome.tabs.sendMessage(tab.id, { type: "DEEPSIGHT_SCAN", pro: false });
    setStatus(`${response.completed} image${response.completed === 1 ? "" : "s"} labeled.`);
  } catch { setStatus("Reload this webpage, then scan again."); }
});

pro.addEventListener("change", async () => {
  await chrome.storage.local.set({ proEnabled: pro.checked });
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tab?.id) chrome.tabs.sendMessage(tab.id, { type: "DEEPSIGHT_PRO", enabled: pro.checked }).catch(() => undefined);
  setStatus(pro.checked ? "Continuous detection enabled." : "Continuous detection stopped.");
});

document.querySelector("#logout").addEventListener("click", async () => {
  await chrome.storage.local.clear();
  form.hidden = false;
  controls.hidden = true;
  account.textContent = "Not signed in";
  setStatus("");
});

function showAccount(user, proEnabled) {
  form.hidden = true;
  controls.hidden = false;
  account.textContent = `${user.email} · ${user.plan}`;
  const lite = user.plan === "lite" || user.role === "admin";
  document.querySelector("#pro-row").hidden = !lite;
  pro.checked = lite && Boolean(proEnabled);
}

function setStatus(message) { status.textContent = message; }
