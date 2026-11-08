/* Tag do Google (Analytics) — mede visitas e de onde vieram (ex.: utm_source=telegram).
   Respeita o aviso de cookies: sem "Aceitar", o Google só recebe sinais sem cookies (Consent Mode). */
(function () {
  if (location.pathname.indexOf("/admin") === 0) return;
  var ID = "GTM-N39FX8CC";
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  window.gtag = gtag;
  var escolha = null;
  try { escolha = localStorage.getItem("aloha-consent"); } catch (e) {}
  gtag("consent", "default", {
    ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied",
    analytics_storage: escolha === "1" ? "granted" : "denied"
  });
  gtag("js", new Date());
  var s = document.createElement("script");
  s.async = true;
  s.src = "https://www.googletagmanager.com/gtm.js?id=" + ID;
  document.head.appendChild(s);
  document.addEventListener("click", function (e) {
    var id = e.target && e.target.id;
    if (id === "consent-sim") gtag("consent", "update", { analytics_storage: "granted" });
    if (id === "consent-nao") gtag("consent", "update", { analytics_storage: "denied" });
  });
})();
