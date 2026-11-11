/* Aviso de cookies: o AdSense só é carregado depois do "Aceitar". Escolha guardada no navegador. */
(function () {
  var tag = document.currentScript, cliente = tag && tag.getAttribute("data-client");
  var box = document.getElementById("consent");
  function ler() { try { return localStorage.getItem("aloha-consent"); } catch (e) { return null; } }
  function gravar(v) { try { localStorage.setItem("aloha-consent", v); } catch (e) {} }
  function carregarAds() {
    if (!cliente || document.getElementById("adsense-js")) return;
    var s = document.createElement("script");
    s.id = "adsense-js"; s.async = true; s.crossOrigin = "anonymous";
    s.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + encodeURIComponent(cliente);
    document.head.appendChild(s);
  }
  function mostrar() { if (box) box.hidden = false; }
  function esconder() { if (box) box.hidden = true; }
  var v = ler();
  if (v === "1") carregarAds(); else if (v !== "0") mostrar();
  var sim = document.getElementById("consent-sim"), nao = document.getElementById("consent-nao"), re = document.getElementById("reabrir-consent");
  if (sim) sim.onclick = function () { gravar("1"); esconder(); carregarAds(); };
  if (nao) nao.onclick = function () { gravar("0"); esconder(); };
  if (re) re.onclick = function (e) { e.preventDefault(); mostrar(); var b = sim || nao; if (b) b.focus(); };
})();
