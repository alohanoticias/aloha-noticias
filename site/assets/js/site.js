/* ALOHA NOTÍCIAS — interações do site */
(function () {
  var raiz = document.documentElement;

  function ler(chave) { try { return localStorage.getItem(chave); } catch (e) { return null; } }
  function gravar(chave, valor) { try { localStorage.setItem(chave, valor); } catch (e) {} }

  // Tema claro/escuro: segue o sistema até a pessoa escolher.
  var salvo = ler("aloha-tema");
  if (salvo === "dark" || salvo === "light") raiz.setAttribute("data-theme", salvo);

  function temaAtual() {
    var t = raiz.getAttribute("data-theme");
    if (t) return t;
    return window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  document.addEventListener("DOMContentLoaded", function () {
    var botoesTema = document.querySelectorAll("#botao-tema, .botao-tema-m");
    var rotular = function () {
      botoesTema.forEach(function (b) { b.setAttribute("aria-label", temaAtual() === "dark" ? "Usar tema claro" : "Usar tema escuro"); });
    };
    rotular();
    botoesTema.forEach(function (b) {
      b.addEventListener("click", function () {
        var novo = temaAtual() === "dark" ? "light" : "dark";
        raiz.setAttribute("data-theme", novo);
        gravar("aloha-tema", novo);
        rotular();
      });
    });

    // Menu no celular
    var botaoMenu = document.getElementById("botao-menu");
    var gaveta = document.getElementById("gaveta");
    if (botaoMenu && gaveta) {
      botaoMenu.addEventListener("click", function () {
        var abrir = gaveta.hidden;
        gaveta.hidden = !abrir;
        botaoMenu.setAttribute("aria-expanded", String(abrir));
      });
    }

    // Copiar link da matéria
    var botaoCopiar = document.getElementById("copiar-link");
    if (botaoCopiar) {
      botaoCopiar.addEventListener("click", function () {
        var url = location.href;
        var falhou = function () { botaoCopiar.textContent = botaoCopiar.getAttribute("data-erro") || "Copie o endereço na barra do navegador"; };
        var ok = function () { botaoCopiar.textContent = botaoCopiar.getAttribute("data-ok") || "Link copiado"; setTimeout(function () { botaoCopiar.textContent = botaoCopiar.getAttribute("data-rotulo") || "Copiar link"; }, 2000); };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(url).then(ok, falhou);
        } else { falhou(); }
      });
    }

    // Newsletter (sem serviço conectado ainda)
    document.querySelectorAll(".form-news").forEach(function (form) {
      form.addEventListener("submit", function (ev) {
        ev.preventDefault();
        var aviso = form.querySelector(".form-aviso");
        if (aviso) aviso.textContent = "Formulário de exemplo. Conecte um serviço de newsletter para receber as inscrições.";
      });
    });

    // Busca
    var formBusca = document.getElementById("form-busca");
    if (formBusca && window.ALOHA_INDICE) {
      var T = window.ALOHA_T || {};
      var campo = document.getElementById("campo-busca");
      var lista = document.getElementById("resultados");
      var info = document.getElementById("info-busca");
      var norm = function (s) { return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); };
      var buscar = function () {
        var termos = norm(campo.value.trim()).split(/\s+/).filter(Boolean);
        lista.innerHTML = "";
        if (!termos.length) { info.textContent = T["Digite um assunto, por exemplo: GTA 6, Marvel ou cinema."]; return; }
        var achados = window.ALOHA_INDICE.filter(function (m) {
          var alvo = norm(m.titulo + " " + m.linha_fina + " " + m.editoria + " " + m.tags.join(" "));
          return termos.every(function (t) { return alvo.indexOf(t) !== -1; });
        });
        info.textContent = achados.length === 0
          ? T["Nada encontrado para"] + " “" + campo.value.trim() + "”. " + T["Tente outra palavra."]
          : achados.length + " " + (achados.length === 1 ? T["matéria encontrada"] : T["matérias encontradas"]);
        achados.forEach(function (m) {
          var li = document.createElement("li");
          li.innerHTML = '<a href="' + m.url + '"><div class="dupla" style="gap:6px"><span class="chapeu">' + m.editoria +
            '</span><h3></h3><p class="meta"></p></div>' + m.capa + "</a>";
          li.querySelector("h3").textContent = m.titulo;
          li.querySelector(".meta").textContent = m.data;
          lista.appendChild(li);
        });
      };
      formBusca.addEventListener("submit", function (ev) { ev.preventDefault(); buscar(); });
      campo.addEventListener("input", buscar);
      buscar();
    }
  });
})();

/* Idiomas: PT, EN e ES são páginas reais (links gerados no servidor). Os demais idiomas usam o tradutor do Google em outra página,
   sem carregar nada do Google aqui no site. O aviso abaixo só aparece para quem navega em outro idioma e nunca para robôs. */
(function () {
  var base = (document.documentElement.lang || "pt").split("-")[0];
  var u = location.href, idioma = (navigator.language || "pt").toLowerCase();
  function google(l) { return "https://translate.google.com/translate?sl=" + base + "&tl=" + l + "&u=" + encodeURIComponent(u); }
  var links = document.querySelectorAll("[data-l]");
  for (var i = 0; i < links.length; i++) { links[i].href = google(links[i].getAttribute("data-l")); links[i].rel = "noopener"; }
  if (location.pathname.indexOf("/admin") === 0 || /bot|crawl|spider|lighthouse/i.test(navigator.userAgent)) return;
  var l = idioma.split("-")[0];
  if (l === base) return;
  try { if (sessionStorage.getItem("aloha-trad") === "1") return; } catch (e) {}
  var nomes = { pt: "Ler esta página em português", en: "Read this page in English", es: "Leer esta página en español", fr: "Lire cette page en français", de: "Diese Seite auf Deutsch lesen", it: "Leggi questa pagina in italiano", ja: "このページを日本語で読む", zh: "用中文阅读此页", ar: "اقرأ هذه الصفحة بالعربية" };
  var alvo = l === "zh" ? "zh-CN" : l, texto = nomes[l] || nomes.en, destino;
  var alt = document.querySelector('link[rel="alternate"][hreflang^="' + l + '"]');
  if (alt) { destino = alt.href; }
  else {
    if (!nomes[l]) { alvo = "en"; texto = nomes.en; var altEn = document.querySelector('link[rel="alternate"][hreflang="en"]'); if (altEn && base !== "en") { destino = altEn.href; } }
    if (!destino) destino = google(alvo);
  }
  var b = document.createElement("div"); b.className = "aviso-idioma";
  b.innerHTML = '<a rel="noopener"></a><button type="button" aria-label="Fechar / Close">×</button>';
  var a = b.querySelector("a"); a.href = destino; a.textContent = texto;
  b.querySelector("button").onclick = function () { try { sessionStorage.setItem("aloha-trad", "1"); } catch (e) {} b.remove(); };
  document.body.insertBefore(b, document.body.firstChild);
})();

/* Fecha o seletor de idioma ao clicar fora */
document.addEventListener("click", function (e) { var m = document.getElementById("idioma-menu"); if (m && m.open && !m.contains(e.target)) m.open = false; });

// Fotos de outras fontes: se uma imagem do texto não carregar, a foto e a legenda somem (sem ícone quebrado)
document.addEventListener("error", function (e) {
  var el = e.target;
  if (el && el.tagName === "IMG" && el.closest && el.closest(".foto-corpo")) { el.closest(".foto-corpo").hidden = true; }
}, true);
