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
  const title = ' title="Days since the issue was submitted"';
  if (status === "passed") return `<span class="progress-days ok"${title}>${days}d</span>`;
  if (status === "waiting-on-prerequisite") {
    return `<span class="progress-days warn"${title}>${days}d queued</span>`;
  }
  if (days >= 5) return `<span class="progress-days breach"${title}>${days}d overdue</span>`;
  if (days >= 3) return `<span class="progress-days warn"${title}>${days}d waiting</span>`;
  return `<span class="progress-days ok"${title}>${days}d</span>`;
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString("en-PH", {
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: "Asia/Manila",
  });
}

function renderViewButtons() {
  for (const mode of ProgressSnapshot.VIEWS) {
    const button = document.getElementById(`btn-${mode === "non-enrolled" ? "non-enrolled" : mode}`);
    if (!button) continue;
    button.classList.toggle("active", viewMode === mode);
    button.setAttribute("aria-pressed", String(viewMode === mode));
  }
}

function setView(mode) {
  viewMode = mode;
  renderViewButtons();
  renderAll();
}

function applyView(issues) {
  if (viewMode === "enrolled" && enrolledSet) {
    return issues.filter((issue) => enrolledSet.has(issue.user.login.toLowerCase()));
  }
  if (viewMode === "non-enrolled" && enrolledSet) {
    return issues.filter((issue) => !enrolledSet.has(issue.user.login.toLowerCase()));
  }
  return issues;
}

function applyFilters(issues) {
  const query = (document.getElementById("search")?.value || "").toLowerCase().trim();
  const milestoneFilter = document.getElementById("filter-milestone")?.value || "";
  const statusFilter = document.getElementById("filter-status")?.value || "";

  return applyView(issues).filter((issue) => {
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

function clearFilters() {
  document.getElementById("search").value = "";
  document.getElementById("filter-milestone").value = "";
  document.getElementById("filter-status").value = "";
  renderAll();
}

function currentDashboardState() {
  return {
    view: viewMode,
    q: document.getElementById("search")?.value || "",
    milestone: document.getElementById("filter-milestone")?.value || "",
    status: document.getElementById("filter-status")?.value || "",
  };
}

function syncDashboardQuery() {
  if (typeof history === "undefined" || typeof history.replaceState !== "function") return;
  const query = ProgressSnapshot.buildDashboardQuery(currentDashboardState());
  const url = `${location.pathname}${query ? `?${query}` : ""}${location.hash}`;
  try {
    history.replaceState(null, "", url);
  } catch (_) {
    // Some local file:// contexts block history updates; filters still work.
  }
}

function applyInitialState() {
  const state = ProgressSnapshot.readDashboardState(window.location.search);
  viewMode = state.view;
  renderViewButtons();
  document.getElementById("search").value = state.q;
  document.getElementById("filter-milestone").value = state.milestone;
  document.getElementById("filter-status").value = state.status;
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

function thSort(tableKey, col, label, title = "") {
  const state = sortState[tableKey];
  const active = state.col === col;
  const icon = active ? (state.dir === "asc" ? "↑" : "↓") : "↕";
  const ariaSort = active ? (state.dir === "asc" ? "ascending" : "descending") : "none";
  const titleAttr = title ? ` title="${title}"` : "";
  return `<th class="progress-sortable${active ? " is-active" : ""}" scope="col" aria-sort="${ariaSort}"${titleAttr}><button type="button" aria-pressed="${String(active)}" onclick="handleSort('${tableKey}','${col}')">${label} <span class="progress-sort-icon" aria-hidden="true">${icon}</span></button></th>`;
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
      ${thSort(tableKey, "days", "Elapsed", "Days since the issue was submitted")}
      ${thSort(tableKey, "status", "Status")}
      <th scope="col">Repo</th><th scope="col">Issue</th>
    </tr></thead>
    <tbody>${rows
      .map((issue) => {
        const repoUrl = ProgressSnapshot.safeExternalUrl(issue._repoUrl);
        const issueUrl = ProgressSnapshot.safeExternalUrl(issue.html_url);
        return `<tr>
      <td>${ProgressSnapshot.escapeHtml(issue._builder)}</td>
      <td class="progress-hide-mobile">${ProgressSnapshot.escapeHtml(issue._cohort)}</td>
      <td><span class="progress-m-badge">${ProgressSnapshot.escapeHtml(issue._milestone)}</span></td>
      <td class="progress-hide-mobile">${formatDate(issue.created_at)}</td>
      <td>${daysBadge(issue._days, issue._status)}</td>
      <td>${statusBadges(issue)}</td>
      <td>${
        repoUrl
          ? `<a href="${repoUrl}" target="_blank" rel="noopener noreferrer">repo<span class="sr-only"> (opens in new tab)</span></a>`
          : "—"
      }</td>
      <td>${
        issueUrl
          ? `<a href="${issueUrl}" target="_blank" rel="noopener noreferrer">#${issue.number}<span class="sr-only"> (opens in new tab)</span></a>`
          : `#${issue.number}`
      }</td>
    </tr>`;
      })
      .join("")}</tbody>
  </table></div>`;
}

function exportCsv() {
  const rows = applySort(applyFilters(allIssues), "all");
  const blob = new Blob([`\uFEFF${ProgressSnapshot.buildCsv(rows)}`], {
    type: "text/csv;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `dep-submissions-${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
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

  const scoped = applyView(allIssues);
  const visible = applyFilters(allIssues);
  document.getElementById("filter-summary").textContent =
    `${visible.length} of ${scoped.length} submissions shown`;
  document.getElementById("clear-filters").hidden = !(
    document.getElementById("search").value ||
    document.getElementById("filter-milestone").value ||
    document.getElementById("filter-status").value
  );

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
    const percent = milestoneIssues.length
      ? Math.round((passedCount / milestoneIssues.length) * 100)
      : 0;
    return `<div class="progress-milestone-col">
      <div class="m-label">${milestone}</div>
      <div class="m-bar">
        <div class="m-passed">${passedCount}<span class="m-denom">/${milestoneIssues.length}</span></div>
        <div class="m-track" role="progressbar" aria-label="${milestone} submissions passed" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${percent}">
          <div class="m-fill" style="width: ${percent}%"></div>
        </div>
        <div class="m-total">${percent}% passed</div>
      </div>
    </div>`;
  }).join("");

  syncDashboardQuery();
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

function filterIssues(batch) {
  return batch.filter((issue) => {
    const labelNames = issue.labels.map((label) => label.name);
    const isDuplicate = labelNames.includes("duplicate");
    const isLegacyLateOnly =
      labelNames.includes("late-submission") &&
      !PROCESS_LABELS.some((label) => labelNames.includes(label));
    return !issue.pull_request && !isDuplicate && !isLegacyLateOnly;
  });
}

// Hourly server-side snapshot published by progress-snapshot.yml to the
// progress-data branch, so no api.github.com rate limit applies to visitors.
async function fetchSnapshot() {
  const response = await fetch(ProgressSnapshot.snapshotUrl(OWNER, REPO));
  if (!response.ok) throw new Error(`snapshot fetch: ${response.status}`);
  const payload = await response.json();
  if (!Array.isArray(payload.issues)) throw new Error("snapshot has no issues array");
  return {
    issues: filterIssues(payload.issues),
    generatedAt: payload.generated_at || null,
    live: false,
  };
}

async function fetchLive() {
  let issues = [];
  let page = 1;
  while (true) {
    const response = await fetch(
      `https://api.github.com/repos/${OWNER}/${REPO}/issues?labels=milestone-submission&state=all&per_page=100&page=${page}`,
    );
    const batch = await response.json();
    if (!Array.isArray(batch) || !batch.length) break;
    issues = issues.concat(filterIssues(batch));
    if (batch.length < 100) break;
    page += 1;
  }
  return issues;
}

async function fetchAll() {
  try {
    return await fetchSnapshot();
  } catch (err) {
    console.warn("Falling back to live GitHub API:", err.message);
    return { issues: await fetchLive(), generatedAt: null, live: true };
  }
}

function renderSnapshotStatus(generatedAt, isLive) {
  const element = document.getElementById("last-updated");
  if (isLive) {
    element.textContent = "Live GitHub API";
    element.classList.remove("is-stale");
    element.title = "The snapshot is unavailable, so the dashboard is reading issues directly.";
    return;
  }

  const status = ProgressSnapshot.formatSnapshotStatus(generatedAt);
  element.textContent = status.text;
  element.classList.toggle("is-stale", status.stale);
  element.title = status.stale
    ? "The dashboard is showing the last snapshot the workflow published successfully."
    : "";
}

async function load() {
  document.getElementById("last-updated").textContent = "Loading…";

  const [enrolled, snapshot] = await Promise.all([fetchEnrolled(), fetchAll()]);
  enrolledSet = enrolled;
  allIssues = snapshot.issues.map(enrich);

  renderAll();
  renderSnapshotStatus(snapshot.generatedAt, snapshot.live);
}

if (typeof document !== "undefined" && typeof window !== "undefined") {
  applyInitialState();
  load();
}
