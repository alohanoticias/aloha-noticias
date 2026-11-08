/* Admin > Parceiros: monta o link do artigo com o nome do parceiro no final e lembra os parceiros já usados. */
(function () {
  var artigo = document.getElementById("p-artigo"), nome = document.getElementById("p-nome"),
      link = document.getElementById("p-link"), codigo = document.getElementById("p-codigo"),
      copiar = document.getElementById("p-copiar"), salvos = document.getElementById("p-salvos");
  if (!artigo || !nome) return;
  var CHAVE = "aloha-parceiros";
  function lista() { try { return JSON.parse(localStorage.getItem(CHAVE) || "[]"); } catch (e) { return []; } }
  function mostrarSalvos() {
    salvos.innerHTML = "";
    lista().forEach(function (n) { var o = document.createElement("option"); o.value = n; salvos.appendChild(o); });
  }
  // "Canal do João" -> "canal_do_joao" (sem acento, sem espaço, até 28 letras)
  function codigoDe(n) {
    return n.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
      .replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 28);
  }
  function atualizar() {
    var c = codigoDe(nome.value);
    if (!c) { link.value = ""; codigo.textContent = ""; return; }
    link.value = artigo.value + "?utm_source=" + c + "&utm_medium=parceiro&utm_campaign=parceiro_" + c;
    codigo.textContent = "No Analytics: parceiro_" + c;
  }
  copiar.addEventListener("click", function () {
    if (!link.value) { nome.focus(); return; }
    var n = nome.value.trim(), l = lista();
    if (n && l.indexOf(n) < 0) { l.unshift(n); try { localStorage.setItem(CHAVE, JSON.stringify(l.slice(0, 50))); } catch (e) {} mostrarSalvos(); }
    function ok() { copiar.textContent = "Copiado!"; setTimeout(function () { copiar.textContent = "Copiar link"; }, 1500); }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(link.value).then(ok, function () { link.select(); document.execCommand("copy"); ok(); });
    else { link.select(); document.execCommand("copy"); ok(); }
  });
  artigo.addEventListener("change", atualizar);
  nome.addEventListener("input", atualizar);
  mostrarSalvos();
})();
