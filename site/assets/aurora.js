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
      description: "172 CTA case의 study/patient key와 series geometry를 확인합니다.",
      connector: "audit units",
      title: "Are task units one-to-one?",
      copy: "Patient/study keys and three sampled headers must support one auditable case unit",
      heights: ["35%", "52%", "73%", "48%", "88%", "64%"]
    },
    point: {
      description: "STL vertex와 DICOM patient coordinate frame의 정합을 검사합니다.",
      connector: "audit frames",
      title: "Do surfaces inhabit the CTA frame?",
      copy: "CRC-verified STL geometry must align with DICOM orientation, position and physical scale",
      heights: ["42%", "57%", "69%", "51%", "76%", "61%"]
    },
    mask: {
      description: "모든 frozen check가 통과해야 method-free P1만 등록합니다.",
      connector: "apply frozen rule",
      title: "All pass to P1; any fail closes",
      copy: "No threshold, tolerance, parser or selection repair after the observed outcome",
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
