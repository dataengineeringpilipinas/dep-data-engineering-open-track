// Exercises the github-script block embedded in project-board-sync.yml.
//
// A workflow_dispatch run needs the workflow file to exist on the default
// branch, so the board sync cannot be executed from a pull request. This test
// runs the same script text against a stubbed GitHub client, and the stub
// reproduces the API behaviours that broke earlier revisions: `id` is only
// returned when the project query selects it, and `optionId` is only returned
// when the item query selects it.

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const WORKFLOW = path.join(__dirname, "..", "workflows", "project-board-sync.yml");

function extractScript(source) {
  const lines = source.split("\n");
  const start = lines.findIndex((line) => /^\s*script:\s*\|\s*$/.test(line));
  assert.notEqual(start, -1, "workflow must embed a github-script block");

  const baseIndent = lines[start].match(/^\s*/)[0].length;
  const body = [];
  for (const line of lines.slice(start + 1)) {
    if (line.trim() === "") {
      body.push("");
      continue;
    }
    if (line.match(/^\s*/)[0].length <= baseIndent) break;
    body.push(line);
  }

  const indent = Math.min(
    ...body.filter((line) => line.trim()).map((line) => line.match(/^\s*/)[0].length),
  );
  return body.map((line) => (line.trim() ? line.slice(indent) : "")).join("\n");
}

const SCRIPT = extractScript(fs.readFileSync(WORKFLOW, "utf8"));

const OPTION = {
  unchecked: "option-unchecked",
  review: "option-review",
  needs: "option-needs",
  passed: "option-passed",
  closed: "option-closed",
};

const LIVE_NAMES = {
  unchecked: "Unchecked/Unassigned",
  review: "In review",
  needs: "Needs Improvement",
  passed: "Passed",
  closed: "Closed/Not passed",
};

const STATUS_FIELD = "PVTSSF_status";
const PROJECT_ID = "PVT_proj7";
const SUBMISSION = "milestone-submission";

function projectRecord(names = LIVE_NAMES) {
  return {
    id: PROJECT_ID,
    number: 7,
    fields: {
      nodes: [
        {
          __typename: "ProjectV2SingleSelectField",
          id: STATUS_FIELD,
          name: "Status",
          options: [
            { id: OPTION.unchecked, name: names.unchecked },
            { id: OPTION.review, name: names.review },
            { id: OPTION.needs, name: names.needs },
            { id: OPTION.passed, name: names.passed },
            { id: OPTION.closed, name: names.closed },
          ],
        },
      ],
    },
  };
}

function boardItem(number, optionId) {
  return {
    id: `item-${number}`,
    content: { number },
    fieldValues: {
      nodes: optionId ? [{ field: { id: STATUS_FIELD }, optionId, name: "any" }] : [],
    },
  };
}

function submission(number, state, labels, extra = {}) {
  return { number, state, labels: labels.map((name) => ({ name })), ...extra };
}

async function runWorkflow({
  names = LIVE_NAMES,
  eventName = "schedule",
  payload = {},
  items = [],
  issues = [],
}) {
  const updates = [];
  const warnings = [];
  const info = [];

  const github = {
    graphql: async (query, variables) => {
      if (query.includes("projectsV2")) {
        const record = projectRecord(names);
        // The API only returns `id` when the selection asks for it.
        if (!/nodes\s*{\s*id\b/.test(query)) delete record.id;
        return { repository: { projectsV2: { nodes: [record] } } };
      }
      if (query.includes("items(first")) {
        // The API only returns `optionId` when the selection asks for it.
        const withOptionId = /\boptionId\b/.test(query);
        return {
          node: {
            items: {
              pageInfo: { hasNextPage: false, endCursor: null },
              nodes: items.map((item) => ({
                id: item.id,
                content: item.content,
                fieldValues: {
                  nodes: item.fieldValues.nodes.map((value) =>
                    withOptionId ? value : { field: value.field, name: value.name },
                  ),
                },
              })),
            },
          },
        };
      }
      if (query.includes("updateProjectV2ItemFieldValue")) {
        updates.push(variables);
        return { updateProjectV2ItemFieldValue: { projectV2Item: { id: variables.itemId } } };
      }
      throw new Error(`unexpected GraphQL document: ${query.slice(0, 60)}`);
    },
    paginate: async () => issues,
    rest: { issues: { listForRepo: "listForRepo" } },
  };

  const core = {
    info: (...args) => info.push(args.join(" ")),
    warning: (...args) => warnings.push(args.join(" ")),
  };
  const context = { repo: { owner: "owner", repo: "repo" }, eventName, payload };

  const previous = process.env.PROJECT_NUMBER;
  process.env.PROJECT_NUMBER = "7";
  try {
    const invoke = new Function(
      "github",
      "core",
      "context",
      "process",
      `return (async () => {\n${SCRIPT}\n})()`,
    );
    await invoke(github, core, context, process);
  } finally {
    if (previous === undefined) delete process.env.PROJECT_NUMBER;
    else process.env.PROJECT_NUMBER = previous;
  }

  return { updates, warnings, info };
}

const SUBMISSIONS = [
  submission(101, "open", [SUBMISSION, "passed"]),
  submission(102, "closed", [SUBMISSION]),
  submission(103, "closed", [SUBMISSION, "needs-improvement"]),
  submission(104, "open", [SUBMISSION, "ready-for-review"]),
  submission(105, "open", [SUBMISSION, "needs-improvement"]),
  submission(106, "open", [SUBMISSION]),
  submission(107, "open", [SUBMISSION, "passed", "duplicate"]),
  submission(108, "open", [SUBMISSION, "ready-for-review"]),
  submission(109, "open", []),
  submission(111, "open", [SUBMISSION, "passed"]),
  submission(200, "open", []),
];

const BOARD = [
  boardItem(101, OPTION.unchecked),
  boardItem(102, OPTION.closed),
  boardItem(103, OPTION.closed),
  boardItem(104, OPTION.unchecked),
  boardItem(105, OPTION.unchecked),
  boardItem(106, OPTION.unchecked),
  boardItem(107, OPTION.unchecked),
  boardItem(108, OPTION.review),
  boardItem(109, OPTION.unchecked),
  boardItem(200, OPTION.unchecked),
];

const EXPECTED = {
  "item-101": OPTION.passed,
  "item-104": OPTION.review,
  "item-105": OPTION.needs,
  "item-107": OPTION.passed,
};

async function reconcile(overrides = {}) {
  return runWorkflow({ items: BOARD, issues: SUBMISSIONS, ...overrides });
}

test("embedded script parses", () => {
  assert.ok(SCRIPT.includes("OPTION_NAMES"));
  assert.doesNotThrow(() => new Function(`return (async () => {\n${SCRIPT}\n})()`));
});

test("queries use the GraphQL shapes GitHub accepts", () => {
  // GitHub rejects the union selection and the old value type name outright.
  assert.doesNotMatch(SCRIPT, /ProjectV2SingleSelectFieldValue/);
  assert.match(SCRIPT, /ProjectV2ItemFieldSingleSelectValue/);
  assert.doesNotMatch(SCRIPT, /\.\.\. on ProjectV2FieldConfiguration \{\s*id/);
  assert.match(SCRIPT, /\.\.\. on ProjectV2FieldCommon \{\s*id name\s*\}/);
});

test("reconcile maps labels and issue state to Status", async () => {
  const { updates } = await reconcile();
  const applied = Object.fromEntries(updates.map((entry) => [entry.itemId, entry.optionId]));
  assert.deepEqual(applied, EXPECTED);
});

test("reconcile writes only when the value changes", async () => {
  const { updates, info } = await reconcile();
  assert.equal(updates.length, 4);
  assert.ok(info.some((line) => line.includes("4 updated, 1 not on the board")));
});

test("reconcile skips issues without milestone-submission", async () => {
  const { updates } = await reconcile();
  const touched = updates.map((entry) => entry.itemId);
  assert.ok(!touched.includes("item-109"));
  assert.ok(!touched.includes("item-200"));
});

test("reconcile carries the project, field and option ids", async () => {
  const { updates } = await reconcile();
  assert.ok(updates.length > 0);
  for (const entry of updates) {
    assert.equal(entry.projectId, PROJECT_ID);
    assert.equal(entry.fieldId, STATUS_FIELD);
    assert.ok(entry.optionId, "option id must be resolved");
  }
});

test("legacy Status option names are still accepted", async () => {
  const legacy = {
    unchecked: "Unchecked",
    review: "In review",
    needs: "Needs Improvement",
    passed: "Passed",
    closed: "Closed",
  };
  const { updates } = await reconcile({ names: legacy });
  assert.equal(updates.length, 4);
});

test("event runs only touch submission issues", async () => {
  const synced = await runWorkflow({
    eventName: "labeled",
    payload: { issue: submission(201, "open", [SUBMISSION, "ready-for-review"]) },
    items: [boardItem(201, OPTION.unchecked)],
  });
  assert.equal(synced.updates.length, 1);
  assert.equal(synced.updates[0].optionId, OPTION.review);

  const skipped = await runWorkflow({
    eventName: "opened",
    payload: { issue: submission(202, "open", []) },
    items: [boardItem(202, OPTION.unchecked)],
  });
  assert.equal(skipped.updates.length, 0);
});

test("workflow_dispatch honours the reconcile input", async () => {
  const off = await reconcile({ eventName: "workflow_dispatch", payload: { inputs: { reconcile: "false" } } });
  assert.equal(off.updates.length, 0);

  const on = await reconcile({ eventName: "workflow_dispatch", payload: { inputs: { reconcile: "true" } } });
  assert.equal(on.updates.length, 4);
});

test("an unknown Status option warns instead of throwing", async () => {
  const { updates, warnings } = await runWorkflow({
    names: { ...LIVE_NAMES, closed: "Done" },
    items: [boardItem(102, OPTION.closed)],
    issues: [submission(102, "closed", [SUBMISSION])],
  });
  assert.equal(updates.length, 0);
  assert.ok(warnings.some((line) => line.includes("Closed")));
});
