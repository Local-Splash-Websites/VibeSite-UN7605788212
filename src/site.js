(function () {
  var toggle = document.querySelector(".nav-check");
  var menu = document.querySelector(".nav-links");
  if (toggle && menu) {
    menu.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        if (window.matchMedia("(max-width: 959px)").matches) {
          toggle.checked = false;
        }
      });
    });
  }

  document.querySelectorAll("form[data-lead]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      var trap = form.querySelector("[name='company_website']");
      if (trap && trap.value) {
        event.preventDefault();
      }
    });
  });
})();
