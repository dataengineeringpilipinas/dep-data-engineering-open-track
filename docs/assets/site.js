const navToggle = document.querySelector(".nav-toggle");
const navLinks = document.querySelector("#nav-links");
const mobileNavQuery = window.matchMedia("(max-width: 767px)");

const setNavOpen = (isOpen) => {
  if (!navToggle || !navLinks) return;
  navLinks.classList.toggle("is-open", isOpen);
  navToggle.setAttribute("aria-expanded", String(isOpen));
  navToggle.querySelector(".sr-only").textContent = isOpen
    ? "Close navigation"
    : "Open navigation";
  navLinks.toggleAttribute("inert", mobileNavQuery.matches && !isOpen);
};

if (navToggle && navLinks) {
  setNavOpen(false);

  navToggle.addEventListener("click", () => {
    const willOpen = !navLinks.classList.contains("is-open");
    setNavOpen(willOpen);
    if (willOpen && mobileNavQuery.matches) {
      const firstLink = navLinks.querySelector("a");
      firstLink?.focus();
    }
  });

  navLinks.addEventListener("click", (event) => {
    if (event.target instanceof HTMLAnchorElement) {
      setNavOpen(false);
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && navLinks.classList.contains("is-open")) {
      setNavOpen(false);
      navToggle.focus();
    }
  });

  mobileNavQuery.addEventListener("change", () => {
    if (!mobileNavQuery.matches) {
      setNavOpen(false);
      navLinks.removeAttribute("inert");
    } else {
      navLinks.toggleAttribute("inert", !navLinks.classList.contains("is-open"));
    }
  });
}

const observedSections = document.querySelectorAll("main section[id]");
const navAnchors = document.querySelectorAll('.nav-links a[href^="#"]');

if ("IntersectionObserver" in window && observedSections.length > 0) {
  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

      if (!visible) {
        return;
      }

      navAnchors.forEach((anchor) => {
        anchor.toggleAttribute(
          "aria-current",
          anchor.getAttribute("href") === `#${visible.target.id}`,
        );
      });
    },
    {
      rootMargin: "-30% 0px -55% 0px",
      threshold: [0.1, 0.3, 0.6],
    },
  );

  observedSections.forEach((section) => observer.observe(section));
}

const revealItems = document.querySelectorAll(".reveal");
let revealObserver = null;

const observeRevealItems = (items) => {
  items.forEach((item) => {
    if (revealObserver) {
      revealObserver.observe(item);
    } else {
      item.classList.add("visible");
    }
  });
};

if ("IntersectionObserver" in window && revealItems.length > 0) {
  revealObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }

        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      });
    },
    {
      rootMargin: "0px 0px -8% 0px",
      threshold: 0.12,
    },
  );

  revealItems.forEach((item) => revealObserver.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add("visible"));
}

const builderDashboard = document.querySelector("[data-builder-dashboard]");

if (builderDashboard) {
  const phaseOrder = [
    "Foundations",
    "Data Collection",
    "Data Processing",
    "Analysis & Insights",
    "Predictive",
    "Non-Predictive",
    "Packaging & Deployment",
  ];
  const statusOrder = ["Active", "At Risk", "Dropped", "Completed"];
  const statusLabels = {
    Active: "Active",
    "At Risk": "At risk",
    Dropped: "Dropped",
    Completed: "Completed",
  };

  const metaEl = builderDashboard.querySelector("[data-builder-meta]");
  const statsEl = builderDashboard.querySelector("[data-builder-stats]");
  const statusChartEl = builderDashboard.querySelector("[data-builder-status-chart]");
  const phaseChartEl = builderDashboard.querySelector("[data-builder-phase-chart]");
  const milestoneEl = builderDashboard.querySelector("[data-builder-milestones]");
  const listEl = builderDashboard.querySelector("[data-builder-list]");
  const countEl = builderDashboard.querySelector("[data-builder-count]");
  const searchEl = builderDashboard.querySelector("[data-builder-search]");
  const statusFilterEl = builderDashboard.querySelector("[data-builder-status-filter]");
  const phaseFilterEl = builderDashboard.querySelector("[data-builder-phase-filter]");
  const expandEl = builderDashboard.querySelector("[data-builder-expand]");
  const timelineEl = builderDashboard.querySelector("[data-timeline]");
  const timelineNowEl = builderDashboard.querySelector("#timeline-now");
  const timelineDateEl = builderDashboard.querySelector("[data-timeline-date]");
  const timelineTimeEl = builderDashboard.querySelector("[data-timeline-time]");
  const reducedMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");

  let builders = [];
  let showAllBuilders = false;
  let clockInterval = null;
  const builderPreviewLimit = 10;
  const manilaTimeZone = "Asia/Manila";
  const milestoneNames = {
    M0: "Problem statement",
    M1: "Repo and source",
    M2: "Data ingestion",
    M3: "Clean dataset",
    M4: "Initial insights",
    M5: "Project packaging",
    M6: "Live deployment",
  };

  const normalizeText = (value) => String(value || "").trim();

  const escapeHtml = (value) =>
    normalizeText(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

  const countBy = (items, key) =>
    items.reduce((counts, item) => {
      const value = normalizeText(item[key]) || "Unassigned";
      counts[value] = (counts[value] || 0) + 1;
      return counts;
    }, {});

  const sumBy = (items, key) =>
    items.reduce((total, item) => total + Number(item[key] || 0), 0);

  const getSafeUrl = (value) => {
    try {
      const url = new URL(normalizeText(value));
      return ["http:", "https:"].includes(url.protocol) ? url.href : "";
    } catch (_) {
      return "";
    }
  };

  const getMilestoneLabel = (builder) => {
    const milestone = Number(builder.currentMilestone || 0);
    return `M${Number.isFinite(milestone) ? milestone : 0}`;
  };

  const metricValue = (value) => (Number(value) > 0 ? value : "-");

  const formatDateTime = (date, options) =>
    new Intl.DateTimeFormat("en-PH", {
      timeZone: manilaTimeZone,
      ...options,
    }).format(date);

  const formatMilestoneDate = (date) =>
    formatDateTime(date, {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
      timeZoneName: "short",
    });

  const formatClockDate = (date) =>
    formatDateTime(date, {
      weekday: "short",
      month: "long",
      day: "numeric",
      year: "numeric",
    });

  const formatClockTime = (date) =>
    formatDateTime(date, {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: true,
    });

  const updateTimelineClock = (now = new Date()) => {
    if (!timelineDateEl || !timelineTimeEl) return;
    timelineDateEl.textContent = formatClockDate(now);
    timelineTimeEl.textContent = formatClockTime(now);
    if (timelineNowEl) {
      timelineNowEl.setAttribute("datetime", now.toISOString());
      timelineNowEl.setAttribute(
        "aria-label",
        `Current time in Asia/Manila: ${formatClockDate(now)}, ${formatClockTime(now)}`,
      );
    }
  };

  const startTimelineClock = () => {
    if (!timelineDateEl || !timelineTimeEl) return;

    if (clockInterval) window.clearInterval(clockInterval);
    updateTimelineClock();

    if (reducedMotionQuery.matches) {
      return;
    }

    clockInterval = window.setInterval(() => updateTimelineClock(), 1000);
  };

  reducedMotionQuery.addEventListener("change", startTimelineClock);

  const formatCountdown = (deadline, now = new Date()) => {
    const diff = deadline.getTime() - now.getTime();
    if (diff <= 0) return "Closed";

    const totalSeconds = Math.floor(diff / 1000);
    const days = Math.floor(totalSeconds / 86400);
    const hours = Math.floor((totalSeconds % 86400) / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);

    if (days > 0) return `${days}d ${hours}h left`;
    if (hours > 0) return `${hours}h ${minutes}m left`;
    return `${minutes}m left`;
  };

  const getMilestoneColumnCenter = (index, total) => ((index + 0.5) / total) * 100;

  const getSegmentPadding = (total) => (100 / total) * 0.34;

  const getNowGridPercent = (entries, now) => {
    const total = entries.length;
    const padding = getSegmentPadding(total);
    const currentIndex = entries.findIndex((entry) => now <= entry.deadline);

    if (currentIndex === -1) {
      const lastCenter = getMilestoneColumnCenter(total - 1, total);
      return Math.max(lastCenter - padding, 0);
    }

    if (currentIndex === 0) {
      const deadline = entries[0].deadline.getTime();
      const progress = Math.min(Math.max(now.getTime() / deadline, 0), 1);
      const segmentEnd = getMilestoneColumnCenter(0, total) - padding;
      return progress * Math.max(segmentEnd, 0);
    }

    const prevDeadline = entries[currentIndex - 1].deadline.getTime();
    const nextDeadline = entries[currentIndex].deadline.getTime();
    const segmentSpan = Math.max(nextDeadline - prevDeadline, 1);
    const progress = Math.min(
      Math.max((now.getTime() - prevDeadline) / segmentSpan, 0),
      1,
    );
    const prevCenter = getMilestoneColumnCenter(currentIndex - 1, total);
    const nextCenter = getMilestoneColumnCenter(currentIndex, total);
    const segmentStart = prevCenter + padding;
    const segmentEnd = nextCenter - padding;
    const usableSpan = Math.max(segmentEnd - segmentStart, 0);

    return segmentStart + progress * usableSpan;
  };

  const toRailPercent = (gridPercent) => {
    const railInset = 5;
    return Math.min(
      Math.max(((gridPercent - railInset) / (100 - railInset * 2)) * 100, 0),
      100,
    );
  };

  const renderTimeline = (deadlines) => {
    if (!timelineEl) return;

    const entries = Object.entries(deadlines || {})
      .filter(([key, value]) => /^M\d$/.test(key) && !Number.isNaN(new Date(value).getTime()))
      .sort(([a], [b]) => a.localeCompare(b, undefined, { numeric: true }))
      .map(([key, value]) => ({
        key,
        label: milestoneNames[key] || key,
        deadline: new Date(value),
      }));

    if (!entries.length) {
      timelineEl.innerHTML = `<p class="builder-empty">Milestone deadline data is unavailable.</p>`;
      return;
    }

    const now = new Date();
    const currentIndex = entries.findIndex((entry) => now <= entry.deadline);
    const nowGridPercent = getNowGridPercent(entries, now);
    const nowRailPercent = toRailPercent(nowGridPercent);

    timelineEl.innerHTML = `
      <div class="timeline-rail" aria-hidden="true">
        <span class="timeline-rail-fill" style="width: ${nowRailPercent}%"></span>
      </div>
      <span class="timeline-now-marker" style="left: ${nowGridPercent}%" aria-hidden="true">
        <span class="timeline-now-label">Now</span>
      </span>
      <ol class="timeline-milestones" aria-label="Milestone deadlines">
        ${entries
          .map((entry, index) => {
            const state = now > entry.deadline
              ? "past"
              : index === currentIndex
                ? "current"
                : "future";

            return `<li class="timeline-milestone ${state}">
              <span class="timeline-node">${escapeHtml(entry.key)}</span>
              <div class="timeline-card">
                <span class="timeline-state">${state === "current" ? "Current gate" : state}</span>
                <strong>${escapeHtml(entry.key)} · ${escapeHtml(entry.label)}</strong>
                <span>${escapeHtml(formatMilestoneDate(entry.deadline))}</span>
                <small>${escapeHtml(formatCountdown(entry.deadline, now))}</small>
              </div>
            </li>`;
          })
          .join("")}
      </ol>
    `;
  };

  const getVisibleBuilders = () => {
    const query = normalizeText(searchEl?.value).toLowerCase();
    const status = normalizeText(statusFilterEl?.value);
    const phase = normalizeText(phaseFilterEl?.value);

    return builders.filter((builder) => {
      const haystack = [
        builder.name,
        builder.github,
        builder.squad,
        builder.projectTopic,
        builder.status,
        builder.phase,
      ]
        .map(normalizeText)
        .join(" ")
        .toLowerCase();

      if (query && !haystack.includes(query)) return false;
      if (status && builder.status !== status) return false;
      if (phase && builder.phase !== phase) return false;
      return true;
    });
  };

  const renderStats = () => {
    const active = builders.filter((builder) => builder.status === "Active").length;
    const atRisk = builders.filter((builder) => builder.status === "At Risk").length;
    const completed = builders.filter((builder) => builder.status === "Completed").length;
    const submitted = sumBy(builders, "milestonesSubmitted");
    const passed = sumBy(builders, "milestonesPassed");

    statsEl.innerHTML = [
      ["Total builders", builders.length],
      ["Active", active],
      ["At risk", metricValue(atRisk)],
      ["Completed", metricValue(completed)],
      ["Milestones submitted", metricValue(submitted)],
      ["Milestones passed", metricValue(passed)],
    ]
      .map(
        ([label, value]) => `<article class="builder-stat-card">
          <span class="builder-stat-number">${escapeHtml(value)}</span>
          <span class="builder-stat-label">${escapeHtml(label)}</span>
        </article>`,
      )
      .join("");
  };

  const renderBars = (target, counts, orderedLabels) => {
    const entries = orderedLabels
      .filter((label) => counts[label])
      .concat(
        Object.keys(counts)
          .filter((label) => !orderedLabels.includes(label))
          .sort((a, b) => a.localeCompare(b)),
      );
    const max = Math.max(...entries.map((label) => counts[label]), 1);

    if (!entries.length) {
      target.innerHTML = `<p class="builder-empty">No public data yet.</p>`;
      return;
    }

    const srSummary = entries
      .map((label) => `${statusLabels[label] || label}: ${counts[label]}`)
      .join(", ");

    target.innerHTML =
      `<p class="builder-chart-sr">${escapeHtml(srSummary)}</p>` +
      entries
        .map((label) => {
          const count = counts[label];
          const width = Math.max((count / max) * 100, 8);
          return `<div class="builder-bar-row">
            <div class="builder-bar-meta">
              <span>${escapeHtml(statusLabels[label] || label)}</span>
              <strong>${escapeHtml(count)}</strong>
            </div>
            <div class="builder-bar-track" aria-hidden="true">
              <span style="width: ${width}%"></span>
            </div>
          </div>`;
        })
        .join("");
  };

  const renderMilestones = () => {
    const submitted = sumBy(builders, "milestonesSubmitted");
    const passed = sumBy(builders, "milestonesPassed");
    const passRate = submitted > 0 ? Math.round((passed / submitted) * 100) : 0;

    milestoneEl.innerHTML = `
      <p class="builder-chart-sr">Submitted: ${escapeHtml(submitted)}, Passed: ${escapeHtml(passed)}, Pass rate: ${submitted > 0 ? `${passRate}%` : "not available"}</p>
      <div class="milestone-funnel-step">
        <span>Submitted</span>
        <strong>${metricValue(submitted)}</strong>
      </div>
      <div class="milestone-funnel-step">
        <span>Passed</span>
        <strong>${metricValue(passed)}</strong>
      </div>
      <div class="milestone-funnel-step">
        <span>Pass rate</span>
        <strong>${submitted > 0 ? `${passRate}%` : "-"}</strong>
      </div>
    `;
  };

  const populateFilter = (select, values) => {
    if (!select) return;
    const current = select.value;
    select.innerHTML = `<option value="">${select.dataset.builderStatusFilter !== undefined ? "All statuses" : "All phases"}</option>`;
    values.forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = statusLabels[value] || value;
      select.append(option);
    });
    select.value = current;
  };

  const renderList = () => {
    const visible = getVisibleBuilders().sort((a, b) =>
      normalizeText(a.name).localeCompare(normalizeText(b.name)),
    );
    const rendered = showAllBuilders
      ? visible
      : visible.slice(0, builderPreviewLimit);

    countEl.textContent = showAllBuilders || visible.length <= builderPreviewLimit
      ? `${visible.length} of ${builders.length} builders shown`
      : `Showing ${rendered.length} of ${visible.length} matching builders`;
    countEl.setAttribute(
      "aria-live",
      reducedMotionQuery.matches ? "off" : "polite",
    );

    if (expandEl) {
      const hasOverflow = visible.length > builderPreviewLimit;
      expandEl.hidden = !hasOverflow;
      expandEl.textContent = showAllBuilders
        ? "Show fewer builders"
        : `Show all ${visible.length} builders`;
      expandEl.setAttribute("aria-expanded", String(showAllBuilders));
    }

    if (!visible.length) {
      listEl.innerHTML = `<p class="builder-empty">No builders match the current filters.</p>`;
      return;
    }

    listEl.innerHTML = rendered
      .map((builder) => {
        const github = getSafeUrl(builder.github);
        const name = escapeHtml(builder.name || builder.id || "Builder");
        const topic = escapeHtml(builder.projectTopic || "Project topic to be announced");
        const squad = escapeHtml(builder.squad || "Squad pending");
        const activeWeek = escapeHtml(builder.activeWeek || "Week pending");
        const phase = escapeHtml(builder.phase || "Phase pending");
        const status = escapeHtml(statusLabels[builder.status] || builder.status || "Status pending");
        const milestone = escapeHtml(getMilestoneLabel(builder));

        return `<article class="builder-card">
          <div class="builder-card-main">
            <div>
              <p class="builder-name">${name}</p>
              <p class="builder-topic">${topic}</p>
            </div>
            <span class="builder-status">${status}</span>
          </div>
          <div class="builder-meta-grid">
            <span>${phase}</span>
            <span>${milestone}</span>
            <span>${activeWeek}</span>
            <span>${squad}</span>
          </div>
          <div class="builder-card-footer">
            <span>${escapeHtml(builder.milestonesPassed || 0)} passed / ${escapeHtml(builder.milestonesSubmitted || 0)} submitted</span>
            ${
              github
                ? `<a href="${escapeHtml(github)}" target="_blank" rel="noopener noreferrer" aria-label="GitHub repository for ${name} (opens in new tab)">GitHub</a>`
                : "<span>GitHub pending</span>"
            }
          </div>
        </article>`;
      })
      .join("");
  };

  const renderBuilders = (snapshot) => {
    builders = Array.isArray(snapshot.builders) ? snapshot.builders : [];
    const updated = normalizeText(snapshot.updatedAt) || "date pending";
    const source = normalizeText(snapshot.source) || "sanitized snapshot";

    metaEl.textContent = `${snapshot.cohort || "Cohort"} public builder data, updated ${updated}. Source: ${source}. Private fields are excluded.`;
    renderStats();
    renderBars(statusChartEl, countBy(builders, "status"), statusOrder);
    renderBars(phaseChartEl, countBy(builders, "phase"), phaseOrder);
    renderMilestones();

    populateFilter(
      statusFilterEl,
      statusOrder.filter((status) => builders.some((builder) => builder.status === status)),
    );
    populateFilter(
      phaseFilterEl,
      phaseOrder.filter((phase) => builders.some((builder) => builder.phase === phase)),
    );
    renderList();
  };

  const bindBuilderFilters = () => {
    [searchEl, statusFilterEl, phaseFilterEl].forEach((control) => {
      if (control) {
        control.addEventListener("input", () => {
          showAllBuilders = false;
          renderList();
        });
      }
    });
    if (expandEl) {
      expandEl.addEventListener("click", () => {
        showAllBuilders = !showAllBuilders;
        renderList();
      });
    }
  };

  fetch("data/builders.json")
    .then((response) => {
      if (!response.ok) throw new Error("Builder data unavailable");
      return response.json();
    })
    .then((snapshot) => {
      bindBuilderFilters();
      renderBuilders(snapshot);
    })
    .catch(() => {
      metaEl.textContent =
        "Builder data is currently unavailable. The public dashboard only renders from a sanitized snapshot.";
    });

  startTimelineClock();

  fetch("data/milestone-deadlines.json")
    .then((response) => {
      if (!response.ok) throw new Error("Milestone data unavailable");
      return response.json();
    })
    .then(renderTimeline)
    .catch(() => {
      if (timelineEl) {
        timelineEl.innerHTML = `<p class="builder-empty">Milestone deadline data is currently unavailable.</p>`;
      }
    });
}

// Render a simple updates/news list from data/updates.json
(function renderUpdates() {
  const container = document.querySelector('[data-updates]');
  if (!container) return;

  const escapeHtml = (value) =>
    String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

  const renderParagraphs = (content) =>
    String(content || "")
      .split(/\n\s*\n/)
      .map((paragraph) => `<p>${escapeHtml(paragraph.trim())}</p>`)
      .join("");

  const formatDate = (iso) => {
    try {
      const d = new Date(iso);
      return new Intl.DateTimeFormat("en-PH", {
        timeZone: "Asia/Manila",
        month: "short",
        day: "numeric",
        year: "numeric",
      }).format(d);
    } catch (_) {
      return "date pending";
    }
  };

  const isLinkedInPost = (post) =>
    post.source === "linkedin" || /linkedin\.com/i.test(String(post.link || ""));

  const linkedInBadge = () =>
    `<span class="update-badge update-badge-linkedin"><svg viewBox="0 0 24 24" width="12" height="12" aria-hidden="true" focusable="false"><path fill="currentColor" d="M20.45 20.45h-3.55v-5.57c0-1.33-.02-3.03-1.85-3.03-1.85 0-2.14 1.45-2.14 2.94v5.66H9.36V9h3.41v1.56h.05c.47-.9 1.63-1.85 3.36-1.85 3.6 0 4.27 2.37 4.27 5.45v6.29zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45z"/></svg>LinkedIn</span>`;

  const renderMainCard = (post) => {
    const title = escapeHtml(post.title || "Update");
    const date = formatDate(post.date);
    const teaser = escapeHtml(post.summaryShort || post.summary || "");
    const body = post.content ? `<div class="update-body">${renderParagraphs(post.content)}</div>` : "";
    const callout = post.callout ? `<p class="update-callout">${escapeHtml(post.callout)}</p>` : "";
    const social = escapeHtml(post.socialBlurb || "");
    const onLinkedIn = isLinkedInPost(post);
    const badges = [
      post.featured ? `<span class="update-badge">Featured story</span>` : "",
      onLinkedIn ? linkedInBadge() : "",
    ].join("");
    const scrollTarget = post.scrollTarget ? `index.html#${post.scrollTarget}` : null;
    const linkHref = scrollTarget || post.link;
    const isScrollLink = Boolean(post.scrollTarget);
    const linkLabel = onLinkedIn ? "View post on LinkedIn ↗" : "Read full update";
    const linkHtml = linkHref
      ? `<p class="update-link"><a href="${escapeHtml(linkHref)}" ${isScrollLink ? 'data-scroll="true"' : 'target="_blank" rel="noopener"'}>${linkLabel}</a></p>`
      : "";

    return `
      <article class="update-card update-card-featured${onLinkedIn ? " update-card-linkedin" : ""}">
        <div>
          ${badges}
          <strong class="update-title">${title}</strong>
          <time class="update-date">${escapeHtml(date)}</time>
          <p class="update-summary">${teaser}</p>
          ${callout}
          ${body}
          ${social ? `<p class="update-social">${social}</p>` : ""}
          ${linkHtml}
        </div>
      </article>
    `;
  };

  const renderSnippetItem = (post, active = false) => {
    const teaser = escapeHtml(post.summaryShort || post.summary || "");
    const onLinkedIn = isLinkedInPost(post);
    return `
      <div class="update-snippet-item${active ? " active" : ""}" data-update-id="${escapeHtml(post.id)}">
        ${onLinkedIn ? linkedInBadge() : ""}
        <strong class="update-title">${escapeHtml(post.title || "Update")}</strong>
        <time class="update-date">${escapeHtml(formatDate(post.date))}</time>
        <p class="update-summary">${teaser}</p>
        <button class="update-snippet-action" type="button">Read more</button>
      </div>
    `;
  };

  const updateMainPanel = (panel, post) => {
    panel.innerHTML = renderMainCard(post);
    const snippetItems = container.querySelectorAll('.update-snippet-item');
    snippetItems.forEach((item) => {
      item.classList.toggle('active', item.dataset.updateId === post.id);
    });
    // Reattach scroll handlers for any update links rendered inside the main panel
    attachUpdateLinkHandlers();
  };

  // Attach click handlers that intercept onboarding links and scroll without reloading
  function attachUpdateLinkHandlers() {
    const links = container.querySelectorAll('.update-link a[data-scroll="true"]');
    links.forEach((a) => {
      // remove any previous handler to avoid duplicates
      a.removeEventListener('click', a._updateScrollHandler || (() => {}));
      const handler = function (e) {
        const href = a.getAttribute('href') || '';
        const hashIndex = href.indexOf('#');
        if (hashIndex === -1) return;
        const targetId = href.slice(hashIndex + 1);
        const path = window.location.pathname;
        const onIndex = path.endsWith('index.html') || path === '/' || path === '';
        if (onIndex) {
          const target = document.getElementById(targetId);
          if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }
      };
      a.addEventListener('click', handler);
      a._updateScrollHandler = handler;
    });
  }

  fetch("data/updates.json")
    .then((r) => {
      if (!r.ok) throw new Error("Updates unavailable");
      return r.json();
    })
    .then((posts) => {
      if (!Array.isArray(posts) || posts.length === 0) {
        container.innerHTML = `<p class="builder-empty">No updates yet.</p>`;
        return;
      }

      posts.sort((a, b) => new Date(b.date) - new Date(a.date));
      const featuredPost = posts.find((post) => post.featured) || posts[0];
      const postsToShow = posts.slice(0, 5);
      if (!postsToShow.some((post) => post.id === featuredPost.id)) {
        postsToShow[postsToShow.length - 1] = featuredPost;
      }
      const snippets = postsToShow;

      container.innerHTML = `
        <div class="updates-panel">
          <div class="update-main-panel">${renderMainCard(featuredPost)}</div>
          <div class="update-snippet-list">
            ${snippets.map((post) => renderSnippetItem(post, post.id === featuredPost.id)).join("")}
          </div>
        </div>
      `;

      const mainPanel = container.querySelector('.update-main-panel');
      const snippetActions = container.querySelectorAll('.update-snippet-action');
      snippetActions.forEach((button) => {
        button.addEventListener('click', (event) => {
          const snippet = event.currentTarget.closest('.update-snippet-item');
          if (!snippet) return;
          const selectedId = snippet.dataset.updateId;
          const selectedPost = posts.find((post) => post.id === selectedId);
          if (selectedPost) {
            updateMainPanel(mainPanel, selectedPost);
          }
        });
      });
      // attach scroll handlers for any links in the initially rendered main panel
      attachUpdateLinkHandlers();
    })
    .catch(() => {
      container.innerHTML = `<p class="builder-empty">Updates unavailable.</p>`;
    });
})();
