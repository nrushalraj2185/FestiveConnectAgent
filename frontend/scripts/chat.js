import ApiService from "../services/apiService.js";
// Match the backend agent name from `backend/constants.py`
const AgentName = "festive_agent";
let activeSessionId = "";

// DOM elements will be assigned after DOMContentLoaded to avoid null refs
let messagesEl;
let form;
let input;
let sendBtn;
let fileInput;
let uploadList;
let sessionsListWrapper;
let filePreview;

document.addEventListener("DOMContentLoaded", () => {
  initChat();
});

function initChat() {
  // Query DOM elements now that document is loaded
  messagesEl = document.getElementById("messages");
  form = document.getElementById("chat-form");
  input = document.getElementById("message-input");
  sendBtn = document.getElementById("send-btn");
  fileInput = document.getElementById("file-input");
  uploadList = document.getElementById("upload-list");
  sessionsListWrapper = document.getElementById("sessions-list");

  const newSessionButton = document.getElementById("new-session");
  if (newSessionButton) newSessionButton.addEventListener("click", createSession);
  const exportSessionsBtn = document.getElementById("exportSessionsBtn");
  const clearSessionsBtn = document.getElementById("clearSessionsBtn");
  if (exportSessionsBtn) exportSessionsBtn.addEventListener("click", exportAllStoredSessions);
  if (clearSessionsBtn) clearSessionsBtn.addEventListener("click", clearAllStoredSessions);

  // Create and insert filePreview element
  filePreview = document.createElement("div");
  filePreview.className = "file-preview";
  if (form) form.insertBefore(filePreview, form.firstChild);

  // Attach other event listeners
  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file) {
        currentFile = file;
        showFilePreview(file);
      }
    });
  }

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const text = input ? input.value.trim() : "";
      if (input) input.value = "";
      await sendMessage(text, currentFile);
    });
  }

  listSessions();
}

function listSessions() {
  ApiService.get(`/apps/${AgentName}/users/user/sessions`)
    .then((sessions) => {
      if (sessions.length) {
        activeSessionId = sessions[0].id;
        for (let i = 0; i < sessions.length; i++) {
          const sid = sessions[i].id;
          // Ensure stored session exists in localStorage
          ensureStoredSession(sid);
          createSessionElement(sid);
        }
      }
    })
    .catch((error) => console.error(error));
}

function createSessionElement(id) {
  const li = document.createElement("li");
  li.setAttribute("id", `id-${id}`);
  li.setAttribute("class", "session-item");
  const exportIcon = document.createElement("i");
  exportIcon.setAttribute("class", "fa fa-file-export export-session");
  exportIcon.setAttribute("title", "Export session");
  exportIcon.onclick = (event) => { event.stopPropagation(); exportStoredSession(id); };

  const deleteIcon = document.createElement("i");
  deleteIcon.setAttribute("class", "fa fa-trash delete-session");
  deleteIcon.onclick = (event) => deleteSession(event, id);
  const spanEl = document.createElement("span");
  spanEl.innerHTML = id;

  // Append to DOM first to ensure updateActiveSession can query it
  if (sessionsListWrapper) sessionsListWrapper.appendChild(li);

  if (activeSessionId === id) {
    const existingSessions =
      sessionsListWrapper ? sessionsListWrapper.querySelectorAll(".session-item") : [];
    if (existingSessions.length) {
      for (let j = 0; j < existingSessions.length; j++) {
        existingSessions[j].classList.remove("active");
      }
    }
    li.classList.add("active");
    updateActiveSession(id);
  }
  li.onclick = () => updateActiveSession(id);
  li.appendChild(spanEl);
  li.appendChild(exportIcon);
  li.appendChild(deleteIcon);
}

function createSession() {
  ApiService.post(`/apps/${AgentName}/users/user/sessions`)
    .then((session) => {
      activeSessionId = session.id;
      // Initialize storage for this session and render
      ensureStoredSession(session.id, true);
      createSessionElement(session.id);
    })
    .catch((error) => console.error(error));
}

function deleteSession(event, id) {
  event.stopPropagation();
  ApiService.delete(`/apps/${AgentName}/users/user/sessions/${id}`)
    .then(() => {
      const session = document.getElementById(`id-${id}`);
      const wasActive = session.classList.contains("active");
      if (wasActive) {
        const firstSession = document.querySelector(".session-item");
        if (firstSession) {
          firstSession.classList.add("active");
          activeSessionId = firstSession.getAttribute("id");
        } else {
          activeSessionId = "";
        }
      }
      // remove DOM element
      session.parentNode.removeChild(session);
      // remove stored session from localStorage as well
      try {
        const key = storedKey(id);
        localStorage.removeItem(key);
      } catch (e) {
        console.warn('Failed to remove stored session:', e);
      }
    })
    .catch((error) => console.error(error));
}

// Export a single stored session to a downloadable JSON file
function exportStoredSession(sessionId) {
  try {
    const stored = loadStoredSession(sessionId);
    if (!stored) {
      alert('No stored data for this session.');
      return;
    }
    const blob = new Blob([JSON.stringify(stored, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `festive_session_${sessionId}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (e) {
    console.error('Export failed:', e);
    alert('Failed to export session. See console for details.');
  }
}

// Export all stored sessions as a single JSON file (map of id->object)
function exportAllStoredSessions() {
  try {
    const all = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('festive_session_')) {
        try { all[key] = JSON.parse(localStorage.getItem(key)); } catch { all[key] = localStorage.getItem(key); }
      }
    }
    if (!Object.keys(all).length) {
      alert('No stored sessions found in localStorage.');
      return;
    }
    const blob = new Blob([JSON.stringify(all, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `festive_sessions_export_${new Date().toISOString()}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (e) {
    console.error('Export all failed:', e);
    alert('Failed to export sessions. See console for details.');
  }
}

// Clear all local stored sessions after confirmation
async function clearAllStoredSessions() {
  const ok = confirm('This will remove all locally stored chat sessions. This cannot be undone. Continue?');
  if (!ok) return;
  try {
    const toRemove = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('festive_session_')) toRemove.push(key);
    }
    toRemove.forEach(k => localStorage.removeItem(k));
    // Clear session list UI items as well
    const list = sessionsListWrapper;
    if (list) list.innerHTML = '';
    activeSessionId = '';
    alert('Local sessions cleared.');
  } catch (e) {
    console.error('Failed to clear stored sessions:', e);
    alert('Failed to clear stored sessions. See console for details.');
  }
}

function updateActiveSession(id) {
  ApiService.get(`/apps/${AgentName}/users/user/sessions/${id}`)
    .then((sessionResponse) => {
      const existingSessions =
        sessionsListWrapper.querySelectorAll(".session-item");
      if (existingSessions.length) {
        for (let j = 0; j < existingSessions.length; j++) {
          existingSessions[j].classList.remove("active");
        }
      }
      const listEl = document.getElementById(`id-${id}`);
      activeSessionId = id;
      listEl.classList.add("active");
      messagesEl.innerHTML = "";
      // Render historical events from server + stored conversation
      renderEvents(sessionResponse.events || []);
      const stored = loadStoredSession(id);
      if (stored && stored.messages && stored.messages.length) {
        // Append stored conversation after server events
        for (const m of stored.messages) {
          appendMessage(m.content, m.who);
        }
      }
    })
    .catch((error) => console.error(error));
}

function renderEvents(events) {
  for (let i = 0; i < events.length; i++) {
    if (events[i].content) {
      appendMessage(events[i].content, events[i].content.role);
    }
  }
}

// Helpers
function appendMessage(content, who = "model") {
  const el = document.createElement("div");
  if (content.parts) {
    for (let i = 0; i < content.parts.length; i++) {
      const part = content.parts[i];
      if (part.functionResponse) {
        el.className = `message model function`;
        el.innerHTML = `<i class="fa fa-check"></i> ${part.functionResponse.name}`;
      } else {
        el.className = `message ${who}`;
        if (part.text) {
          el.innerHTML = marked.parse(part.text);
        }
        if (part.functionCall) {
          el.classList.add("function");
          el.innerHTML = `<i class="fa fa-bolt"></i> ${part.functionCall.name}`;
        }
        if (part.inlineData) {
          const mediaEl = createMediaElement(part.inlineData);
          if (mediaEl) {
            el.appendChild(mediaEl);
          }
        }
      }
    }
  }
  messagesEl.appendChild(el);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  // Persist message to local storage if a session is active
  try {
    if (activeSessionId) {
      const stored = loadStoredSession(activeSessionId) || { id: activeSessionId, createdAt: new Date().toISOString(), messages: [] };
      stored.messages.push({ who, content });
      saveStoredSession(activeSessionId, stored);
    }
  } catch (e) {
    console.warn('Failed to persist message:', e);
  }
  return el;
}

// -- Local storage helpers for session persistence --
function storedKey(sessionId) {
  return `festive_session_${sessionId}`;
}

function ensureStoredSession(sessionId, createIfMissing = false) {
  const key = storedKey(sessionId);
  const v = localStorage.getItem(key);
  if (!v && createIfMissing) {
    const obj = { id: sessionId, createdAt: new Date().toISOString(), messages: [] };
    localStorage.setItem(key, JSON.stringify(obj));
    return obj;
  }
  try {
    return v ? JSON.parse(v) : null;
  } catch {
    return null;
  }
}

function loadStoredSession(sessionId) {
  const key = storedKey(sessionId);
  try {
    return JSON.parse(localStorage.getItem(key));
  } catch {
    return null;
  }
}

function saveStoredSession(sessionId, obj) {
  const key = storedKey(sessionId);
  localStorage.setItem(key, JSON.stringify(obj));
}

function createMediaElement({ data, mimeType, displayName }) {
  const wrapper = document.createElement("div");
  wrapper.className = "message-media";
  const encrpytedData = data.replace(/_/g, "/").replace(/-/g, "+");
  if (mimeType.startsWith("image/")) {
    const img = document.createElement("img");
    img.src = `data:${mimeType};base64,${encrpytedData}`;
    img.alt = displayName;
    img.loading = "lazy";
    wrapper.appendChild(img);
  } else {
    // For non-image files, show a download link
    const link = document.createElement("a");
    link.href = `data:${mimeType};base64,${encrpytedData}`;
    link.download = displayName;
    link.innerHTML = `<i class="fa fa-download"></i> ${displayName}`;
    wrapper.appendChild(link);
  }

  return wrapper;
}

function setSending(isSending) {
  sendBtn.disabled = isSending;
  input.disabled = isSending;
}

// File handling
let currentFile = null;
// `filePreview` is created inside initChat after DOM loads

async function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      // Extract the base64 data from the DataURL
      const base64Data = reader.result.split(",")[1];
      resolve({
        data: base64Data,
        displayName: file.name,
        mimeType: file.type,
      });
    };
    reader.onerror = (error) => reject(error);
  });
}

function showFilePreview(file) {
  filePreview.innerHTML = "";
  if (!file) return;

  const wrapper = document.createElement("div");
  wrapper.className = "preview-wrapper";

  if (file.type.startsWith("image/")) {
    const img = document.createElement("img");
    img.className = "message-media preview";
    const reader = new FileReader();
    reader.onload = (e) => (img.src = e.target.result);
    reader.readAsDataURL(file);
    wrapper.appendChild(img);
  } else {
    const fileInfo = document.createElement("div");
    fileInfo.className = "file-info";
    fileInfo.innerHTML = `<i class="fa fa-file"></i> ${file.name}`;
    wrapper.appendChild(fileInfo);
  }

  const removeBtn = document.createElement("button");
  removeBtn.className = "remove-preview";
  removeBtn.innerHTML = '<i class="fa fa-times"></i>';
  removeBtn.onclick = clearFilePreview;
  wrapper.appendChild(removeBtn);

  filePreview.appendChild(wrapper);
}

function clearFilePreview() {
  filePreview.innerHTML = "";
  currentFile = null;
  fileInput.value = "";
}

async function sendMessage(text, attachedFile = null) {
  if (!text && !attachedFile) return;

  // Show user's message
  setSending(true);
  const parts = [];

  if (text) {
    parts.push({ text });
  }

  if (attachedFile) {
    const base64Data = await fileToBase64(attachedFile);
    parts.push({ inlineData: base64Data });
  }

  appendMessage({ parts }, "user");
  clearFilePreview();

  const payload = {
    appName: AgentName,
    newMessage: { role: "user", parts },
    sessionId: activeSessionId,
    stateDelta: null,
    streaming: false,
    userId: "user",
  };

  try {
    await ApiService.postWithStream("/run_sse", payload, async (chunk) => {
      if (chunk && typeof chunk === "object") {
        appendMessage(chunk.content, "model");
        messagesEl.scrollTop = messagesEl.scrollHeight;
      }
    });
  } catch (err) {
    console.error("Chat error:", err);
  } finally {
    setSending(false);
  }
}

// File input handler
// Event listeners for file input and form are attached in `initChat`.
