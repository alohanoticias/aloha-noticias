/* Admin > Parceiros: monta o link do artigo com o nome do parceiro no final e lembra os parceiros já usados. */
(function () {
  var artigo = document.getElementById("p-artigo"), idioma = document.getElementById("p-idioma"), nome = document.getElementById("p-nome"),
      link = document.getElementById("p-link"), rede = document.getElementById("p-rede"), codigo = document.getElementById("p-codigo"),
      copiar = document.getElementById("p-copiar"), salvos = document.getElementById("p-salvos");
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
    var c = codigoDe(nome.value);
    if (artigo.value && !urls) { link.value = ""; codigo.textContent = "Carregando endereços…"; return; }
    if (!c) { link.value = ""; codigo.textContent = ""; return; }
    if (!rede.value) { link.value = ""; codigo.textContent = "Escolha onde o parceiro vai divulgar."; return; }
    var base = enderecoBase();
    if (!base) { link.value = ""; codigo.textContent = "Não achei o endereço deste artigo."; return; }
    // marca as três coisas: parceiro (utm_source), rede (utm_medium) e idioma (utm_content)
    link.value = base + "?utm_source=" + c + "&utm_medium=" + rede.value + "&utm_campaign=parceiro&utm_content=" + idioma.value;
    codigo.textContent = "No Analytics: parceiro_" + c + "_" + rede.value + "_" + idioma.value + aviso;
  }
  copiar.addEventListener("click", function () {
    if (!link.value) { (nome.value ? rede : nome).focus(); return; }
    var n = nome.value.trim(), l = lista();
    if (n && l.indexOf(n) < 0) { l.unshift(n); try { localStorage.setItem(CHAVE, JSON.stringify(l.slice(0, 50))); } catch (e) {} mostrarSalvos(); }
    function ok() { copiar.textContent = "Copiado!"; setTimeout(function () { copiar.textContent = "Copiar link"; }, 1500); }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(link.value).then(ok, function () { link.select(); document.execCommand("copy"); ok(); });
    else { link.select(); document.execCommand("copy"); ok(); }
  });
  artigo.addEventListener("change", atualizar);
  idioma.addEventListener("change", atualizar);
  nome.addEventListener("input", atualizar);
  rede.addEventListener("change", atualizar);
  mostrarSalvos();
})();
