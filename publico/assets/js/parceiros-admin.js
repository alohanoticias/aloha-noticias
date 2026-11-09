/* Admin > Parceiros: monta o link do artigo com o nome do parceiro no final e lembra os parceiros já usados. */
(function () {
  var artigo = document.getElementById("p-artigo"), idioma = document.getElementById("p-idioma"), nome = document.getElementById("p-nome"),
      link = document.getElementById("p-link"), rede = document.getElementById("p-rede"), codigo = document.getElementById("p-codigo"),
      jogo = document.getElementById("p-jogo"), copiar = document.getElementById("p-copiar"), salvos = document.getElementById("p-salvos");
  if (!artigo || !nome) return;
  var CHAVE = "aloha-parceiros";
  function lista() { try { return JSON.parse(localStorage.getItem(CHAVE) || "[]"); } catch (e) { return []; } }
  function mostrarSalvos() {
    salvos.innerHTML = "";
    lista().forEach(function (n) { var o = document.createElement("option"); o.value = n; salvos.appendChild(o); });
  }
  // nome do parceiro como vai no link: "João Silva" -> "joao_silva" (sem acento, sem espaço, até 20 letras)
  function codigoDe(n) {
    return n.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
      .replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 20).replace(/_+$/, "");
  }
  // endereço do artigo em cada idioma (o mesmo arquivo que o site já publica)
  var urls = null, aviso = "";
  fetch("/push-urls.json", { cache: "no-store" }).then(function (r) { return r.json(); })
    .then(function (d) { urls = d; atualizar(); }, function () { urls = {}; atualizar(); });
  function enderecoBase() {
    var l = idioma.value, raiz = "https://alohanoticias.com/";
    aviso = "";
    if (!artigo.value) return l === "pt" ? raiz : raiz + l + "/";
    var u = urls && urls[artigo.value] && (urls[artigo.value][l] || urls[artigo.value].pt);
    if (urls && urls[artigo.value] && !urls[artigo.value][l]) aviso = " (este artigo ainda não tem versão nesse idioma: usei o português)";
    return u ? u.replace(/\.html$/, "") : "";
  }
  function atualizar() {
    var c = codigoDe(nome.value), j = jogo ? codigoDe(jogo.value) : "";
    if (artigo.value && !urls) { link.value = ""; codigo.textContent = "Carregando endereços…"; return; }
    if (!c) { link.value = ""; codigo.textContent = ""; return; }
    if (!rede.value) { link.value = ""; codigo.textContent = "Escolha onde o parceiro vai divulgar."; return; }
    var base = enderecoBase();
    if (!base) { link.value = ""; codigo.textContent = "Não achei o endereço deste artigo."; return; }
    // marca: parceiro (utm_source), rede (utm_medium), idioma (utm_content) e jogo/assunto (utm_term, opcional)
    link.value = base + "?utm_source=" + c + "&utm_medium=" + rede.value + "&utm_campaign=parceiro&utm_content=" + idioma.value + (j ? "&utm_term=" + j : "");
    codigo.textContent = "No Analytics: parceiro_" + c + "_" + rede.value + "_" + idioma.value + (j ? " (jogo: " + j + ")" : "") + aviso;
  }
  // Registro: um único link por parceiro e artigo. Guardado neste navegador (use Exportar/Importar para levar a outro aparelho).
  var REG = "aloha-parceiros-links";
  function registro() { try { return JSON.parse(localStorage.getItem(REG) || "{}"); } catch (e) { return {}; } }
  function gravarReg(r) { try { localStorage.setItem(REG, JSON.stringify(r)); } catch (e) {} }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  var aviso2 = document.getElementById("p-aviso"), painelReg = document.getElementById("p-registro");
  function tituloArtigo() { return artigo.options[artigo.selectedIndex].text; }
  function existente() {
    var c = codigoDe(nome.value), r = registro();
    return c && r[c] && r[c].links[artigo.value] ? r[c].links[artigo.value] : null;
  }
  function verExistente() {
    var e = existente();
    if (aviso2) aviso2.textContent = e ? "Este parceiro já tem um link para este artigo (" + e.rede + ", " + e.idioma + (e.jogo ? ", " + e.jogo : "") + "). Ao salvar, o link é atualizado: continua sendo um só." : "";
  }
  function salvar() {
    var c = codigoDe(nome.value);
    if (!c || !link.value) return false;
    var r = registro(), item = r[c] || (r[c] = { nome: nome.value.trim(), links: {} });
    var ja = !!item.links[artigo.value];
    item.links[artigo.value] = { artigo: tituloArtigo(), idioma: idioma.value, rede: rede.value, jogo: jogo ? codigoDe(jogo.value) : "", url: link.value, quando: new Date().toISOString().slice(0, 10) };
    gravarReg(r); desenhar();
    if (aviso2) aviso2.textContent = ja ? "Link deste artigo atualizado para este parceiro (continua sendo um só)." : "Link salvo na lista do parceiro.";
    return true;
  }
  function desenhar() {
    if (!painelReg) return;
    var r = registro(), nomes = Object.keys(r).sort();
    if (!nomes.length) { painelReg.innerHTML = '<p class="meta">Nenhum link salvo ainda. Gere um link e toque em Copiar link: ele entra aqui, organizado por parceiro.</p>'; return; }
    painelReg.innerHTML = nomes.map(function (c) {
      var p = r[c], ids = Object.keys(p.links);
      return '<details class="p-parc" open><summary><strong>' + esc(p.nome) + '</strong> <span class="meta">' + ids.length + (ids.length === 1 ? " link" : " links") + '</span></summary><ul class="p-parc-lista">' +
        ids.map(function (id) { var l = p.links[id];
          return '<li><div><b>' + esc(l.artigo) + '</b><br><small>' + esc(l.rede) + ' · ' + esc(l.idioma) + (l.jogo ? " · " + esc(l.jogo) : "") + ' · ' + esc(l.quando) + '</small><input readonly value="' + esc(l.url) + '"></div>' +
            '<button type="button" class="botao-sec" data-copiar="' + esc(c) + '|' + esc(id) + '">Copiar</button> <button type="button" class="botao-sec" data-tirar="' + esc(c) + '|' + esc(id) + '">Remover</button></li>'; }).join("") + '</ul></details>';
    }).join("");
  }
  function copiarTexto(t, b) {
    function ok() { var o = b.textContent; b.textContent = "Copiado!"; setTimeout(function () { b.textContent = o; }, 1500); }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(ok, function () {});
    else { var a = document.createElement("textarea"); a.value = t; document.body.appendChild(a); a.select(); document.execCommand("copy"); a.remove(); ok(); }
  }
  if (painelReg) painelReg.addEventListener("click", function (e) {
    var b = e.target.closest("button"); if (!b) return;
    var k = (b.getAttribute("data-copiar") || b.getAttribute("data-tirar") || "").split("|"), r = registro();
    if (!r[k[0]] || !r[k[0]].links[k[1]]) return;
    if (b.hasAttribute("data-copiar")) copiarTexto(r[k[0]].links[k[1]].url, b);
    else { delete r[k[0]].links[k[1]]; if (!Object.keys(r[k[0]].links).length) delete r[k[0]]; gravarReg(r); desenhar(); }
  });
  var exp = document.getElementById("p-exportar"), imp = document.getElementById("p-importar");
  if (exp) exp.addEventListener("click", function () {
    var a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([JSON.stringify(registro(), null, 1)], { type: "application/json" })); a.download = "links-parceiros-aloha.json"; a.click();
  });
  if (imp) imp.addEventListener("change", function () {
    var f = imp.files[0]; if (!f) return; var rd = new FileReader();
    rd.onload = function () { try { var n = JSON.parse(rd.result), r = registro(); Object.keys(n).forEach(function (c) { if (!r[c]) r[c] = n[c]; else { r[c].nome = n[c].nome || r[c].nome; Object.keys(n[c].links).forEach(function (id) { r[c].links[id] = n[c].links[id]; }); } }); gravarReg(r); desenhar(); } catch (e) { alert("Arquivo inválido."); } };
    rd.readAsText(f);
  });
  copiar.addEventListener("click", function () {
    if (!link.value) { (nome.value ? rede : nome).focus(); return; }
    var n = nome.value.trim(), l = lista();
    if (n && l.indexOf(n) < 0) { l.unshift(n); try { localStorage.setItem(CHAVE, JSON.stringify(l.slice(0, 50))); } catch (e) {} mostrarSalvos(); }
    salvar(); copiarTexto(link.value, copiar);
  });
  [artigo, nome].forEach(function (el) { el.addEventListener(el === nome ? "input" : "change", function () {
    var e = existente(); verExistente();
    if (e && el === artigo) { idioma.value = e.idioma; rede.value = e.rede; if (jogo) jogo.value = e.jogo; atualizar(); }
  }); });
  desenhar();
  artigo.addEventListener("change", atualizar);
  idioma.addEventListener("change", atualizar);
  nome.addEventListener("input", atualizar);
  rede.addEventListener("change", atualizar);
  if (jogo) { jogo.addEventListener("input", atualizar); jogo.addEventListener("change", atualizar); }
  mostrarSalvos();
})();
