// Interactive model-fitting demos for "What is Machine Learning?".
//
// Every `.fit-demo[data-stage]` element on the page becomes one demo:
//   1:   data + line, slope slider (intercept fixed)
//   2:   same, plus the cost traced for every slope the reader tries
//   3:   slope and intercept sliders, plus a cost map over both parameters
//   4.1: curved data (y = a·x²), a line with slope and intercept: no good fit
//   4.2: same data, model a·x² + b·x + c with b and c locked at 0
//   4.3: data from a·x² + b·x + c, all three parameters free
//   4.4: data from a degree-4 curve; the slider sets the degree, the best
//        parameters for that degree are computed, the cost is traced per degree
//   5:   the 4.4 demo plus test data behind a toggle: training and test cost
//        per degree
//   6:   classification: two classes in the (x₁, x₂) plane, a straight line as
//        the decision boundary, misclassified points counted
// Colors come from CSS custom properties in styles.css, so the charts follow
// the site's light/dark toggle.

(() => {
  "use strict";

  // Sections 1-3: roughly linear data.
  const LINE_DATA = [
    [0.8, 3.5], [1.7, 3.0], [2.6, 7.8], [3.4, 7.1], [4.5, 11.3],
    [5.3, 9.7], [6.2, 14.0], [7.1, 17.0], [8.0, 15.8], [9.2, 19.0],
  ];
  // Section 4.1-4.2: generated from y = 0.8·x² plus noise.
  const SQUARE_DATA = [
    [-4.6, 16.2], [-3.3, 9.2], [-2.7, 6.2], [-1.8, 1.9], [-0.6, 2.3],
    [0.6, 1.1], [1.7, 1.1], [2.6, 4.4], [3.5, 10.1], [4.8, 18.7],
  ];
  // Section 4.3 and 5: generated from y = 0.5·x² + 1.2·x + 2 plus noise.
  const QUAD_DATA = [
    [-4.5, 7.2], [-3.5, 3.6], [-2.5, 1.9], [-1.7, 2.1], [-0.7, 2.1],
    [0.7, 2.6], [1.5, 4.6], [2.4, 6.0], [3.8, 15.5], [4.8, 19.1],
  ];
  // Section 4.4: generated from a degree-4 curve plus noise (sd 0.96):
  // y = 6.8 − 5.08·t − 1.71·t² + 6.98·t³ + 5.6·t⁴, with t = x / 5.
  // Training cost per degree 1-9: 5.08 3.15 2.15 1.08 0.46 0.23 0.16 0.06 0.
  const QUARTIC_DATA = [
    [-4.8, 10.0], [-3.4, 6.9], [-2.7, 7.1], [-1.5, 8.4], [-0.5, 8.2],
    [0.6, 5.4], [1.5, 4.5], [2.8, 3.1], [3.7, 8.6], [4.6, 10.7],
  ];
  // Section 6: [x₁, x₂, class], class 0 = A, 1 = B. A straight line separates
  // the classes (e.g. x₂ = 0.9·x₁ + 1.2); every point is at least 0.55 from it.
  const CLASS_DATA = [
    [0.8, 4.0, 1], [1.2, 7.6, 1], [1.4, 5.8, 1], [1.5, 1.4, 0], [1.7, 3.6, 1],
    [3.9, 9.0, 1], [4.0, 5.8, 1], [4.0, 6.8, 1], [4.7, 3.1, 0], [4.8, 3.9, 0],
    [5.1, 6.7, 1], [5.8, 5.2, 0], [5.9, 3.1, 0], [5.9, 2.2, 0], [5.9, 9.3, 1],
    [6.3, 8.2, 1], [6.3, 4.7, 0], [7.1, 3.3, 0], [8.3, 4.3, 0], [8.9, 7.7, 0],
  ];
  const CLASS_NAMES = ["A", "B"];

  // Section 5: test data from the same curve. Test cost per degree 1-9, with
  // each degree fitted to QUARTIC_DATA: 1.91 1.22 0.89 0.49 0.89 1.80 2.11
  // 4.49 11.21 (lowest at 4).
  const QUARTIC_TEST = [
    [-4.3, 7.7], [-2.9, 6.5], [-1.9, 8.0], [-0.6, 6.4],
    [0.5, 6.0], [1.8, 4.9], [2.8, 5.5], [4.3, 8.9],
  ];

  const GOOD_FIT = 1.1; // "great fit" when the cost is within 10% of the minimum
  const COST_MAX = 130; // y-axis top of the stage-2 cost plot
  const NS = "http://www.w3.org/2000/svg";

  // Parameters. `unit` is how the term is written in the equation, `phi` its
  // feature: every model here is a sum of parameter × feature.
  const P = {
    slope: { key: "s", label: "Slope", unit: "·x", phi: (x) => x },
    intercept: { key: "b", label: "Intercept", unit: "", phi: () => 1 },
    a: { key: "a", label: "a", unit: "·x²", phi: (x) => x * x },
    b: { key: "b", label: "b", unit: "·x", phi: (x) => x },
    c: { key: "c", label: "c", unit: "", phi: () => 1 },
  };
  const SLOPE = { min: 0, max: 4, step: 0.01, digits: 2 };
  const INTERCEPT = { min: -4, max: 6, step: 0.1, digits: 1 };
  const LINE_AXES = { x: [0, 10], xTicks: [0, 10, 2], y: [0, 24], yTicks: [0, 24, 4] };
  const CURVE_AXES = { x: [-5, 5], xTicks: [-4, 4, 2], y: [0, 24], yTicks: [0, 24, 4] };
  const DEGREE_AXES = { ...CURVE_AXES, y: [0, 16], yTicks: [0, 16, 4] };
  const DEGREES = { min: 1, max: 9, init: 1 };
  const A_RANGE = { min: -0.5, max: 1.5, step: 0.01, digits: 2 };
  const B_RANGE = { min: -3, max: 3, step: 0.1, digits: 1 };
  const C_RANGE = { min: -4, max: 8, step: 0.1, digits: 1 };
  const QUADRATIC = (init, locked) => [
    { ...P.a, range: A_RANGE, init: init[0] },
    { ...P.b, range: B_RANGE, init: init[1], locked },
    { ...P.c, range: C_RANGE, init: init[2], locked },
  ];

  // `locked: "hidden"` fixes a parameter without showing it; "shown" draws a
  // greyed-out slider so the reader sees the term exists but cannot move it.
  const STAGES = {
    1: {
      data: LINE_DATA, axes: LINE_AXES, residuals: false,
      params: [{ ...P.slope, range: SLOPE, init: 0.5 }, { ...P.intercept, range: INTERCEPT, init: 1, locked: "hidden" }],
    },
    2: {
      data: LINE_DATA, axes: LINE_AXES, side: "curve",
      params: [{ ...P.slope, range: SLOPE, init: 0 }, { ...P.intercept, range: INTERCEPT, init: 1, locked: "hidden" }],
    },
    3: {
      data: LINE_DATA, axes: LINE_AXES, side: "map",
      params: [{ ...P.slope, range: SLOPE, init: 0.5 }, { ...P.intercept, range: INTERCEPT, init: 4 }],
    },
    4.1: {
      data: SQUARE_DATA, axes: CURVE_AXES, badge: "Best a line can do",
      params: [
        { ...P.slope, range: { min: -3, max: 3, step: 0.01, digits: 2 }, init: 1.5 },
        { ...P.intercept, range: { min: -4, max: 16, step: 0.1, digits: 1 }, init: 2 },
      ],
    },
    4.2: { data: SQUARE_DATA, axes: CURVE_AXES, params: QUADRATIC([0.3, 0, 0], "shown") },
    4.3: { data: QUAD_DATA, axes: CURVE_AXES, params: QUADRATIC([0.3, 0, 0]) },
    4.4: { data: QUARTIC_DATA, axes: DEGREE_AXES, degree: DEGREES },
    5: { data: QUARTIC_DATA, test: QUARTIC_TEST, axes: DEGREE_AXES, degree: DEGREES },
    6: {
      classify: true, data: CLASS_DATA,
      params: [
        { ...P.slope, range: { min: -1, max: 3, step: 0.01, digits: 2 }, init: 0 },
        { ...P.intercept, range: { min: -4, max: 10, step: 0.1, digits: 1 }, init: 5 },
      ],
    },
  };

  // Lighter = lower cost, in both themes, so the page text stays true.
  const RAMP = {
    light: ["#f2f8fe", "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec",
            "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95"],
    dark: ["#cde2fb", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5",
           "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"],
  };

  let uid = 0;

  // ---------- model maths ----------

  const predict = (params, p, x) => params.reduce((sum, q) => sum + p[q.key] * q.phi(x), 0);

  const cost = (params, p, data) =>
    data.reduce((sum, [x, y]) => sum + (y - predict(params, p, x)) ** 2, 0) / data.length;

  // Least squares: weights w minimising the mean of (y − Σ w_k·feats(x)_k)².
  // Normal equations solved by Gaussian elimination with partial pivoting.
  function leastSquares(feats, data) {
    const rows = data.map(([x, y]) => [feats(x), y]);
    const k = rows[0][0].length;
    const A = Array.from({ length: k }, () => new Array(k + 1).fill(0));
    for (const [f, y] of rows) {
      for (let i = 0; i < k; i++) {
        for (let j = 0; j < k; j++) A[i][j] += f[i] * f[j];
        A[i][k] += f[i] * y;
      }
    }
    for (let i = 0; i < k; i++) {
      let piv = i;
      for (let r = i + 1; r < k; r++) if (Math.abs(A[r][i]) > Math.abs(A[piv][i])) piv = r;
      [A[i], A[piv]] = [A[piv], A[i]];
      for (let r = i + 1; r < k; r++) {
        const m = A[r][i] / A[i][i];
        for (let c = i; c <= k; c++) A[r][c] -= m * A[i][c];
      }
    }
    const w = new Array(k).fill(0);
    for (let i = k - 1; i >= 0; i--) {
      let s = A[i][k];
      for (let j = i + 1; j < k; j++) s -= A[i][j] * w[j];
      w[i] = s / A[i][i];
    }
    return w;
  }

  // Best values for the free parameters, locked ones held at their value.
  // Used only for the "great fit" feedback.
  function bestFit(params, p, data) {
    const free = params.filter((q) => !q.locked);
    const lockedPart = (x) => params.filter((q) => q.locked).reduce((s, q) => s + p[q.key] * q.phi(x), 0);
    const w = leastSquares((x) => free.map((q) => q.phi(x)), data.map(([x, y]) => [x, y - lockedPart(x)]));
    const out = { ...p };
    free.forEach((q, i) => { out[q.key] = w[i]; });
    return out;
  }

  // Best polynomial of a given degree. x is scaled to [−1, 1] first so that
  // high powers stay well conditioned; returns the prediction function.
  function polyFit(degree, data, xMax) {
    const feats = (x) => Array.from({ length: degree + 1 }, (_, k) => (x / xMax) ** k);
    const w = leastSquares(feats, data);
    return (x) => feats(x).reduce((s, f, k) => s + w[k] * f, 0);
  }

  // ---------- small helpers ----------

  function svgEl(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {})) e.setAttribute(k, v);
    if (parent) parent.appendChild(e);
    return e;
  }

  function htmlEl(tag, className, parent, text) {
    const e = document.createElement(tag);
    if (className) e.className = className;
    if (text !== undefined) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }

  function scale([d0, d1], [r0, r1]) {
    const f = (v) => r0 + ((v - d0) / (d1 - d0)) * (r1 - r0);
    f.invert = (p) => d0 + ((p - r0) / (r1 - r0)) * (d1 - d0);
    return f;
  }

  const ticks = (min, max, step) => {
    const out = [];
    for (let v = min; v <= max + 1e-9; v += step) out.push(+v.toFixed(6));
    return out;
  };

  const snap = (v, { min, max, step }) =>
    Math.min(max, Math.max(min, Math.round((v - min) / step) * step + min));

  const fmt = (v, digits) => (Math.abs(v) < 1e-9 ? 0 : v).toFixed(digits);

  // "ŷ = 0.50·x + 1": locked values that are whole numbers print without decimals.
  function equation(params, p) {
    return "ŷ = " + params.map((q, i) => {
      const v = p[q.key];
      const abs = Math.abs(v) < 1e-9 ? 0 : Math.abs(v);
      const num = q.locked && Number.isInteger(abs) ? String(abs) : fmt(abs, q.range.digits);
      const sign = v < -1e-9 ? "−" : "+";
      return (i === 0 ? (sign === "−" ? "−" : "") : ` ${sign} `) + num + q.unit;
    }).join("");
  }

  const isDark = () => document.body.classList.contains("quarto-dark");

  // ---------- chart frame: axes, grid, ticks ----------

  // Builds an SVG with gridlines, axes and labels inside `host` and returns
  // the scales plus the SVG, so a chart can add its own marks.
  function frame(host, opts) {
    const width = host.clientWidth;
    const height = Math.round(Math.min(width * 0.72, 360));
    const m = { t: 14, r: 14, b: 42, l: 46 };
    host.querySelector("svg")?.remove();

    const svg = svgEl("svg", {
      class: "fit-svg", width, height, viewBox: `0 0 ${width} ${height}`,
      role: "img", "aria-label": opts.label,
    });
    host.appendChild(svg);

    const x = scale(opts.x.domain, [m.l, width - m.r]);
    const y = scale(opts.y.domain, [height - m.b, m.t]);
    const [x0, x1] = opts.x.domain;
    const [y0, y1] = opts.y.domain;

    if (opts.grid !== false) {
      for (const v of opts.y.ticks) {
        svgEl("line", { class: "fit-grid", x1: x(x0), x2: x(x1), y1: y(v), y2: y(v) }, svg);
      }
      for (const v of opts.x.ticks) {
        svgEl("line", { class: "fit-grid", x1: x(v), x2: x(v), y1: y(y0), y2: y(y1) }, svg);
      }
    }
    svgEl("line", { class: "fit-axis", x1: x(x0), x2: x(x1), y1: y(y0), y2: y(y0) }, svg);
    svgEl("line", { class: "fit-axis", x1: x(x0), x2: x(x0), y1: y(y0), y2: y(y1) }, svg);

    for (const v of opts.x.ticks) {
      svgEl("text", { class: "fit-tick", x: x(v), y: y(y0) + 16, "text-anchor": "middle" }, svg)
        .textContent = v < 0 ? `−${-v}` : v;
    }
    for (const v of opts.y.ticks) {
      svgEl("text", { class: "fit-tick", x: x(x0) - 8, y: y(v) + 4, "text-anchor": "end" }, svg)
        .textContent = v < 0 ? `−${-v}` : v;
    }
    svgEl("text", {
      class: "fit-axis-label", x: (x(x0) + x(x1)) / 2, y: height - 6, "text-anchor": "middle",
    }, svg).textContent = opts.x.label;
    svgEl("text", {
      class: "fit-axis-label", x: 0, y: 0, "text-anchor": "middle",
      transform: `translate(12 ${(y(y0) + y(y1)) / 2}) rotate(-90)`,
    }, svg).textContent = opts.y.label;

    const clipId = `fit-clip-${++uid}`;
    const clip = svgEl("clipPath", { id: clipId }, svgEl("defs", {}, svg));
    svgEl("rect", { x: x(x0), y: y(y1), width: x(x1) - x(x0), height: y(y0) - y(y1) }, clip);

    return { svg, x, y, width, height, m, clip: `url(#${clipId})` };
  }

  function tooltip(host) {
    return htmlEl("div", "fit-tooltip", host);
  }

  function showTip(tip, host, px, py, text) {
    tip.textContent = text;
    tip.style.left = `${px}px`;
    tip.style.top = `${py}px`;
    tip.classList.toggle("is-left", px > host.clientWidth * 0.6);
    tip.classList.add("is-visible");
  }

  // ---------- chart 1: data + model ----------

  function dataChart(host, cfg) {
    const { params = [], data, test = [], axes, residuals } = cfg;
    let f, curve, tip, state;
    let trainErr = [];
    let testErr = [];
    let testMarks = [];

    function points(set, isTest) {
      const errs = set.map(() =>
        svgEl("line", { class: `fit-residual${isTest ? " is-test" : ""}`, "clip-path": f.clip },
          residuals ? f.svg : null));
      return errs;
    }

    function marks(set, isTest) {
      const out = [];
      for (const [px, py] of set) {
        const dot = svgEl("circle", {
          class: isTest ? "fit-point-test" : "fit-point", cx: f.x(px), cy: f.y(py), r: isTest ? 4.5 : 5,
        }, f.svg);
        const hit = svgEl("circle", { class: "fit-hit", cx: f.x(px), cy: f.y(py), r: 13 }, f.svg);
        hit.addEventListener("pointerenter", () => {
          if (isTest && !state.showTest) return;
          const pred = model(px);
          const what = isTest ? "test point: " : "";
          const text = residuals
            ? `${what}x = ${px}, y = ${py} · predicted ${fmt(pred, 1)} · error ${fmt(py - pred, 1)}`
            : `x = ${px}, y = ${py}`;
          showTip(tip, host, f.x(px), f.y(py), text);
        });
        hit.addEventListener("pointerleave", () => tip.classList.remove("is-visible"));
        out.push(dot, hit);
      }
      return out;
    }

    function build() {
      f = frame(host, {
        label: test.length
          ? "Scatter plot of the training data, optional test data and the model's curve"
          : "Scatter plot of the data with the model's line",
        x: { domain: axes.x, ticks: ticks(...axes.xTicks), label: "x" },
        y: { domain: axes.y, ticks: ticks(...axes.yTicks), label: "y" },
      });
      tip = host.querySelector(".fit-tooltip") || tooltip(host);
      trainErr = points(data, false);
      testErr = points(test, true);
      curve = svgEl("path", { class: "fit-line", "clip-path": f.clip }, f.svg);
      testMarks = marks(test, true);
      marks(data, false);
      if (state) update(state);
    }

    // The model's prediction: a fitted function (degree demo) or the parameters.
    const model = (x) => (state.f ? state.f(x) : predict(params, state.p, x));
    // Keep wild high-degree curves at a drawable size; the clip hides them.
    const yPx = (v) => Math.max(-1e4, Math.min(1e4, f.y(v)));

    function update(next) {
      state = next;
      const [x0, x1] = axes.x;
      const steps = 240;
      let d = "";
      for (let i = 0; i <= steps; i++) {
        const v = x0 + ((x1 - x0) * i) / steps;
        d += `${i ? "L" : "M"}${f.x(v).toFixed(1)},${yPx(model(v)).toFixed(1)}`;
      }
      curve.setAttribute("d", d);
      const place = (set, errs) => set.forEach(([px, py], i) => {
        errs[i].setAttribute("x1", f.x(px));
        errs[i].setAttribute("x2", f.x(px));
        errs[i].setAttribute("y1", f.y(py));
        errs[i].setAttribute("y2", yPx(model(px)));
      });
      place(data, trainErr);
      place(test, testErr);
      for (const e of [...testErr, ...testMarks]) e.style.display = state.showTest ? "" : "none";
    }

    return { build, update };
  }

  // ---------- chart 2: cost traced along one parameter ----------

  // The curve runs from the slider's minimum up to the current value, so it
  // grows as the reader moves right and shrinks back as they move left.
  function costCurveChart(host, { param, costAt }) {
    let f, path, guide, dot, state;

    function build() {
      f = frame(host, {
        label: `Cost for each ${param.label.toLowerCase()} up to the current one`,
        x: { domain: [param.range.min, param.range.max], ticks: ticks(param.range.min, param.range.max, 1),
             label: param.label.toLowerCase() },
        y: { domain: [0, COST_MAX], ticks: ticks(0, 125, 25), label: "cost" },
      });
      path = svgEl("path", { class: "fit-cost-curve", "clip-path": f.clip }, f.svg);
      guide = svgEl("line", { class: "fit-guide" }, f.svg);
      dot = svgEl("circle", { class: "fit-current", r: 6 }, f.svg);
      if (state) update(state);
    }

    function update(next) {
      state = next;
      const v0 = state.p[param.key];
      const lo = param.range.min;
      const hi = v0;

      const steps = Math.max(1, Math.round((hi - lo) / 0.01));
      let d = "";
      for (let i = 0; i <= steps; i++) {
        const v = lo + ((hi - lo) * i) / steps;
        d += `${i ? "L" : "M"}${f.x(v).toFixed(1)},${f.y(costAt({ ...state.p, [param.key]: v })).toFixed(1)}`;
      }
      path.setAttribute("d", d);

      const c = costAt(state.p);
      guide.setAttribute("x1", f.x(v0));
      guide.setAttribute("x2", f.x(v0));
      guide.setAttribute("y1", f.y(0));
      guide.setAttribute("y2", f.y(Math.min(c, COST_MAX)));
      dot.setAttribute("cx", f.x(v0));
      dot.setAttribute("cy", f.y(Math.min(c, COST_MAX)));
    }

    return { build, update };
  }

  // ---------- chart 2b: cost for each polynomial degree tried ----------

  // With `testCosts`, training is drawn in the training-data color and test
  // in the test color (when shown); the current degree gets a guide line.
  // The axis is scaled to the training costs: higher test costs are drawn as
  // a marker on the top edge.
  function degreeCostChart(host, { range, costs, testCosts }) {
    let f, line, testLine, guide, layer, state;
    const top = Math.ceil(Math.max(...Object.values(costs)));
    const step = top <= 6 ? 1 : 2;
    const split = Boolean(testCosts);

    function build() {
      f = frame(host, {
        label: split
          ? "Training cost and, optionally, test cost for each polynomial degree up to the current one"
          : "Cost for each polynomial degree up to the current one",
        x: { domain: [range.min - 0.5, range.max + 0.5], ticks: ticks(range.min, range.max, 1), label: "degree" },
        y: { domain: [0, top], ticks: ticks(0, top, step), label: "cost" },
      });
      guide = svgEl("line", { class: "fit-guide", style: split ? "" : "display:none" }, f.svg);
      testLine = svgEl("path", { class: "fit-cost-curve is-test", "clip-path": f.clip }, f.svg);
      line = svgEl("path", { class: `fit-cost-curve${split ? " is-train" : ""}` }, f.svg);
      layer = svgEl("g", {}, f.svg);
      if (state) update(state);
    }

    const label = (x, y, text, cls) =>
      svgEl("text", { class: `fit-value ${cls}`, x, y, "text-anchor": "start" }, layer).textContent = text;

    function update(next) {
      state = next;
      const showTest = split && state.showTest;
      const ds = ticks(range.min, state.degree, 1); // from the lowest degree up to the current one
      const path = (vals) => ds.map((d, i) => `${i ? "L" : "M"}${f.x(d)},${Math.max(-1e4, f.y(vals[d]))}`).join("");
      line.setAttribute("d", path(costs));
      testLine.style.display = showTest ? "" : "none";
      if (showTest) testLine.setAttribute("d", path(testCosts));
      guide.setAttribute("x1", f.x(state.degree));
      guide.setAttribute("x2", f.x(state.degree));
      guide.setAttribute("y1", f.y(0));
      guide.setAttribute("y2", f.y(top));

      layer.replaceChildren();
      for (const d of ds) {
        const current = d === state.degree;
        const x = f.x(d);
        const yTrain = f.y(costs[d]);
        const trainCls = split ? `fit-tried is-train${current ? " is-current" : ""}` : current ? "fit-current" : "fit-tried";
        svgEl("circle", { class: trainCls, cx: x, cy: yTrain, r: current ? 6 : 4 }, layer);
        if (!showTest || current) label(x + 5, yTrain - 9, fmt(costs[d], 2), current ? "is-current" : "");
        if (!showTest) continue;

        const v = testCosts[d];
        const over = v > top;
        const yTest = f.y(Math.min(v, top));
        if (over) {
          const r = current ? 7 : 5;
          svgEl("path", {
            class: `fit-tried is-test${current ? " is-current" : ""}`,
            d: `M${x - r},${yTest + r * 0.6} L${x + r},${yTest + r * 0.6} L${x},${yTest - r} Z`,
          }, layer);
        } else {
          svgEl("circle", { class: `fit-tried is-test${current ? " is-current" : ""}`, cx: x, cy: yTest, r: current ? 6 : 4 }, layer);
        }
        if (current || over) {
          // Put the test label on the side away from the training label.
          const below = !over && v < costs[d];
          label(x + 5, below ? yTest + 17 : yTest - 9, `${fmt(v, 2)}${over ? " ↑" : ""}`,
            `is-test${current ? " is-current" : ""}`);
        }
      }
    }

    return { build, update };
  }

  // ---------- chart 4: classification with a straight decision boundary ----------

  // Points above the line x₂ = s·x₁ + b are predicted class B, the rest class A.
  const predictClass = (p, x1, x2) => (x2 > p.s * x1 + p.b ? 1 : 0);

  function classChart(host, { data }) {
    let f, regionA, regionB, line, rings, tip, state;
    const D = [0, 10];

    function build() {
      f = frame(host, {
        label: "Two classes of points in the plane of x₁ and x₂, with the model's decision boundary",
        x: { domain: D, ticks: ticks(0, 10, 2), label: "x₁" },
        y: { domain: D, ticks: ticks(0, 10, 2), label: "x₂" },
      });
      tip = host.querySelector(".fit-tooltip") || tooltip(host);
      regionB = svgEl("path", { class: "fit-region is-b", "clip-path": f.clip }, f.svg);
      regionA = svgEl("path", { class: "fit-region is-a", "clip-path": f.clip }, f.svg);
      line = svgEl("line", { class: "fit-line", "clip-path": f.clip }, f.svg);
      rings = data.map(([x1, x2]) => svgEl("circle", { class: "fit-wrong", cx: f.x(x1), cy: f.y(x2), r: 10 }, f.svg));
      for (const [x1, x2, c] of data) {
        const cx = f.x(x1);
        const cy = f.y(x2);
        if (c === 0) svgEl("circle", { class: "fit-class-a", cx, cy, r: 5.5 }, f.svg);
        else svgEl("rect", { class: "fit-class-b", x: cx - 5, y: cy - 5, width: 10, height: 10 }, f.svg);
        const hit = svgEl("circle", { class: "fit-hit", cx, cy, r: 13 }, f.svg);
        hit.addEventListener("pointerenter", () => {
          const pred = predictClass(state.p, x1, x2);
          showTip(tip, host, cx, cy, `x₁ = ${x1}, x₂ = ${x2} · class ${CLASS_NAMES[c]} · predicted ${CLASS_NAMES[pred]} ${pred === c ? "✓" : "✗"}`);
        });
        hit.addEventListener("pointerleave", () => tip.classList.remove("is-visible"));
      }
      if (state) update(state);
    }

    function update(next) {
      state = next;
      const { s, b } = state.p;
      // Line end points just outside the plot; the regions extend far beyond it and are clipped.
      const [x0, x1] = [D[0] - 1, D[1] + 1];
      const y0 = s * x0 + b;
      const y1 = s * x1 + b;
      const px = (v) => f.x(v).toFixed(1);
      const py = (v) => Math.max(-1e4, Math.min(1e4, f.y(v))).toFixed(1);
      line.setAttribute("x1", px(x0));
      line.setAttribute("y1", py(y0));
      line.setAttribute("x2", px(x1));
      line.setAttribute("y2", py(y1));
      const far = 1e3;
      regionB.setAttribute("d", `M${px(x0)},${py(y0)} L${px(x1)},${py(y1)} L${px(x1)},${py(far)} L${px(x0)},${py(far)} Z`);
      regionA.setAttribute("d", `M${px(x0)},${py(y0)} L${px(x1)},${py(y1)} L${px(x1)},${py(-far)} L${px(x0)},${py(-far)} Z`);
      data.forEach(([a, c2, c], i) => {
        rings[i].style.display = predictClass(state.p, a, c2) === c ? "none" : "";
      });
    }

    return { build, update };
  }

  // ---------- chart 3: cost map over two parameters ----------

  function costMapChart(host, { px: qx, py: qy, costAt, minCost, onPick }) {
    let f, canvas, crossV, crossH, dot, tip, state;
    const X = qx.range;
    const Y = qy.range;
    const at = (s, b) => costAt({ [qx.key]: s, [qy.key]: b });

    function paint() {
      const { x, y } = f;
      const left = x(X.min);
      const top = y(Y.max);
      const w = Math.round(x(X.max) - left);
      const h = Math.round(y(Y.min) - top);
      const dpr = window.devicePixelRatio || 1;

      canvas.style.left = `${left}px`;
      canvas.style.top = `${top}px`;
      canvas.style.width = `${w}px`;
      canvas.style.height = `${h}px`;
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);

      const ramp = (isDark() ? RAMP.dark : RAMP.light).map((hex) => [
        parseInt(hex.slice(1, 3), 16), parseInt(hex.slice(3, 5), 16), parseInt(hex.slice(5, 7), 16),
      ]);
      const corners = [at(X.min, Y.min), at(X.min, Y.max), at(X.max, Y.min), at(X.max, Y.max)];
      const lmin = Math.log(minCost);
      const lmax = Math.log(Math.max(...corners));

      const ctx = canvas.getContext("2d");
      const img = ctx.createImageData(canvas.width, canvas.height);
      for (let j = 0; j < canvas.height; j++) {
        const b = Y.max - ((j + 0.5) / canvas.height) * (Y.max - Y.min);
        for (let i = 0; i < canvas.width; i++) {
          const s = X.min + ((i + 0.5) / canvas.width) * (X.max - X.min);
          const t = (Math.log(at(s, b)) - lmin) / (lmax - lmin);
          const band = Math.min(ramp.length - 1, Math.max(0, Math.floor(t * ramp.length)));
          const [r, g, bl] = ramp[band];
          const k = (j * canvas.width + i) * 4;
          img.data[k] = r;
          img.data[k + 1] = g;
          img.data[k + 2] = bl;
          img.data[k + 3] = 255;
        }
      }
      ctx.putImageData(img, 0, 0);
    }

    function pick(ev) {
      const rect = f.svg.getBoundingClientRect();
      onPick(snap(f.x.invert(ev.clientX - rect.left), X), snap(f.y.invert(ev.clientY - rect.top), Y));
    }

    function hover(ev) {
      const rect = f.svg.getBoundingClientRect();
      const px = ev.clientX - rect.left;
      const py = ev.clientY - rect.top;
      const s = f.x.invert(px);
      const b = f.y.invert(py);
      const inside = s >= X.min && s <= X.max && b >= Y.min && b <= Y.max;
      crossV.style.display = crossH.style.display = inside ? "" : "none";
      if (!inside) {
        tip.classList.remove("is-visible");
        return;
      }
      crossV.setAttribute("x1", px);
      crossV.setAttribute("x2", px);
      crossH.setAttribute("y1", py);
      crossH.setAttribute("y2", py);
      showTip(tip, host, px, py,
        `${qx.label.toLowerCase()} ${fmt(s, X.digits)} · ${qy.label.toLowerCase()} ${fmt(b, Y.digits)} · cost ${fmt(at(s, b), 1)}`);
    }

    function build() {
      if (!canvas) canvas = htmlEl("canvas", "fit-map", host);
      f = frame(host, {
        label: `Cost map: cost for every combination of ${qx.label.toLowerCase()} and ${qy.label.toLowerCase()}`,
        grid: false,
        x: { domain: [X.min, X.max], ticks: ticks(X.min, X.max, 1), label: qx.label.toLowerCase() },
        y: { domain: [Y.min, Y.max], ticks: ticks(Y.min, Y.max, 2), label: qy.label.toLowerCase() },
      });
      tip = host.querySelector(".fit-tooltip") || tooltip(host);
      paint();

      crossV = svgEl("line", {
        class: "fit-crosshair", y1: f.y(Y.min), y2: f.y(Y.max), style: "display:none",
      }, f.svg);
      crossH = svgEl("line", {
        class: "fit-crosshair", x1: f.x(X.min), x2: f.x(X.max), style: "display:none",
      }, f.svg);
      dot = svgEl("circle", { class: "fit-current", r: 7 }, f.svg);

      f.svg.classList.add("is-draggable");
      f.svg.addEventListener("pointerdown", (ev) => {
        f.svg.setPointerCapture(ev.pointerId);
        pick(ev);
      });
      f.svg.addEventListener("pointermove", (ev) => {
        if (f.svg.hasPointerCapture(ev.pointerId)) pick(ev);
        hover(ev);
      });
      f.svg.addEventListener("pointerleave", () => {
        crossV.style.display = crossH.style.display = "none";
        tip.classList.remove("is-visible");
      });
      if (state) update(state);
    }

    function update(next) {
      state = next;
      dot.setAttribute("cx", f.x(state.p[qx.key]));
      dot.setAttribute("cy", f.y(state.p[qy.key]));
    }

    return { build, update, repaint: () => f && paint() };
  }

  // ---------- controls ----------

  function slider(parent, label, range, value, onInput, locked) {
    const wrap = htmlEl("label", `fit-slider${locked ? " is-locked" : ""}`, parent);
    htmlEl("span", "fit-slider-label", wrap, label);
    const input = htmlEl("input", "", wrap);
    Object.assign(input, { type: "range", min: range.min, max: range.max, step: range.step, value });
    if (locked) {
      input.disabled = true;
      wrap.title = `${label} is fixed at ${value} in this model`;
    }
    const out = htmlEl("output", "fit-slider-value", wrap, fmt(value, range.digits));
    const paintTrack = () => {
      const pct = ((input.value - range.min) / (range.max - range.min)) * 100;
      input.style.setProperty("--fit-fill", `${pct}%`);
    };
    input.addEventListener("input", () => {
      out.textContent = fmt(+input.value, range.digits);
      paintTrack();
      onInput(+input.value);
    });
    paintTrack();
    return {
      set(v) {
        input.value = v;
        out.textContent = fmt(v, range.digits);
        paintTrack();
      },
    };
  }

  function toggle(parent, label, onChange) {
    const wrap = htmlEl("label", "fit-toggle", parent);
    const input = htmlEl("input", "", wrap);
    input.type = "checkbox";
    input.setAttribute("role", "switch");
    htmlEl("span", "fit-toggle-track", wrap);
    htmlEl("span", "fit-toggle-label", wrap, label);
    input.addEventListener("change", () => onChange(input.checked));
  }

  function panel(parent, title) {
    const fig = htmlEl("figure", "fit-panel", parent);
    if (title) htmlEl("figcaption", "fit-panel-title", fig, title);
    return htmlEl("div", "fit-chart", fig);
  }

  // Key ("Training data", "Test data") and the "Show test data" switch.
  // Returns the key, whose test entry shows with the class `is-test-on`.
  function testToolbar(parent, onToggle) {
    const bar = htmlEl("div", "fit-toolbar", parent);
    const key = htmlEl("div", "fit-key", bar);
    htmlEl("span", "fit-key-train", key, "Training data");
    htmlEl("span", "fit-key-test", key, "Test data");
    toggle(bar, "Show test data", onToggle);
    return key;
  }

  function costReadout(parent, label) {
    const c = htmlEl("span", "fit-cost", parent);
    htmlEl("span", "fit-cost-label", c, label);
    return { wrap: c, value: htmlEl("strong", "", c) };
  }

  // ---------- stages ----------

  // Re-render the charts when the demo's width changes.
  function onResize(root, buildAll) {
    let lastWidth = root.clientWidth;
    new ResizeObserver(() => {
      if (root.clientWidth !== lastWidth) {
        lastWidth = root.clientWidth;
        buildAll();
      }
    }).observe(root);
  }

  // Degree demo: the reader picks the degree, the parameters are fitted.
  function mountDegree(root, cfg) {
    const { data, test = [], degree: range } = cfg;
    const xMax = Math.max(...cfg.axes.x.map(Math.abs));
    const mse = (fn, set) => set.reduce((s, [x, y]) => s + (y - fn(x)) ** 2, 0) / set.length;
    const fits = {};
    const costs = {};
    const testCosts = test.length ? {} : null;
    for (let d = range.min; d <= range.max; d++) {
      fits[d] = polyFit(d, data, xMax);
      costs[d] = mse(fits[d], data);
      if (testCosts) testCosts[d] = mse(fits[d], test);
    }
    const state = { degree: range.init, showTest: false };

    const plots = htmlEl("div", "fit-plots fit-plots-2", root);
    const legend = test.length ? testToolbar(plots, (on) => {
      state.showTest = on;
      refresh();
    }) : null;
    const charts = [
      dataChart(panel(plots, "Data and best curve of this degree"), { ...cfg, residuals: true }),
      degreeCostChart(panel(plots, "Cost of each degree you try"), { range, costs, testCosts }),
    ];

    const controls = htmlEl("div", "fit-controls", root);
    const sliders = htmlEl("div", "fit-sliders", controls);
    slider(sliders, "Degree", { ...range, step: 1, digits: 0 }, state.degree, (v) => {
      state.degree = v;
      refresh();
    });
    const readout = htmlEl("div", "fit-readout", controls);
    readout.setAttribute("aria-live", "polite");
    const eq = htmlEl("span", "fit-equation", readout);
    const c = costReadout(readout, testCosts ? "Training cost" : "Cost");
    const t = testCosts ? costReadout(readout, "Test cost") : null;

    function refresh() {
      const d = state.degree;
      eq.textContent = `${d + 1} parameters`;
      c.value.textContent = fmt(costs[d], 2);
      if (t) {
        t.value.textContent = fmt(testCosts[d], 2);
        t.wrap.classList.toggle("is-hidden", !state.showTest);
        legend.classList.toggle("is-test-on", state.showTest);
      }
      for (const chart of charts) chart.update({ f: fits[d], degree: d, showTest: state.showTest });
    }

    const buildAll = () => {
      for (const chart of charts) chart.build();
      refresh();
    };
    buildAll();
    onResize(root, buildAll);
  }

  // Classification demo: slope and intercept move the decision boundary.
  function mountClassify(root, cfg) {
    const { data, params } = cfg;
    const state = { p: Object.fromEntries(params.map((q) => [q.key, q.init])) };

    const plots = htmlEl("div", "fit-plots", root);
    const bar = htmlEl("div", "fit-toolbar", plots);
    const key = htmlEl("div", "fit-key", bar);
    htmlEl("span", "fit-key-a", key, "Class A");
    htmlEl("span", "fit-key-b", key, "Class B");
    htmlEl("span", "fit-key-wrong", key, "Misclassified");
    const charts = [classChart(panel(plots, null), { data })];

    const controls = htmlEl("div", "fit-controls", root);
    const sliders = htmlEl("div", "fit-sliders", controls);
    for (const q of params) {
      slider(sliders, q.label, q.range, q.init, (v) => {
        state.p[q.key] = v;
        refresh();
      });
    }
    const readout = htmlEl("div", "fit-readout", controls);
    readout.setAttribute("aria-live", "polite");
    const eq = htmlEl("span", "fit-equation", readout);
    const wrong = costReadout(readout, "Misclassified");
    const acc = costReadout(readout, "Accuracy");
    const badge = htmlEl("span", "fit-badge", readout, "✓ All correct");

    function refresh() {
      const { s, b } = state.p;
      const n = data.filter(([x1, x2, c]) => predictClass(state.p, x1, x2) !== c).length;
      eq.textContent = `boundary: x₂ = ${fmt(s, 2)}·x₁ ${b < 0 ? "−" : "+"} ${fmt(Math.abs(b), 1)}`;
      wrong.value.textContent = `${n} of ${data.length}`;
      acc.value.textContent = `${Math.round((100 * (data.length - n)) / data.length)}%`;
      badge.classList.toggle("is-visible", n === 0);
      for (const chart of charts) chart.update({ p: { ...state.p } });
    }

    const buildAll = () => {
      for (const chart of charts) chart.build();
      refresh();
    };
    buildAll();
    onResize(root, buildAll);
  }

  function mount(root) {
    const cfg = STAGES[root.dataset.stage];
    if (!cfg) return;
    if (cfg.classify) {
      mountClassify(root, cfg);
      return;
    }
    if (cfg.degree) {
      mountDegree(root, cfg);
      return;
    }
    const { params, data } = cfg;
    const stage = root.dataset.stage;
    const state = { p: Object.fromEntries(params.map((q) => [q.key, q.init])) };
    const costAt = (p) => cost(params, p, data);
    const minCost = costAt(bestFit(params, state.p, data));
    const residuals = cfg.residuals !== false;

    const plots = htmlEl("div", `fit-plots${cfg.side ? " fit-plots-2" : ""}`, root);
    const charts = [dataChart(panel(plots, cfg.side ? "Data and model" : null), { ...cfg, residuals })];
    const ctl = {};

    let map = null;
    if (cfg.side === "curve") {
      charts.push(costCurveChart(panel(plots, "Cost of each slope you try"), { param: params[0], costAt }));
    }
    if (cfg.side === "map") {
      const host = panel(plots, "Cost map");
      const [qx, qy] = params;
      map = costMapChart(host, {
        px: qx, py: qy, costAt, minCost,
        onPick: (s, b) => {
          state.p[qx.key] = s;
          state.p[qy.key] = b;
          ctl[qx.key].set(s);
          ctl[qy.key].set(b);
          refresh();
        },
      });
      charts.push(map);
      const key = htmlEl("div", "fit-legend", host.parentElement);
      htmlEl("span", "", key, "Lower cost");
      htmlEl("span", "fit-legend-ramp", key);
      htmlEl("span", "", key, "Higher cost");
    }

    const controls = htmlEl("div", "fit-controls", root);
    const sliders = htmlEl("div", "fit-sliders", controls);
    for (const q of params) {
      if (q.locked === "hidden") continue;
      ctl[q.key] = slider(sliders, q.label, q.range, q.init, (v) => {
        state.p[q.key] = v;
        refresh();
      }, q.locked);
    }

    const readout = htmlEl("div", "fit-readout", controls);
    readout.setAttribute("aria-live", "polite");
    const eq = htmlEl("span", "fit-equation", readout);
    const showCost = stage !== "1";
    const trainCost = showCost ? costReadout(readout, "Cost") : null;
    const badge = htmlEl("span", "fit-badge", readout, cfg.badge ? cfg.badge : "✓ Great fit");

    function refresh() {
      const c = costAt(state.p);
      eq.textContent = equation(params, state.p);
      if (trainCost) trainCost.value.textContent = fmt(c, 2);
      badge.classList.toggle("is-visible", c <= minCost * GOOD_FIT);
      for (const chart of charts) chart.update({ p: { ...state.p }, showTest: false });
    }

    const buildAll = () => {
      for (const chart of charts) chart.build();
      refresh();
    };
    buildAll();
    onResize(root, buildAll);

    if (map) {
      new MutationObserver(map.repaint).observe(document.body, {
        attributes: true, attributeFilter: ["class"],
      });
    }
  }

  function init() {
    document.querySelectorAll(".fit-demo[data-stage]").forEach(mount);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
