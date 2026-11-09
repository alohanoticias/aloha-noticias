/* Painel de métricas: lê /admin/api/metricas (contador próprio, worker/index.js) e desenha cartões, gráficos e tabelas. */
(function () {
  var NOMES = {};
  try { NOMES = JSON.parse(document.getElementById("m-nomes").textContent); } catch (e) {}
  var IDIOMA = { pt: "Português", en: "Inglês", es: "Espanhol", fr: "Francês", de: "Alemão", it: "Italiano", ja: "Japonês", zh: "Chinês", ar: "Árabe" };
  var ORIGEM = { direto: "Direto (sem link de origem)", google: "Google", bing: "Bing", facebook: "Facebook", instagram: "Instagram", x: "X (Twitter)",
    telegram: "Telegram", youtube: "YouTube", tiktok: "TikTok", whatsapp: "WhatsApp", reddit: "Reddit" };
  var APAR = { celular: "Celular", computador: "Computador", tablet: "Tablet" };
  var nf = new Intl.NumberFormat("pt-BR");
  var paisNome; try { paisNome = new Intl.DisplayNames(["pt-BR"], { type: "region" }); } catch (e) {}
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var n = function (v) { return nf.format(v || 0); };
  var diaCurto = function (d) { return d.slice(8, 10) + "/" + d.slice(5, 7); };

  function nomePagina(c) {
    if (NOMES[c]) return NOMES[c];
    var m = c.match(/^\/(en|es|fr|de|it|ja|zh|ar)(\/.*)$/);
    if (m) return (m[2] === "/" ? "Página inicial" : m[2].replace(/^\//, "").replace(/\.html$/, "").replace(/-/g, " ")) + " (" + IDIOMA[m[1]] + ")";
    return c;
  }

  // ---------------------------------------------------------------- cartões
  function cards(r) {
    var dados = [
      ["Agora", r.agora.visualizacoes, "visualizações nos últimos 30 min", true],
      ["Hoje", r.hoje.visualizacoes, n(r.hoje.visitantes) + " visitantes"],
      ["Ontem", r.ontem.visualizacoes, n(r.ontem.visitantes) + " visitantes"],
      ["Últimos 7 dias", r.semana.visualizacoes, n(r.semana.visitantes) + " visitantes (soma diária)"],
      ["Desde o início", r.total.visualizacoes, n(r.total.visitantes) + " visitantes (soma diária)"],
    ];
    $("m-cards").innerHTML = dados.map(function (d) {
      return '<div class="p-stat' + (d[3] ? " m-agora" : "") + '"><span>' + d[0] + "</span><b>" + n(d[1]) + "</b><small>" + d[2] + "</small></div>";
    }).join("");
    var av = $("m-aviso");
    if (r.inicio_contagem) {
      var t = new Date(r.inicio_contagem);
      av.textContent = "Contagem própria ativa desde " + t.toLocaleDateString("pt-BR") + " às " + t.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) +
        ". Visitas anteriores a esse momento não existem neste contador.";
    } else av.textContent = "O contador está ligado, mas ainda não registrou nenhuma visita. Abra uma página do site para testar.";
    av.hidden = false;
  }

  // ---------------------------------------------------------------- gráfico de barras (uma série, com dica ao passar o mouse)
  function barras(alvo, itens, rotulo, dica) {
    var el = $(alvo);
    if (!itens.length) { el.innerHTML = '<div class="p-vazio">Sem visitas no período.</div>'; return; }
    var max = Math.max.apply(null, itens.map(function (i) { return i.v; })) || 1;
    var W = 1000, H = 220, base = H - 24, topo = 14, gap = 2, bw = W / itens.length;
    var passo = Math.ceil(itens.length / ((el.clientWidth || 800) < 600 ? 6 : 12));
    var svg = '<svg viewBox="0 0 ' + W + " " + H + '" preserveAspectRatio="none" role="img" aria-label="' + esc(rotulo) + '">';
    [0.5, 1].forEach(function (f) {
      var y = base - (base - topo) * f;
      svg += '<line class="m-grade" x1="0" x2="' + W + '" y1="' + y + '" y2="' + y + '"/>';
    });
    svg += '<line class="m-eixo" x1="0" x2="' + W + '" y1="' + base + '" y2="' + base + '"/>';
    itens.forEach(function (it, i) {
      var h = it.v ? Math.max(2, (base - topo) * it.v / max) : 0, x = i * bw + gap / 2, w = Math.max(1, bw - gap);
      var r = Math.min(4, w / 2, h);
      if (h) svg += '<path class="m-barra" d="M' + x + "," + base + "V" + (base - h + r) + "Q" + x + "," + (base - h) + " " + (x + r) + "," + (base - h) + "H" + (x + w - r) + "Q" + (x + w) + "," + (base - h) + " " + (x + w) + "," + (base - h + r) + "V" + base + 'Z"/>';
      svg += '<rect class="m-alvo" data-i="' + i + '" x="' + i * bw + '" y="0" width="' + bw + '" height="' + base + '"/>';
    });
    svg += "</svg>";
    var eixo = '<div class="m-eixo-x">' + itens.map(function (it, i) {
      return '<span style="left:' + ((i + 0.5) * 100 / itens.length) + '%">' + (i % passo === 0 ? esc(it.rot) : "") + "</span>";
    }).join("") + '</div><div class="m-max">máx. ' + n(max) + "</div>";
    el.innerHTML = '<div class="m-plot">' + svg + '<div class="m-dica" hidden></div></div>' + eixo;
    var dicaEl = el.querySelector(".m-dica"), plot = el.querySelector(".m-plot");
    el.querySelectorAll(".m-alvo").forEach(function (a) {
      a.addEventListener("mouseenter", function () {
        var i = +a.getAttribute("data-i");
        dicaEl.innerHTML = dica(itens[i]); dicaEl.hidden = false;
        var pct = (i + 0.5) / itens.length;
        dicaEl.style.left = (pct * 100) + "%";
        dicaEl.style.transform = "translateX(" + (pct > 0.75 ? "-100%" : pct < 0.25 ? "0" : "-50%") + ")";
        el.querySelectorAll(".m-barra")[0] && plot.classList.add("m-foco");
      });
      a.addEventListener("mouseleave", function () { dicaEl.hidden = true; plot.classList.remove("m-foco"); });
    });
  }

  function serie(r) {
    var mapa = {}; r.serie.forEach(function (s) { mapa[s.dia] = s; });
    var itens = [], fim = new Date(r.gerado - 3 * 3600000);
    for (var k = r.dias - 1; k >= 0; k--) {
      var d = new Date(fim.getTime() - k * 86400000).toISOString().slice(0, 10), s = mapa[d] || { v: 0, u: 0 };
      itens.push({ rot: diaCurto(d), dia: d, v: s.v, u: s.u });
    }
    barras("m-serie", itens, "Visualizações por dia", function (it) {
      return "<b>" + it.dia.split("-").reverse().join("/") + "</b><br>" + n(it.v) + " visualizações<br>" + n(it.u) + " visitantes";
    });
    $("m-serie-tab").innerHTML = tabela(["Dia", "Visualizações", "Visitantes"], itens.slice().reverse().map(function (it) {
      return [it.dia.split("-").reverse().join("/"), n(it.v), n(it.u)];
    }));
  }

  function horas(r) {
    var mapa = {}; r.horas.forEach(function (h) { mapa[h.hora] = h.v; });
    var itens = []; for (var h = 0; h < 24; h++) itens.push({ rot: h + "h", h: h, v: mapa[h] || 0 });
    barras("m-horas", itens, "Visualizações por hora do dia", function (it) { return "<b>" + it.h + "h às " + it.h + "h59</b><br>" + n(it.v) + " visualizações"; });
  }

  // ---------------------------------------------------------------- tabelas com barra de proporção
  function tabela(cab, linhas, numDesde) {
    if (numDesde == null) numDesde = 1;
    return '<div class="m-tab"><table><thead><tr>' + cab.map(function (c, i) { return "<th" + (i >= numDesde ? ' class="num"' : "") + ">" + c + "</th>"; }).join("") +
      "</tr></thead><tbody>" + linhas.map(function (l) {
        return "<tr>" + l.map(function (c, i) { return "<td" + (i >= numDesde ? ' class="num"' : "") + ">" + c + "</td>"; }).join("") + "</tr>";
      }).join("") + "</tbody></table></div>";
  }

  function ranking(alvo, itens, nome, vazio) {
    var el = $(alvo);
    if (!itens.length) { el.innerHTML = '<div class="p-vazio">' + (vazio || "Sem dados no período.") + "</div>"; return; }
    var max = itens[0].v || 1;
    el.innerHTML = '<ul class="m-rank">' + itens.map(function (it) {
      return '<li title="' + esc(n(it.v) + " visualizações · " + n(it.u) + " visitantes") + '"><div class="m-rank-t"><span>' + nome(it) + "</span><b>" + n(it.v) + "</b></div>" +
        '<i style="width:' + Math.max(2, 100 * it.v / max) + '%"></i></li>';
    }).join("") + "</ul>";
  }

  function desenhar(r) {
    cards(r); serie(r); horas(r);
    ranking("m-paginas", r.paginas, function (it) {
      return '<a href="' + esc(it.nome) + '" target="_blank" rel="noopener">' + esc(nomePagina(it.nome)) + "</a>";
    });
    ranking("m-origens", r.origens, function (it) { return esc(ORIGEM[it.nome] || it.nome); });
    ranking("m-fontes", r.fontes, function (it) { return esc(it.nome); }, "Nenhuma visita por link etiquetado no período.");
    ranking("m-paises", r.paises, function (it) { return esc(it.nome ? ((paisNome && paisNome.of(it.nome)) || it.nome) : "Desconhecido"); });
    ranking("m-aparelhos", r.aparelhos, function (it) { return esc(APAR[it.nome] || it.nome); });
    ranking("m-idiomas", r.idiomas, function (it) { return esc(IDIOMA[it.nome] || it.nome); });
    $("m-parceiros").innerHTML = r.parceiros.length ? tabela(["Parceiro", "Rede", "Jogo/assunto", "Visualizações", "Visitantes"], r.parceiros.map(function (p) {
      return [esc(p.parceiro || "—"), esc(p.rede || "—"), esc(p.jogo || "—"), n(p.v), n(p.u)];
    }), 3) : '<div class="p-vazio">Nenhuma visita por link de parceiro no período.</div>';
  }

  function carregar() {
    var dias = $("m-dias").value;
    fetch("/admin/api/metricas?dias=" + dias, { credentials: "same-origin", cache: "no-store" })
      .then(function (res) { if (!res.ok) throw new Error(res.status); return res.json(); })
      .then(desenhar)
      .catch(function (e) {
        $("m-cards").innerHTML = '<div class="p-stat"><span>Sem conexão com o contador</span><b>—</b><small>' +
          (String(e.message) === "403" ? "faça login no painel de novo" : "o contador ainda não está no ar ou o deploy falhou (erro " + esc(e.message) + ")") + "</small></div>";
      });
  }

  $("m-dias").addEventListener("change", carregar);
  $("m-tabela-dia").addEventListener("click", function (e) {
    e.preventDefault(); var t = $("m-serie-tab"); t.hidden = !t.hidden; this.textContent = t.hidden ? "Ver tabela" : "Esconder tabela";
  });

  // "não contar meus acessos" (vale para este navegador)
  function eu() {
    var fora = false; try { fora = localStorage.getItem("aloha-nao-contar") === "1"; } catch (e) {}
    $("m-eu").textContent = fora ? "Voltar a contar meus acessos" : "Não contar meus acessos neste navegador";
    $("m-eu-txt").textContent = fora ? "Seus acessos neste navegador não entram na contagem." : "Seus acessos neste navegador estão sendo contados.";
  }
  $("m-eu").addEventListener("click", function () {
    try { localStorage.getItem("aloha-nao-contar") === "1" ? localStorage.removeItem("aloha-nao-contar") : localStorage.setItem("aloha-nao-contar", "1"); } catch (e) {}
    eu();
  });
  eu(); carregar();
  setInterval(function () { if (document.visibilityState === "visible") carregar(); }, 60000);
})();
