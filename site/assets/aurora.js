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
      description: "두 official archive의 byte/MD5는 고정했고 CSV/model payload는 아직 읽지 않았습니다.",
      connector: "identity pinned",
      title: "Official source identity",
      copy: "AneuX v1.0 tabular and model archive sizes and MD5 are frozen",
      heights: ["35%", "52%", "73%", "48%", "88%", "64%"]
    },
    point: {
      description: "750 lesion의 patient, cut, morphometry mapping과 model listing 구조를 P0에서만 검사합니다.",
      connector: "audit pending",
      title: "Same-lesion orbit contract",
      copy: "Patient groups, three resolutions, four cuts and 170 features must agree",
      heights: ["42%", "57%", "69%", "51%", "76%", "61%"]
    },
    mask: {
      description: "All checks pass면 별도 method-free P1만, fail/incomplete면 이 candidate version을 닫습니다.",
      connector: "all or close",
      title: "No model authorization",
      copy: "No architecture, GPU, outer test or rupture-status performance claim",
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
