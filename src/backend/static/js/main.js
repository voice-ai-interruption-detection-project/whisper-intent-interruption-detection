const state = {
  // 서버에서 받은 어휘 목록을 기준으로 UI와 백엔드 계약을 맞춘다.
  activeTab: "playground",
  schema: null,
  policies: [],
  datasets: [],
  scenarios: [],
  runs: [],
  selectedScenarioId: null,
  selectedRunId: null,
  focusResult: null,
  comparisonResults: [],
};

const ACTION_LABELS = {
  continue: "계속 말하기",
  brief_ack: "짧게 인정",
  respond_and_continue: "답하고 계속",
  stop_and_switch: "멈추고 전환",
  ask_clarifying: "확인 질문",
  handoff: "상담사 연결 후보",
};

const EVENT_TYPE_LABELS = {
  no_speech: "고객 발화 없음",
  noise: "소음",
  backchannel: "맞장구",
  same_intent_question: "같은 주제 질문",
  intent_shift: "의도 전환",
  complaint: "불만/긴급",
  ambiguous: "모호함",
};

const TONE_HINT_LABELS = {
  neutral: "보통",
  frustrated: "불만",
  urgent: "긴급",
};

const PRIMARY_FAILURE_LABELS = {
  false_stop: "불필요한 멈춤",
  missed_switch: "전환 놓침",
  action_confusion: "행동 혼동",
  ambiguous_intent: "모호한 의도",
  STT_uncertainty: "STT 불확실",
};

const INPUT_MODE_LABELS = {
  text: "Text Replay",
  audio_file: "Audio File Test",
};

// DOM 접근 경계를 한 곳에 모아 렌더링 함수가 같은 요소 참조를 쓰게 한다.
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
  predictTextButton: document.querySelector("#predictTextButton"),
  predictAudioButton: document.querySelector("#predictAudioButton"),
  textCurrentIntent: document.querySelector("#textCurrentIntent"),
  textToneHint: document.querySelector("#textToneHint"),
  textAiUtterance: document.querySelector("#textAiUtterance"),
  textUserUtterance: document.querySelector("#textUserUtterance"),
  textHasUserSpeech: document.querySelector("#textHasUserSpeech"),
  audioFileInput: document.querySelector("#audioFileInput"),
  audioTranscriber: document.querySelector("#audioTranscriber"),
  audioTranscript: document.querySelector("#audioTranscript"),
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
  runInputMode: document.querySelector("#runInputMode"),
  runDataset: document.querySelector("#runDataset"),
  runInputSummary: document.querySelector("#runInputSummary"),
  audioRunManifest: document.querySelector("#audioRunManifest"),
  audioBenchTranscriber: document.querySelector("#audioBenchTranscriber"),
  audioBenchWhisperModel: document.querySelector("#audioBenchWhisperModel"),
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
elements.predictTextButton.addEventListener("click", predictTextInput);
elements.predictAudioButton.addEventListener("click", predictAudioInput);
elements.compareButton.addEventListener("click", comparePolicies);
elements.runFocusButton.addEventListener("click", runFocusPolicy);
elements.runAllPoliciesButton.addEventListener("click", runAllPolicies);
elements.runInputMode.addEventListener("change", renderRunInputControls);
elements.runDataset.addEventListener("change", renderRunInputControls);
elements.audioBenchTranscriber.addEventListener("change", renderRunInputControls);
elements.audioRunManifest.addEventListener("input", renderRunInputControls);
elements.audioBenchWhisperModel.addEventListener("input", renderRunInputControls);
elements.tabButtons.forEach((button) => {
  button.addEventListener("click", () => setActiveTab(button.dataset.tab));
});

// 첫 화면에 필요한 어휘, 정책, 판단 케이스(Scenario), 실행 목록을 한 번에 준비한다.
async function bootstrap() {
  await checkHealth();
  // 초기 데이터는 함께 가져와 첫 렌더링의 기준을 서로 맞춘다.
  const [schema, policies, datasets, scenarios, runs] = await Promise.all([
    fetchJson("/schema"),
    fetchJson("/policies"),
    fetchJson("/datasets"),
    fetchJson("/scenarios"),
    fetchJson("/runs"),
  ]);
  state.schema = schema;
  state.policies = policies.policies;
  state.datasets = datasets.datasets;
  state.scenarios = scenarios.scenarios;
  state.runs = runs.runs;
  state.selectedScenarioId = state.scenarios[0]?.scenario_id || null;
  state.selectedRunId = state.runs[0]?.run_id || null;

  renderControls(datasets.default_dataset_id);
  renderScenarioList();
  renderSelectedScenario();
  renderRunCards();
  renderRecentRuns();
  renderRunInputControls();
  setActiveTab("playground");
}

// 백엔드 상태를 확인해 사이드바 상태 표시를 갱신한다.
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

// 정책 선택, event_type 필터, 데이터셋 요약의 초기 선택지를 채운다.
function renderControls(defaultDatasetId) {
  elements.policySelect.replaceChildren(
    ...state.policies.map((policy) => option(policy.name, policy.name))
  );
  renderDatasetOptions(defaultDatasetId);
  elements.eventFilter.replaceChildren(
    option("", "전체 고객 신호"),
    ...state.schema.event_types.map((eventType) => option(eventType, formatEventType(eventType)))
  );
  elements.textToneHint.replaceChildren(
    ...state.schema.user_tone_hints.map((tone) => option(tone, formatToneHint(tone)))
  );
  renderPolicySnapshot();
  renderDatasetStats();
}

// Test Bench dataset 선택지는 registry와 input_mode 지원 범위를 기준으로 표시한다.
function renderDatasetOptions(preferredDatasetId) {
  const inputMode = elements.runInputMode.value;
  const currentDatasetId = preferredDatasetId || elements.runDataset.value;

  elements.runDataset.replaceChildren(
    ...state.datasets.map((dataset) => {
      const datasetOption = option(dataset.id, `${dataset.label} (${dataset.scope})`);
      datasetOption.disabled = !datasetSupportsInputMode(dataset, inputMode);

      return datasetOption;
    })
  );

  const selected = state.datasets.find((dataset) => {
    return dataset.id === currentDatasetId && datasetSupportsInputMode(dataset, inputMode);
  });
  const fallback = state.datasets.find((dataset) => datasetSupportsInputMode(dataset, inputMode));

  elements.runDataset.value = (selected || fallback)?.id || "";
}

// 현재 policy snapshot을 사이드바에 표시한다.
function renderPolicySnapshot() {
  const policy = focusPolicy();
  if (!policy) return;

  const snapshot = policy.snapshot || {};
  const entries = Object.entries(snapshot.rule_mapping || snapshot.rule || snapshot.llm || snapshot);

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

// 데이터셋의 판단 케이스(Scenario), 고객 신호, 행동 라벨 규모를 요약한다.
function renderDatasetStats() {
  const eventCounts = countBy(state.scenarios, "event_type");

  elements.datasetStats.replaceChildren(
    statBlock("cases", String(state.scenarios.length)),
    statBlock("event_types", String(Object.keys(eventCounts).length)),
    statBlock("actions", String(state.schema.action_labels.length))
  );
}

// event_type 필터를 반영해 판단 케이스(Scenario) 목록을 다시 그린다.
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
      meta.textContent = `${formatEventType(scenario.event_type)} / ${formatExpectedActions(
        scenario
      )}`;

      const utterance = document.createElement("span");
      utterance.className = "scenario-utterance";
      utterance.textContent = scenario.user_utterance || "고객 발화 없음";

      item.append(title, meta, utterance);
      return item;
    })
  );
}

// 현재 선택된 판단 케이스(Scenario)의 입력 발화와 기준 메타데이터를 표시한다.
function renderSelectedScenario() {
  const scenario = selectedScenario();
  if (!scenario) return;

  elements.scenarioTitle.textContent = scenario.scenario_id;
  elements.expectedChip.textContent = `expected ${formatExpectedActions(scenario)}`;
  elements.aiUtterance.textContent = scenario.ai_utterance;
  elements.userUtterance.textContent = scenario.user_utterance || "고객 발화 없음";

  renderDefinitionList(elements.scenarioMeta, [
    ["고객 신호(event_type)", formatEventType(scenario.event_type)],
    ["현재 AI 의도", scenario.ai_current_intent],
    ["기준 고객 의도", scenario.expected_user_intent || "없음"],
    ["톤", formatToneHint(scenario.user_tone_hint)],
    ["난이도", String(scenario.level)],
  ]);
  fillTextInputsFromScenario(scenario);
}

// Playground의 선택 판단 케이스(Scenario)를 현재 policy로 실행한다.
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

// 직접 입력한 Text Replay transcript를 현재 policy로 실행한다.
async function predictTextInput() {
  setBusy(elements.predictTextButton, true);

  try {
    const result = await fetchJson("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        policy: elements.policySelect.value,
        ai_current_intent: elements.textCurrentIntent.value,
        ai_utterance: elements.textAiUtterance.value,
        user_utterance: elements.textUserUtterance.value,
        user_tone_hint: elements.textToneHint.value,
        has_user_speech: elements.textHasUserSpeech.checked,
      }),
    });

    state.focusResult = result;
    renderFocusResult(result);
  } finally {
    setBusy(elements.predictTextButton, false);
  }
}

// 업로드 오디오를 선택 판단 케이스(Scenario) context와 합쳐 같은 runner 경로로 실행한다.
async function predictAudioInput() {
  const scenario = selectedScenario();
  const file = elements.audioFileInput.files[0];
  if (!scenario || !file) return;

  setBusy(elements.predictAudioButton, true);

  try {
    const form = new FormData();

    form.append("file", file);
    form.append("scenario_id", scenario.scenario_id);
    form.append("policy", elements.policySelect.value);
    form.append("transcriber", elements.audioTranscriber.value);
    form.append("transcript", elements.audioTranscript.value);

    const result = await fetchJson("/audio/predict", {
      method: "POST",
      body: form,
    });

    state.focusResult = result;
    renderFocusResult(result);
  } finally {
    setBusy(elements.predictAudioButton, false);
  }
}

// 선택된 판단 케이스(Scenario)를 등록된 모든 policy로 실행해 결과를 비교한다.
async function comparePolicies() {
  const scenario = selectedScenario();
  if (!scenario) return;

  setBusy(elements.compareButton, true);
  elements.comparisonStatus.textContent = "실행 중";

  try {
    state.comparisonResults = await Promise.all(
      state.policies.map((policy) => predictScenario(scenario.scenario_id, policy.name))
    );

    renderComparison();
  } finally {
    setBusy(elements.compareButton, false);
  }
}

// 판단 케이스(Scenario) 재생 API를 호출한다.
async function predictScenario(scenarioId, policyName) {
  return fetchJson(`/scenarios/${scenarioId}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ policy: policyName }),
  });
}

// 단일 policy 판단 결과를 결과 패널의 expected/actual 비교 형태로 표시한다.
function renderFocusResult(result) {
  const decision = result.decision;
  const hasExpected = Array.isArray(result.expected_actions);
  const isMatch = hasExpected && resultActionMatch(result);

  elements.actualAction.textContent = formatActionLabel(decision.actual_action);
  elements.matchChip.textContent = hasExpected ? (isMatch ? "match" : "mismatch") : "unscored";
  elements.matchChip.dataset.state = hasExpected ? (isMatch ? "match" : "mismatch") : "";
  elements.reason.textContent = decision.reason;

  renderDefinitionList(elements.decisionMeta, [
    ["policy", decision.policy_name],
    ["expected_actions", hasExpected ? formatExpectedActions(result) : "n/a"],
    ["actual_action", decision.actual_action],
    ["latency", `${decision.latency_ms} ms`],
  ]);

  elements.signals.textContent = JSON.stringify(decision.signals, null, 2);
}

// 선택한 판단 케이스(Scenario)를 텍스트/오디오 입력의 시작값으로 복사한다.
function fillTextInputsFromScenario(scenario) {
  elements.textCurrentIntent.value = scenario.ai_current_intent;
  elements.textAiUtterance.value = scenario.ai_utterance;
  elements.textUserUtterance.value = scenario.user_utterance;
  elements.textToneHint.value = scenario.user_tone_hint;
  elements.textHasUserSpeech.checked = scenario.has_user_speech;
  elements.audioTranscript.value = scenario.user_utterance;
}

// 여러 policy의 판단 결과를 카드 형태로 비교 표시한다.
function renderComparison() {
  const selectedPolicyName = elements.policySelect.value;
  const matches = state.comparisonResults.filter((result) => {
    return resultActionMatch(result);
  }).length;

  elements.comparisonStatus.textContent = `${matches}/${state.comparisonResults.length} match`;
  elements.comparisonGrid.replaceChildren(
    ...state.comparisonResults.map((result) => {
      const decision = result.decision;
      const isMatch = resultActionMatch(result);
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
      action.textContent = formatActionLabel(decision.actual_action);

      const expected = document.createElement("p");
      expected.className = "compare-expected";
      expected.textContent = `expected ${formatExpectedActions(result)}`;

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

// Test Bench에서 현재 선택 policy의 run artifact를 생성한다.
async function runFocusPolicy() {
  setBusy(elements.runFocusButton, true);

  try {
    await createRun(elements.policySelect.value);
  } finally {
    setBusy(elements.runFocusButton, false);
  }
}

// Test Bench에서 등록된 모든 policy의 run artifact를 순서대로 생성한다.
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

// run 생성 API를 호출한 뒤 목록과 상세 화면을 최신 상태로 맞춘다.
async function createRun(policyName) {
  // run artifact 생성 책임은 백엔드에 두고, UI는 생성 뒤 조회만 한다.
  const body = {
    policy: policyName,
    input_mode: elements.runInputMode.value,
  };
  const datasetId = elements.runDataset.value;

  if (datasetId) {
    body.dataset_id = datasetId;
  }

  if (body.input_mode === "audio_file") {
    body.audio_manifest = elements.audioRunManifest.value;
    body.audio_transcriber = elements.audioBenchTranscriber.value;

    const whisperModel = elements.audioBenchWhisperModel.value.trim();

    if (body.audio_transcriber === "whisper" && whisperModel) {
      body.whisper_model = whisperModel;
    }
  }

  const result = await fetchJson("/runs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  await refreshRuns();

  state.selectedRunId = result.run_id;

  await renderSelectedRun(result.run_id);
  setActiveTab("report");
}

// run artifact 목록을 다시 가져와 리포트와 사이드바 영역을 갱신한다.
async function refreshRuns() {
  const result = await fetchJson("/runs");
  state.runs = result.runs;

  if (!state.selectedRunId) {
    state.selectedRunId = state.runs[0]?.run_id || null;
  }

  renderRunCards();
  renderRecentRuns();
}

// 리포트 상단의 run artifact 카드 목록을 렌더링한다.
function renderRunCards() {
  if (!state.runs.length) {
    elements.runCardGrid.replaceChildren(emptyState("아직 run artifact가 없습니다"));
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

      const mode = document.createElement("span");
      mode.className = "chip";
      mode.textContent = run.mode || "text";

      badges.append(mode);

      if (run.policy_version === selectedPolicyName) {
        const focus = document.createElement("span");
        focus.className = "chip";
        focus.dataset.state = "selected";
        focus.textContent = "focus policy";
        badges.append(focus);
      }

      const target = document.createElement("span");
      target.className = "run-failures";
      target.textContent = runTargetSummary(run);

      const metric = document.createElement("span");
      metric.className = "metric";
      metric.textContent = `${percent(run.action_accuracy)} action_accuracy`;

      const failures = document.createElement("span");
      failures.className = "run-failures";
      failures.textContent = summarizeFailures(run.failures);

      card.append(runId, policy, badges, target, metric, failures);
      return card;
    })
  );
}

// 사이드바에 최근 run artifact 몇 개를 빠르게 접근할 수 있게 표시한다.
function renderRecentRuns() {
  const recent = state.runs.slice(0, 5);
  if (!recent.length) {
    elements.recentRuns.replaceChildren(emptyState("run 없음"));
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

// 선택된 run artifact의 메타데이터와 판단 로그 표를 그린다.
async function renderSelectedRun(runId) {
  if (!runId) return;

  const artifacts = await fetchJson(`/runs/${runId}`);

  elements.runTableTitle.textContent = `${runId} 판단 로그`;
  elements.runArtifactPath.textContent = artifacts.run_dir;
  elements.runMeta.textContent = JSON.stringify(artifacts.run_meta, null, 2);

  elements.decisionLogRows.replaceChildren(
    ...artifacts.decision_logs.map((log) => {
      const row = document.createElement("tr");
      const isMatch = log.action_match ?? logActionMatch(log);
      const cells = [
        log.scenario_id,
        log.event_type,
        formatExpectedActions(log),
        log.actual_action,
        log.primary_failure || "none",
        `${log.latency_ms} ms`,
      ];
      cells.forEach((value, index) => {
        const cell = document.createElement("td");
        cell.textContent = value;

        if (index === 3) {
          cell.className = isMatch ? "ok-text" : "bad-text";
        }

        row.append(cell);
      });

      return row;
    })
  );
}

// Playground와 Test Bench 탭 전환 상태를 화면과 body 데이터셋에 반영한다.
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

// 판단 케이스(Scenario)나 정책이 바뀌었을 때 이전 판단 결과를 비운다.
function clearResults() {
  state.focusResult = null;
  state.comparisonResults = [];

  elements.actualAction.textContent = "결과 대기";
  elements.matchChip.textContent = "ready";
  elements.matchChip.dataset.state = "";
  elements.reason.textContent = "실행하면 reason, signals, latency를 여기에서 확인합니다.";
  elements.decisionMeta.replaceChildren();
  elements.signals.textContent = "{}";
  elements.comparisonStatus.textContent = "No comparison yet";
  elements.comparisonGrid.replaceChildren();
}

// Test Bench의 input_mode에 따라 audio 옵션 표시와 입력 요약을 갱신한다.
function renderRunInputControls() {
  const isAudio = elements.runInputMode.value === "audio_file";

  renderDatasetOptions();

  document.querySelectorAll(".audio-run-field").forEach((field) => {
    field.hidden = !isAudio;
  });

  elements.audioBenchWhisperModel.disabled = elements.audioBenchTranscriber.value !== "whisper";
  const dataset = selectedDatasetSpec();
  const datasetSummary = dataset
    ? `${dataset.label} / ${dataset.scope}`
    : "dataset";
  elements.runInputSummary.textContent = isAudio
    ? `Audio File Test / ${datasetSummary} / ${elements.audioBenchTranscriber.value}`
    : `Text Replay / ${datasetSummary}`;
}

// 현재 선택된 판단 케이스(Scenario) 식별자에 해당하는 객체를 찾는다.
function selectedScenario() {
  return state.scenarios.find((scenario) => {
    return scenario.scenario_id === state.selectedScenarioId;
  });
}

// 현재 선택 상자 값에 해당하는 policy 정보를 찾는다.
function focusPolicy() {
  return state.policies.find((policy) => {
    return policy.name === elements.policySelect.value;
  }) || state.policies[0];
}

// 이름/값 쌍을 정의 목록 화면 요소로 바꿔 넣는다.
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

// 작은 숫자 통계 블록 화면 요소를 만든다.
function statBlock(label, value) {
  const block = document.createElement("div");
  const number = document.createElement("strong");
  number.textContent = value;

  const text = document.createElement("span");
  text.textContent = label;

  block.append(number, text);
  return block;
}

// 목록이 비었을 때 보여줄 빈 상태 문구를 만든다.
function emptyState(text) {
  const item = document.createElement("p");
  item.className = "empty-state";
  item.textContent = text;
  return item;
}

// 선택 상자에 넣을 option 화면 요소를 만든다.
function option(value, label) {
  const item = document.createElement("option");
  item.value = value;
  item.textContent = label;
  return item;
}

// 객체 배열을 특정 속성값 기준으로 집계한다.
function countBy(items, key) {
  return items.reduce((acc, item) => {
    acc[item[key]] = (acc[item[key]] || 0) + 1;
    return acc;
  }, {});
}

// 정책 스냅샷 값이 문자열/객체 어느 쪽이어도 한 줄로 표시한다.
function formatSnapshotValue(value) {
  if (typeof value === "string") return value;

  if (value && typeof value === "object") {
    return Object.entries(value)
      .map(([key, action]) => `${key}:${action}`)
      .join(" ");
  }

  return String(value);
}

// primary failure 집계를 리포트 카드에 들어갈 짧은 문장으로 압축한다.
function summarizeFailures(failures = {}) {
  const pairs = Object.entries(failures).filter(([, value]) => value > 0);
  if (!pairs.length) return "no primary failures";

  return pairs.map(([key, value]) => `${key} ${value}`).join(" / ");
}

// run card에서 text/audio target을 짧게 표시한다.
function runTargetSummary(run) {
  const datasetLabel = run.dataset_label || run.dataset_id || run.dataset || run.target || "dataset";
  const datasetScope = run.dataset_scope ? ` / ${run.dataset_scope}` : "";

  if (run.mode === "audio_file") {
    const transcriber = run.input_adapter_snapshot?.transcriber?.provider || "audio";
    return `${datasetLabel}${datasetScope} / ${transcriber}`;
  }

  return `${datasetLabel}${datasetScope}`;
}

// 현재 선택된 Test Bench dataset registry 항목을 반환한다.
function selectedDatasetSpec() {
  return state.datasets.find((dataset) => dataset.id === elements.runDataset.value);
}

function datasetSupportsInputMode(dataset, inputMode) {
  return (dataset.input_modes || ["text"]).includes(inputMode);
}

// 날짜 접두어를 줄여 사이드바에서 실행 식별자를 읽기 쉽게 만든다.
function compactRunId(runId) {
  return runId.replace(/^\d{8}_/, "");
}

// 0~1 비율 값을 정수 퍼센트 문자열로 바꾼다.
function percent(value) {
  if (value === undefined || value === null) return "n/a";

  return `${Math.round(Number(value) * 100)}%`;
}

function resultActionMatch(result) {
  if (typeof result.action_match === "boolean") {
    return result.action_match;
  }

  const expectedActions = Array.isArray(result.expected_actions)
    ? result.expected_actions
    : [result.expected_action].filter(Boolean);

  return expectedActions.includes(result.decision.actual_action);
}

function formatExpectedActions(item) {
  const expectedActions = Array.isArray(item.expected_actions)
    ? item.expected_actions
    : [item.expected_action].filter(Boolean);

  return expectedActions.filter(Boolean).join(", ");
}

function logActionMatch(log) {
  const expectedActions = Array.isArray(log.expected_actions)
    ? log.expected_actions
    : [log.expected_action].filter(Boolean);

  return expectedActions.includes(log.actual_action);
}

function formatCodeLabel(value, labels) {
  if (value === undefined || value === null || value === "") return "";

  const label = labels[value];

  return label ? `${label} (${value})` : value;
}

function formatActionLabel(value) {
  return formatCodeLabel(value, ACTION_LABELS);
}

function formatEventType(value) {
  return formatCodeLabel(value, EVENT_TYPE_LABELS);
}

function formatToneHint(value) {
  return formatCodeLabel(value, TONE_HINT_LABELS);
}

function formatPrimaryFailure(value) {
  return formatCodeLabel(value, PRIMARY_FAILURE_LABELS);
}

function formatInputMode(value) {
  return formatCodeLabel(value, INPUT_MODE_LABELS);
}

// 비동기 작업 중 버튼의 중복 클릭을 막는다.
function setBusy(button, busy) {
  button.disabled = busy;
  button.dataset.busy = busy ? "true" : "false";
}

// fetch 응답을 JSON으로 읽고 실패 응답은 오류로 올린다.
async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message);
  }

  return response.json();
}
