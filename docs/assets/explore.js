// Explore page: cutoff explorer and applicant browser on the test set (saved predictions from notebook 11)
(async function () {
  const [raw, choices] = await Promise.all([
    fetch("data/applicants.json").then(r => r.json()),
    fetch("data/choices.json").then(r => r.json()),
  ]);
  const apps = raw.rows.map(row => Object.fromEntries(raw.fields.map((f, i) => [f, row[i]])));
  const NAME = { ref: "Reference", A: "Pipeline A", B: "Pipeline B" };
  const COLOR = { ref: "#4c78a8", A: "#f58518", B: "#54a24b" };
  const CUT = { ref: choices.ref.cutoff, A: choices.A.cutoff, B: choices.B.cutoff };
  const pct = v => (100 * v).toFixed(1) + "%";
  const fmt = (v, d = 3) => (v == null ? "-" : v.toFixed(d));

  // ---------------- 1. cutoff explorer ----------------
  let setting = "A";
  const slider = document.getElementById("cut");

  function counts(s, c) {
    let tp = 0, fp = 0, fn = 0, tn = 0;
    for (const a of apps) {
      const flag = a["pd_" + s] >= c;
      if (a.defaulted) flag ? tp++ : fn++; else flag ? fp++ : tn++;
    }
    const prec = tp + fp ? tp / (tp + fp) : 0, rec = tp / (tp + fn);
    const f1 = prec + rec ? 2 * prec * rec / (prec + rec) : 0;
    return { tp, fp, fn, tn, prec, rec, f1, acc: (tp + tn) / apps.length, approved: (tn + fn) / apps.length };
  }
  const grid = Array.from({ length: 97 }, (_, i) => +(0.02 + i * 0.01).toFixed(2));
  const curves = {};
  ["ref", "A", "B"].forEach(s => { curves[s] = grid.map(c => counts(s, c)); });

  function drawCut() {
    const c = +slider.value;
    document.getElementById("cutVal").textContent = c.toFixed(2);
    const k = counts(setting, c);
    document.getElementById("cm").innerHTML = `
      <div class="h"></div><div class="h">predicted: repay (approve)</div><div class="h">predicted: default (decline)</div>
      <div class="h">actually<br>repaid</div><div class="tn"><b>${k.tn.toLocaleString()}</b>good customers approved</div>
      <div class="fp"><b>${k.fp.toLocaleString()}</b>good customers declined</div>
      <div class="h">actually<br>defaulted</div><div class="fn"><b>${k.fn.toLocaleString()}</b>defaulters approved (missed)</div>
      <div class="tp"><b>${k.tp.toLocaleString()}</b>defaulters caught</div>`;
    document.getElementById("cutMetrics").innerHTML = [
      ["F1", fmt(k.f1)], ["precision", fmt(k.prec)], ["recall", fmt(k.rec)],
      ["accuracy", fmt(k.acc)], ["approved", pct(k.approved)]].map(m => `<div><b>${m[1]}</b><span>${m[0]}</span></div>`).join("");
    const ch = counts(setting, CUT[setting]);
    document.getElementById("cutStory").innerHTML =
      `<b>${NAME[setting]}</b>, cutoff ${c.toFixed(2)}: of the ${(k.tp + k.fn).toLocaleString()} test applicants who defaulted, ` +
      `<b>${k.tp.toLocaleString()} are caught</b> and ${k.fn.toLocaleString()} are missed; of the ${(k.tn + k.fp).toLocaleString()} who repaid, ` +
      `${k.fp.toLocaleString()} are wrongly declined. At the cutoff chosen on the training set (${CUT[setting].toFixed(3)}) F1 is ${fmt(ch.f1)}` +
      (Math.abs(c - CUT[setting]) > 0.005 ? `; here it is ${fmt(k.f1)}.` : ".");
    const cv = curves[setting];
    const traces = [
      { x: grid, y: cv.map(r => r.prec), name: "precision", line: { color: "#4c78a8" } },
      { x: grid, y: cv.map(r => r.rec), name: "recall", line: { color: "#e45756" } },
      { x: grid, y: cv.map(r => r.f1), name: "F1", line: { color: "#111", width: 3 } },
    ];
    Plotly.react("cutChart", traces, {
      height: 360, margin: { t: 30, r: 10, b: 50, l: 50 }, font: { size: 13 },
      xaxis: { title: "cutoff (decline if PD ≥ cutoff)", range: [0, 1] }, yaxis: { range: [0, 1.02], title: "test-set score" },
      legend: { orientation: "h", y: 1.13 },
      shapes: [
        { type: "line", x0: c, x1: c, y0: 0, y1: 1, line: { color: COLOR[setting], width: 3 } },
        { type: "line", x0: CUT[setting], x1: CUT[setting], y0: 0, y1: 1, line: { color: "#555", dash: "dash", width: 1.5 } }],
      annotations: [{ x: CUT[setting], y: 1.02, text: "chosen", showarrow: false, font: { size: 11, color: "#555" } }],
    }, { displayModeBar: false, responsive: true });
  }
  function setSetting(s) {
    setting = s;
    document.querySelectorAll("#cutSetting button").forEach(b => b.classList.toggle("on", b.dataset.v === s));
    slider.value = CUT[s].toFixed(2); drawCut();
  }
  document.querySelectorAll("#cutSetting button").forEach(b => b.addEventListener("click", () => setSetting(b.dataset.v)));
  slider.addEventListener("input", drawCut);
  document.getElementById("cutReset").addEventListener("click", () => setSetting(setting));
  setSetting("A");

  // ---------------- 2. applicant browser ----------------
  const ids = { type: "fType", pipe: "fPipe", home: "fHome", grade: "fGrade", lti: "fLti" };
  const val = k => document.getElementById(ids[k]).value;
  const declined = (a, s) => a["pd_" + s] >= CUT[s];
  let current = [], selected = null;

  function matches(a) {
    const s = val("pipe"), t = val("type");
    if (t === "missed" && !(a.defaulted && !declined(a, s))) return false;
    if (t === "falsealarm" && !(!a.defaulted && declined(a, s))) return false;
    if (t === "caught" && !(a.defaulted && declined(a, s))) return false;
    if (t === "disagree" && declined(a, "A") === declined(a, "B")) return false;
    if (val("home") && a.home !== val("home")) return false;
    if (val("grade") && a.grade !== val("grade")) return false;
    if (val("lti")) {
      const [lo, hi] = val("lti").split("-").map(Number);
      if (!(a.lti > lo && a.lti <= hi) && !(lo === 0 && a.lti === 0)) return false;
    }
    return true;
  }
  function decision(a, s) {
    return declined(a, s) ? '<span class="dec-no">decline</span>' : '<span class="dec-ok">approve</span>';
  }
  function showCard(a) {
    const rateCell = (r, s) => declined(a, s) ? `<span style="color:#5b6370">no rate (declined); model estimate ${fmt(r, 2)}%</span>` : `<b>${fmt(r, 2)}%</b>`;
    document.getElementById("appCard").innerHTML = `
      <h3 style="margin-top:0">Test applicant · actually <span class="${a.defaulted ? "dec-no" : "dec-ok"}">${a.defaulted ? "DEFAULTED" : "repaid"}</span></h3>
      <div class="table-wrap"><table>
        <tr><td>Age / income</td><td>${a.age} years · $${Math.round(a.income).toLocaleString()} a year</td></tr>
        <tr><td>Home / employment</td><td>${a.home} · ${a.emp == null ? "unknown" : a.emp + " years"}</td></tr>
        <tr><td>Loan</td><td>$${Math.round(a.amount).toLocaleString()} for ${a.intent.toLowerCase()} · ${Math.round(a.lti * 100)}% of income</td></tr>
        <tr><td>Credit history</td><td>${a.hist} years · past default on file: ${a.pastdef === "Y" ? "yes" : "no"}</td></tr>
        <tr><td>Lender's grade / rate</td><td>${a.grade} · ${a.rate == null ? "not recorded" : a.rate.toFixed(2) + "%"}</td></tr>
      </table></div>
      <div class="table-wrap"><table>
        <tr><th>Setting</th><th class="num">PD</th><th>Decision</th><th>Suggested rate</th></tr>
        <tr><td><span class="tag ref">Reference</span></td><td class="num">${fmt(a.pd_ref)}</td><td>${decision(a, "ref")}</td><td style="color:#5b6370">rate already known</td></tr>
        <tr><td><span class="tag A">Pipeline A</span></td><td class="num">${fmt(a.pd_A)}</td><td>${decision(a, "A")}</td><td>${a.rate_A == null ? "-" : rateCell(a.rate_A, "A")}</td></tr>
        <tr><td><span class="tag B">Pipeline B</span></td><td class="num">${fmt(a.pd_B)}</td><td>${decision(a, "B")}</td><td>${a.rate_B == null ? "-" : rateCell(a.rate_B, "B")}</td></tr>
      </table></div>
      <p style="font-size:13px;color:#5b6370;margin-bottom:0">PD = predicted probability of default. Cutoffs: Reference ${CUT.ref.toFixed(3)},
      A ${CUT.A.toFixed(3)}, B ${CUT.B.toFixed(3)}. Suggested rates are only offered to approved applicants; rates are shown only for applicants whose actual rate is recorded.</p>`;
  }
  function renderList() {
    current = apps.filter(matches);
    document.getElementById("fCount").textContent =
      `${current.length.toLocaleString()} of ${apps.length.toLocaleString()} test applicants match (showing up to 200).`;
    const s = val("pipe");
    let html = `<table><tr><th>Age</th><th>Income</th><th>Home</th><th>Grade</th><th>Loan/inc</th><th class="num">PD (${NAME[s]})</th><th>Outcome</th></tr>`;
    current.slice(0, 200).forEach((a, i) => {
      html += `<tr data-i="${i}"><td>${a.age}</td><td>$${Math.round(a.income / 1000)}k</td><td>${a.home}</td><td>${a.grade}</td>
        <td>${Math.round(a.lti * 100)}%</td><td class="num">${fmt(a["pd_" + s])}</td>
        <td class="${a.defaulted ? "dec-no" : "dec-ok"}">${a.defaulted ? "defaulted" : "repaid"}</td></tr>`;
    });
    document.getElementById("appList").innerHTML = html + "</table>";
    document.querySelectorAll("#appList tr[data-i]").forEach(tr => tr.addEventListener("click", () => {
      document.querySelectorAll("#appList tr").forEach(x => x.classList.remove("sel"));
      tr.classList.add("sel"); showCard(current[+tr.dataset.i]);
    }));
    if (current.length) showCard(current[0]);
    else document.getElementById("appCard").innerHTML = "<p>No test applicant matches these filters.</p>";
  }
  Object.values(ids).forEach(id => document.getElementById(id).addEventListener("change", renderList));
  document.getElementById("fRandom").addEventListener("click", () => {
    if (!current.length) return;
    const i = Math.floor(Math.random() * Math.min(current.length, 200));
    document.querySelectorAll("#appList tr").forEach(x => x.classList.remove("sel"));
    const tr = document.querySelector(`#appList tr[data-i="${i}"]`);
    if (tr) { tr.classList.add("sel"); tr.scrollIntoView({ block: "nearest" }); }
    showCard(current[i]);
  });
  renderList();
})();
