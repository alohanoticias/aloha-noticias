/* ALOHA NOTÍCIAS — sino de notificações com histórico (matérias novas, lidas/não lidas) */
(function () {
  var N = window.ALOHA_NOVID; if (!N || !N.itens) return;
  var T = N.t || {};
  function ler(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function gravar(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function js(k, pad) { try { return JSON.parse(ler(k)) || pad; } catch (e) { return pad; } }
  var KL = "aloha-sino-lidas", KC = "aloha-sino-limpo", KV = "aloha-sino-visto";
  var lidas = js(KL, []), limpo = js(KC, []);
  function visiveis() { return N.itens.filter(function (i) { return limpo.indexOf(i.id) < 0; }); }
  function naoLidas() { return visiveis().filter(function (i) { return lidas.indexOf(i.id) < 0; }).length; }

  var btn = document.createElement("button");
  btn.type = "button"; btn.className = "sino-btn"; btn.setAttribute("aria-label", T.titulo || "Notificações");
  btn.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path fill="currentColor" d="M12 22a2.4 2.4 0 0 0 2.4-2.4h-4.8A2.4 2.4 0 0 0 12 22Zm7-6.6V11a7 7 0 0 0-5.2-6.8V3.4a1.8 1.8 0 0 0-3.6 0v.8A7 7 0 0 0 5 11v4.4l-2 2V19h18v-1.6l-2-2Z"/></svg><span class="sino-n" hidden></span>';
  var pn = document.createElement("section");
  pn.className = "sino-painel"; pn.hidden = true; pn.setAttribute("aria-label", T.titulo || "Notificações");
  pn.innerHTML = '<header><span></span><button type="button" class="sino-x" aria-label="×">×</button></header><div class="sino-lista"></div><footer><button type="button" data-a="ler"></button><button type="button" data-a="limpar"></button></footer>';
  pn.querySelector("header span").textContent = "⏱ " + (T.titulo || "Histórico de push");
  pn.querySelector('[data-a="ler"]').textContent = T.ler || "marcar tudo como lido";
  pn.querySelector('[data-a="limpar"]').textContent = T.limpar || "Limpar tudo";
  document.body.appendChild(pn); document.body.appendChild(btn);

  function esc(s) { var d = document.createElement("div"); d.textContent = s; return d.innerHTML; }
  function desenharContador() { var nl = naoLidas(), c = btn.querySelector(".sino-n"); c.hidden = !nl; c.textContent = nl > 9 ? "9+" : nl; }
  function desenhar() {
    var v = visiveis();
    desenharContador();
    var l = pn.querySelector(".sino-lista");
    if (!v.length) { l.innerHTML = '<p class="sino-vazio">' + esc(T.vazio || "O histórico de notificações está vazio") + "</p>"; return; }
    l.innerHTML = v.map(function (i) {
      return '<a class="sino-item' + (lidas.indexOf(i.id) < 0 ? " nova" : "") + '" href="' + esc(i.url) + '" data-id="' + esc(i.id) + '">' +
        (i.capa ? '<img src="' + esc(i.capa) + '" alt="" loading="lazy">' : "") +
        '<span><small>' + esc(i.editoria) + " · " + esc(i.data) + "</small><b>" + esc(i.titulo) + "</b></span></a>";
    }).join("");
  }
  btn.onclick = function () { pn.hidden = !pn.hidden; if (!pn.hidden) pedirPermissao(); };
  pn.querySelector(".sino-x").onclick = function () { pn.hidden = true; };
  pn.querySelector('[data-a="ler"]').onclick = function () { lidas = N.itens.map(function (i) { return i.id; }); gravar(KL, JSON.stringify(lidas)); desenhar(); };
  pn.querySelector('[data-a="limpar"]').onclick = function () { limpo = N.itens.map(function (i) { return i.id; }); gravar(KC, JSON.stringify(limpo)); desenhar(); };
  pn.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a.sino-item");
    if (a) { var id = a.getAttribute("data-id"); if (lidas.indexOf(id) < 0) { lidas.push(id); gravar(KL, JSON.stringify(lidas)); a.classList.remove("nova"); desenharContador(); } }
  });

  // Avisos do navegador: quem permitir recebe um aviso, ao abrir o site, das matérias publicadas desde a última visita.
  function pedirPermissao() {
    if (!("Notification" in window) || Notification.permission !== "default") return;
    try { Notification.requestPermission(); } catch (e) {}
  }
  function avisarNovas() {
    var visto = js(KV, null);
    gravar(KV, JSON.stringify(N.itens.map(function (i) { return i.id; })));
    if (!visto || !("Notification" in window) || Notification.permission !== "granted") return;
    N.itens.filter(function (i) { return visto.indexOf(i.id) < 0; }).slice(0, 3).forEach(function (i) {
      try { var n = new Notification(i.titulo, { body: i.editoria, icon: i.capa || undefined }); n.onclick = function () { window.open(i.url, "_self"); }; } catch (e) {}
    });
  }
  // Sobe o sino acima da faixa de cookies enquanto ela estiver na tela.
  function posicionar() {
    var c = document.getElementById("consent"), h = (c && !c.hidden) ? c.offsetHeight : 0;
    btn.style.bottom = (18 + h) + "px"; pn.style.bottom = (80 + h) + "px";
  }
  window.addEventListener("resize", posicionar);
  document.addEventListener("click", function () { setTimeout(posicionar, 60); });
  window.addEventListener("load", posicionar); setTimeout(posicionar, 300);
  document.addEventListener("click", function (e) { if (!pn.hidden && !pn.contains(e.target) && !btn.contains(e.target)) pn.hidden = true; });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !pn.hidden) { pn.hidden = true; btn.focus(); } });
  desenhar(); avisarNovas(); posicionar();
})();
