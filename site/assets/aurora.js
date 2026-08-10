(() => {
  "use strict";

  const data = window.AURORA_DATA;
  if (!data) return;

  const escapeHtml = (value) =>
    String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

  const lineageList = document.querySelector("#lineage-list");
  lineageList.innerHTML = data.lineage
    .map(
      (item) => `
        <article class="lineage-item">
          <div class="lineage-year">${escapeHtml(item.year)}</div>
          <div>
            <h3>${escapeHtml(item.title)}</h3>
            <p>${escapeHtml(item.copy)}</p>
            <div class="status">${escapeHtml(item.status)}</div>
          </div>
          <a href="${escapeHtml(item.url)}" aria-label="${escapeHtml(item.title)} 1차 출처 열기">↗</a>
        </article>`
    )
    .join("");

  const competitionBody = document.querySelector("#competition-body");
  competitionBody.innerHTML = data.competition
    .map(
      (row) =>
        `<tr>${row.map((cell) => `<td>${escapeHtml(cell)}</td>`).join("")}</tr>`
    )
    .join("");

  const gateList = document.querySelector("#gate-list");
  gateList.innerHTML = data.gates
    .map(
      (gate) => `
        <article class="gate-item">
          <span class="gate-id">${escapeHtml(gate.id)}</span>
          <h3>${escapeHtml(gate.title)}</h3>
          <p>${escapeHtml(gate.copy)}</p>
          <span class="gate-state ${gate.blocking ? "blocking" : ""}">${escapeHtml(gate.state)}</span>
        </article>`
    )
    .join("");

  const datasetList = document.querySelector("#dataset-list");
  datasetList.innerHTML = data.datasets
    .map(
      (dataset) => `
        <article class="dataset-item">
          <h4>${escapeHtml(dataset.name)}</h4>
          <p>${escapeHtml(dataset.role)}</p>
          <span>${escapeHtml(dataset.provenance)}</span>
        </article>`
    )
    .join("");

  const changeList = document.querySelector("#change-list");
  const renderChanges = (filter = "all") => {
    const changes =
      filter === "all"
        ? data.changes
        : data.changes.filter((item) => item.category === filter);
    changeList.innerHTML = changes.length
      ? changes
          .map(
            (item) => `
              <article class="change-item">
                <time class="change-date">${escapeHtml(item.date)}</time>
                <span class="change-category">${escapeHtml(item.category)}</span>
                <div class="change-copy">
                  <h3>${escapeHtml(item.title)}</h3>
                  <p>${escapeHtml(item.copy)}</p>
                  <div class="change-files">
                    ${item.files.map((file) => `<code>${escapeHtml(file)}</code>`).join("")}
                  </div>
                </div>
              </article>`
          )
          .join("")
      : `<p class="change-empty">이 category의 변경 이력이 없습니다.</p>`;
  };
  renderChanges();

  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      document
        .querySelectorAll("[data-filter]")
        .forEach((candidate) => candidate.classList.remove("active"));
      button.classList.add("active");
      renderChanges(button.dataset.filter);
    });
  });

  const modes = {
    presence: {
      description: "Official release는 417 scan/409 patient, 52 location leaf와 3 type을 명시합니다.",
      connector: "source audited",
      title: "Silver anatomy boundary",
      copy: "Vessel masks are organizer predictions: train-time privilege, never a test-time requirement",
      heights: ["35%", "52%", "73%", "48%", "88%", "64%"]
    },
    point: {
      description: "52 leaf를 territory·laterality·branch role로 분해할 수 있는지는 payload support로 검증해야 합니다.",
      connector: "labels factorized",
      title: "Observable hierarchy",
      copy: "The factor map is a testable hypothesis, not a renamed taxonomy head",
      heights: ["42%", "57%", "69%", "51%", "76%", "61%"]
    },
    mask: {
      description: "Terms를 수락해도 P0-R 전체 통과 뒤 method-free P1만 열립니다.",
      connector: "gate closed",
      title: "No model authorization",
      copy: "Terms, payload, P0, P1, architecture, GPU, outer test and claim are all zero",
      heights: ["48%", "61%", "44%", "68%", "51%", "57%"]
    }
  };

  const setMode = (modeName) => {
    const mode = modes[modeName];
    document.querySelector("#mode-description").textContent = mode.description;
    document.querySelector("#bc-connector-label").innerHTML = mode.connector;
    document.querySelector("#bc-node-title").textContent = mode.title;
    document.querySelector("#bc-node-copy").textContent = mode.copy;
    document.querySelectorAll(".scenario-row i").forEach((bar, index) => {
      bar.style.setProperty("--h", mode.heights[index]);
    });
  };

  document.querySelectorAll("[data-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      document
        .querySelectorAll("[data-mode]")
        .forEach((candidate) => candidate.classList.remove("active"));
      button.classList.add("active");
      setMode(button.dataset.mode);
    });
  });

  const topbar = document.querySelector("[data-topbar]");
  const updateTopbar = () => topbar.classList.toggle("scrolled", window.scrollY > 30);
  updateTopbar();
  window.addEventListener("scroll", updateTopbar, { passive: true });

  const menuButton = document.querySelector(".menu-button");
  const nav = document.querySelector(".nav");
  menuButton.addEventListener("click", () => {
    const open = menuButton.getAttribute("aria-expanded") === "true";
    menuButton.setAttribute("aria-expanded", String(!open));
    nav.classList.toggle("open", !open);
  });
  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      nav.classList.remove("open");
      menuButton.setAttribute("aria-expanded", "false");
    });
  });
})();
