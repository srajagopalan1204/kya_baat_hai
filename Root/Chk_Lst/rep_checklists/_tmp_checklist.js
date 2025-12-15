
/*** CONSTANTS ***/
const TEMPLATE_TAGLINE_DEFAULT = "v8 – SOP_Build + READYBASE split + validate_story + Stage publish (git add assets)";

/*** STORAGE ***/
const STORAGE_KEY_BASE = "SOP_BUILD_CHECKLIST_V8_STATE_V8";
function getStorageKey(){
  // Namespace saved state per SOP_ID when available so multiple SOPs don't overwrite each other.
  const id = (sopInfo && sopInfo.id) ? String(sopInfo.id).trim() : "";
  return id ? `${STORAGE_KEY_BASE}__${id}` : STORAGE_KEY_BASE;
}

/*** SOP INFO MODEL ***/
let sopInfo = {
  name: "",
  id: "",
  entity: "",
  repo: "/workspaces/SOP_Build",
  webRoot: "/SOP_Stage",
  runLabel: "",
  imgFolder: "../outputs/images/<SOP_ID>",
  templateTag: TEMPLATE_TAGLINE_DEFAULT
};

/*** STEPS MODEL – Local PC → SOP_Build → SOP_Stage ***/
let steps = [
  {
    "id": "GatherInputs (weekly TXT files)",
    "order": 1,
    "title": "upload text files only",
    "command": "cd /workspaces/grph_hw_cons/rep_new

[Program] GitHub Upload function",
    "reminder": "Inputs: C:\Users\scottuser\Documents\ERP\Analysis\Training\Trn_attainment\Cono1\Weekly_run\inputfilesRaw | Hints: The weekly reports will show up in the email on Friday night ",
    "notes": "",
    "runs": []
  },
  {
    "id": "BuildP1",
    "order": 2,
    "title": "Build the first of two extract",
    "command": "python src/V5_Build_Slim_P1.py

[Program] V5_Build_Slim_P1.py

[Variants] python src/V5_Build_Slim_P1.py --latest-per-cono  for quick sanity check with latest file",
    "reminder": "Inputs: /workspaces/grph_hw_cons/rep_new/inputs/V5/by_cono",
    "notes": "",
    "runs": []
  },
  {
    "id": "EnhanceP1",
    "order": 3,
    "title": "Enhance the out put by adding additional information",
    "command": "python src/V5_Post_Enhance_Pivot.py   --in-xlsx \"outputs/V5/weekly/<P1_XLSX_FROM_STEP_1>.xlsx\"   --out-xlsx \"outputs/V5/weekly/<P1_ENH_XLSX>.xlsx\"

[Program] V5_Post_Enhance_Pivot.py",
    "reminder": "Inputs: /workspaces/grph_hw_cons/rep_new/outputs/V5/weekly/V5_Slim_P1_ALLConos_20251116_1914.xlsx",
    "notes": "",
    "runs": []
  },
  {
    "id": "BuildP2",
    "order": 4,
    "title": "Build the second extract",
    "command": "python src/V5_Build_Slim_P2.py

[Program] V5_Build_Slim_P2.py

[Variants] python src/V5_Post_Enhance_Pivot.py   --in-xlsx  \"outputs/V5/weekly/V5_Slim_P1_ALLConos_YYYYMMDD_HHMM.xlsx\"   --out-xlsx \"outputs/V5/weekly/V5_Slim_P1_ALLConos_ENH_YYYYMMDD_HHMM.xlsx\"   --emp-dir  \"inputs/V5/emp\"   --super-map \"configs/V5/super_function_map.json5\"",
    "reminder": "Inputs: same as for P1 build input text file",
    "notes": "",
    "runs": []
  },
  {
    "id": "PublishMerge",
    "order": 5,
    "title": "Merge the two extracts into one",
    "command": "python src/V5_Publish_Merge.py   --p1 \"/workspaces/grph_hw_cons/rep_new/outputs/V5/weekly/V5_Slim_P1_ENH_ALLConos_20251116_1914.xlsx\"   --p2 \"/workspaces/grph_hw_cons/rep_new/outputs/V5/weekly/V5_Slim_P2_ALLConos_20251116_1920.xlsx\"

[Variants] python src/V5_Publish_Merge.py   --p1 \"outputs/V5/weekly/V5_Slim_P1_ALLConos_ENH_YYYYMMDD_HHMM.xlsx\"   --p2 \"outputs/V5/weekly/V5_Slim_P2_ALLConos_YYYYMMDD_HHMM.xlsx\"   --out-xlsx \"outputs/V5/weekly/V5_Slim_Publish_ALLConos_CUSTOM.xlsx\"   --tz \"America/New_York\"",
    "reminder": "Inputs: out puts from EnhanceP1 and BuildP2 | Hints: `V5_Post_Enhance_Pivot.py` accepts a JSON5-style role map (comments, single quotes, trailing commas ok).
- Unmatched users get placeholders: `Un_Name`, `Un_Manager`, `Un_Loc`, `Un_Loc_Num`, `Un_Posi`, `Un_Role`, `Un_Sup_G`.
- Totals are **not** modified by enhancement; only `Metric == \"User_Hit\"` rows receive employee joins.",
    "notes": "",
    "runs": []
  },
  {
    "id": "QC Quick Checks",
    "order": 6,
    "title": "The first run is made to check the latest week is extracting correctly",
    "command": "",
    "reminder": "Inputs: Download the latest cono run to see if all the sections are there then rerun without the -latest-per-cono ",
    "notes": "",
    "runs": []
  },
  {
    "id": "DownloadToPC",
    "order": 7,
    "title": "Download the _publish_ file",
    "command": "C:\Users\scottuser\Documents\ERP\Analysis\Training\Trn_attainment\V5\outputs\weekly  under the appropriate week 
\"C:\Users\scottuser\Documents\ERP\Analysis\Training\Trn_attainment\V5\outputs\weekly\251115\"
\"C:\Users\scottuser\Documents\ERP\Analysis\Training\Trn_attainment\V5\outputs\weekly\251108\"

[Variants] after running it for all available weeks",
    "reminder": "Inputs: down load the out put file mentioned in 7 to the pc copy it over the folder ",
    "notes": "",
    "runs": []
  },
  {
    "id": "RefreshPivots",
    "order": 8,
    "title": "Use Data refresh to update the tables Then hind the raw data tabs after converting column w in userHits data tab",
    "command": "Refresh the data",
    "reminder": "Inputs: copy the contents to the corresponding sheets in the template ",
    "notes": "",
    "runs": []
  },
  {
    "id": "VisualCheck",
    "order": 9,
    "title": "Inspect data for anomalies",
    "command": "",
    "reminder": "Inputs: Check the numbers for accuracy this take a lot of time a one has to see two specific week - most current and any other random week",
    "notes": "",
    "runs": []
  },
  {
    "id": "Distribute",
    "order": 10,
    "title": "Distribute",
    "command": "",
    "reminder": "",
    "notes": "",
    "runs": []
  }
];

/*** ENHANCEMENTS MODEL ***/
let enhancements = [];

/*** UI INIT ***/
document.getElementById("taglinePill").textContent = TEMPLATE_TAGLINE_DEFAULT;

/*** HELPERS ***/
function nowStamp(){
  const d = new Date();
  const pad = (n)=> String(n).padStart(2,"0");
  const mm = pad(d.getMonth()+1);
  const dd = pad(d.getDate());
  const yy = String(d.getFullYear()).slice(-2);
  const hh = pad(d.getHours());
  const mi = pad(d.getMinutes());
  return `${mm}/${dd}/${d.getFullYear()} ${hh}:${mi}`;
}
function buildExportStamp(){
  const d = new Date();
  const pad = (n)=> String(n).padStart(2,"0");
  const mm = pad(d.getMonth()+1);
  const dd = pad(d.getDate());
  const yy = String(d.getFullYear()).slice(-2);
  const hh = pad(d.getHours());
  const mi = pad(d.getMinutes());
  return `${mm}${dd}${yy}_${hh}${mi}`;
}
function safeReplaceAll(s, find, repl){
  return String(s||"").split(find).join(repl);
}
function replaceTokens(text){
  // Replace only the common tokens; leave YYYYMMDD_HHMM/MMDDYY_HHMM as human hints.
  let out = text;
  out = safeReplaceAll(out, "<SOP_ID>", sopInfo.id || "<SOP_ID>");
  return out;
}


/*** ROBUSTNESS HELPERS (v8a) ***/
function normalizeOrders(){
  steps = steps || [];
  steps.forEach((s,i)=>{ s.order = i+1; });
}
function uid(prefix){
  return (prefix||"X") + "_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2,7);
}
function autosaveNotice(){
  const el = document.getElementById("autosavePill");
  if(!el) return;
  el.style.display = "inline-flex";
  el.textContent = "Autosaved";
  clearTimeout(autosaveNotice._t);
  autosaveNotice._t = setTimeout(()=>{ el.style.display="none"; }, 900);
}
let _saveDebounce = null;
function saveStateDebounced(){
  clearTimeout(_saveDebounce);
  _saveDebounce = setTimeout(()=>{ saveState(true); autosaveNotice(); }, 300);
}
window.addEventListener("beforeunload", ()=>{ 
  try{ saveState(true); }catch(e){} 
});

/*** STEP CRUD (add/insert/move/delete) ***/
function addStepPrompt(){
  const title = prompt("Step title (required):", "New step");
  if(!title) return;
  const cmd = prompt("Command / procedure (optional):", "");
  const rem = prompt("Reminder / hints (optional):", "");
  const st = {
    id: uid("Custom"),
    order: steps.length + 1,
    title: title,
    command: cmd || "",
    reminder: rem || "",
    notes: "",
    done: false,
    runs: []
  };
  steps.push(st);
  normalizeOrders();
  saveState(true);
  renderSteps();
}
function insertStepAfter(idx){
  const title = prompt("Insert step title (required):", "Inserted step");
  if(!title) return;
  const cmd = prompt("Command / procedure (optional):", "");
  const rem = prompt("Reminder / hints (optional):", "");
  const st = {
    id: uid("Insert"),
    order: idx+2,
    title,
    command: cmd || "",
    reminder: rem || "",
    notes: "",
    done: false,
    runs: []
  };
  steps.splice(idx+1, 0, st);
  normalizeOrders();
  saveState(true);
  renderSteps();
}
function duplicateStep(idx){
  const src = steps[idx];
  const copy = JSON.parse(JSON.stringify(src));
  copy.id = uid("Copy");
  copy.title = (src.title || "Step") + " (copy)";
  copy.done = false;
  copy.runs = [];
  steps.splice(idx+1, 0, copy);
  normalizeOrders();
  saveState(true);
  renderSteps();
}
function moveStep(idx, dir){
  const j = idx + dir;
  if(j < 0 || j >= steps.length) return;
  const tmp = steps[idx];
  steps[idx] = steps[j];
  steps[j] = tmp;
  normalizeOrders();
  saveState(true);
  renderSteps();
}
function deleteStep(idx){
  if(!confirm("Delete this step?")) return;
  steps.splice(idx,1);
  normalizeOrders();
  saveState(true);
  renderSteps();
}

/*** EXPORT / IMPORT JSON (portable state) ***/
function exportStateJson(){
  const state = { sopInfo, steps, enhancements, exported_at: new Date().toISOString() };
  const blob = new Blob([JSON.stringify(state, null, 2)], {type:"application/json"});
  const a = document.createElement("a");
  const id = (sopInfo && sopInfo.id) ? sopInfo.id : "SOP";
  a.download = `${id}_checklist_state_${buildExportStamp()}.json`;
  a.href = URL.createObjectURL(blob);
  document.body.appendChild(a);
  a.click();
  setTimeout(()=>{ URL.revokeObjectURL(a.href); a.remove(); }, 200);
}
function triggerImportJson(){
  const f = document.getElementById("importJsonFile");
  if(f) f.click();
}
function handleImportJsonFile(ev){
  const file = ev.target.files && ev.target.files[0];
  if(!file) return;
  const reader = new FileReader();
  reader.onload = ()=>{
    try{
      const st = JSON.parse(String(reader.result||""));
      sopInfo = st.sopInfo || sopInfo;
      steps = st.steps || steps;
      enhancements = st.enhancements || enhancements;
    normalizeOrders();
      normalizeOrders();
      populateSOPFieldsFromState();
      document.getElementById("taglinePill").textContent = sopInfo.templateTag || TEMPLATE_TAGLINE_DEFAULT;
      saveState(true);
      renderSteps();
      renderEnhancements();
      alert("Imported JSON state.");
    }catch(e){
      alert("Import failed: " + e);
    }finally{
      ev.target.value = "";
    }
  };
  reader.readAsText(file);
}

/*** DOWNLOAD exported text as .txt ***/
function downloadExportText(){
  exportText();
  const out = document.getElementById("exportArea").value || "";
  const blob = new Blob([out], {type:"text/plain"});
  const a = document.createElement("a");
  const id = (sopInfo && sopInfo.id) ? sopInfo.id : "SOP";
  a.download = `${id}_build_log_${buildExportStamp()}.txt`;
  a.href = URL.createObjectURL(blob);
  document.body.appendChild(a);
  a.click();
  setTimeout(()=>{ URL.revokeObjectURL(a.href); a.remove(); }, 200);
}
/*** RENDER ***/
function renderSteps(){
  const wrap = document.getElementById("stepsWrap");
  wrap.innerHTML = "";

  normalizeOrders();
  steps.forEach((st, idx)=>{
    const stepEl = document.createElement("div");
    stepEl.className = "step";

    const top = document.createElement("div");
    top.className = "step-top";

    const title = document.createElement("div");
    title.className = "step-title";
    title.textContent = `Step ${idx+1}: ${st.title}`;

    const meta = document.createElement("div");
    meta.className = "step-meta";

    const pill = document.createElement("span");
    pill.className = "pill " + (st.done ? "ok" : "warn");
    pill.textContent = st.done ? "Done" : "Not done";

    const btnToggleDone = document.createElement("button");
    btnToggleDone.className = "small";
    btnToggleDone.textContent = st.done ? "Mark not done" : "Mark done";
    btnToggleDone.onclick = ()=>{
      st.done = !st.done;
      saveState(true);
      renderSteps();
    };

    meta.appendChild(pill);
    meta.appendChild(btnToggleDone);

    const btnUp = document.createElement("button");
    btnUp.className = "small";
    btnUp.textContent = "↑";
    btnUp.title = "Move step up";
    btnUp.onclick = ()=>moveStep(idx, -1);

    const btnDown = document.createElement("button");
    btnDown.className = "small";
    btnDown.textContent = "↓";
    btnDown.title = "Move step down";
    btnDown.onclick = ()=>moveStep(idx, +1);

    const btnInsert = document.createElement("button");
    btnInsert.className = "small";
    btnInsert.textContent = "+ after";
    btnInsert.title = "Insert a new step after this one";
    btnInsert.onclick = ()=>insertStepAfter(idx);

    const btnDup = document.createElement("button");
    btnDup.className = "small";
    btnDup.textContent = "Duplicate";
    btnDup.onclick = ()=>duplicateStep(idx);

    const btnDelStep = document.createElement("button");
    btnDelStep.className = "small";
    btnDelStep.textContent = "Delete step";
    btnDelStep.onclick = ()=>deleteStep(idx);

    meta.appendChild(btnUp);
    meta.appendChild(btnDown);
    meta.appendChild(btnInsert);
    meta.appendChild(btnDup);
    meta.appendChild(btnDelStep);

    top.appendChild(title);
    top.appendChild(meta);

    const body = document.createElement("div");
    body.className = "step-body";

    const left = document.createElement("div");
    const right = document.createElement("div");

    const cmdLabel = document.createElement("div");
    cmdLabel.className = "cmdlabel";
    cmdLabel.textContent = "Command / Procedure";

    const cmd = document.createElement("textarea");
    cmd.value = replaceTokens(st.command || "");
    cmd.oninput = ()=>{ st.command = cmd.value; saveStateDebounced(); };

    const remLabel = document.createElement("div");
    remLabel.className = "cmdlabel";
    remLabel.textContent = "Reminder / Hints";

    const rem = document.createElement("textarea");
    rem.value = replaceTokens(st.reminder || "");
    rem.oninput = ()=>{ st.reminder = rem.value; saveStateDebounced(); };

    const notesLabel = document.createElement("div");
    notesLabel.className = "cmdlabel";
    notesLabel.textContent = "Notes (what happened this run)";

    const notes = document.createElement("textarea");
    notes.value = st.notes || "";
    notes.oninput = ()=>{ st.notes = notes.value; saveStateDebounced(); };

    const act = document.createElement("div");
    act.className = "step-actions";

    const btnRun = document.createElement("button");
    btnRun.className = "small brand";
    btnRun.textContent = "Start run";
    btnRun.onclick = ()=>{
      st.runs = st.runs || [];
      st.runs.push({kind:"run", start: nowStamp(), end:""});
      saveState(true);
      renderSteps();
    };

    const btnRedo = document.createElement("button");
    btnRedo.className = "small";
    btnRedo.textContent = "Start redo";
    btnRedo.onclick = ()=>{
      st.runs = st.runs || [];
      st.runs.push({kind:"redo", start: nowStamp(), end:""});
      saveState(true);
      renderSteps();
    };

    act.appendChild(btnRun);
    act.appendChild(btnRedo);

    const runsWrap = document.createElement("div");
    runsWrap.className = "runs";

    const runTitle = document.createElement("div");
    runTitle.className = "cmdlabel";
    runTitle.textContent = "Run history (timestamps)";

    runsWrap.appendChild(runTitle);

    (st.runs||[]).forEach((r, i)=>{
      const row = document.createElement("div");
      row.className = "runrow";

      const kind = document.createElement("span");
      kind.className = "kind";
      kind.textContent = (r.kind==="redo") ? "[Redo]" : "[Run]";

      const start = document.createElement("input");
      start.value = r.start || "";
      start.size = 18;
      start.oninput = ()=>{ r.start = start.value; saveStateDebounced(); };

      const end = document.createElement("input");
      end.value = r.end || "";
      end.size = 18;
      end.placeholder = "Done time";
      end.oninput = ()=>{ r.end = end.value; saveStateDebounced(); };

      const btnDone = document.createElement("button");
      btnDone.className = "small";
      btnDone.textContent = "Mark done time";
      btnDone.onclick = ()=>{
        r.end = nowStamp();
        saveState(true);
        renderSteps();
      };

      const btnDel = document.createElement("button");
      btnDel.className = "small";
      btnDel.textContent = "Delete";
      btnDel.onclick = ()=>{
        st.runs.splice(i,1);
        saveState(true);
        renderSteps();
      };

      row.appendChild(kind);
      row.appendChild(start);
      row.appendChild(end);
      row.appendChild(btnDone);
      row.appendChild(btnDel);

      runsWrap.appendChild(row);
    });

    left.appendChild(cmdLabel);
    left.appendChild(cmd);
    left.appendChild(remLabel);
    left.appendChild(rem);

    right.appendChild(notesLabel);
    right.appendChild(notes);
    right.appendChild(act);
    right.appendChild(runsWrap);

    body.appendChild(left);
    body.appendChild(right);

    stepEl.appendChild(top);
    stepEl.appendChild(body);

    wrap.appendChild(stepEl);
  });

  renderProgress();
}

function renderProgress(){
  const total = steps.length;
  const done = steps.filter(s=>!!s.done).length;
  const pct = total ? Math.round((done/total)*100) : 0;
  document.getElementById("progText").textContent = pct + "%";
  document.getElementById("progFill").style.width = pct + "%";
  document.getElementById("progMini").textContent = `${done} of ${total} steps marked done`;
}

/*** SOP APPLY ***/
function applySOPInfo(){
  sopInfo.name = document.getElementById("sopName").value.trim();
  sopInfo.id = document.getElementById("sopId").value.trim();
  sopInfo.entity = document.getElementById("sopEntity").value.trim();
  sopInfo.runLabel = document.getElementById("runLabel").value.trim();
  sopInfo.repo = document.getElementById("metaRepo").value.trim() || sopInfo.repo;
  sopInfo.webRoot = document.getElementById("webRoot").value.trim() || sopInfo.webRoot;
  sopInfo.imgFolder = document.getElementById("sopImgFolder").value.trim();
  sopInfo.templateTag = document.getElementById("templateTag").value.trim() || TEMPLATE_TAGLINE_DEFAULT;

  document.getElementById("taglinePill").textContent = sopInfo.templateTag || TEMPLATE_TAGLINE_DEFAULT;
  saveState(true);
  renderSteps();
}

/*** ENHANCEMENTS ***/
function addEnhancement(){
  const main = (document.getElementById("enhMain").value || "").trim();
  if(!main){ alert("Main point is required."); return; }
  const cat = document.getElementById("enhCategory").value;
  const notes = (document.getElementById("enhNotes").value || "").trim();
  enhancements.unshift({
    main,
    category: cat,
    notes,
    ts: nowStamp()
  });
  clearEnhFields();
  saveState(true);
  renderEnhancements();
}
function clearEnhFields(){
  document.getElementById("enhMain").value = "";
  document.getElementById("enhNotes").value = "";
  document.getElementById("enhCategory").value = "Enhancement";
}
function renderEnhancements(){
  const el = document.getElementById("enhList");
  el.innerHTML = "";
  enhancements.forEach((e, idx)=>{
    const wrap = document.createElement("div");
    wrap.className = "enh-item";
    const top = document.createElement("div");
    top.className = "enh-top";

    const left = document.createElement("div");
    left.innerHTML = `<div class="enh-main"></div><div class="enh-ts"></div>`;
    left.querySelector(".enh-main").textContent = e.main;
    left.querySelector(".enh-ts").textContent = e.ts;

    const right = document.createElement("div");
    right.innerHTML = `<span class="enh-cat"></span> <button class="small">Delete</button>`;
    right.querySelector(".enh-cat").textContent = e.category || "Enhancement";
    right.querySelector("button").onclick = ()=>{
      enhancements.splice(idx,1);
      saveState(true);
      renderEnhancements();
    };

    top.appendChild(left);
    top.appendChild(right);
    wrap.appendChild(top);

    if(e.notes){
      const n = document.createElement("div");
      n.className = "enh-notes";
      n.textContent = e.notes;
      wrap.appendChild(n);
    }

    el.appendChild(wrap);
  });
}

/*** EXPORT TEXT ***/
function exportText(){
  const lines = [];

  lines.push("=== SOP BUILD CHECKLIST v8 ===");
  const nm = sopInfo.name||"(not set)";
  const id = sopInfo.id||"(not set)";
  lines.push(`SOP Name : ${nm}`);
  lines.push(`SOP ID   : ${id}`);
  lines.push(`Entity   : ${sopInfo.entity||"(not set)"}`);
  lines.push(`Repo     : ${sopInfo.repo||"(not set)"}`);
  lines.push(`WebRoot  : ${sopInfo.webRoot||"(not set)"}`);
  lines.push(`RunLabel : ${sopInfo.runLabel||"(not set)"}`);
  lines.push(`ImgFolder: ${sopInfo.imgFolder||"(not set)"}`);
  lines.push(`TemplateTag: ${sopInfo.templateTag||TEMPLATE_TAGLINE_DEFAULT}`);
  lines.push(`Exported   : ${buildExportStamp()}`);
  lines.push("");

  lines.push("=== STEP RUN HISTORY ===");
  steps.forEach((st, idx)=>{
    lines.push(`Step ${idx+1}: ${st.title}`);
    const rem = (replaceTokens(st.reminder||"")).replace(/\s+/g," ").trim();
    if(rem) lines.push(`  Reminder: ${rem}`);
    if(!st.runs || !st.runs.length){
      lines.push(`  Runs: (no runs yet)`);
    } else {
      st.runs.forEach((r,i)=>{
        const mark = r.kind==="redo" ? "[Redo]" : "[Run]";
        lines.push(`  ${mark} #${i+1}: Start=${r.start||"(?)"}   Done=${r.end||"(not done)"}`);
      });
    }
    const n = (st.notes||"").replace(/\s+/g," ").trim();
    if(n) lines.push(`  Notes: ${n}`);
    lines.push("");
  });

  lines.push("=== Enhancements / Future Enhancements ===");
  enhancements.forEach((e,i)=>{
    lines.push(`Enh #${i+1}: ${e.main}`);
    lines.push(`   When    : ${e.ts}`);
    if(e.category) lines.push(`   Category: ${e.category}`);
    if(e.notes){
      const flat = e.notes.replace(/\s+/g," ").trim();
      lines.push(`   Notes   : ${flat}`);
    }
    lines.push("");
  });

  const finalText = lines.join("\n");
  const outArea = document.getElementById('exportArea');
  outArea.value = finalText;
  outArea.focus();
  outArea.select();
}

/*** SAVE/LOAD ***/
function saveState(silent){
  const state = { sopInfo, steps, enhancements };
  localStorage.setItem(getStorageKey(), JSON.stringify(state));
  if(!silent) alert("Saved.");
}
function loadState(){
  const raw = localStorage.getItem(getStorageKey());
  if(!raw){ alert("No saved state found."); return; }
  try{
    const st = JSON.parse(raw);
    sopInfo = st.sopInfo || sopInfo;
    steps = st.steps || steps;
    enhancements = st.enhancements || enhancements;
    populateSOPFieldsFromState();
    document.getElementById("taglinePill").textContent = sopInfo.templateTag || TEMPLATE_TAGLINE_DEFAULT;
    renderSteps();
    renderEnhancements();
    alert("Loaded.");
  }catch(e){
    alert("Failed to load state: " + e);
  }
}
function resetEverything(){
  if(!confirm("Reset ALL fields, steps, and enhancements?")) return;
  localStorage.removeItem(getStorageKey());
  location.reload();
}
function populateSOPFieldsFromState(){
  document.getElementById('sopName').value      = sopInfo.name || "";
  document.getElementById('sopId').value        = sopInfo.id || "";
  document.getElementById('sopEntity').value    = sopInfo.entity || "";
  document.getElementById('sopImgFolder').value = sopInfo.imgFolder || "";
  document.getElementById('metaRepo').value     = sopInfo.repo || "/workspaces/SOP_Build";
  document.getElementById('webRoot').value      = sopInfo.webRoot || "/SOP_Stage";
  document.getElementById('runLabel').value     = sopInfo.runLabel || "";
  document.getElementById('templateTag').value  = sopInfo.templateTag || TEMPLATE_TAGLINE_DEFAULT;
}

/*** INIT ***/
populateSOPFieldsFromState();
renderSteps();
renderEnhancements();
