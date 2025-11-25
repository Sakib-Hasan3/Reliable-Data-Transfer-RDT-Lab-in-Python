// frontend/app.js

const BACKEND_URL = "http://127.0.0.1:5000/api/simulate";

const runBtn = document.getElementById("runBtn");
const statusEl = document.getElementById("status");
const statsEl = document.getElementById("stats");
const finalDataEl = document.getElementById("finalData");
const eventsListEl = document.getElementById("eventsList");

runBtn.addEventListener("click", async () => {
  const message = document.getElementById("message").value;
  const packetSize = Number(document.getElementById("packetSize").value);
  const lossRate = Number(document.getElementById("lossRate").value);
  const corruptionRate = Number(document.getElementById("corruptionRate").value);
  const ackLossRate = Number(document.getElementById("ackLossRate").value);
  const maxRetries = Number(document.getElementById("maxRetries").value);

  statusEl.textContent = "Running simulation...";
  runBtn.disabled = true;

  try {
    const response = await fetch(BACKEND_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        packet_size: packetSize,
        loss_rate: lossRate,
        corruption_rate: corruptionRate,
        ack_loss_rate: ackLossRate,
        max_retries_per_packet: maxRetries,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }

    const result = await response.json();
    renderResult(result);
    statusEl.textContent = "Simulation complete.";
  } catch (err) {
    console.error(err);
    statusEl.textContent = "Error: " + err.message;
  } finally {
    runBtn.disabled = false;
  }
});

function renderResult(result) {
  // Stats
  const stats = result.stats || {};
  const cfg = result.config_used || {};
  statsEl.textContent = JSON.stringify(
    {
      ...stats,
      config_used: cfg,
    },
    null,
    2
  );

  // Final reconstructed data
  finalDataEl.textContent = result.final_data || "";

  // Events
  const events = result.events || [];
  eventsListEl.innerHTML = "";

  events.forEach((ev) => {
    const card = document.createElement("div");
    card.className = "event-card";

    const step = document.createElement("div");
    step.className = "event-step";
    step.textContent = "#" + (ev.step ?? "?");

    const who = document.createElement("div");
    who.className = "event-who";
    who.textContent = ev.who || "";

    const type = document.createElement("div");
    type.className = "event-type";
    type.textContent = (ev.type || "").replace(/_/g, " ");

    const descWrapper = document.createElement("div");
    const seq = document.createElement("div");
    seq.className = "event-seq";
    if (typeof ev.seq === "number") {
      seq.textContent = "seq=" + ev.seq;
    } else {
      seq.textContent = "";
    }

    const desc = document.createElement("div");
    desc.className = "event-description";
    desc.textContent = ev.description || "";

    descWrapper.appendChild(seq);
    descWrapper.appendChild(desc);

    card.appendChild(step);
    card.appendChild(who);
    card.appendChild(type);
    card.appendChild(descWrapper);

    eventsListEl.appendChild(card);
  });
}
