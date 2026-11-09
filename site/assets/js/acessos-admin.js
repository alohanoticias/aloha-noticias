// Painel de acessos (admin): busca os números do Google Analytics em /api/ga e desenha tabelas e gráficos.
(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  var fmt = new Intl.NumberFormat("pt-BR");
  var estado = { inicio: "6daysAgo", fim: "today", dias: 7, agrupar: "dia" };
  var NOMES_IDIOMA = { pt: "Português", en: "Inglês", es: "Espanhol", fr: "Francês", de: "Alemão", it: "Italiano", ja: "Japonês", zh: "Chinês", ar: "Árabe" };
  var SEMANA = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];
  var APARELHOS = { mobile: "Celular", desktop: "Computador", tablet: "Tablet", "smart tv": "TV" };
  var CANAIS = { Direct: "Direto", "Organic Search": "Busca (Google etc.)", "Organic Social": "Redes sociais", Referral: "Outros sites", Email: "E-mail", Unassigned: "Não identificado", "Paid Search": "Busca paga", "Organic Video": "Vídeo" };

  function cor(nome, reserva) {
    var v = getComputedStyle(document.documentElement).getPropertyValue(nome).trim();
    return v || reserva;
  }

  function api(corpo) {
    return fetch("/api/ga", { method: "POST", headers: { "Content-Type": "application/json" }, credentials: "same-origin", body: JSON.stringify(corpo) })
      .then(function (r) { return r.json().then(function (j) { if (!r.ok || j.erro) throw new Error(j.erro || ("Erro " + r.status)); return j; }); });
  }

  function iso(d) { return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); }
  function diasEntre(a, b) { return Math.round((new Date(b + "T12:00") - new Date(a + "T12:00")) / 864e5) + 1; }
  function datasReais() {
    var hoje = new Date();
    function conv(s) {
      if (s === "today") return iso(hoje);
      if (s === "yesterday") { var d = new Date(hoje); d.setDate(d.getDate() - 1); return iso(d); }
      var m = /^(\d+)daysAgo$/.exec(s);
      if (m) { var e = new Date(hoje); e.setDate(e.getDate() - Number(m[1])); return iso(e); }
      return s;
    }
    return { inicio: conv(estado.inicio), fim: conv(estado.fim) };
  }
  function periodoAnterior() {
    var r = datasReais(), n = diasEntre(r.inicio, r.fim);
    var fim = new Date(r.inicio + "T12:00"); fim.setDate(fim.getDate() - 1);
    var ini = new Date(fim); ini.setDate(ini.getDate() - n + 1);
    return { inicio: iso(ini), fim: iso(fim) };
  }
  function pedido(tipo, extra) {
    var o = { tipo: tipo, inicio: estado.inicio, fim: estado.fim };
    for (var k in extra || {}) o[k] = extra[k];
    return o;
  }

  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  // tabela simples: colunas = [{t: título, k: chave, n: numérica, f: função de formatação}]
  function tabela(el, linhas, colunas, vazio) {
    if (!linhas.length) { el.innerHTML = '<p class="meta">' + (vazio || "Sem dados neste período.") + "</p>"; return; }
    var principal = colunas.filter(function (c) { return c.n; })[0];
    var max = principal ? Math.max.apply(null, linhas.map(function (l) { return l[principal.k] || 0; })) || 1 : 1;
    var h = "<table><thead><tr>" + colunas.map(function (c) { return "<th" + (c.n ? ' class="n"' : "") + ">" + c.t + "</th>"; }).join("") + "</tr></thead><tbody>";
    linhas.forEach(function (l) {
      h += "<tr>" + colunas.map(function (c, i) {
        var v = c.f ? c.f(l[c.k], l) : l[c.k];
        if (c.n) return '<td class="n">' + fmt.format(Math.round(v || 0)) + "</td>";
        var barra = i === 0 && principal ? '<div class="barra" style="width:' + Math.max(2, (l[principal.k] / max) * 100).toFixed(1) + '%"></div>' : "";
        return "<td>" + (c.html ? v : esc(v)) + barra + "</td>";
      }).join("") + "</tr>";
    });
    el.innerHTML = h + "</tbody></table>";
  }

  // ---------- gráficos em canvas ----------
  function prepararCanvas(cv) {
    var dpr = window.devicePixelRatio || 1, w = cv.clientWidth, h = Number(cv.getAttribute("height"));
    cv.width = w * dpr; cv.height = h * dpr; cv.style.height = h + "px";
    var ctx = cv.getContext("2d"); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { ctx: ctx, w: w, h: h };
  }
  function eixos(c, max, esq, base, dir, topo) {
    var ctx = c.ctx, tinta = cor("--tinta", "#222"), linha = cor("--linha", "#ddd");
    ctx.font = "12px system-ui, sans-serif"; ctx.fillStyle = tinta; ctx.strokeStyle = linha; ctx.lineWidth = 1;
    for (var i = 0; i <= 4; i++) {
      var y = base - (base - topo) * i / 4;
      ctx.globalAlpha = 0.5; ctx.beginPath(); ctx.moveTo(esq, y); ctx.lineTo(c.w - dir, y); ctx.stroke(); ctx.globalAlpha = 1;
      ctx.textAlign = "right"; ctx.fillText(fmt.format(Math.round(max * i / 4)), esq - 6, y + 4);
    }
  }
  function teto(v) { if (v <= 4) return 4; var p = Math.pow(10, Math.floor(Math.log10(v))); return Math.ceil(v / p) * p; }

  function linhasGrafico(cv, rotulos, series) {
    var c = prepararCanvas(cv), ctx = c.ctx, esq = 52, dir = 12, topo = 12, base = c.h - 28;
    var max = teto(Math.max.apply(null, [1].concat.apply([], series.map(function (s) { return s.v; }))));
    eixos(c, max, esq, base, dir, topo);
    var n = rotulos.length, passo = n > 1 ? (c.w - esq - dir) / (n - 1) : 0;
    var x = function (i) { return n > 1 ? esq + i * passo : (esq + c.w - dir) / 2; };
    ctx.textAlign = "center"; ctx.fillStyle = cor("--tinta", "#222");
    var cada = Math.max(1, Math.ceil(n / Math.floor((c.w - esq) / 70)));
    rotulos.forEach(function (r, i) { if (i % cada === 0) ctx.fillText(r, x(i), c.h - 8); });
    series.forEach(function (s) {
      ctx.strokeStyle = s.c; ctx.fillStyle = s.c; ctx.lineWidth = 2; ctx.beginPath();
      s.v.forEach(function (v, i) { var y = base - (base - topo) * v / max; if (i) ctx.lineTo(x(i), y); else ctx.moveTo(x(i), y); });
      ctx.stroke();
      if (n <= 40) s.v.forEach(function (v, i) { ctx.beginPath(); ctx.arc(x(i), base - (base - topo) * v / max, 2.5, 0, 7); ctx.fill(); });
    });
  }

  function barras(cv, rotulos, valores, corBarra) {
    var c = prepararCanvas(cv), ctx = c.ctx, esq = 44, dir = 8, topo = 10, base = c.h - 24;
    var max = teto(Math.max.apply(null, [1].concat(valores)));
    eixos(c, max, esq, base, dir, topo);
    var n = valores.length, larg = (c.w - esq - dir) / n;
    ctx.textAlign = "center";
    valores.forEach(function (v, i) {
      var h = (base - topo) * v / max;
      ctx.fillStyle = corBarra; ctx.fillRect(esq + i * larg + larg * 0.15, base - h, larg * 0.7, h);
      ctx.fillStyle = cor("--tinta", "#222");
      if (n <= 12 || i % 2 === 0) ctx.fillText(rotulos[i], esq + i * larg + larg / 2, c.h - 6);
    });
  }

  // ---------- rótulos de tempo ----------
  function rotuloTempo(dim, v) {
    if (dim === "dateHour") return v.slice(6, 8) + "/" + v.slice(4, 6) + " " + v.slice(8) + "h";
    if (dim === "date") return v.slice(6, 8) + "/" + v.slice(4, 6);
    if (dim === "isoYearIsoWeek") return "Sem " + Number(v.slice(4)) + "/" + v.slice(2, 4);
    if (dim === "yearMonth") return ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"][Number(v.slice(4)) - 1] + "/" + v.slice(2, 4);
    return v;
  }

  // ---------- blocos ----------
  function variacao(atual, ant) {
    if (ant == null) return "";
    if (!ant) return atual ? '<small class="ac-sobe">novo</small>' : "";
    var p = (atual - ant) / ant * 100;
    return '<small class="' + (p >= 0 ? "ac-sobe" : "ac-desce") + '">' + (p >= 0 ? "▲ " : "▼ ") + Math.abs(p).toFixed(0) + "% vs. período anterior</small>";
  }
  function tempo(seg) { seg = Math.round(seg || 0); return Math.floor(seg / 60) + "min " + String(seg % 60).padStart(2, "0") + "s"; }

  function carregarResumo() {
    return api(pedido("resumo", { anterior: periodoAnterior() })).then(function (j) {
      var atual = {}, ant = null;
      j.linhas.forEach(function (l) { if (l.dateRange === "anterior") ant = l; else if (!l.dateRange || l.dateRange === "atual") atual = l; });
      if (!j.linhas.some(function (l) { return l.dateRange; })) atual = j.linhas[0] || {};
      var cards = [
        ["Visitantes", "activeUsers"], ["Visitantes novos", "newUsers"], ["Visitas (sessões)", "sessions"],
        ["Páginas vistas", "screenPageViews"], ["Tempo médio por visita", "averageSessionDuration", tempo], ["Taxa de engajamento", "engagementRate", function (v) { return ((v || 0) * 100).toFixed(0) + "%"; }],
      ];
      $("ac-resumo").innerHTML = cards.map(function (c) {
        var v = atual[c[1]] || 0;
        return '<div class="ac-card">' + c[0] + "<b>" + (c[2] ? c[2](v) : fmt.format(v)) + "</b>" + variacao(v, ant ? ant[c[1]] || 0 : null) + "</div>";
      }).join("");
    });
  }

  function carregarSerie() {
    return api(pedido("serie", { agrupar: estado.agrupar })).then(function (j) {
      var rot = j.linhas.map(function (l) { return rotuloTempo(j.dimensao, l[j.dimensao]); });
      linhasGrafico($("ac-grafico"), rot, [
        { c: cor("--marca", "#d6336c"), v: j.linhas.map(function (l) { return l.activeUsers; }) },
        { c: "#1c7ed6", v: j.linhas.map(function (l) { return l.sessions; }) },
        { c: "#f59f00", v: j.linhas.map(function (l) { return l.screenPageViews; }) },
      ]);
      var dim = j.dimensao;
      tabela($("ac-serie-tabela"), j.linhas.slice().reverse(), [
        { t: "Período", k: dim, f: function (v) { return rotuloTempo(dim, v); } },
        { t: "Visitantes", k: "activeUsers", n: 1 }, { t: "Visitas", k: "sessions", n: 1 }, { t: "Páginas vistas", k: "screenPageViews", n: 1 },
      ]);
    });
  }

  function carregarHoras() {
    return Promise.all([api(pedido("horas")), api(pedido("dias_semana"))]).then(function (r) {
      var h = new Array(24).fill(0);
      r[0].linhas.forEach(function (l) { h[Number(l.hour)] = l.sessions; });
      barras($("ac-horas"), h.map(function (_, i) { return i + "h"; }), h, cor("--marca", "#d6336c"));
      var s = new Array(7).fill(0);
      r[1].linhas.forEach(function (l) { s[Number(l.dayOfWeek)] = l.sessions; });
      barras($("ac-semana"), SEMANA, s, "#1c7ed6");
    });
  }

  function carregarTabelas() {
    var lista = [
      ["parceiros", "ac-parceiros", [
        { t: "Parceiro", k: "sessionSource" }, { t: "Rede", k: "sessionMedium" },
        { t: "Idioma", k: "sessionManualAdContent", f: function (v) { return NOMES_IDIOMA[v] || v || "—"; } },
        { t: "Visitas", k: "sessions", n: 1 }, { t: "Visitantes", k: "activeUsers", n: 1 }, { t: "Páginas vistas", k: "screenPageViews", n: 1 }],
        "Nenhuma visita por link de parceiro neste período."],
      ["canais", "ac-canais", [{ t: "Canal", k: "sessionDefaultChannelGroup", f: function (v) { return CANAIS[v] || v; } }, { t: "Visitas", k: "sessions", n: 1 }]],
      ["origens", "ac-origens", [{ t: "Origem", k: "sessionSource", f: function (v) { return v === "(direct)" ? "Direto (digitou o endereço)" : v; } }, { t: "Mídia", k: "sessionMedium", f: function (v) { return v === "(none)" ? "—" : v; } }, { t: "Visitas", k: "sessions", n: 1 }, { t: "Visitantes", k: "activeUsers", n: 1 }]],
      ["paginas", "ac-paginas", [{ t: "Página", k: "pageTitle", html: 1, f: function (v, l) { return '<a href="' + esc(l.pagePath) + '" target="_blank" rel="noopener">' + esc((v || l.pagePath).replace(/\s*[|·–-]\s*Aloha.*$/i, "")) + "</a>"; } }, { t: "Vistas", k: "screenPageViews", n: 1 }, { t: "Visitantes", k: "activeUsers", n: 1 }]],
      ["paises", "ac-paises", [{ t: "País", k: "country" }, { t: "Visitantes", k: "activeUsers", n: 1 }, { t: "Visitas", k: "sessions", n: 1 }]],
      ["cidades", "ac-cidades", [{ t: "Cidade", k: "city", f: function (v) { return v === "(not set)" ? "Não identificada" : v; } }, { t: "Visitantes", k: "activeUsers", n: 1 }, { t: "Visitas", k: "sessions", n: 1 }]],
      ["aparelhos", "ac-aparelhos", [{ t: "Aparelho", k: "deviceCategory", f: function (v) { return APARELHOS[v] || v; } }, { t: "Visitantes", k: "activeUsers", n: 1 }, { t: "Visitas", k: "sessions", n: 1 }]],
      ["versoes", "ac-versoes", [{ t: "Versão", k: "versao", f: function (v) { return NOMES_IDIOMA[v] || v; } }, { t: "Páginas vistas", k: "screenPageViews", n: 1 }]],
      ["idiomas", "ac-idiomas", [{ t: "Idioma", k: "language" }, { t: "Visitantes", k: "activeUsers", n: 1 }, { t: "Visitas", k: "sessions", n: 1 }]],
    ];
    return Promise.all(lista.map(function (t) {
      return api(pedido(t[0], { limite: t[0] === "paginas" ? 50 : 25 })).then(function (j) { tabela($(t[1]), j.linhas, t[2], t[3]); })
        .catch(function (e) { $(t[1]).innerHTML = '<p class="meta">' + esc(e.message) + "</p>"; });
    }));
  }

  function carregarTempoReal() {
    return api({ tipo: "tempo_real" }).then(function (j) {
      var el = $("ac-tempo-real");
      el.innerHTML = '<p><b class="ac-num">' + fmt.format(j.ativos) + "</b> pessoa(s) no site nos últimos 30 minutos</p>" +
        '<div class="ac-duas"><div id="ac-rt-pag"></div><div id="ac-rt-pais"></div></div><div id="ac-rt-ev"></div>';
      tabela($("ac-rt-pag"), j.paginas, [{ t: "Página agora", k: "unifiedScreenName", f: function (v) { return (v || "").replace(/\s*[|·–-]\s*Aloha.*$/i, ""); } }, { t: "Pessoas", k: "activeUsers", n: 1 }], "Ninguém no momento.");
      tabela($("ac-rt-pais"), j.paises, [{ t: "País", k: "country" }, { t: "Pessoas", k: "activeUsers", n: 1 }], "Ninguém no momento.");
      tabela($("ac-rt-ev"), j.eventos, [{ t: "Chegadas por canal / parceiro (30 min)", k: "eventName" }, { t: "Vezes", k: "eventCount", n: 1 }], "Nenhuma chegada marcada por Telegram ou parceiro nos últimos 30 minutos.");
    });
  }

  function tudo() {
    var r = datasReais();
    $("ac-status").textContent = "Carregando " + r.inicio.split("-").reverse().join("/") + " a " + r.fim.split("-").reverse().join("/") + "...";
    $("ac-ini").value = r.inicio; $("ac-fim").value = r.fim;
    Promise.all([carregarResumo(), carregarSerie(), carregarHoras(), carregarTabelas()]).then(function () {
      $("ac-status").textContent = "Período: " + r.inicio.split("-").reverse().join("/") + " a " + r.fim.split("-").reverse().join("/") + " · atualizado às " + new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
    }).catch(function (e) { $("ac-status").textContent = "Não foi possível carregar: " + e.message; });
  }

  function marcar(grupo, botao) {
    document.querySelectorAll(grupo).forEach(function (b) { b.classList.toggle("ativo", b === botao); });
  }

  document.querySelectorAll("[data-p]").forEach(function (b) {
    b.addEventListener("click", function () {
      var p = b.getAttribute("data-p");
      if (p === "hoje") { estado.inicio = "today"; estado.fim = "today"; estado.agrupar = "hora"; }
      else if (p === "ontem") { estado.inicio = "yesterday"; estado.fim = "yesterday"; estado.agrupar = "hora"; }
      else { var n = Number(p); estado.inicio = (n - 1) + "daysAgo"; estado.fim = "today"; estado.agrupar = n > 120 ? "mes" : n > 45 ? "semana" : "dia"; }
      marcar("[data-p]", b); marcar("[data-g]", document.querySelector('[data-g="' + estado.agrupar + '"]'));
      tudo();
    });
  });
  document.querySelectorAll("[data-g]").forEach(function (b) {
    b.addEventListener("click", function () {
      estado.agrupar = b.getAttribute("data-g"); marcar("[data-g]", b);
      carregarSerie().catch(function (e) { $("ac-status").textContent = e.message; });
    });
  });
  $("ac-aplicar").addEventListener("click", function () {
    var a = $("ac-ini").value, f = $("ac-fim").value;
    if (!a || !f || a > f) { $("ac-status").textContent = "Escolha uma data de início anterior à data de fim."; return; }
    estado.inicio = a; estado.fim = f;
    var n = diasEntre(a, f); estado.agrupar = n <= 2 ? "hora" : n > 120 ? "mes" : n > 45 ? "semana" : "dia";
    marcar("[data-p]", null); marcar("[data-g]", document.querySelector('[data-g="' + estado.agrupar + '"]'));
    tudo();
  });
  var redim; window.addEventListener("resize", function () { clearTimeout(redim); redim = setTimeout(function () { carregarSerie(); carregarHoras(); }, 300); });

  tudo();
  carregarTempoReal().catch(function (e) { $("ac-tempo-real").innerHTML = '<p class="meta">' + esc(e.message) + "</p>"; });
  setInterval(function () { carregarTempoReal().catch(function () {}); }, 60000);
})();
