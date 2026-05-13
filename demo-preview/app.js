const files = {
  trainers: "../data/trainers.csv",
  courses: "../data/courses.csv",
  sessions: "../data/sessions.csv",
  workload: "../data/workload_entries.csv",
  evaluations: "../data/evaluation_responses.csv",
  feedback: "../data/feedback_comments.csv",
  signals: "../data/fairness_signals.csv",
};

const categoryColors = {
  Lesgeven: "#176b5b",
  Voorbereiding: "#315f9f",
  Nazorg: "#b9432f",
  Administratie: "#8a7c68",
  "AI/innovatie": "#c77713",
  Materiaalontwikkeling: "#6f4a8e",
  Verplaatsing: "#6a8f3a",
  Overleg: "#2f7f8f",
};

const fmt = new Intl.NumberFormat("nl-BE", { maximumFractionDigits: 1 });

function parseCsv(text) {
  const rows = [];
  let cell = "";
  let row = [];
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    const next = text[i + 1];
    if (char === '"' && quoted && next === '"') {
      cell += '"';
      i += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      row.push(cell);
      cell = "";
    } else if ((char === "\n" || char === "\r") && !quoted) {
      if (char === "\r" && next === "\n") i += 1;
      row.push(cell);
      if (row.some((value) => value.length)) rows.push(row);
      row = [];
      cell = "";
    } else {
      cell += char;
    }
  }
  if (cell || row.length) {
    row.push(cell);
    rows.push(row);
  }
  const headers = rows.shift();
  return rows.map((values) => Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""])));
}

async function loadData() {
  const entries = await Promise.all(
    Object.entries(files).map(async ([name, path]) => {
      const response = await fetch(path);
      if (!response.ok) throw new Error(`Cannot load ${path}`);
      return [name, parseCsv(await response.text())];
    }),
  );
  return Object.fromEntries(entries);
}

function sum(rows, field = "Hours") {
  return rows.reduce((total, row) => total + Number(row[field] || 0), 0);
}

function groupBy(rows, keyFn) {
  return rows.reduce((groups, row) => {
    const key = keyFn(row);
    groups[key] ||= [];
    groups[key].push(row);
    return groups;
  }, {});
}

function weightedAverage(rows) {
  const weighted = rows.reduce((total, row) => total + Number(row.AverageScore) * Number(row.ResponseCount), 0);
  const responses = rows.reduce((total, row) => total + Number(row.ResponseCount), 0);
  return responses ? weighted / responses : 0;
}

function byId(rows, key) {
  return Object.fromEntries(rows.map((row) => [row[key], row]));
}

function renderKpis(data, refs) {
  const total = sum(data.workload);
  const contact = sum(data.workload.filter((row) => row.Category === "Lesgeven"));
  const prep = sum(data.workload.filter((row) => row.Category === "Voorbereiding"));
  const responses = sum(data.evaluations, "ResponseCount");
  const kpis = [
    ["Totale workload", `${fmt.format(total)} u`],
    ["Contacturen", `${fmt.format(contact)} u`],
    ["Prep/contact", `${fmt.format(prep / contact)}x`],
    ["Gem. evaluatie", `${fmt.format(weightedAverage(data.evaluations))}/5`],
    ["Responses", fmt.format(responses)],
  ];
  refs.overviewKpis.innerHTML = kpis.map(([label, value]) => `<div class="kpi"><span>${label}</span><strong>${value}</strong></div>`).join("");
}

function renderBars(target, items, valueKey = "value", options = {}) {
  const max = Math.max(...items.map((item) => item[valueKey]), 1);
  target.innerHTML = items
    .map((item) => {
      const width = Math.max((item[valueKey] / max) * 100, 2);
      const color = item.color || options.color || "var(--accent)";
      return `<div class="bar-row">
        <div class="bar-label">${item.label}</div>
        <div class="track"><div class="fill" style="width:${width}%;background:${color}"></div></div>
        <div class="bar-value">${fmt.format(item[valueKey])}${options.suffix || ""}</div>
      </div>`;
    })
    .join("");
}

function renderSignals(target, data, courseMap, trainerMap, all = false) {
  const rows = all ? data.signals : data.signals.slice(0, 4);
  target.innerHTML = rows
    .map((signal) => {
      const context = signal.TrainerId ? trainerMap[signal.TrainerId].Trainer : courseMap[signal.CourseId]?.Course || "Team";
      return `<article class="signal ${signal.Severity === "High" ? "high" : ""}">
        <strong>${signal.SignalType} · ${context}</strong>
        <p>${signal.Signal}</p>
        <small>${signal.RecommendedAction}</small>
      </article>`;
    })
    .join("");
}

function renderOverview(data, refs, courseMap, trainerMap) {
  renderKpis(data, refs);
  const byCategory = Object.entries(groupBy(data.workload, (row) => row.Category)).map(([label, rows]) => ({
    label,
    value: sum(rows),
    color: categoryColors[label],
  }));
  renderBars(refs.categoryBars, byCategory.sort((a, b) => b.value - a.value));

  const byCourse = Object.entries(groupBy(data.workload.filter((row) => row.CourseId), (row) => row.CourseId)).map(([id, rows]) => ({
    label: courseMap[id].Course,
    value: sum(rows),
  }));
  renderBars(refs.courseBars, byCourse.sort((a, b) => b.value - a.value).slice(0, 5), "value", { suffix: " u" });

  const themes = Object.entries(groupBy(data.feedback, (row) => row.Theme)).map(([label, rows]) => ({
    label,
    value: rows.length,
    color: label === "Materiaal" || label === "Moeilijkheid" ? "var(--accent-2)" : "var(--accent)",
  }));
  renderBars(refs.themeBars, themes.sort((a, b) => b.value - a.value), "value", { suffix: "x" });
  renderSignals(refs.overviewSignals, data, courseMap, trainerMap);
}

function renderTrainer(data, refs, trainerMap) {
  const byTrainer = Object.entries(groupBy(data.workload, (row) => row.TrainerId)).map(([id, rows]) => ({ id, rows }));
  const maxTotal = Math.max(...byTrainer.map((item) => sum(item.rows)), 1);
  const legend = Object.entries(categoryColors)
    .map(([label, color]) => `<span><i style="background:${color}"></i>${label}</span>`)
    .join("");
  const bars = byTrainer
    .map(({ id, rows }) => {
      const trainer = trainerMap[id].Trainer;
      const categories = Object.entries(groupBy(rows, (row) => row.Category));
      const total = sum(rows);
      const segments = categories
        .map(([category, categoryRows]) => {
          const width = (sum(categoryRows) / maxTotal) * 100;
          return `<div class="seg" title="${category}" style="width:${width}%;background:${categoryColors[category] || "#999"}"></div>`;
        })
        .join("");
      return `<div class="stacked-trainer"><strong>${trainer}</strong><div class="stack">${segments}</div><span>${fmt.format(total)} u</span></div>`;
    })
    .join("");

  refs.trainerWorkload.innerHTML = `<section class="panel"><h3>Workloadmix per trainer</h3>${bars}<div class="legend">${legend}</div></section>
    <aside class="callout"><strong>Demo-observatie</strong>
    <p>Lennert heeft veel nieuwe onderwerpen, voorbereiding en nazorg. Jarno heeft minder contacturen, maar zijn innovatie- en dashboardwerk wordt zichtbaar als echte workload.</p>
    <p>Dit ondersteunt planning en gesprek; het is geen trainer-ranking.</p></aside>`;

  const sessionGroups = groupBy(data.sessions, (row) => row.TrainerId);
  const rows = byTrainer.map(({ id, rows: workloadRows }) => {
    const contact = sum(workloadRows.filter((row) => row.Category === "Lesgeven"));
    const total = sum(workloadRows);
    const invisible = total - contact;
    const newTopics = (sessionGroups[id] || []).filter((row) => row.IsNewTopic === "true").length;
    return [trainerMap[id].Trainer, newTopics, `${fmt.format(total)} u`, `${fmt.format(invisible / total * 100)}%`];
  });
  refs.trainerTable.innerHTML = table(["Trainer", "Nieuwe topics", "Totale workload", "Visibility gap"], rows);
}

function renderCourse(data, refs, courseMap) {
  const courseRows = Object.entries(groupBy(data.workload.filter((row) => row.CourseId), (row) => row.CourseId)).map(([id, rows]) => {
    const evaluations = data.evaluations.filter((evaluation) => data.sessions.find((session) => session.SessionId === evaluation.SessionId)?.CourseId === id);
    const prep = sum(rows.filter((row) => row.Category === "Voorbereiding"));
    const contact = sum(rows.filter((row) => row.Category === "Lesgeven"));
    return {
      id,
      label: courseMap[id].Course,
      rows,
      prep,
      contact,
      aftercare: sum(rows.filter((row) => row.Category === "Nazorg")),
      ratio: contact ? prep / contact : 0,
      score: weightedAverage(evaluations),
    };
  });
  renderBars(refs.prepBars, courseRows.sort((a, b) => b.prep - a.prep), "prep", { suffix: " u" });
  renderBars(refs.aftercareBars, [...courseRows].sort((a, b) => b.aftercare - a.aftercare), "aftercare", { suffix: " u", color: "var(--accent-2)" });

  refs.scatter.innerHTML = courseRows
    .map((item) => {
      const x = Math.min((item.ratio / 1.1) * 92 + 4, 94);
      const y = Math.max(8, Math.min(92, (5 - item.score) * 45));
      return `<div class="dot" style="left:${x}%;bottom:${100 - y}%"><span>${item.label}</span></div>`;
    })
    .join("");

  const matrix = courseRows.map((item) => {
    const grouped = groupBy(item.rows, (row) => row.Category);
    return [
      item.label,
      fmt.format(sum(grouped.Lesgeven || [])),
      fmt.format(sum(grouped.Voorbereiding || [])),
      fmt.format(sum(grouped.Nazorg || [])),
      fmt.format(sum(grouped.Materiaalontwikkeling || [])),
    ];
  });
  refs.courseMatrix.innerHTML = table(["Opleiding", "Les", "Prep", "Nazorg", "Materiaal"], matrix);
}

function renderEvaluation(data, refs, courseMap, trainerMap) {
  const sessions = byId(data.sessions, "SessionId");
  const byCourse = Object.entries(groupBy(data.evaluations, (row) => sessions[row.SessionId].CourseId)).map(([id, rows]) => ({
    label: courseMap[id].Course,
    value: weightedAverage(rows),
    color: weightedAverage(rows) < 4 ? "var(--accent-2)" : "var(--accent)",
  }));
  renderBars(refs.scoreCourseBars, byCourse.sort((a, b) => b.value - a.value), "value", { suffix: "/5" });

  const trainerRows = Object.entries(groupBy(data.evaluations, (row) => sessions[row.SessionId].TrainerId)).map(([id, rows]) => [
    trainerMap[id].Trainer,
    `${fmt.format(weightedAverage(rows))}/5`,
    fmt.format(sum(rows, "ResponseCount")),
    [...new Set(rows.map((row) => courseMap[sessions[row.SessionId].CourseId].Course))].join(", "),
  ]);
  refs.scoreTrainer.innerHTML = table(["Trainer", "Score", "Responses", "Context"], trainerRows);

  const audienceRows = Object.entries(groupBy(data.evaluations, (row) => `${sessions[row.SessionId].Audience} · ${sessions[row.SessionId].SessionType}`)).map(([key, rows]) => [
    key,
    `${fmt.format(weightedAverage(rows))}/5`,
    fmt.format(sum(rows, "ResponseCount")),
  ]);
  refs.audienceTable.innerHTML = table(["Doelgroep en type", "Score", "Responses"], audienceRows);

  refs.feedbackTable.innerHTML = table(
    ["Thema", "Sentiment", "Commentaar"],
    data.feedback.slice(0, 8).map((row) => [row.Theme, row.Sentiment, row.Comment]),
  );
}

function renderFairness(data, refs, courseMap, trainerMap) {
  renderSignals(refs.fairnessCards, data, courseMap, trainerMap, true);
  refs.actionsTable.innerHTML = table(
    ["Signaal", "Context", "Aanbevolen actie"],
    data.signals.map((signal) => [
      signal.SignalType,
      signal.TrainerId ? trainerMap[signal.TrainerId].Trainer : courseMap[signal.CourseId]?.Course || "Team",
      signal.RecommendedAction,
    ]),
  );
}

function table(headers, rows) {
  return `<table><thead><tr>${headers.map((header) => `<th>${header}</th>`).join("")}</tr></thead>
    <tbody>${rows.map((row) => `<tr>${row.map((cell) => `<td>${cell}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
}

function setupTabs() {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
      document.querySelectorAll(".report-page").forEach((item) => item.classList.remove("active"));
      tab.classList.add("active");
      document.getElementById(tab.dataset.page).classList.add("active");
      window.history.replaceState(null, "", `#${tab.dataset.page}`);
    });
  });
  const page = window.location.hash.replace("#", "");
  if (page) document.querySelector(`[data-page="${page}"]`)?.click();
}

loadData().then((data) => {
  const trainerMap = byId(data.trainers, "TrainerId");
  const courseMap = byId(data.courses, "CourseId");
  const refs = {
    overviewKpis: document.getElementById("overview-kpis"),
    categoryBars: document.getElementById("category-bars"),
    courseBars: document.getElementById("course-bars"),
    themeBars: document.getElementById("theme-bars"),
    overviewSignals: document.getElementById("overview-signals"),
    trainerWorkload: document.getElementById("trainer-workload"),
    trainerTable: document.getElementById("trainer-table"),
    prepBars: document.getElementById("prep-bars"),
    scatter: document.getElementById("scatter"),
    courseMatrix: document.getElementById("course-matrix"),
    aftercareBars: document.getElementById("aftercare-bars"),
    scoreCourseBars: document.getElementById("score-course-bars"),
    scoreTrainer: document.getElementById("score-trainer"),
    audienceTable: document.getElementById("audience-table"),
    feedbackTable: document.getElementById("feedback-table"),
    fairnessCards: document.getElementById("fairness-cards"),
    actionsTable: document.getElementById("actions-table"),
  };
  renderOverview(data, refs, courseMap, trainerMap);
  renderTrainer(data, refs, trainerMap);
  renderCourse(data, refs, courseMap);
  renderEvaluation(data, refs, courseMap, trainerMap);
  renderFairness(data, refs, courseMap, trainerMap);
  setupTabs();
});
