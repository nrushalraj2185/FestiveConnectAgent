import ApiService from "../services/apiService.js";

const eventListEl = document.getElementById("eventList");
const addEventBtn = document.getElementById("addEventBtn");
const modal = document.getElementById("eventModal");
const closeModalBtn = document.getElementById("closeModalBtn");
const eventForm = document.getElementById("eventForm");
const modalTitle = document.getElementById("modalTitle");
const sortSelect = document.getElementById("sortSelect");

let editEventId = null;

document.addEventListener("DOMContentLoaded", () => {
  if (!eventListEl) return;
  loadEvents();
});

// ---------------- CUSTOM CONFIRM DIALOG ----------------
async function customConfirm(message) {
  return new Promise((resolve) => {
    const wrapper = document.createElement("div");
    wrapper.className = "confirm-modal";

    wrapper.innerHTML = `
      <div class="confirm-content">
        <p>${message}</p>
        <div class="confirm-actions">
          <button id="confirmYes" class="btn danger">Yes</button>
          <button id="confirmNo" class="btn ghost">No</button>
        </div>
      </div>
    `;

    document.body.appendChild(wrapper);

    wrapper.querySelector("#confirmYes").onclick = () => {
      wrapper.remove();
      resolve(true);
    };

    wrapper.querySelector("#confirmNo").onclick = () => {
      wrapper.remove();
      resolve(false);
    };
  });
}
// --------------------------------------------------------


addEventBtn.addEventListener("click", () => openModal());
closeModalBtn.addEventListener("click", () => closeModal());
sortSelect.addEventListener("change", () => loadEvents());

eventForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const form = eventForm;
  const eventData = {
    title: form.title.value.trim(),
    date: form.date.value,
    location: form.location.value.trim(),
    performers: form.performers.value
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean),
    description: form.description.value.trim(),
  };

  try {
    if (editEventId) {
      await ApiService.put(`/events/${encodeURIComponent(editEventId)}`, eventData);
    } else {
      await ApiService.post("/events/", eventData);
    }
    closeModal();
    await loadEvents();
  } catch (error) {
    console.error("Error saving event:", error);
    alert("❌ Failed to save event. Please try again.");
  }
});

async function loadEvents() {
  try {
    eventListEl.innerHTML = `<p>Loading events...</p>`;
    const events = await ApiService.get("/events/");
    renderEvents(events);
  } catch (error) {
    console.error("Error loading events:", error);
    eventListEl.innerHTML = `<p class="error-text">⚠️ Failed to load events. Please check the server.</p>`;
  }
}

function renderEvents(events = []) {
  if (!events.length) {
    eventListEl.innerHTML = `<p>No events found. Click "Add Event" to create one.</p>`;
    return;
  }

  const sorted = [...events].sort((a, b) => {
    const aT = new Date(a.date).getTime();
    const bT = new Date(b.date).getTime();
    return sortSelect.value === "date_desc" ? bT - aT : aT - bT;
  });

  eventListEl.innerHTML = sorted
    .map(
      (ev) => `
      <article class="event-card">
        <div class="event-main">
          <h3>${escapeHtml(ev.title)}</h3>
          <p class="meta"><strong>${formatDateTime(ev.date)}</strong></p>
          <p class="location"><i class="fa-solid fa-location-dot"></i> ${escapeHtml(ev.location)}</p>
          ${ev.description ? `<p class="desc">${escapeHtml(ev.description)}</p>` : ""}
          ${
            ev.performers?.length
              ? `<p class="lineup"><strong>Lineup:</strong> ${escapeHtml(ev.performers.join(", "))}</p>`
              : ""
          }
        </div>
        <div class="event-actions">
          <button type="button" class="btn small ghost" data-action="edit" data-id="${ev.id}">
            <i class="fa-solid fa-pen"></i>
          </button>
          <button type="button" class="btn small danger" data-action="delete" data-id="${ev.id}">
            <i class="fa-solid fa-trash"></i>
          </button>
        </div>
      </article>
    `
    )
    .join("");
}

eventListEl.addEventListener("click", async (e) => {
  const btn = e.target.closest("button[data-action]");
  if (!btn) return;

  const action = btn.dataset.action;
  const id = (btn.dataset.id || "").trim();

  if (!id) return;

  try {
    if (action === "edit") {
      const ev = await ApiService.get(`/events/${encodeURIComponent(id)}`);
      editEventId = id;
      openModal(ev);
    } else if (action === "delete") {
      const confirmed = await customConfirm("🗑️ Delete this event?");
      if (!confirmed) return;

      await ApiService.delete(`/events/${encodeURIComponent(id)}`);
      await loadEvents();
    }
  } catch (error) {
    console.error(`Error handling ${action}:`, error);
    alert("⚠️ Failed to perform action. Please check the server.");
  }
});

function openModal(eventData = null) {
  modal.style.display = "flex";
  if (eventData) {
    modalTitle.textContent = "Edit Event";
    eventForm.title.value = eventData.title || "";
    eventForm.date.value = eventData.date || "";
    eventForm.location.value = eventData.location || "";
    eventForm.performers.value = eventData.performers?.join(", ") || "";
    eventForm.description.value = eventData.description || "";
  } else {
    modalTitle.textContent = "Add New Event";
    eventForm.reset();
    editEventId = null;
  }
}

function closeModal() {
  modal.style.display = "none";
  editEventId = null;
}

function escapeHtml(str = "") {
  return String(str).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
}

function formatDateTime(value) {
  if (!value) return "TBA";
  try {
    return new Date(value).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
  } catch {
    return value;
  }
}

window.onclick = function (event) {
  if (event.target === modal) closeModal();
};
