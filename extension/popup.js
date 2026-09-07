const API_URL = globalThis.DEEPSIGHT_CONFIG.apiBaseUrl;
const websiteUrl = API_URL.replace(/\/api\/v1\/?$/, "").replace(":8000", ":5173");
const $ = selector => document.querySelector(selector);
let settings = { modelId: "efficientnet", mode: "page", interval: 1.5, duration: 180, overlay: true, imageOverlays: true };

initialize();

async function initialize() {
  const stored = await chrome.storage.local.get(["accessToken", "user", "extensionSettings"]);
  settings = { ...settings, ...(stored.extensionSettings || {}) };
  applySettings();
  if (!stored.accessToken || !stored.user) return showLoggedOut();
  showLoggedIn(stored.user); await Promise.all([loadAccount(), loadModels()]); selectTab(settings.mode === "video" ? "video" : settings.mode === "image" ? "image" : "page");
}

$("#login-form").addEventListener("submit", async event => {
  event.preventDefault(); setStatus("Authenticating..."); toggleBusy(true);
  try {
    const response = await fetch(`${API_URL}/auth/login`, { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({email:$("#email").value,password:$("#password").value}) });
    const payload = await response.json(); if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : "Sign in failed.");
    await chrome.storage.local.set({ accessToken:payload.access_token, user:payload.user }); showLoggedIn(payload.user); await Promise.all([loadAccount(),loadModels()]); setStatus("Signed in securely.");
  } catch(error) { setStatus(error.message); } finally { toggleBusy(false); }
});

document.querySelectorAll("[data-tab]").forEach(button => button.addEventListener("click", () => selectTab(button.dataset.tab)));
function selectTab(name){document.querySelectorAll("[data-tab]").forEach(item=>item.classList.toggle("active",item.dataset.tab===name));document.querySelectorAll("[data-panel]").forEach(item=>item.hidden=item.dataset.panel!==name);if(name==="history")loadHistory();}

for (const id of ["scan","image-scan"]) $("#"+id).addEventListener("click", () => sendToTab({type:"DEEPSIGHT_SCAN",modelId:settings.modelId}, response => setStatus(`${response?.completed||0} of ${response?.found||0} visible images analysed.`)));
$("#scan-stop").addEventListener("click", () => sendToTab({type:"DEEPSIGHT_LOGOUT"}, () => setStatus("Scan stopped and overlays cleared.")));
$("#video-start").addEventListener("click",()=>sendToTab({type:"DEEPSIGHT_VIDEO_START",modelId:settings.modelId,intervalMs:settings.interval*1000,maxDurationSeconds:settings.duration,showOverlay:settings.overlay},response=>setStatus(response?.message||"Detection started.")));
$("#video-pause").addEventListener("click",()=>sendToTab({type:"DEEPSIGHT_VIDEO_PAUSE"},response=>setStatus(response?.message||"Detection updated.")));
$("#video-stop").addEventListener("click",()=>sendToTab({type:"DEEPSIGHT_VIDEO_STOP"},response=>{setStatus(response?.message||"Detection stopped.");if(response?.result)showResult(response.result);}));

async function sendToTab(message, callback){const [tab]=await chrome.tabs.query({active:true,currentWindow:true});if(!tab?.id)return setStatus("No active webpage.");try{const response=await chrome.tabs.sendMessage(tab.id,message);callback(response);}catch{setStatus("Reload this webpage, then try again.");}}

async function loadAccount(){const response=await chrome.runtime.sendMessage({type:"DEEPSIGHT_ACCOUNT"});if(!response.ok)return handleSessionError(response.error);const value=response.result;$("#plan").textContent=`${value.plan?.name||value.planName||"Starter"} plan`;$("#usage").textContent=value.remaining==null?"Unlimited":`${value.remaining} left`;$("#connection").textContent="Connected: online";}
async function loadModels(){const response=await chrome.runtime.sendMessage({type:"DEEPSIGHT_MODELS"});if(!response.ok)return setStatus(response.error);const models=Array.isArray(response.result)?response.result:response.result.models||[];$("#model").innerHTML="";for(const model of models){const option=document.createElement("option");option.value=model.id;option.textContent=`${model.name} v${model.version}`;$("#model").append(option);}if(models.some(item=>item.id===settings.modelId))$("#model").value=settings.modelId;else if(models.length)settings.modelId=models.find(item=>item.is_default)?.id||models[0].id;}
async function loadHistory(){const response=await chrome.runtime.sendMessage({type:"DEEPSIGHT_HISTORY"});if(!response.ok)return $("#history").textContent=response.error;const items=response.result;$("#history").innerHTML=items.length?items.map(item=>`<article><b>${escapeHtml(formatResult(item.overallResult))} - ${item.overallConfidence==null?"--":Number(item.overallConfidence).toFixed(1)+"%"}</b><small>${escapeHtml(item.pageDomain)} - ${escapeHtml(item.actualModelId||item.selectedModelId)} - ${Math.round(item.durationSeconds)}s</small></article>`).join(""):"No continuous sessions yet.";}

$("#interval").addEventListener("input",()=>$("#interval-value").textContent=`${$("#interval").value} s`);
$("#save-settings").addEventListener("click",async()=>{settings={modelId:$("#model").value,mode:$("#mode").value,interval:Number($("#interval").value),duration:Number($("#duration").value),overlay:$("#overlay").checked,imageOverlays:$("#image-overlays").checked};await chrome.storage.local.set({extensionSettings:settings});setStatus("Settings saved.");});
$("#logout").addEventListener("click",async()=>{await chrome.runtime.sendMessage({type:"DEEPSIGHT_LOGOUT"});sendToTab({type:"DEEPSIGHT_LOGOUT"},()=>{});showLoggedOut();setStatus("Signed out. Protected extension state was cleared.");});
$("#dashboard").addEventListener("click",()=>chrome.tabs.create({url:websiteUrl}));$("#view-all").addEventListener("click",()=>chrome.tabs.create({url:`${websiteUrl}/history`}));

function applySettings(){$("#mode").value=settings.mode;$("#interval").value=String(settings.interval);$("#interval-value").textContent=`${settings.interval} s`;$("#duration").value=String(settings.duration);$("#overlay").checked=settings.overlay;$("#image-overlays").checked=settings.imageOverlays;}
function showLoggedOut(){$("#logged-out").hidden=false;$("#app").hidden=true;$("#connection").textContent="Connected: sign in required";}
function showLoggedIn(user){$("#logged-out").hidden=true;$("#app").hidden=false;$("#account").textContent=user.email;$("#plan").textContent=`${user.plan||"Starter"} plan`;}
function showResult(result){$("#frames").textContent=result.framesAnalysed||0;$("#prediction").textContent=formatResult(result.overallResult);$("#confidence").textContent=result.overallConfidence==null?"--":`${Number(result.overallConfidence).toFixed(1)}%`;}
function handleSessionError(error){setStatus(error);if(/expired|log in/i.test(error||""))showLoggedOut();}
function setStatus(message){$("#status").textContent=message||"";}
function toggleBusy(value){$("#login-form button").disabled=value;}
function formatResult(value){return String(value||"Ready").replaceAll("_"," ").replace(/\b\w/g,c=>c.toUpperCase());}
function escapeHtml(value){const node=document.createElement("span");node.textContent=String(value||"");return node.innerHTML;}
