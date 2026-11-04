(function () {
  var f = document.querySelector(".faixa-rascunho[data-slug]");
  if (!f) return;
  var campo = document.getElementById("quando"), botao = document.getElementById("agendar");
  if (!campo || !botao) return;
  var slug = f.getAttribute("data-slug"), repo = f.getAttribute("data-repo");
  function atualizar() {
    var q = campo.value;
    var titulo = "Aprovar: " + slug + (q ? " | " + q : "");
    botao.href = "https://github.com/" + repo + "/issues/new?title=" + encodeURIComponent(titulo) +
      "&body=" + encodeURIComponent("Clique em Submit new issue para confirmar.");
    botao.setAttribute("aria-disabled", q ? "false" : "true");
    botao.style.opacity = q ? "1" : "0.5";
  }
  botao.addEventListener("click", function (e) { if (!campo.value) { e.preventDefault(); campo.focus(); } });
  campo.addEventListener("input", atualizar);
  atualizar();
})();
