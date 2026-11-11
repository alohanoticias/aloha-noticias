/* Painel > Mensagens: lista o que chegou pelo formulário de contato (GET /admin/api/contatos, atrás do login) */
(function () {
  var box = document.getElementById("msg-lista");
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  fetch("/admin/api/contatos", { credentials: "same-origin" })
    .then(function (r) { if (!r.ok) throw r.status; return r.json(); })
    .then(function (d) {
      var l = d.mensagens || [];
      if (!l.length) { box.innerHTML = "<p>Nenhuma mensagem ainda.</p>"; return; }
      box.innerHTML = l.map(function (m) {
        var quando = new Date(m.ts).toLocaleString("pt-BR", { timeZone: "America/Sao_Paulo" });
        var resp = "mailto:" + encodeURIComponent(m.email) + "?subject=" + encodeURIComponent("Re: " + m.motivo + " (ALOHA NOTÍCIAS)");
        return '<article class="msg"><header><b>' + esc(m.nome) + '</b> · <a href="' + esc(resp) + '">' + esc(m.email) + '</a>' +
          '<span class="msg-meta">' + esc(m.motivo) + " · " + esc(m.idioma) + " · " + esc(quando) + "</span></header>" +
          '<p style="white-space:pre-wrap">' + esc(m.mensagem) + "</p></article>";
      }).join("");
    })
    .catch(function () { box.innerHTML = "<p>Não foi possível carregar. As mensagens só aparecem no endereço alohanoticias.com/admin, com login.</p>"; });
})();
