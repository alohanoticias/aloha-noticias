/* Tag do Google (Analytics) — mede visitas e de onde vieram (ex.: utm_source=telegram).
   Respeita o aviso de cookies: sem "Aceitar", o Google só recebe sinais sem cookies (Consent Mode). */
(function () {
  if (location.pathname.indexOf("/admin") === 0) return;
  var ID = "G-GLYYDDCN1Q";  // Google Analytics 4 (fluxo alohanoticias.com)
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  window.gtag = gtag;
  var escolha = null;
  try { escolha = localStorage.getItem("aloha-consent"); } catch (e) {}
  gtag("consent", "default", {
    ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied",
    analytics_storage: escolha === "1" ? "granted" : "denied"
  });
  // modo de teste: com ?aloha_debug=1 no endereço, os dados aparecem em Administrador > DebugView
  var opcoes = /[?&]aloha_debug=1/.test(location.search) ? { debug_mode: true } : {};
  gtag("js", new Date());
  gtag("config", ID, opcoes);
  var s = document.createElement("script");
  s.async = true;
  s.src = "https://www.googletagmanager.com/gtag/js?id=" + ID;
  document.head.appendChild(s);
  document.addEventListener("click", function (e) {
    var id = e.target && e.target.id;
    if (id === "consent-sim") {
      gtag("consent", "update", { analytics_storage: "granted" });
      // refaz a medição da página já com cookies: leva o endereço completo, com a etiqueta de origem (ex.: telegram)
      var o = { page_location: location.href };
      if (document.referrer) o.page_referrer = document.referrer;
      for (var k in opcoes) o[k] = opcoes[k];
      gtag("config", ID, o);
    }
    if (id === "consent-nao") gtag("consent", "update", { analytics_storage: "denied" });
  });
})();
