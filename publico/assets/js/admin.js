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
  campo.addEventListener("input", function () { atualizar(); avisar(); });

  // Aviso de agenda: no máximo 3 artigos por dia. Mostra o próximo horário livre.
  var ag = {}; try { ag = JSON.parse(f.getAttribute("data-agenda") || "{}"); } catch (e) {}
  var ocup = ag.ocupacao || {}, max = ag.max || 3, livre = ag.livre;
  var aviso = document.getElementById("aviso-agenda"), agora_ = document.getElementById("publicar-agora");
  function dm(iso) { return iso.slice(8, 10) + "/" + iso.slice(5, 7); }
  function listaDia(dia) { return (ocup[dia] || []).slice(); }
  function mensagem(dia, quando) {
    var h = listaDia(dia);
    if (h.length < max) return "";
    var txt = "Atenção: " + (quando === "hoje" ? "hoje" : "o dia " + dm(dia)) + " já tem " + h.length +
      " artigos (" + h.join(", ") + "). O limite é " + max + " por dia.";
    if (livre) txt += " Próximo horário livre: " + dm(livre) + " às " + livre.slice(11, 16) + ".";
    return txt;
  }
  function mostrar(txt, usarLivre) {
    if (!aviso) return;
    if (!txt) { aviso.hidden = true; aviso.innerHTML = ""; return; }
    aviso.hidden = false; aviso.textContent = txt;
    if (usarLivre && livre) {
      var b = document.createElement("button"); b.type = "button"; b.className = "chip"; b.textContent = "Usar o horário livre";
      b.addEventListener("click", function () { campo.value = livre; atualizar(); avisar(); });
      aviso.appendChild(document.createTextNode(" ")); aviso.appendChild(b);
    }
  }
  function avisar() { mostrar(campo.value ? mensagem(campo.value.slice(0, 10), "") : "", true); }
  if (agora_) {
    agora_.addEventListener("click", function (e) {
      var hoje = fmt(new Date()).slice(0, 10), txt = mensagem(hoje, "hoje");
      if (txt && !window.confirm(txt + "\n\nPublicar agora mesmo assim?")) { e.preventDefault(); mostrar(txt, true); }
    });
  }
  atualizar(); avisar();
})();
