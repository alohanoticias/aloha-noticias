/* Admin > Links: botão Copiar de cada link etiquetado. */
(function () {
  document.addEventListener("click", function (e) {
    var b = e.target;
    if (!b.classList || !b.classList.contains("copiar")) return;
    var campo = b.parentNode.querySelector("input");
    if (!campo) return;
    function ok() { var t = b.textContent; b.textContent = "Copiado!"; setTimeout(function () { b.textContent = t; }, 1500); }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(campo.value).then(ok, function () { campo.select(); document.execCommand("copy"); ok(); });
    else { campo.select(); document.execCommand("copy"); ok(); }
  });
})();
