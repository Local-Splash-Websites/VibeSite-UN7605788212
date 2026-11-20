(function () {
  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".nav-toggle");
  var panel = document.querySelector(".nav-panel");
  var fineHover = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  function onScroll() {
    if (!header) return;
    header.classList.toggle("is-stuck", window.scrollY > 8);
  }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  function setMenu(open) {
    if (!header || !toggle) return;
    header.classList.toggle("is-menu-open", open);
    document.body.classList.toggle("nav-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.textContent = open ? "Close" : "Menu";
    if (open) {
      var bottom = header.getBoundingClientRect().bottom;
      document.documentElement.style.setProperty("--nav-top", Math.max(bottom, 0) + "px");
    }
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      setMenu(toggle.getAttribute("aria-expanded") !== "true");
    });
  }

  function closeDrop(drop) {
    drop.classList.remove("is-open");
    var btn = drop.querySelector(".nav-drop-btn");
    if (btn) btn.setAttribute("aria-expanded", "false");
  }

  function openDrop(drop) {
    document.querySelectorAll(".nav-drop").forEach(function (other) {
      if (other !== drop) closeDrop(other);
    });
    drop.classList.add("is-open");
    var btn = drop.querySelector(".nav-drop-btn");
    if (btn) btn.setAttribute("aria-expanded", "true");
  }

  document.querySelectorAll(".nav-drop").forEach(function (drop) {
    var btn = drop.querySelector(".nav-drop-btn");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var open = btn.getAttribute("aria-expanded") === "true";
      var desktop = window.matchMedia("(min-width: 960px)").matches;
      if (fineHover && desktop) {
        if (!open) openDrop(drop);
        return;
      }
      if (open) closeDrop(drop);
      else openDrop(drop);
    });
    if (fineHover) {
      drop.addEventListener("pointerenter", function () {
        if (window.matchMedia("(min-width: 960px)").matches) openDrop(drop);
      });
      drop.addEventListener("pointerleave", function () {
        if (window.matchMedia("(min-width: 960px)").matches) closeDrop(drop);
      });
    }
    drop.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        closeDrop(drop);
        btn.focus();
      }
    });
  });

  document.addEventListener("click", function (event) {
    if (!event.target.closest(".nav-drop")) {
      document.querySelectorAll(".nav-drop").forEach(closeDrop);
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape") return;
    document.querySelectorAll(".nav-drop").forEach(closeDrop);
    if (header && header.classList.contains("is-menu-open")) {
      setMenu(false);
      if (toggle) toggle.focus();
    }
  });

  if (panel) {
    panel.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        if (window.matchMedia("(max-width: 959px)").matches) setMenu(false);
      });
    });
  }

  document.querySelectorAll('details[name="faq"]').forEach(function (item) {
    item.addEventListener("toggle", function () {
      if (!item.open) return;
      var group = item.getAttribute("name");
      document.querySelectorAll('details[name="' + group + '"]').forEach(function (other) {
        if (other !== item) other.open = false;
      });
    });
  });

  document.querySelectorAll("form[data-lead]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      var trap = form.querySelector("[name='company_website']");
      if (trap && trap.value) event.preventDefault();
    });
  });

  function blurPhoneLink(el) {
    if (!el || !el.matches) return;
    if (el.matches("a[href^='tel:']")) el.blur();
  }

  document.addEventListener("click", function (event) {
    var el = event.target.closest("a[href^='tel:']");
    if (!el) return;
    window.setTimeout(function () {
      if (document.activeElement === el) el.blur();
    }, 0);
  });

  window.addEventListener("pagehide", function () {
    blurPhoneLink(document.activeElement);
  });
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible") blurPhoneLink(document.activeElement);
  });
})();
