/* Contador de visitas próprio da ALOHA NOTÍCIAS: avisa o servidor que esta página foi vista.
   Sem cookies e sem dados pessoais (veja worker/index.js). Quem marcou "não contar meus acessos" no painel não é contado. */
(function () {
  try {
    if (localStorage.getItem("aloha-nao-contar") === "1") return;
    if (navigator.webdriver || document.visibilityState === "prerender") return;
  } catch (e) {}
  var meta = document.querySelector('meta[name="aloha-slug"]');
  var dados = JSON.stringify({ u: location.href, r: document.referrer, s: meta ? meta.content : "" });
  function enviar() {
    try {
      if (navigator.sendBeacon && navigator.sendBeacon("/api/v", new Blob([dados], { type: "text/plain" }))) return;
    } catch (e) {}
    try { fetch("/api/v", { method: "POST", body: dados, keepalive: true, credentials: "omit" }); } catch (e) {}
  }
  if (document.visibilityState === "hidden") {
    document.addEventListener("visibilitychange", function f() {
      if (document.visibilityState === "visible") { document.removeEventListener("visibilitychange", f); enviar(); }
    });
  } else enviar();
})();
