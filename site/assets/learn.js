(() => {
  "use strict";

  const tabs = [...document.querySelectorAll("[data-chapter]")];
  const panels = [...document.querySelectorAll("[data-chapter-panel]")];
  const progress = document.querySelector("#chapter-progress");
  const validChapters = new Set(panels.map((panel) => panel.id));

  const activate = (chapter, { updateHistory = true, focus = true } = {}) => {
    const resolved = validChapters.has(chapter) ? chapter : "foundation";
    const activeIndex = panels.findIndex((panel) => panel.id === resolved);

    tabs.forEach((tab) => {
      const active = tab.dataset.chapter === resolved;
      tab.classList.toggle("active", active);
      tab.setAttribute("aria-selected", String(active));
      tab.tabIndex = active ? 0 : -1;
    });
    panels.forEach((panel) => {
      const active = panel.id === resolved;
      panel.hidden = !active;
      panel.classList.toggle("active", active);
    });
    progress.textContent = `${String(activeIndex + 1).padStart(2, "0")} / ${String(
      panels.length
    ).padStart(2, "0")}`;

    if (updateHistory) history.pushState(null, "", `#${resolved}`);
    if (focus) {
      panels[activeIndex].focus({ preventScroll: true });
      window.scrollTo({
        top: document.querySelector(".learn-shell").offsetTop - 62,
        behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
          ? "auto"
          : "smooth"
      });
    }
  };

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => activate(tab.dataset.chapter));
    tab.addEventListener("keydown", (event) => {
      if (!["ArrowDown", "ArrowRight", "ArrowUp", "ArrowLeft"].includes(event.key)) return;
      event.preventDefault();
      const direction = ["ArrowDown", "ArrowRight"].includes(event.key) ? 1 : -1;
      const nextIndex = (index + direction + tabs.length) % tabs.length;
      tabs[nextIndex].focus();
      activate(tabs[nextIndex].dataset.chapter);
    });
  });

  document.querySelectorAll("[data-next]").forEach((button) => {
    button.addEventListener("click", () => activate(button.dataset.next));
  });

  document.querySelectorAll("[data-chapter-link]").forEach((link) => {
    link.addEventListener("click", (event) => {
      const chapter = link.getAttribute("href").replace(/^#/, "");
      if (!validChapters.has(chapter)) return;
      event.preventDefault();
      activate(chapter);
    });
  });

  window.addEventListener("hashchange", () => {
    const chapter = window.location.hash.replace(/^#/, "");
    if (validChapters.has(chapter)) activate(chapter, { updateHistory: false });
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

  const initial = window.location.hash.replace(/^#/, "");
  activate(initial, { updateHistory: false, focus: false });
})();
