const API = "/api";

const STATUS_FLOW = {
  todo: ["in_progress", "cancelled"],
  in_progress: ["done", "todo", "cancelled"],
  done: [],
  cancelled: ["todo"],
};

const STATUS_LABELS = {
  todo: "К выполнению",
  in_progress: "В работе",
  done: "Готово",
  cancelled: "Отменено",
};

const STATUS_ICONS = {
  in_progress: "▶",
  done: "✓",
  todo: "↩",
  cancelled: "✕",
};

const VIEW_META = {
  board: { title: "Доска задач", desc: "Kanban-управление задачами" },
  notifications: { title: "Уведомления", desc: "Лента in-app уведомлений" },
};

let usersMap = {};
let allTasks = [];

// ── API ──────────────────────────────────────────────

async function fetchJSON(url, options = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(typeof err.detail === "string" ? err.detail : res.statusText);
  }
  return res.json();
}

// ── Utils ────────────────────────────────────────────

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString("ru-RU", { day: "numeric", month: "short" });
}

function initials(name) {
  return name.split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase();
}

function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

function openModal() {
  document.getElementById("modal-overlay").classList.remove("hidden");
  document.getElementById("title").focus();
}

function closeModal() {
  document.getElementById("modal-overlay").classList.add("hidden");
  document.getElementById("create-form").reset();
}

// ── Navigation ───────────────────────────────────────

function switchView(view) {
  document.querySelectorAll(".nav-btn").forEach(b =>
    b.classList.toggle("active", b.dataset.view === view)
  );
  document.querySelectorAll(".view").forEach(v =>
    v.classList.toggle("active", v.id === `view-${view}`)
  );
  const meta = VIEW_META[view];
  document.getElementById("page-title").textContent = meta.title;
  document.getElementById("page-desc").textContent = meta.desc;

  if (view === "notifications") loadNotifications();
}

document.querySelectorAll(".nav-btn").forEach(btn => {
  btn.addEventListener("click", () => switchView(btn.dataset.view));
});

// ── Sidebar ──────────────────────────────────────────

async function loadUsers() {
  const users = await fetchJSON(`${API}/users`);
  usersMap = Object.fromEntries(users.map(u => [u.id, u]));

  document.getElementById("user-list").innerHTML = users.map(u => `
    <li>
      <span class="avatar">${initials(u.name)}</span>
      <span>${escapeHtml(u.name)}</span>
      <span class="role-tag">${u.role}</span>
    </li>
  `).join("");

  const assigneeOpts = '<option value="">— Без исполнителя —</option>' +
    users.map(u => `<option value="${u.id}">${escapeHtml(u.name)}</option>`).join("");

  document.getElementById("assignee").innerHTML = assigneeOpts;
  document.getElementById("filter-assignee").innerHTML =
    '<option value="">Все исполнители</option>' +
    users.map(u => `<option value="${u.id}">${escapeHtml(u.name)}</option>`).join("");

  document.getElementById("notif-user").innerHTML =
    users.map(u => `<option value="${u.email}">${escapeHtml(u.name)}</option>`).join("");
}

async function loadProjects() {
  const projects = await fetchJSON(`${API}/projects`);
  document.getElementById("project-list").innerHTML = projects.map(p => `
    <li>
      <span>📁 ${escapeHtml(p.name)}</span>
      <span class="role-tag">${p.task_count}</span>
    </li>
  `).join("");

  document.getElementById("project").innerHTML =
    '<option value="">— Без проекта —</option>' +
    projects.map(p => `<option value="${p.id}">${escapeHtml(p.name)}</option>`).join("");
}

// ── Stats ────────────────────────────────────────────

function renderStats(tasks) {
  const total = tasks.length;
  const done = tasks.filter(t => t.status === "done").length;
  const overdue = tasks.filter(t => t.is_overdue).length;
  document.getElementById("stats").innerHTML = `
    <span class="stat-chip"><strong>${total}</strong> всего</span>
    <span class="stat-chip"><strong>${done}</strong> готово</span>
    <span class="stat-chip"><strong>${overdue}</strong> просрочено</span>
  `;
}

// ── Kanban Board ─────────────────────────────────────

function getFilteredTasks() {
  const priority = document.getElementById("filter-priority").value;
  const assignee = document.getElementById("filter-assignee").value;
  const search = document.getElementById("filter-search").value.toLowerCase();

  return allTasks.filter(t => {
    if (priority && t.priority !== priority) return false;
    if (assignee && t.assignee_id !== assignee) return false;
    if (search && !t.title.toLowerCase().includes(search)) return false;
    return true;
  });
}

function renderTaskCard(task) {
  const user = task.assignee_id ? usersMap[task.assignee_id] : null;
  const nextStatuses = STATUS_FLOW[task.status] || [];

  const actionBtns = nextStatuses.map(s => `
    <button class="status-btn" title="${STATUS_LABELS[s]}"
      data-task-id="${task.id}" data-status="${s}">${STATUS_ICONS[s]}</button>
  `).join("");

  return `
    <article class="task-card ${task.is_overdue ? "overdue" : ""}" data-id="${task.id}">
      <h3>${escapeHtml(task.title)}</h3>
      ${task.description ? `<p class="desc">${escapeHtml(task.description)}</p>` : ""}
      <div class="task-meta">
        <span class="badge ${task.priority}">${task.urgency_label}</span>
        ${task.is_overdue ? '<span class="badge overdue">Просрочено</span>' : ""}
        <span class="badge deadline">${formatDate(task.deadline)}</span>
      </div>
      <div class="task-footer">
        ${user
          ? `<span class="assignee-chip"><span class="avatar">${initials(user.name)}</span>${escapeHtml(user.name)}</span>`
          : `<span class="assignee-chip" style="opacity:0.5">Не назначен</span>`}
        <div class="status-actions">${actionBtns}</div>
      </div>
    </article>
  `;
}

async function loadTasks() {
  allTasks = await fetchJSON(`${API}/tasks`);
  renderBoard();
}

function renderBoard() {
  const tasks = getFilteredTasks();
  renderStats(allTasks);

  const columns = ["todo", "in_progress", "done", "cancelled"];
  columns.forEach(status => {
    const colTasks = tasks.filter(t => t.status === status);
    const body = document.getElementById(`col-${status}`);
    document.getElementById(`count-${status}`).textContent = colTasks.length;

    body.innerHTML = colTasks.length
      ? colTasks.map(renderTaskCard).join("")
      : '<p class="col-empty">Нет задач</p>';

    body.querySelectorAll(".status-btn").forEach(btn => {
      btn.addEventListener("click", () => updateStatus(btn.dataset.taskId, btn.dataset.status));
    });
  });
}

async function updateStatus(taskId, status) {
  try {
    await fetchJSON(`${API}/tasks/${taskId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
    showToast(`Статус → ${STATUS_LABELS[status]}`);
    await loadTasks();
    updateNotifBadge();
  } catch (err) {
    showToast(err.message, "error");
    loadTasks();
  }
}

// ── Create Task ──────────────────────────────────────

document.getElementById("create-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = {
    title: document.getElementById("title").value.trim(),
    description: document.getElementById("description").value.trim(),
    priority: document.getElementById("priority").value,
    assignee_id: document.getElementById("assignee").value || null,
    project_id: document.getElementById("project").value || null,
  };
  try {
    await fetchJSON(`${API}/tasks`, { method: "POST", body: JSON.stringify(body) });
    closeModal();
    showToast("Задача создана");
    await loadTasks();
    loadProjects();
    updateNotifBadge();
  } catch (err) {
    showToast(err.message, "error");
  }
});

document.getElementById("btn-new-task").addEventListener("click", openModal);
document.getElementById("modal-close").addEventListener("click", closeModal);
document.getElementById("modal-cancel").addEventListener("click", closeModal);
document.getElementById("modal-overlay").addEventListener("click", (e) => {
  if (e.target === e.currentTarget) closeModal();
});

// ── Filters ──────────────────────────────────────────

["filter-priority", "filter-assignee"].forEach(id => {
  document.getElementById(id).addEventListener("change", renderBoard);
});
document.getElementById("filter-search").addEventListener("input", renderBoard);

// ── Notifications ────────────────────────────────────

async function loadNotifications() {
  const email = document.getElementById("notif-user").value;
  const notifs = await fetchJSON(`${API}/notifications/${encodeURIComponent(email)}`);
  const list = document.getElementById("notif-list");

  if (!notifs.length) {
    list.innerHTML = '<p class="notif-empty">Нет уведомлений. Создайте задачу с исполнителем.</p>';
    return;
  }

  list.innerHTML = notifs.map(n => `
    <article class="notif-item">
      <div class="notif-icon">✉</div>
      <div class="notif-body">
        <h4>${escapeHtml(n.subject)}</h4>
        <p>${escapeHtml(n.body)}</p>
        <div class="notif-time">${formatDate(n.created_at)}</div>
      </div>
    </article>
  `).join("");
}

async function updateNotifBadge() {
  const email = document.getElementById("notif-user")?.value;
  if (!email) return;
  const notifs = await fetchJSON(`${API}/notifications/${encodeURIComponent(email)}`);
  const badge = document.getElementById("notif-badge");
  if (notifs.length) {
    badge.textContent = notifs.length;
    badge.classList.remove("hidden");
  } else {
    badge.classList.add("hidden");
  }
}

document.getElementById("notif-user").addEventListener("change", loadNotifications);
document.getElementById("btn-refresh-notif").addEventListener("click", loadNotifications);

// ── Init ─────────────────────────────────────────────

async function init() {
  await loadUsers();
  await loadProjects();
  await loadTasks();
  updateNotifBadge();
}

init();
