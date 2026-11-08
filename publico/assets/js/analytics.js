/* Tag do Google (Analytics) — mede visitas e de onde vieram (ex.: utm_source=telegram).
   Links sem etiqueta: reconhece a rede (YouTube, Instagram, TikTok, Facebook, X...) pelo site de origem ou pelo app.
   Toda chegada por rede gera também o evento visita_<rede> (aparece na hora no Tempo real).
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
  // origem da visita (etiquetas utm do link): vai explícita para o Google, sem depender de ele ler o endereço
  function param(n) { var m = location.search.match(new RegExp("[?&]" + n + "=([^&#]*)")); return m ? decodeURIComponent(m[1].replace(/\+/g, " ")) : ""; }
  var fonte = param("utm_source"), midia = param("utm_medium"), campanha = param("utm_campaign");
  // sem etiqueta no link: descobre a rede pelo site de origem ou pelo navegador interno do app
  if (!fonte) {
    var ref = (document.referrer || "").toLowerCase(), ua = navigator.userAgent || "";
    var pelaOrigem = [["youtube", /(^|[./])(youtube\.com|youtu\.be)\//], ["instagram", /(^|[./])instagram\.com\//],
      ["facebook", /(^|[./])(facebook\.com|fb\.com|fb\.me)\//], ["tiktok", /(^|[./])tiktok\.com\//], ["x", /(^|[./])(t\.co|x\.com|twitter\.com)\//],
      ["threads", /(^|[./])threads\.(net|com)\//], ["whatsapp", /(^|[./])(whatsapp\.com|wa\.me)\//], ["telegram", /(^|[./])(t\.me|telegram\.(org|me))\//],
      ["kwai", /(^|[./])kwai\.com\//], ["pinterest", /(^|[./])pinterest\.[a-z.]+\//], ["reddit", /(^|[./])reddit\.com\//],
      ["discord", /(^|[./])discord(app)?\.com\//], ["linkedin", /(^|[./])(linkedin\.com|lnkd\.in)\//]];
    var peloApp = [["instagram", /Instagram/], ["facebook", /FBAN|FBAV|FB_IAB/], ["tiktok", /musical_ly|BytedanceWebview|TikTok/i],
      ["threads", /Barcelona/], ["telegram", /Telegram/i], ["kwai", /Kwai/i], ["pinterest", /Pinterest/i], ["linkedin", /LinkedInApp/],
      ["snapchat", /Snapchat/i], ["discord", /Discord/i]];
    for (var i = 0; i < pelaOrigem.length && !fonte; i++) if (pelaOrigem[i][1].test(ref)) fonte = pelaOrigem[i][0];
    for (var j = 0; j < peloApp.length && !fonte; j++) if (peloApp[j][1].test(ua)) fonte = peloApp[j][0];
    if (fonte) { midia = "social"; campanha = "detectado_automaticamente"; }
  }
  if (fonte) {
    opcoes.campaign_source = fonte;
    if (midia) opcoes.campaign_medium = midia;
    if (campanha) opcoes.campaign_name = campanha;
  }
  gtag("js", new Date());
  gtag("config", ID, opcoes);
  // evento próprio que aparece na hora no Tempo real (quadro "Contagem de eventos"): ex. visita_telegram
  if (fonte && /^[a-z0-9_]{1,30}$/i.test(fonte)) {
    gtag("event", "visita_" + fonte.toLowerCase(), { fonte: fonte, midia: midia, campanha: campanha });
  }
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
