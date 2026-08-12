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

  const venueStatus = document.querySelector("#venue-status");
  const venueRequirement = document.querySelector("#venue-requirement");
  const venueContractGrid = document.querySelector("#venue-contract-grid");
  venueStatus.textContent = data.venue.status;
  venueRequirement.textContent = data.venue.requirement;
  venueContractGrid.innerHTML = data.venue.rules
    .map(
      (rule, index) => `
        <article class="venue-rule">
          <span>${String(index + 1).padStart(2, "0")} · ${escapeHtml(rule.label)}</span>
          <h3>${escapeHtml(rule.title)}</h3>
          <p>${escapeHtml(rule.copy)}</p>
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
      description: "Anchor-relative gain should follow the reference CFD sweep.",
      connector: "gain",
      title: "Preserve response magnitude",
      copy: "Compare the norm of each target-minus-anchor field, not only the absolute target field",
      heights: ["35%", "52%", "73%", "48%", "88%", "64%"]
    },
    point: {
      description: "The predicted change must point in the same high-dimensional direction as the reference response.",
      connector: "direction",
      title: "Preserve response direction",
      copy: "Measure cosine error on target-minus-anchor response fields so anchor bias cannot masquerade as fidelity",
      heights: ["42%", "57%", "69%", "51%", "76%", "61%"]
    },
    mask: {
      description: "A smooth-looking field can still bend incorrectly as mass flow changes.",
      connector: "derivative",
      title: "Preserve tangent and curvature",
      copy: "Use the registered nonuniform flow grid to evaluate first- and second-order discrete response errors",
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
