(function () {
  var b = document.body;
  var m = document.querySelector(".p-menu");
  if (m) m.addEventListener("click", function () { b.classList.toggle("menu-aberto"); });
  document.addEventListener("click", function (e) { if (b.classList.contains("menu-aberto") && !e.target.closest(".p-lado") && !e.target.closest(".p-menu")) b.classList.remove("menu-aberto"); });
  var tema = document.getElementById("p-tema");
  try { var t = localStorage.getItem("aloha-painel-tema"); if (t) document.documentElement.setAttribute("data-tema", t); } catch (e) {}
  if (tema) tema.addEventListener("click", function () {
    var r = document.documentElement, escuro = r.getAttribute("data-tema") === "escuro" || (!r.getAttribute("data-tema") && matchMedia("(prefers-color-scheme: dark)").matches);
    var novo = escuro ? "claro" : "escuro"; r.setAttribute("data-tema", novo);
    try { localStorage.setItem("aloha-painel-tema", novo); } catch (e) {}
  });
  var q = document.getElementById("p-busca");
  if (q) q.addEventListener("input", function () {
    var v = q.value.toLowerCase();
    Array.prototype.forEach.call(document.querySelectorAll("[data-busca]"), function (li) { li.style.display = li.getAttribute("data-busca").indexOf(v) < 0 ? "none" : ""; });
  });
})();
