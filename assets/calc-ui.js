"use strict";
/* Calculator UI: reads the embedded price data, computes locally. */
(function () {
  var dataEl = document.getElementById("price-data");
  var data = JSON.parse(dataEl.textContent);
  var sel = document.getElementById("model");
  data.models.forEach(function (m) {
    var o = document.createElement("option");
    o.value = m.id;
    o.textContent = m.provider + " — " + m.id +
      " ($" + (m.input_per_token * 1e6).toFixed(2) + " / $" +
      (m.output_per_token * 1e6).toFixed(2) + " per 1M tokens)";
    sel.appendChild(o);
  });
  function fmt(n) { return "$" + n.toFixed(n < 1 ? 4 : 2); }
  function update() {
    var m = data.models.find(function (x) { return x.id === sel.value; });
    if (!m) return;
    var inp = parseFloat(document.getElementById("inp").value) || 0;
    var out = parseFloat(document.getElementById("out").value) || 0;
    var req = parseFloat(document.getElementById("req").value) || 0;
    var r = window.CWCalc.computeCost(m, inp, out, req);
    document.getElementById("result").innerHTML =
      "Per request: <strong>" + fmt(r.perRequest) + "</strong> · " +
      "Per day: <strong>" + fmt(r.daily) + "</strong> · " +
      "Per month (30 days): <strong>" + fmt(r.monthly) + "</strong>";
  }
  ["model", "inp", "out", "req"].forEach(function (id) {
    document.getElementById(id).addEventListener("input", update);
  });
  update();
})();
