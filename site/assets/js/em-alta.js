/* Selo "🔥 Em alta" e lista "Mais lidas" com as leituras reais dos últimos 7 dias (contador próprio, sem números na página).
   Sem resposta do servidor ou sem dados suficientes, nada muda: o selo fica escondido e a lista mantém a ordem padrão. */
(function () {
  if (!window.fetch) return;
  fetch("/api/em-alta", { credentials: "omit" })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (d) {
      if (!d) return;
      (d.alta || []).forEach(function (slug) {
        Array.prototype.forEach.call(document.querySelectorAll('[data-alta="' + slug + '"]'), function (el) { el.hidden = false; });
      });
      var lidas = d.lidas || [];
      if (lidas.length < 3) return;
      var atual = document.querySelector('meta[name="aloha-slug"]');
      atual = atual ? atual.content : "";
      Array.prototype.forEach.call(document.querySelectorAll("ol[data-ml]"), function (ol) {
        var itens = Array.prototype.slice.call(ol.children), por = {};
        itens.forEach(function (li) { por[li.getAttribute("data-slug")] = li; });
        var ordem = [];
        lidas.forEach(function (s) { if (por[s] && s !== atual) ordem.push(por[s]); });
        itens.forEach(function (li) { if (ordem.indexOf(li) < 0 && li.getAttribute("data-slug") !== atual) ordem.push(li); });
        itens.forEach(function (li) { li.hidden = true; });
        ordem.forEach(function (li, i) { ol.appendChild(li); li.hidden = i >= 5; });
      });
    })
    .catch(function () {});
})();
