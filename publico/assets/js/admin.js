(function () {
  var f = document.querySelector(".faixa-rascunho[data-slug]");
  if (!f) return;
  var campo = document.getElementById("quando"), botao = document.getElementById("agendar");
  if (!campo || !botao) return;
  var slug = f.getAttribute("data-slug"), repo = f.getAttribute("data-repo"), acao = f.getAttribute("data-acao") || "Aprovar";
  function atualizar() {
    var q = campo.value;
    var titulo = acao + ": " + slug + (q ? " | " + q : "");
    botao.href = "https://github.com/" + repo + "/issues/new?title=" + encodeURIComponent(titulo) +
      "&body=" + encodeURIComponent("Clique em Submit new issue para confirmar.");
    botao.setAttribute("aria-disabled", q ? "false" : "true");
    botao.style.opacity = q ? "1" : "0.5";
  }
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function fmt(d) { return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) + "T" + pad(d.getHours()) + ":" + pad(d.getMinutes()); }
  // Atalho de horário: escolhe a próxima ocorrência (hoje se ainda faltar mais de 15 min, senão amanhã); clicar de novo avança um dia.
  Array.prototype.forEach.call(f.querySelectorAll(".chip[data-hora]"), function (c) {
    c.addEventListener("click", function () {
      var hm = c.getAttribute("data-hora").split(":"), agora = new Date(), d = new Date();
      d.setHours(+hm[0], +hm[1], 0, 0);
      if (d.getTime() - agora.getTime() < 15 * 60000) d.setDate(d.getDate() + 1);
      if (campo.value && campo.value.slice(11) === fmt(d).slice(11) && campo.value >= fmt(d)) {
        var a = new Date(campo.value); a.setDate(a.getDate() + 1); d = a;
      }
      campo.value = fmt(d); atualizar();
    });
  });
  botao.addEventListener("click", function (e) { if (!campo.value) { e.preventDefault(); campo.focus(); } });
  campo.addEventListener("input", atualizar);
  atualizar();
})();
