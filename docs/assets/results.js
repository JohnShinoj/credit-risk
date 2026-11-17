// Results page: interactive comparison of every model (validation scores from notebooks 06-10)
(async function () {
  const [clf, rate] = await Promise.all([
    fetch("data/validation_classification.json").then(r => r.json()),
    fetch("data/validation_rate.json").then(r => r.json()),
  ]);
  const SETTINGS = ["Reference (rate + grade)", "Pipeline A (grade)", "Pipeline B (newcomer)"];
  const COLORS = { "Reference (rate + grade)": "#4c78a8", "Pipeline A (grade)": "#f58518", "Pipeline B (newcomer)": "#54a24b" };
  const CLF_ORDER = ["Random Forest", "Tree", "RBF SVM", "RBF SVM + SMOTE", "Linear SVM", "Linear SVM + SMOTE", "LogReg", "LogReg + SMOTE"];
  const RATE_ORDER = ["Linear regression", "Ridge", "Lasso", "Random Forest regressor", "Gradient boosting regressor"];
  const METRICS = {
    clf: [["F1", "F1 (higher is better)", false], ["precision", "Precision", false], ["recall", "Recall", false],
          ["ROC-AUC", "ROC-AUC", false], ["Brier", "Brier score (lower is better)", true], ["accuracy", "Accuracy", false]],
    rate: [["R2", "R² (higher is better)", false], ["RMSE", "RMSE in pp (lower is better)", true], ["MAE", "MAE in pp (lower is better)", true]],
  };
  // best input set per rate model and pipeline (lowest RMSE), excluding the "mean rate" floor
  const bestRate = {};
  rate.filter(r => r.model !== "Mean rate (no model)").forEach(r => {
    const k = r.setting + "|" + r.model;
    if (!bestRate[k] || r.RMSE < bestRate[k].RMSE) bestRate[k] = r;
  });
  let task = "clf";
  const sel = document.getElementById("metric");

  function fillMetrics() {
    sel.innerHTML = METRICS[task].map(m => `<option value="${m[0]}">${m[1]}</option>`).join("");
  }
  function draw() {
    const m = sel.value, lowerBetter = METRICS[task].find(x => x[0] === m)[2];
    const settings = task === "clf" ? SETTINGS : SETTINGS.slice(1);
    const order = task === "clf" ? CLF_ORDER : RATE_ORDER;
    const get = (s, model) => task === "clf"
      ? (clf.find(r => r.setting === s && r.model === model) || {})[m]
      : (bestRate[s + "|" + model] || {})[m];
    const traces = settings.map(s => ({
      type: "bar", name: s, x: order, y: order.map(o => get(s, o)), marker: { color: COLORS[s] },
      hovertemplate: "%{x}<br>" + s + "<br>" + m + " = %{y:.4f}<extra></extra>",
    }));
    Plotly.react("cmpChart", traces, {
      barmode: "group", margin: { t: 30, r: 10, b: 110, l: 60 }, height: 430,
      yaxis: { title: METRICS[task].find(x => x[0] === m)[1], rangemode: "tozero" },
      legend: { orientation: "h", y: 1.12 }, xaxis: { tickangle: -25 }, font: { size: 13 },
    }, { displayModeBar: false, responsive: true });
    // table with the best value per setting highlighted
    let html = "<table><tr><th>Model</th>" + settings.map(s => `<th class="num">${s}</th>`).join("") + "</tr>";
    const best = {};
    settings.forEach(s => {
      const vals = order.map(o => get(s, o)).filter(v => v != null);
      best[s] = lowerBetter ? Math.min(...vals) : Math.max(...vals);
    });
    order.forEach(o => {
      html += `<tr><td>${o}</td>` + settings.map(s => {
        const v = get(s, o);
        const isBest = v != null && Math.abs(v - best[s]) < 1e-9;
        return `<td class="num"${isBest ? ' style="background:#eef7f1;font-weight:700"' : ""}>${v == null ? "-" : v.toFixed(4)}</td>`;
      }).join("") + "</tr>";
    });
    html += "</table>";
    if (task === "rate") html += '<p style="font-size:13px;color:#5b6370">Each cell uses that model\'s best input set (notebooks 07 and 09). The Reference setting has no rate model: its rate is already known.</p>';
    document.getElementById("cmpTable").innerHTML = html;
  }
  document.querySelectorAll("#task button").forEach(b => b.addEventListener("click", () => {
    document.querySelectorAll("#task button").forEach(x => x.classList.toggle("on", x === b));
    task = b.dataset.v; fillMetrics(); draw();
  }));
  sel.addEventListener("change", draw);
  fillMetrics(); draw();
})();
