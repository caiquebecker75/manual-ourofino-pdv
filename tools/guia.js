(function () {
  var d = document, de = d.documentElement, b = d.body;
  de.classList.add("js");
  function $$(s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); }
  function guarda(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }

  /* topo, progresso e capítulo atual */
  var topo = d.querySelector(".topo"), prog = d.querySelector(".topo-prog i"), capTxt = d.querySelector(".topo-cap");
  function rolar() {
    var y = window.scrollY, h = de.scrollHeight - innerHeight;
    topo.classList.toggle("vis", y > innerHeight * 0.6);
    prog.style.width = (h > 0 ? (y / h) * 100 : 0) + "%";
  }
  addEventListener("scroll", rolar, { passive: true }); rolar();
  var caps = $$(".cap"), linksGav = $$(".gav-painel li a");
  if ("IntersectionObserver" in window) {
    var obCap = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var id = e.target.id, n = parseInt(id.slice(3), 10);
        capTxt.textContent = (n < 97 ? "Cap. " + id.slice(3) + " · " : "") + e.target.getAttribute("data-titulo");
        linksGav.forEach(function (a) { a.classList.toggle("atual", a.getAttribute("href") === "#" + id); });
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    caps.forEach(function (c) { obCap.observe(c); });
  }

  /* gaveta de capítulos */
  var gav = d.getElementById("gaveta");
  function abre() { gav.hidden = false; b.style.overflow = "hidden"; var a = gav.querySelector("a.atual") || gav.querySelector("a"); if (a) a.focus({ preventScroll: true }); }
  function fecha() { gav.hidden = true; b.style.overflow = ""; }
  $$("[data-abre]").forEach(function (x) { x.addEventListener("click", abre); });
  $$("[data-fecha]", gav).forEach(function (x) { x.addEventListener("click", fecha); });
  $$("a", gav).forEach(function (x) { x.addEventListener("click", fecha); });
  addEventListener("keydown", function (e) { if (e.key === "Escape" && !gav.hidden) fecha(); });

  /* modo revisão */
  var rev = d.querySelector("[data-rev]");
  function setRev(on) { b.classList.toggle("revisao", on); rev.setAttribute("aria-pressed", on ? "true" : "false"); guarda("ourofino-guia-revisao", on ? "1" : "0"); }
  rev.addEventListener("click", function () { setRev(!b.classList.contains("revisao")); });
  if (/[?&]revisao=1/.test(location.search) || guarda("ourofino-guia-revisao") === "1") setRev(true);

  /* PDF */
  var abertos = [];
  function antesImprimir() { abertos = $$("details.saiba:not([open])"); abertos.forEach(function (x) { x.open = true; }); $$("img[loading=lazy]").forEach(function (i) { i.loading = "eager"; }); }
  function depoisImprimir() { abertos.forEach(function (x) { x.open = false; }); }
  addEventListener("beforeprint", antesImprimir); addEventListener("afterprint", depoisImprimir);
  $$("[data-pdf]").forEach(function (x) { x.addEventListener("click", function () { antesImprimir(); setTimeout(function () { window.print(); }, 350); }); });

  /* marcações nas fotos */
  $$(".rot-btn").forEach(function (bt) {
    bt.addEventListener("click", function () {
      var r = bt.parentNode.querySelector(".rot"), off = r.classList.toggle("off");
      bt.textContent = off ? "Mostrar marcações" : "Ocultar marcações"; bt.setAttribute("aria-pressed", off ? "false" : "true");
    });
  });

  /* comparador antes e depois */
  $$("[data-comp]").forEach(function (f) {
    var q = f.querySelector(".comp-quadro"), r = f.querySelector(".comp-range");
    function set() { q.style.setProperty("--p", r.value + "%"); }
    r.addEventListener("input", set); set();
  });

  /* testes */
  var placar = d.querySelector(".placar");
  function atualizaPlacar() {
    if (!placar) return;
    var ts = $$(".final [data-teste]"), resp = ts.filter(function (t) { return t.classList.contains("feito"); }),
        certas = resp.filter(function (t) { return t.classList.contains("acertou"); });
    placar.querySelector("b").textContent = certas.length;
    placar.querySelector(".pl-txt").textContent = (certas.length === 1 ? "certa" : "certas") + " de " + ts.length + " · " + resp.length + " de " + ts.length + " respondidas";
  }
  $$("[data-teste]").forEach(function (t) {
    var ops = $$(".op", t), exp = t.querySelector(".teste-exp"), res = t.querySelector(".teste-res");
    ops.forEach(function (op) {
      op.addEventListener("click", function () {
        var ok = op.getAttribute("data-ok") === "1";
        ops.forEach(function (o) {
          o.disabled = true;
          if (o.getAttribute("data-ok") === "1") o.classList.add("certa");
          else if (o === op) o.classList.add("errada");
          else o.classList.add("apagada");
        });
        res.textContent = ok ? "Isso mesmo." : "Não é essa.";
        exp.hidden = false; t.classList.add("feito"); if (ok) t.classList.add("acertou");
        atualizaPlacar();
      });
    });
  });
  atualizaPlacar();

  /* checklist com memória no aparelho */
  var CK = "ourofino-checklist-v2", est = {};
  try { est = JSON.parse(guarda(CK) || "{}") || {}; } catch (e) { est = {}; }
  var chks = $$(".chk input"), barra = d.querySelector(".chk-prog i"), txt = d.querySelector(".chk-txt");
  function contaChk() {
    var n = chks.filter(function (c) { return c.checked; }).length;
    if (barra) barra.style.width = (chks.length ? n / chks.length * 100 : 0) + "%";
    if (txt) txt.textContent = n + " de " + chks.length + " itens";
  }
  chks.forEach(function (c) {
    c.checked = !!est[c.getAttribute("data-k")];
    c.addEventListener("change", function () { est[c.getAttribute("data-k")] = c.checked; guarda(CK, JSON.stringify(est)); contaChk(); });
  });
  var limpar = d.querySelector("[data-limpar]");
  if (limpar) limpar.addEventListener("click", function () { est = {}; guarda(CK, "{}"); chks.forEach(function (c) { c.checked = false; }); contaChk(); });
  contaChk();

  /* glossário */
  var busca = d.querySelector(".g-busca input");
  if (busca) {
    var itens = $$(".g-item"), letras = $$(".g-letra"), vazio = d.querySelector(".g-vazio");
    var norm = function (s) { return s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); };
    busca.addEventListener("input", function () {
      var q = norm(busca.value.trim()), vis = 0;
      itens.forEach(function (it) { var m = !q || norm(it.textContent).indexOf(q) > -1; it.classList.toggle("some", !m); if (m) vis++; });
      letras.forEach(function (l) {
        var n = l.nextElementSibling, tem = false;
        while (n && !n.classList.contains("g-letra")) { if (!n.classList.contains("some")) tem = true; n = n.nextElementSibling; }
        l.classList.toggle("some", !tem);
      });
      vazio.hidden = vis > 0;
    });
  }

  /* revelação suave */
  if ("IntersectionObserver" in window && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var alvos = $$(".cap-corpo > .fig, .cap-corpo > .cards, .cap-corpo > .erro, .cap-corpo > .ce, .cap-corpo > .cbv, .cap-corpo > .ficha, .cap-corpo > .teste, .cap-corpo > .passos, .ab-txt");
    var obR = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("on"); obR.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    alvos.forEach(function (a) { a.classList.add("rv"); obR.observe(a); });
  }
})();
