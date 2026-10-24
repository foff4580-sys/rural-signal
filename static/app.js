const byId = (id) => document.getElementById(id);
const labels = {
  incident_type: "Incident",
  location: "Location",
  observed_at: "Observed",
  valid_until: "Valid until",
  source_name: "Source",
  source_status: "Trust status",
};

let cases = [];
let active = null;

function makeList(items) {
  return items.map((text) => {
    const li = document.createElement("li");
    li.textContent = text;
    return li;
  });
}

function renderResult(result) {
  if (!result || !result.passed) {
    byId("result").hidden = true;
    byId("empty-state").hidden = false;
    return;
  }
  const value = result.output;
  byId("facts").replaceChildren(...Object.entries(active.locked).map(([key, raw]) => {
    const cell = document.createElement("div");
    cell.className = "fact";
    const label = document.createElement("b");
    label.textContent = labels[key] || key;
    const text = document.createElement("span");
    text.textContent = raw;
    cell.append(label, text);
    return cell;
  }));
  byId("plain-summary").textContent = value.plain_summary;
  byId("actions").replaceChildren(...makeList(value.do_now));
  byId("unknowns").replaceChildren(...makeList(value.unknowns));
  byId("sms").textContent = value.sms;
  byId("sms-count").textContent = `${value.sms.length}/160 characters`;
  byId("result").hidden = false;
  byId("empty-state").hidden = true;
}

function selectCase(id) {
  active = cases.find((item) => item.id === id);
  document.querySelectorAll(".case-button").forEach((button) => {
    button.setAttribute("aria-current", String(button.dataset.id === id));
  });
  byId("case-eyebrow").textContent = active.eyebrow;
  byId("case-title").textContent = active.title;
  byId("raw-notice").textContent = active.raw_notice;
  const badge = byId("trust-badge");
  badge.textContent = active.locked.source_status;
  badge.className = `trust-badge ${active.locked.source_status.toLowerCase()}`;
  renderResult(active.result);
  byId("run-status").textContent = active.result
    ? `Last validator-approved local run: ${active.result.elapsed_seconds}s · ${active.result.model}`
    : "Nothing is sent and no internet service is contacted.";
}

async function loadCases() {
  const response = await fetch("/api/cases");
  if (!response.ok) throw new Error("Could not load demonstration cases");
  cases = await response.json();
  byId("case-list").replaceChildren(...cases.map((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "case-button";
    button.dataset.id = item.id;
    const eyebrow = document.createElement("span");
    eyebrow.textContent = item.eyebrow;
    const title = document.createElement("strong");
    title.textContent = item.title;
    button.append(eyebrow, title);
    button.addEventListener("click", () => selectCase(item.id));
    return button;
  }));
  selectCase(cases[0].id);
}

byId("run").addEventListener("click", async () => {
  const button = byId("run");
  button.disabled = true;
  button.textContent = "Spark is interpreting…";
  byId("run-status").textContent = "Running local CPU inference, then checking every safety gate…";
  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({case_id: active.id}),
    });
    const value = await response.json();
    if (!response.ok) throw new Error(value.error || "The run failed");
    active.result = value;
    renderResult(value);
    const held = active.id === "stress_unverified_prompt_injection" ? " Trust boundary held." : "";
    byId("run-status").textContent = `Validator passed in ${value.elapsed_seconds}s.${held} Nothing was sent.`;
  } catch (error) {
    renderResult(null);
    byId("run-status").textContent = `Output withheld: ${error.message}`;
  } finally {
    button.disabled = false;
    button.textContent = "Run Spark locally";
  }
});

loadCases().catch((error) => {
  byId("case-title").textContent = "Demo unavailable";
  byId("run-status").textContent = error.message;
  byId("run").disabled = true;
});
