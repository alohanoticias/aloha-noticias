/* Tag do Google (Analytics) — mede visitas e de onde vieram (ex.: utm_source=telegram).
   Fora da Europa a medição já começa ao abrir a página (mesmo sem tocar em "Aceitar");
   na UE/Reino Unido/Suíça espera o "Aceitar", como a lei de lá exige. "Recusar" desliga em qualquer lugar. */
(function () {
  if (location.pathname.indexOf("/admin") === 0) return;
  var ID = "G-GLYYDDCN1Q";  // Google Analytics 4 (fluxo alohanoticias.com)
  var EUROPA = ["AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IS","IE","IT","LV","LI","LT",
                "LU","MT","NL","NO","PL","PT","RO","SK","SI","ES","SE","GB","CH"];
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  window.gtag = gtag;
  var escolha = null;
  try { escolha = localStorage.getItem("aloha-consent"); } catch (e) {}
  var anuncios = { ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied" };
  function com(extra) { var o = {}; for (var k in anuncios) o[k] = anuncios[k]; for (var j in extra) o[j] = extra[j]; return o; }
  // Europa: só mede depois do "Aceitar"
  gtag("consent", "default", com({ analytics_storage: escolha === "1" ? "granted" : "denied", region: EUROPA }));
  // resto do mundo: mede desde o início, a não ser que a pessoa tenha tocado em "Recusar"
  gtag("consent", "default", com({ analytics_storage: escolha === "0" ? "denied" : "granted" }));
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
    if (id === "consent-sim") gtag("consent", "update", { analytics_storage: "granted" });
    if (id === "consent-nao") gtag("consent", "update", { analytics_storage: "denied" });
  });
})();
