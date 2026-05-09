const state = {
  activeTab: "playground",
  schema: null,
  policies: [],
  scenarios: [],
  runs: [],
  selectedScenarioId: null,
  selectedRunId: null,
  focusResult: null,
  comparisonResults: [],
};

const elements = {
  healthStatus: document.querySelector("#healthStatus"),
  policySelect: document.querySelector("#policySelect"),
  policySnapshot: document.querySelector("#policySnapshot"),
  eventFilter: document.querySelector("#eventFilter"),
  datasetStats: document.querySelector("#datasetStats"),
  scenarioCount: document.querySelector("#scenarioCount"),
  scenarioList: document.querySelector("#scenarioList"),
  refreshRunsButton: document.querySelector("#refreshRunsButton"),
  recentRuns: document.querySelector("#recentRuns"),
  playgroundView: document.querySelector("#playgroundView"),
  reportView: document.querySelector("#reportView"),
  tabButtons: [...document.querySelectorAll(".tab-button")],
  scenarioTitle: document.querySelector("#scenarioTitle"),
  expectedChip: document.querySelector("#expectedChip"),
  scenarioMeta: document.querySelector("#scenarioMeta"),
  aiUtterance: document.querySelector("#aiUtterance"),
  userUtterance: document.querySelector("#userUtterance"),
  predictButton: document.querySelector("#predictButton"),
  compareButton: document.querySelector("#compareButton"),
  actualAction: document.querySelector("#actualAction"),
  matchChip: document.querySelector("#matchChip"),
  reason: document.querySelector("#reason"),
  decisionMeta: document.querySelector("#decisionMeta"),
  signals: document.querySelector("#signals"),
  comparisonStatus: document.querySelector("#comparisonStatus"),
  comparisonGrid: document.querySelector("#comparisonGrid"),
  runFocusButton: document.querySelector("#runFocusButton"),
  runAllPoliciesButton: document.querySelector("#runAllPoliciesButton"),
  runCardGrid: document.querySelector("#runCardGrid"),
  runTableTitle: document.querySelector("#runTableTitle"),
  runArtifactPath: document.querySelector("#runArtifactPath"),
  decisionLogRows: document.querySelector("#decisionLogRows"),
  runMeta: document.querySelector("#runMeta"),
};

document.addEventListener("DOMContentLoaded", bootstrap);
elements.policySelect.addEventListener("change", () => {
  renderPolicySnapshot();
  clearResults();
});
elements.eventFilter.addEventListener("change", renderScenarioList);
elements.refreshRunsButton.addEventListener("click", refreshRuns);
elements.predictButton.addEventListener("click", predictSelected);
elements.compareButton.addEventListener("click", comparePolicies);
elements.runFocusButton.addEventListener("click", runFocusPolicy);
elements.runAllPoliciesButton.addEventListener("click", runAllPolicies);
elements.tabButtons.forEach((button) => {
  button.addEventListener("click", () => setActiveTab(button.dataset.tab));
});

async function bootstrap() {
  await checkHealth();
  const [schema, policies, scenarios, runs] = await Promise.all([
    fetchJson("/schema"),
    fetchJson("/policies"),
    fetchJson("/scenarios"),
    fetchJson("/runs"),
  ]);
  state.schema = schema;
  state.policies = policies.policies;
  state.scenarios = scenarios.scenarios;
  state.runs = runs.runs;
  state.selectedScenarioId = state.scenarios[0]?.scenario_id || null;
  state.selectedRunId = state.runs[0]?.run_id || null;

  renderControls();
  renderScenarioList();
  renderSelectedScenario();
  renderRunCards();
  renderRecentRuns();
  setActiveTab("playground");
}

async function checkHealth() {
  try {
    const health = await fetchJson("/health");
    elements.healthStatus.textContent = health.status;
    elements.healthStatus.dataset.state = "ok";
  } catch (error) {
    elements.healthStatus.textContent = "offline";
    elements.healthStatus.dataset.state = "error";
  }
}

function renderControls() {
  elements.policySelect.replaceChildren(
    ...state.policies.map((policy) => option(policy.name, policy.name))
  );
  elements.eventFilter.replaceChildren(
    option("", "All events"),
    ...state.schema.event_types.map((eventType) => option(eventType, eventType))
  );
  renderPolicySnapshot();
  renderDatasetStats();
}

function renderPolicySnapshot() {
  const policy = focusPolicy();
  if (!policy) return;
  const snapshot = policy.snapshot || {};
  const entries = Object.entries(snapshot.rule_mapping || snapshot.rule || {});
  elements.policySnapshot.replaceChildren(
    ...entries.slice(0, 7).map(([key, value]) => {
      const row = document.createElement("div");
      const label = document.createElement("span");
      label.textContent = key;
      const action = document.createElement("strong");
      action.textContent = formatSnapshotValue(value);
      row.append(label, action);
      return row;
    })
  );
}

function renderDatasetStats() {
  const eventCounts = countBy(state.scenarios, "event_type");
  elements.datasetStats.replaceChildren(
    statBlock("scenarios", String(state.scenarios.length)),
    statBlock("events", String(Object.keys(eventCounts).length)),
    statBlock("actions", String(state.schema.action_labels.length))
  );
}

function renderScenarioList() {
  const eventFilter = elements.eventFilter.value;
  const visible = state.scenarios.filter((scenario) => {
    return !eventFilter || scenario.event_type === eventFilter;
  });
  elements.scenarioCount.textContent = `${visible.length}/${state.scenarios.length}`;
  elements.scenarioList.replaceChildren(
    ...visible.map((scenario) => {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "scenario-item";
      item.dataset.active = scenario.scenario_id === state.selectedScenarioId;
      item.addEventListener("click", () => {
        state.selectedScenarioId = scenario.scenario_id;
        clearResults();
        renderScenarioList();
        renderSelectedScenario();
      });

      const title = document.createElement("span");
      title.className = "scenario-id";
      title.textContent = scenario.scenario_id;
      const meta = document.createElement("span");
      meta.className = "scenario-meta";
      meta.textContent = `${scenario.event_type} / ${scenario.expected_action}`;
      const utterance = document.createElement("span");
      utterance.className = "scenario-utterance";
      utterance.textContent = scenario.user_utterance || "no user utterance";
      item.append(title, meta, utterance);
      return item;
    })
  );
}

function renderSelectedScenario() {
  const scenario = selectedScenario();
  if (!scenario) return;
  elements.scenarioTitle.textContent = scenario.scenario_id;
  elements.expectedChip.textContent = `expected ${scenario.expected_action}`;
  elements.aiUtterance.textContent = scenario.ai_utterance;
  elements.userUtterance.textContent = scenario.user_utterance || "No user utterance";
  renderDefinitionList(elements.scenarioMeta, [
    ["event", scenario.event_type],
    ["current intent", scenario.ai_current_intent],
    ["expected user intent", scenario.expected_user_intent || "none"],
    ["tone", scenario.user_tone_hint],
    ["level", String(scenario.level)],
  ]);
}

async function predictSelected() {
  const scenario = selectedScenario();
  if (!scenario) return;
  setBusy(elements.predictButton, true);
  try {
    const result = await predictScenario(scenario.scenario_id, elements.policySelect.value);
    state.focusResult = result;
    renderFocusResult(result);
  } finally {
    setBusy(elements.predictButton, false);
  }
}

async function comparePolicies() {
  const scenario = selectedScenario();
  if (!scenario) return;
  setBusy(elements.compareButton, true);
  elements.comparisonStatus.textContent = "Running";
  try {
    state.comparisonResults = await Promise.all(
      state.policies.map((policy) => predictScenario(scenario.scenario_id, policy.name))
    );
    renderComparison();
  } finally {
    setBusy(elements.compareButton, false);
  }
}

async function predictScenario(scenarioId, policyName) {
  return fetchJson(`/scenarios/${scenarioId}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ policy: policyName }),
  });
}

function renderFocusResult(result) {
  const decision = result.decision;
  const isMatch = result.expected_action === decision.actual_action;
  elements.actualAction.textContent = decision.actual_action;
  elements.matchChip.textContent = isMatch ? "match" : "mismatch";
  elements.matchChip.dataset.state = isMatch ? "match" : "mismatch";
  elements.reason.textContent = decision.reason;
  renderDefinitionList(elements.decisionMeta, [
    ["policy", decision.policy_name],
    ["expected", result.expected_action],
    ["actual", decision.actual_action],
    ["latency", `${decision.latency_ms} ms`],
  ]);
  elements.signals.textContent = JSON.stringify(decision.signals, null, 2);
}

function renderComparison() {
  const selectedPolicyName = elements.policySelect.value;
  const matches = state.comparisonResults.filter((result) => {
    return result.expected_action === result.decision.actual_action;
  }).length;
  elements.comparisonStatus.textContent = `${matches}/${state.comparisonResults.length} match`;
  elements.comparisonGrid.replaceChildren(
    ...state.comparisonResults.map((result) => {
      const decision = result.decision;
      const isMatch = result.expected_action === decision.actual_action;
      const card = document.createElement("article");
      card.className = "compare-card";
      card.dataset.state = isMatch ? "match" : "mismatch";
      card.dataset.selected = decision.policy_name === selectedPolicyName ? "true" : "false";

      const header = document.createElement("div");
      header.className = "compare-header";
      const policy = document.createElement("h4");
      policy.textContent = decision.policy_name;
      const badges = document.createElement("div");
      badges.className = "compare-badges";
      if (decision.policy_name === selectedPolicyName) {
        const selected = document.createElement("span");
        selected.className = "chip";
        selected.dataset.state = "selected";
        selected.textContent = "selected";
        badges.append(selected);
      }
      const badge = document.createElement("span");
      badge.className = "chip";
      badge.dataset.state = isMatch ? "match" : "mismatch";
      badge.textContent = isMatch ? "match" : "mismatch";
      badges.append(badge);
      header.append(policy, badges);

      const action = document.createElement("p");
      action.className = "compare-action";
      action.textContent = decision.actual_action;
      const expected = document.createElement("p");
      expected.className = "compare-expected";
      expected.textContent = `expected ${result.expected_action}`;
      const reason = document.createElement("p");
      reason.className = "compare-reason";
      reason.textContent = decision.reason;
      const latency = document.createElement("p");
      latency.className = "compare-latency";
      latency.textContent = `${decision.latency_ms} ms`;

      card.append(header, action, expected, reason, latency);
      return card;
    })
  );
}

async function runFocusPolicy() {
  setBusy(elements.runFocusButton, true);
  try {
    await createRun(elements.policySelect.value);
  } finally {
    setBusy(elements.runFocusButton, false);
  }
}

async function runAllPolicies() {
  setBusy(elements.runAllPoliciesButton, true);
  try {
    for (const policy of state.policies) {
      await createRun(policy.name);
    }
  } finally {
    setBusy(elements.runAllPoliciesButton, false);
  }
}

async function createRun(policyName) {
  const result = await fetchJson("/runs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ policy: policyName }),
  });
  await refreshRuns();
  state.selectedRunId = result.run_id;
  await renderSelectedRun(result.run_id);
  setActiveTab("report");
}

async function refreshRuns() {
  const result = await fetchJson("/runs");
  state.runs = result.runs;
  if (!state.selectedRunId) {
    state.selectedRunId = state.runs[0]?.run_id || null;
  }
  renderRunCards();
  renderRecentRuns();
}

function renderRunCards() {
  if (!state.runs.length) {
    elements.runCardGrid.replaceChildren(emptyState("No run artifacts yet"));
    return;
  }
  const selectedPolicyName = elements.policySelect.value;
  elements.runCardGrid.replaceChildren(
    ...state.runs.map((run) => {
      const card = document.createElement("button");
      card.type = "button";
      card.className = "run-card";
      card.dataset.active = run.run_id === state.selectedRunId;
      card.dataset.focusPolicy = run.policy_version === selectedPolicyName ? "true" : "false";
      card.addEventListener("click", async () => {
        state.selectedRunId = run.run_id;
        renderRunCards();
        await renderSelectedRun(run.run_id);
      });

      const runId = document.createElement("span");
      runId.className = "run-id";
      runId.textContent = run.run_id;
      const policy = document.createElement("strong");
      policy.textContent = run.policy_version;
      const badges = document.createElement("div");
      badges.className = "run-badges";
      if (run.policy_version === selectedPolicyName) {
        const focus = document.createElement("span");
        focus.className = "chip";
        focus.dataset.state = "selected";
        focus.textContent = "focus policy";
        badges.append(focus);
      }
      const metric = document.createElement("span");
      metric.className = "metric";
      metric.textContent = `${percent(run.action_accuracy)} action accuracy`;
      const failures = document.createElement("span");
      failures.className = "run-failures";
      failures.textContent = summarizeFailures(run.failures);
      card.append(runId, policy, badges, metric, failures);
      return card;
    })
  );
}

function renderRecentRuns() {
  const recent = state.runs.slice(0, 5);
  if (!recent.length) {
    elements.recentRuns.replaceChildren(emptyState("No runs"));
    return;
  }
  elements.recentRuns.replaceChildren(
    ...recent.map((run) => {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "recent-run";
      item.addEventListener("click", async () => {
        state.selectedRunId = run.run_id;
        setActiveTab("report");
        renderRunCards();
        await renderSelectedRun(run.run_id);
      });
      const name = document.createElement("span");
      name.textContent = compactRunId(run.run_id);
      const metric = document.createElement("strong");
      metric.textContent = percent(run.action_accuracy);
      item.append(name, metric);
      return item;
    })
  );
}

async function renderSelectedRun(runId) {
  if (!runId) return;
  const artifacts = await fetchJson(`/runs/${runId}`);
  elements.runTableTitle.textContent = `${runId} decision logs`;
  elements.runArtifactPath.textContent = artifacts.run_dir;
  elements.runMeta.textContent = JSON.stringify(artifacts.run_meta, null, 2);
  elements.decisionLogRows.replaceChildren(
    ...artifacts.decision_logs.map((log) => {
      const row = document.createElement("tr");
      const cells = [
        log.scenario_id,
        log.event_type,
        log.expected_action,
        log.actual_action,
        log.primary_failure || "none",
        `${log.latency_ms} ms`,
      ];
      cells.forEach((value, index) => {
        const cell = document.createElement("td");
        cell.textContent = value;
        if (index === 3) {
          cell.className = log.expected_action === log.actual_action ? "ok-text" : "bad-text";
        }
        row.append(cell);
      });
      return row;
    })
  );
}

function setActiveTab(tab) {
  state.activeTab = tab;
  document.body.dataset.activeView = tab;
  elements.playgroundView.hidden = tab !== "playground";
  elements.reportView.hidden = tab !== "report";
  elements.tabButtons.forEach((button) => {
    button.dataset.active = button.dataset.tab === tab;
  });
  if (tab === "report" && state.selectedRunId) {
    renderSelectedRun(state.selectedRunId);
  }
}

function clearResults() {
  state.focusResult = null;
  state.comparisonResults = [];
  elements.actualAction.textContent = "No inspection";
  elements.matchChip.textContent = "pending";
  elements.matchChip.dataset.state = "";
  elements.reason.textContent = "Inspect the selected policy to debug reason, signals, and latency.";
  elements.decisionMeta.replaceChildren();
  elements.signals.textContent = "{}";
  elements.comparisonStatus.textContent = "No comparison yet";
  elements.comparisonGrid.replaceChildren();
}

function selectedScenario() {
  return state.scenarios.find((scenario) => {
    return scenario.scenario_id === state.selectedScenarioId;
  });
}

function focusPolicy() {
  return state.policies.find((policy) => {
    return policy.name === elements.policySelect.value;
  }) || state.policies[0];
}

function renderDefinitionList(target, items) {
  target.replaceChildren(
    ...items.flatMap(([label, value]) => {
      const term = document.createElement("dt");
      term.textContent = label;
      const detail = document.createElement("dd");
      detail.textContent = value;
      return [term, detail];
    })
  );
}

function statBlock(label, value) {
  const block = document.createElement("div");
  const number = document.createElement("strong");
  number.textContent = value;
  const text = document.createElement("span");
  text.textContent = label;
  block.append(number, text);
  return block;
}

function emptyState(text) {
  const item = document.createElement("p");
  item.className = "empty-state";
  item.textContent = text;
  return item;
}

function option(value, label) {
  const item = document.createElement("option");
  item.value = value;
  item.textContent = label;
  return item;
}

function countBy(items, key) {
  return items.reduce((acc, item) => {
    acc[item[key]] = (acc[item[key]] || 0) + 1;
    return acc;
  }, {});
}

function formatSnapshotValue(value) {
  if (typeof value === "string") return value;
  if (value && typeof value === "object") {
    return Object.entries(value)
      .map(([key, action]) => `${key}:${action}`)
      .join(" ");
  }
  return String(value);
}

function summarizeFailures(failures = {}) {
  const pairs = Object.entries(failures).filter(([, value]) => value > 0);
  if (!pairs.length) return "no primary failures";
  return pairs.map(([key, value]) => `${key} ${value}`).join(" / ");
}

function compactRunId(runId) {
  return runId.replace(/^\d{8}_/, "");
}

function percent(value) {
  if (value === undefined || value === null) return "n/a";
  return `${Math.round(Number(value) * 100)}%`;
}

function setBusy(button, busy) {
  button.disabled = busy;
  button.dataset.busy = busy ? "true" : "false";
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message);
  }
  return response.json();
}
