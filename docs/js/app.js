(() => {
  "use strict";

  const screens = [...document.querySelectorAll("[data-screen]")];
  const nav = document.querySelector("#bottom-nav");
  const toast = document.querySelector("#toast");
  const allowedScreens = new Set(screens.map((screen) => screen.dataset.screen));
  let toastTimer;

  const details = {
    "1": {
      status: "En revisión",
      tag: "tag-info",
      folio: "DEMO-001",
      title: "Revisión de condición en EQ-001",
      description: "Condición genérica detectada durante una inspección visual.",
      classification: "Disciplina Alfa · Observación",
      location: "Zona 1 · EQ-001",
      date: "24 ago 2026 · 10:18"
    },
    "2": {
      status: "Pendiente",
      tag: "tag-warning",
      folio: "DEMO-002",
      title: "Observación durante recorrido",
      description: "Registro ficticio pendiente de revisión por el siguiente turno.",
      classification: "Disciplina Beta · Incidencia",
      location: "Zona 2 · EQ-002",
      date: "23 ago 2026 · 14:05"
    },
    "3": {
      status: "Cerrada",
      tag: "tag-success",
      folio: "DEMO-003",
      title: "Verificación completada",
      description: "La condición genérica fue revisada y cerrada para la demostración.",
      classification: "Disciplina Alfa · Observación",
      location: "Zona 1 · EQ-001",
      date: "22 ago 2026 · 09:40"
    }
  };

  function showToast(message) {
    window.clearTimeout(toastTimer);
    toast.textContent = message;
    toast.classList.add("is-visible");
    toastTimer = window.setTimeout(() => toast.classList.remove("is-visible"), 3200);
  }

  function showScreen(name, updateHash = true) {
    if (!allowedScreens.has(name)) name = "login";
    screens.forEach((screen) => screen.classList.toggle("is-active", screen.dataset.screen === name));
    nav.hidden = name === "login";
    document.querySelectorAll("[data-nav]").forEach((item) => {
      const active = item.dataset.nav === name || (name === "completar" && item.dataset.nav === "borradores");
      item.classList.toggle("is-active", active);
      if (active) item.setAttribute("aria-current", "page");
      else item.removeAttribute("aria-current");
    });
    if (updateHash) history.replaceState(null, "", `#${name}`);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  document.addEventListener("click", (event) => {
    const trigger = event.target.closest("[data-go]");
    if (trigger) showScreen(trigger.dataset.go);
  });

  document.querySelector("#login-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const user = document.querySelector("#login-user").value.trim();
    const password = document.querySelector("#login-password").value;
    const error = document.querySelector("#login-error");
    error.hidden = Boolean(user && password);
    if (!error.hidden) return;
    event.currentTarget.reset();
    showScreen("jornada");
    showToast("Ingreso de demostración correcto. No se enviaron credenciales.");
  });

  const description = document.querySelector("#capture-description");
  description.addEventListener("input", () => {
    document.querySelector("#description-count").textContent = `${description.value.length}/500`;
  });

  ["#camera-input", "#gallery-input"].forEach((selector) => {
    document.querySelector(selector).addEventListener("change", (event) => {
      const file = event.target.files[0];
      document.querySelector("#selected-photo").textContent = file ? `Seleccionada: ${file.name}` : "Ninguna fotografía seleccionada.";
    });
  });

  const connectivity = document.querySelector("#connectivity-select");
  connectivity.addEventListener("change", () => {
    const label = document.querySelector("#connectivity-label");
    const offline = connectivity.value === "offline";
    label.classList.toggle("is-offline", offline);
    label.innerHTML = `<span></span> ${offline ? "Sin cobertura" : "Con conexión"}`;
  });

  function validCapture() {
    const hasDescription = description.value.trim().length > 0;
    const hasPhoto = document.querySelector("#camera-input").files.length > 0 || document.querySelector("#gallery-input").files.length > 0;
    document.querySelector("#capture-error").hidden = hasDescription || hasPhoto;
    return hasDescription || hasPhoto;
  }

  document.querySelector("#capture-form").addEventListener("submit", (event) => {
    event.preventDefault();
    if (!validCapture()) return;
    const offline = connectivity.value === "offline";
    document.querySelector("#capture-count").textContent = "5";
    document.querySelector("#draft-count").textContent = "3";
    document.querySelector("#pending-count").textContent = offline ? "3" : "2";
    showToast(offline ? "Captura simulada: guardada localmente y pendiente de sincronización." : "Captura simulada: guardada como borrador.");
    showScreen("borradores");
  });

  document.querySelector("#continue-capture").addEventListener("click", () => {
    if (!validCapture()) return;
    const text = description.value.trim();
    if (text) document.querySelector("#complete-description").value = text;
    showScreen("completar");
  });

  document.querySelector("#draft-filter").addEventListener("input", (event) => {
    const query = event.target.value.toLocaleLowerCase("es").trim();
    const cards = [...document.querySelectorAll("#draft-list .record-card")];
    cards.forEach((card) => { card.hidden = !card.dataset.search.includes(query); });
    document.querySelector("#draft-empty").hidden = cards.some((card) => !card.hidden);
  });

  document.querySelector("#complete-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const required = [
      ["complete-title-field", "Título"], ["complete-description", "Descripción"],
      ["discipline", "Disciplina"], ["type", "Tipo"], ["shift", "Turno"], ["priority", "Prioridad"]
    ];
    const missing = required.filter(([id]) => !document.getElementById(id).value.trim()).map(([, label]) => label);
    const box = document.querySelector("#complete-errors");
    if (missing.length) {
      box.hidden = false;
      box.innerHTML = `<strong>Complete los campos obligatorios:</strong><ul>${missing.map((item) => `<li>${item}</li>`).join("")}</ul>`;
      return;
    }
    box.hidden = true;
    showToast("Novedad finalizada en la simulación y agregada al histórico.");
    showScreen("historico");
  });

  document.querySelector("#preview-summary").addEventListener("click", () => {
    const activities = document.querySelector("#activities").value.trim() || "Sin actividades descritas.";
    const relevant = document.querySelector("#relevant").value.trim() || "Sin novedades destacadas.";
    const pending = document.querySelector("#pending").value.trim() || "Sin pendientes informados.";
    const selected = document.querySelectorAll(".selection-list input:checked").length;
    const preview = document.querySelector("#summary-preview");
    preview.hidden = false;
    preview.innerHTML = `<h2>Vista previa manual</h2><p><strong>Capturas seleccionadas:</strong> ${selected}</p><p><strong>Actividades:</strong> ${activities}</p><p><strong>Novedades:</strong> ${relevant}</p><p><strong>Pendientes:</strong> ${pending}</p>`;
  });

  document.querySelector("#summary-form").addEventListener("submit", (event) => {
    event.preventDefault();
    showToast("Resumen guardado en la simulación.");
    showScreen("jornada");
  });

  function renderDetail(id) {
    const detail = details[id];
    if (!detail) return;
    document.querySelector("#history-detail").innerHTML = `
      <div class="record-top"><span class="tag ${detail.tag}">${detail.status}</span><span>Folio ${detail.folio}</span></div>
      <h2>${detail.title}</h2>
      <img src="assets/images/evidencia-ficticia.svg" alt="Evidencia ficticia del registro de demostración">
      <dl><div><dt>Descripción</dt><dd>${detail.description}</dd></div><div><dt>Clasificación</dt><dd>${detail.classification}</dd></div><div><dt>Ubicación</dt><dd>${detail.location}</dd></div><div><dt>Fecha de ocurrencia</dt><dd>${detail.date}</dd></div><div><dt>Autor</dt><dd>Usuario Demo</dd></div></dl>`;
  }

  document.querySelectorAll("[data-history]").forEach((item) => {
    item.addEventListener("click", () => {
      document.querySelectorAll("[data-history]").forEach((other) => other.classList.remove("is-selected"));
      item.classList.add("is-selected");
      renderDetail(item.dataset.history);
    });
  });

  ["#history-discipline", "#history-priority", "#history-status"].forEach((selector) => {
    document.querySelector(selector).addEventListener("change", () => {
      const discipline = document.querySelector("#history-discipline").value;
      const priority = document.querySelector("#history-priority").value;
      const status = document.querySelector("#history-status").value;
      const items = [...document.querySelectorAll("[data-history]")];
      items.forEach((item) => {
        item.hidden = !((discipline === "all" || item.dataset.discipline === discipline) && (priority === "all" || item.dataset.priority === priority) && (status === "all" || item.dataset.status === status));
      });
      const visible = items.filter((item) => !item.hidden);
      document.querySelector("#history-empty").hidden = visible.length > 0;
      document.querySelector("#history-detail").hidden = visible.length === 0;
      if (visible.length) {
        items.forEach((item) => item.classList.remove("is-selected"));
        visible[0].classList.add("is-selected");
        renderDetail(visible[0].dataset.history);
      }
    });
  });

  window.addEventListener("hashchange", () => showScreen(location.hash.slice(1), false));

  if ("serviceWorker" in navigator && location.protocol.startsWith("http")) {
    window.addEventListener("load", () => navigator.serviceWorker.register("service-worker.js").catch(() => {}));
  }

  showScreen(location.hash.slice(1) || "login", false);
})();
