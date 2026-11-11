/* Formulário de contato: envia para /api/contato (Worker) sem sair da página */
(function () {
  var f = document.getElementById("form-contato");
  if (!f) return;
  var st = document.getElementById("fc-status");
  f.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!f.reportValidity()) return;
    var bt = f.querySelector("button[type=submit]");
    var dados = {};
    new FormData(f).forEach(function (v, k) { dados[k] = String(v); });
    dados.pagina = location.pathname;
    bt.disabled = true;
    st.className = "fc-status";
    st.textContent = f.dataset.enviando;
    fetch("/api/contato", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(dados) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok && j.ok, j: j }; }); })
      .then(function (r) {
        if (r.ok) { f.reset(); st.className = "fc-status ok"; st.textContent = f.dataset.ok; }
        else { st.className = "fc-status erro"; st.textContent = f.dataset.erro; }
      })
      .catch(function () { st.className = "fc-status erro"; st.textContent = f.dataset.erro; })
      .then(function () { bt.disabled = false; });
  });
})();
