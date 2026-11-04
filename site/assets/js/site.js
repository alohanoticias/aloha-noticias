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
    var botaoTema = document.getElementById("botao-tema");
    if (botaoTema) {
      var rotular = function () {
        botaoTema.setAttribute("aria-label", temaAtual() === "dark" ? "Usar tema claro" : "Usar tema escuro");
      };
      rotular();
      botaoTema.addEventListener("click", function () {
        var novo = temaAtual() === "dark" ? "light" : "dark";
        raiz.setAttribute("data-theme", novo);
        gravar("aloha-tema", novo);
        rotular();
      });
    }

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
        var falhou = function () { botaoCopiar.textContent = "Copie o endereço na barra do navegador"; };
        var ok = function () { botaoCopiar.textContent = "Link copiado"; setTimeout(function () { botaoCopiar.textContent = "Copiar link"; }, 2000); };
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
      var campo = document.getElementById("campo-busca");
      var lista = document.getElementById("resultados");
      var info = document.getElementById("info-busca");
      var norm = function (s) { return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); };
      var buscar = function () {
        var termos = norm(campo.value.trim()).split(/\s+/).filter(Boolean);
        lista.innerHTML = "";
        if (!termos.length) { info.textContent = "Digite um assunto, por exemplo: bateria, juros ou cinema."; return; }
        var achados = window.ALOHA_INDICE.filter(function (m) {
          var alvo = norm(m.titulo + " " + m.linha_fina + " " + m.editoria + " " + m.tags.join(" "));
          return termos.every(function (t) { return alvo.indexOf(t) !== -1; });
        });
        info.textContent = achados.length === 0
          ? "Nada encontrado para “" + campo.value.trim() + "”. Tente outra palavra."
          : achados.length + (achados.length === 1 ? " matéria encontrada" : " matérias encontradas");
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

  // Seções da home: setas para passar e voltar entre as páginas de matérias.
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-carrossel]").forEach(function (car) {
      var paginas = car.querySelectorAll(".pagina-lista");
      var pager = car.querySelector(".pager");
      if (!pager || paginas.length < 2) return;
      var ant = pager.querySelector(".pager-ant");
      var prox = pager.querySelector(".pager-prox");
      var info = pager.querySelector(".pager-info");
      var atual = 0;
      raiz.classList.add("js");
      pager.hidden = false;
      function mostrar(n, rolar) {
        atual = n;
        paginas.forEach(function (p, i) { p.hidden = i !== n; });
        ant.hidden = n === 0;
        prox.hidden = n === paginas.length - 1;
        info.textContent = (n + 1) + " / " + paginas.length;
        if (rolar) { car.parentNode.parentNode.scrollIntoView({ block: "start", behavior: "smooth" }); }
      }
      prox.addEventListener("click", function () { mostrar(Math.min(atual + 1, paginas.length - 1), true); });
      ant.addEventListener("click", function () { mostrar(Math.max(atual - 1, 0), true); });
      mostrar(0, false);
    });
  });
})();
