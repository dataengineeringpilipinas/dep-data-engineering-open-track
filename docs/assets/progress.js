const OWNER = "dataengineeringpilipinas";
const REPO = "dep-data-engineering-open-track";
const MILESTONES = ["M0", "M1", "M2", "M3", "M4", "M5", "M6"];
const PROCESS_LABELS = [
  "auto-check-pending",
  "waiting-on-prerequisite",
  "ready-for-review",
  "needs-improvement",
  "passed",
];

let allIssues = [];
let enrolledSet = null;
let viewMode = "enrolled";

const sortState = {
  waiting: { col: "days", dir: "desc" },
  pending: { col: "days", dir: "desc" },
  improvement: { col: "days", dir: "desc" },
  all: { col: "days", dir: "desc" },
};

function extract(body, heading) {
  const match = (body || "").match(new RegExp(`###\\s+${heading}\\s*\\n+([^\\n#]+)`, "i"));
  return match ? match[1].trim() : "—";
}

function getStatus(labels) {
  const names = labels.map((label) => label.name);
  if (names.includes("passed")) return "passed";
  if (names.includes("needs-improvement")) return "needs-improvement";
  if (names.includes("waiting-on-prerequisite")) return "waiting-on-prerequisite";
  if (names.includes("ready-for-review")) return "ready-for-review";
  if (names.includes("auto-check-pending")) return "checking";
  return "pending-review";
}

function getMilestone(labels) {
  const names = labels.map((label) => label.name);
  return names.find((name) => /^M\d$/.test(name)) || "?";
}

function enrich(issue) {
  return {
    ...issue,
    _builder: extract(issue.body, "Builder Name"),
    _cohort: extract(issue.body, "Cohort"),
    _repoUrl: extract(issue.body, "GitHub Repo URL"),
    _milestone: getMilestone(issue.labels),
    _status: getStatus(issue.labels),
    _isLate: issue.labels.some((label) => label.name === "late-submission"),
    _days: Math.floor((Date.now() - new Date(issue.created_at).getTime()) / 86400000),
  };
}

function statusBadge(status) {
  const map = {
    passed: ["passed", "Passed"],
    "needs-improvement": ["needs-improvement", "Needs Improvement"],
    "waiting-on-prerequisite": ["waiting-on-prerequisite", "Waiting on prerequisite"],
    "ready-for-review": ["ready-for-review", "Ready for review"],
    "pending-review": ["pending-review", "Pending Review"],
    checking: ["checking", "Checking"],
  };
  const [className, label] = map[status] || ["checking", status];
  return `<span class="progress-badge ${className}">${label}</span>`;
}

function statusBadges(issue) {
  const lateBadge = issue._isLate
    ? '<span class="progress-badge late-submission">Late</span>'
    : "";
  return `<span class="progress-badge-group">${statusBadge(issue._status)}${lateBadge}</span>`;
}

function daysBadge(days, status) {
  if (status === "passed") return `<span class="progress-days ok">${days}d</span>`;
  if (status === "waiting-on-prerequisite") {
    return `<span class="progress-days warn">${days}d queued</span>`;
  }
  if (days >= 5) return `<span class="progress-days breach">${days}d overdue</span>`;
  if (days >= 3) return `<span class="progress-days warn">${days}d waiting</span>`;
  return `<span class="progress-days ok">${days}d</span>`;
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString("en-PH", {
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: "Asia/Manila",
  });
}

function setView(mode) {
  viewMode = mode;
  document.getElementById("btn-enrolled").classList.toggle("active", mode === "enrolled");
  document.getElementById("btn-non-enrolled").classList.toggle("active", mode === "non-enrolled");
  document.getElementById("btn-all").classList.toggle("active", mode === "all");
  document.getElementById("btn-enrolled").setAttribute("aria-pressed", String(mode === "enrolled"));
  document.getElementById("btn-non-enrolled").setAttribute("aria-pressed", String(mode === "non-enrolled"));
  document.getElementById("btn-all").setAttribute("aria-pressed", String(mode === "all"));
  renderAll();
}

function applyFilters(issues) {
  let filtered = issues;

  if (viewMode === "enrolled" && enrolledSet) {
    filtered = filtered.filter((issue) => enrolledSet.has(issue.user.login.toLowerCase()));
  } else if (viewMode === "non-enrolled" && enrolledSet) {
    filtered = filtered.filter((issue) => !enrolledSet.has(issue.user.login.toLowerCase()));
  }

  const query = (document.getElementById("search")?.value || "").toLowerCase().trim();
  const milestoneFilter = document.getElementById("filter-milestone")?.value || "";
  const statusFilter = document.getElementById("filter-status")?.value || "";

  return filtered.filter((issue) => {
    if (
      query &&
      !`${issue._builder} ${issue._cohort} ${issue._milestone}`.toLowerCase().includes(query)
    ) {
      return false;
    }
    if (milestoneFilter && issue._milestone !== milestoneFilter) return false;
    if (statusFilter && issue._status !== statusFilter) return false;
    return true;
  });
}

function applySort(issues, tableKey) {
  const { col, dir } = sortState[tableKey];
  return [...issues].sort((a, b) => {
    let left;
    let right;
    if (col === "builder") {
      left = a._builder;
      right = b._builder;
    } else if (col === "cohort") {
      left = a._cohort;
      right = b._cohort;
    } else if (col === "milestone") {
      left = MILESTONES.indexOf(a._milestone);
      right = MILESTONES.indexOf(b._milestone);
    } else if (col === "days") {
      left = a._days;
      right = b._days;
    } else if (col === "status") {
      left = a._status;
      right = b._status;
    } else {
      left = a.created_at;
      right = b.created_at;
    }
    if (left < right) return dir === "asc" ? -1 : 1;
    if (left > right) return dir === "asc" ? 1 : -1;
    return 0;
  });
}

function thSort(tableKey, col, label) {
  const state = sortState[tableKey];
  const active = state.col === col;
  const icon = active ? (state.dir === "asc" ? "↑" : "↓") : "↕";
  return `<th class="progress-sortable${active ? " is-active" : ""}" scope="col"><button type="button" aria-pressed="${String(active)}" onclick="handleSort('${tableKey}','${col}')">${label} <span class="progress-sort-icon" aria-hidden="true">${icon}</span></button></th>`;
}

function handleSort(tableKey, col) {
  const state = sortState[tableKey];
  if (state.col === col) {
    state.dir = state.dir === "asc" ? "desc" : "asc";
  } else {
    state.col = col;
    state.dir = "asc";
  }
  renderAll();
}

function buildTable(issues, tableKey) {
  if (!issues.length) return `<div class="progress-empty">No submissions here.</div>`;
  const rows = applySort(applyFilters(issues), tableKey);
  if (!rows.length) return `<div class="progress-empty">No results match your filters.</div>`;
  return `<div class="progress-table-wrap"><table class="progress-table">
    <thead><tr>
      ${thSort(tableKey, "builder", "Builder")}
      <th class="progress-hide-mobile" scope="col">Cohort</th>
      ${thSort(tableKey, "milestone", "Milestone")}
      <th class="progress-hide-mobile" scope="col">Submitted</th>
      ${thSort(tableKey, "days", "Days")}
      ${thSort(tableKey, "status", "Status")}
      <th scope="col">Repo</th><th scope="col">Issue</th>
    </tr></thead>
    <tbody>${rows
      .map(
        (issue) => `<tr>
      <td>${issue._builder}</td>
      <td class="progress-hide-mobile">${issue._cohort}</td>
      <td><span class="progress-m-badge">${issue._milestone}</span></td>
      <td class="progress-hide-mobile">${formatDate(issue.created_at)}</td>
      <td>${daysBadge(issue._days, issue._status)}</td>
      <td>${statusBadges(issue)}</td>
      <td>${
        issue._repoUrl !== "—"
          ? `<a href="${issue._repoUrl}" target="_blank" rel="noopener noreferrer">repo<span class="sr-only"> (opens in new tab)</span></a>`
          : "—"
      }</td>
      <td><a href="${issue.html_url}" target="_blank" rel="noopener noreferrer">#${issue.number}<span class="sr-only"> (opens in new tab)</span></a></td>
    </tr>`,
      )
      .join("")}</tbody>
  </table></div>`;
}

function renderAll() {
  const waiting = allIssues.filter((issue) => issue._status === "waiting-on-prerequisite");
  const pending = allIssues.filter(
    (issue) => issue._status === "ready-for-review" || issue._status === "pending-review",
  );
  const improvement = allIssues.filter((issue) => issue._status === "needs-improvement");

  document.getElementById("queue-waiting").innerHTML = buildTable(waiting, "waiting");
  document.getElementById("queue-pending").innerHTML = buildTable(pending, "pending");
  document.getElementById("queue-improvement").innerHTML = buildTable(improvement, "improvement");
  document.getElementById("queue-all").innerHTML = buildTable(allIssues, "all");

  const visible = applyFilters(allIssues);
  document.getElementById("s-total").textContent = visible.length;
  document.getElementById("s-waiting").textContent = visible.filter(
    (issue) => issue._status === "waiting-on-prerequisite",
  ).length;
  document.getElementById("s-pending").textContent = visible.filter(
    (issue) => issue._status === "ready-for-review" || issue._status === "pending-review",
  ).length;
  document.getElementById("s-improvement").textContent = visible.filter(
    (issue) => issue._status === "needs-improvement",
  ).length;
  document.getElementById("s-passed").textContent = visible.filter(
    (issue) => issue._status === "passed",
  ).length;

  document.getElementById("milestone-grid").innerHTML = MILESTONES.map((milestone) => {
    const milestoneIssues = visible.filter((issue) => issue._milestone === milestone);
    const passedCount = milestoneIssues.filter((issue) => issue._status === "passed").length;
    return `<div class="progress-milestone-col">
      <div class="m-label">${milestone}</div>
      <div class="m-bar">
        <div class="m-passed">${passedCount}</div>
        <div class="m-total">${milestoneIssues.length} submitted</div>
      </div>
    </div>`;
  }).join("");
}

async function fetchEnrolled() {
  try {
    const response = await fetch(
      `https://raw.githubusercontent.com/${OWNER}/${REPO}/main/.github/enrolled-participants.json`,
    );
    const data = await response.json();
    const cohort = data.cohort || "Cohort";
    document.getElementById("btn-enrolled").textContent = `Cohort: ${cohort}`;
    return new Set((data.participants || []).map((user) => user.toLowerCase()));
  } catch (_) {
    return null;
  }
}

async function fetchAll() {
  let issues = [];
  let page = 1;
  while (true) {
    const response = await fetch(
      `https://api.github.com/repos/${OWNER}/${REPO}/issues?labels=milestone-submission&state=all&per_page=100&page=${page}`,
    );
    const batch = await response.json();
    if (!Array.isArray(batch) || !batch.length) break;
    issues = issues.concat(
      batch.filter(
        (issue) => {
          const labelNames = issue.labels.map((label) => label.name);
          const isDuplicate = labelNames.includes("duplicate");
          const isLegacyLateOnly =
            labelNames.includes("late-submission") &&
            !PROCESS_LABELS.some((label) => labelNames.includes(label));
          return !issue.pull_request && !isDuplicate && !isLegacyLateOnly;
        },
      ),
    );
    if (batch.length < 100) break;
    page += 1;
  }
  return issues;
}

async function load() {
  document.getElementById("last-updated").textContent = "Loading…";

  [enrolledSet, allIssues] = await Promise.all([
    fetchEnrolled(),
    fetchAll().then((raw) => raw.map(enrich)),
  ]);

  renderAll();

  document.getElementById("last-updated").textContent =
    `Updated ${new Date().toLocaleTimeString("en-PH", {
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "Asia/Manila",
    })}`;
}

load();
