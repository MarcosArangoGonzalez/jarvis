(function () {
  const editor = document.getElementById("note-editor");
  const saveState = document.getElementById("save-state");
  const eventsEl = document.getElementById("calendar-events");
  const countEl = document.getElementById("calendar-count");
  if (!editor) return;

  let dirty = false;
  let saving = false;

  editor.addEventListener("input", function () {
    dirty = true;
    saveState.textContent = "pendiente";
  });

  async function save() {
    if (!dirty || saving) return;
    saving = true;
    saveState.textContent = "guardando";
    try {
      const response = await fetch(`/api/notes/${editor.dataset.path}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: editor.value }),
      });
      if (!response.ok) throw new Error("No se pudo guardar.");
      dirty = false;
      saveState.textContent = "guardado";
    } catch (error) {
      saveState.textContent = "error";
    } finally {
      saving = false;
    }
  }

  async function loadCalendar() {
    const now = new Date();
    const response = await fetch(`/api/calendar/events?year=${now.getFullYear()}&month=${now.getMonth() + 1}`);
    const events = await response.json();
    countEl.textContent = String(events.length);
    if (!events.length) {
      eventsEl.textContent = "Sin notas fechadas este mes.";
      return;
    }
    eventsEl.innerHTML = events.map((item) => (
      `<button class="calendar-item" type="button" data-path="${escapeHtml(item.path)}"><span>${escapeHtml(item.date)}</span><strong>${escapeHtml(item.title)}</strong></button>`
    )).join("");
    eventsEl.querySelectorAll(".calendar-item").forEach((button) => {
      button.addEventListener("click", async function () {
        await save();
        const note = await fetch(`/api/notes/${button.dataset.path}`).then((res) => res.json());
        editor.dataset.path = note.path;
        editor.value = note.content;
        dirty = false;
        saveState.textContent = "guardado";
      });
    });
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  setInterval(save, 30000);
  window.addEventListener("beforeunload", save);
  loadCalendar().catch(function () {
    eventsEl.textContent = "No se pudo cargar el calendario.";
  });
})();
