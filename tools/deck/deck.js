/* Guia Ourofino Pet · motor de slides
   paisagem (computador/tablet deitado): palco 1600x900 escalado, um slide por vez
   retrato (celular): slides em tela cheia, rolagem com encaixe vertical */
(function () {
  var d = document, de = d.documentElement, b = d.body;
  function $$(s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); }
  function guarda(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  de.classList.add("js");

  var slides = $$(".slide"), total = slides.length, atual = 0;
  var palco = d.querySelector(".palco"), rolo = d.querySelector(".rolo");
  var cont = d.querySelector("[data-cont]"), capTxt = d.querySelector("[data-cap-txt]"), barra = d.querySelector(".prog i");
  var W = 1600, H = 900;
  slides.forEach(function (s, i) { var p = s.querySelector("[data-pagina]"); if (p) p.textContent = i + 1; });

  function modo() {
    var r = innerWidth / innerHeight, pais = r >= 1.05 && innerWidth >= 760;
    de.classList.toggle("paisagem", pais); de.classList.toggle("retrato", !pais);
    if (pais) {
      var top = 0, livreH = innerHeight - 64, esc = Math.min(innerWidth / W, livreH / H);
      de.style.setProperty("--esc", esc.toFixed(4));
    }
    return pais;
  }

  function marcar(i, origem) {
    i = Math.max(0, Math.min(total - 1, i));
    var ant = slides[atual]; atual = i;
    slides.forEach(function (s, k) { s.classList.toggle("ativo", k === i); s.classList.toggle("antes", k < i); });
    var s = slides[i];
    if (ant !== s) { s.classList.remove("viu"); void s.offsetWidth; }
    s.classList.add("viu");
    cont.textContent = (i + 1) + " / " + total;
    capTxt.textContent = s.getAttribute("data-cap-nome") || "";
    barra.style.width = ((i + 1) / total * 100) + "%";
    $$(".indice a").forEach(function (a) { a.classList.toggle("atual", a.getAttribute("data-cap") === s.getAttribute("data-cap")); });
    if (origem !== "hash") history.replaceState(null, "", "#" + (s.id || "s" + (i + 1)));
    guarda("ourofino-v5-slide", String(i));
  }

  function ir(i) {
    if (de.classList.contains("paisagem")) marcar(i);
    else slides[Math.max(0, Math.min(total - 1, i))].scrollIntoView({ behavior: "smooth", block: "start" });
  }
  function prox() { ir(atual + 1); } function ant() { ir(atual - 1); }
  d.querySelector("[data-prox]").addEventListener("click", prox);
  d.querySelector("[data-ant]").addEventListener("click", ant);

  addEventListener("keydown", function (e) {
    if (e.target.closest("input, textarea, [contenteditable]")) return;
    if (!de.classList.contains("paisagem")) return;
    if (["ArrowRight", "PageDown", " "].indexOf(e.key) > -1) { e.preventDefault(); prox(); }
    else if (["ArrowLeft", "PageUp"].indexOf(e.key) > -1) { e.preventDefault(); ant(); }
    else if (e.key === "Home") { e.preventDefault(); ir(0); }
    else if (e.key === "End") { e.preventDefault(); ir(total - 1); }
  });

  /* deslize no palco (tablet deitado) */
  var x0 = null;
  palco.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  palco.addEventListener("touchend", function (e) {
    if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 50) dx < 0 ? prox() : ant();
  });

  /* retrato: o slide visível vira o ativo */
  if ("IntersectionObserver" in window) {
    var ob = new IntersectionObserver(function (es) {
      if (de.classList.contains("paisagem")) return;
      es.forEach(function (e) { if (e.isIntersecting) marcar(slides.indexOf(e.target)); });
    }, { root: null, rootMargin: "-45% 0px -50% 0px", threshold: 0 });
    slides.forEach(function (s) { ob.observe(s); });
  }

  function doHash() {
    var h = location.hash.slice(1); if (!h) return false;
    var el = d.getElementById(h); var s = el && (el.classList.contains("slide") ? el : el.closest(".slide"));
    if (!s) return false; var i = slides.indexOf(s);
    if (de.classList.contains("paisagem")) marcar(i, "hash"); else s.scrollIntoView();
    return true;
  }
  addEventListener("hashchange", doHash);
  addEventListener("resize", function () { var era = de.classList.contains("paisagem"); var e = modo(); if (era !== e) ir(atual); });
  /* texto que não cabe no slide diminui até caber (só no palco) */
  function ajusta() {
    var pais = de.classList.contains("paisagem");
    $$("[data-fit]").forEach(function (e) {
      var f = 1; e.style.setProperty("--fit", "1");
      if (!pais) return;
      for (var i = 0; i < 14 && e.scrollHeight > e.clientHeight + 2; i++) { f -= 0.03; e.style.setProperty("--fit", f.toFixed(2)); }
    });
  }
  modo(); ajusta();
  if (d.fonts && d.fonts.ready) d.fonts.ready.then(ajusta);
  addEventListener("beforeprint", function () { de.classList.add("paisagem"); de.classList.remove("retrato"); ajusta(); });
  if (!doHash()) marcar(0);

  /* links internos (sumário, referências "capítulo N") */
  d.addEventListener("click", function (e) {
    var a = e.target.closest('a[href^="#"]'); if (!a) return;
    var el = d.getElementById(a.getAttribute("href").slice(1)); if (!el) return;
    e.preventDefault(); fecha(); var s = el.classList.contains("slide") ? el : el.closest(".slide"); ir(slides.indexOf(s));
  });

  /* índice */
  var ind = d.getElementById("indice");
  function abre() { ind.hidden = false; }
  function fecha() { if (ind) ind.hidden = true; }
  $$("[data-abre-indice]").forEach(function (x) { x.addEventListener("click", abre); });
  $$("[data-fecha]").forEach(function (x) { x.addEventListener("click", fecha); });
  addEventListener("keydown", function (e) { if (e.key === "Escape") fecha(); });

  /* revisão */
  var rev = d.querySelector("[data-rev]");
  function setRev(on) { b.classList.toggle("revisao", on); rev.setAttribute("aria-pressed", on ? "true" : "false"); guarda("ourofino-v5-rev", on ? "1" : "0"); }
  rev.addEventListener("click", function () { setRev(!b.classList.contains("revisao")); });
  if (/[?&]revisao=1/.test(location.search) || guarda("ourofino-v5-rev") === "1") setRev(true);

  /* PDF */
  $$("[data-pdf]").forEach(function (x) { x.addEventListener("click", function () { $$("details").forEach(function (dd) { dd.open = true; }); window.print(); }); });

  /* comparador antes e depois */
  $$("[data-comp]").forEach(function (f) {
    var q = f.querySelector(".comp-quadro"), r = f.querySelector(".comp-range");
    function set() { q.style.setProperty("--p", r.value + "%"); }
    r.addEventListener("input", set); set();
  });

  /* marcações nas fotos */
  $$(".rot-btn").forEach(function (bt) {
    bt.addEventListener("click", function () {
      var r = bt.parentNode.querySelector(".rot"), off = r.classList.toggle("off");
      bt.textContent = off ? "Mostrar marcações" : "Ocultar marcações";
    });
  });

  /* testes */
  var placar = d.querySelector(".placar");
  function atualizaPlacar() {
    if (!placar) return;
    var ts = $$("[data-final] [data-teste]"), resp = ts.filter(function (t) { return t.classList.contains("feito"); }),
        certas = resp.filter(function (t) { return t.classList.contains("acertou"); });
    placar.querySelector("b").textContent = certas.length;
    placar.querySelector(".pl-txt").textContent = (certas.length === 1 ? "certa" : "certas") + " de " + ts.length;
  }
  $$("[data-teste]").forEach(function (t) {
    var ops = $$(".op", t), exp = t.querySelector(".teste-exp"), res = t.querySelector(".teste-res");
    ops.forEach(function (op) {
      op.addEventListener("click", function () {
        var ok = op.getAttribute("data-ok") === "1";
        ops.forEach(function (o) {
          o.disabled = true;
          if (o.getAttribute("data-ok") === "1") o.classList.add("certa");
          else if (o === op) o.classList.add("errada"); else o.classList.add("apagada");
        });
        res.textContent = ok ? "Isso mesmo." : "Não é essa.";
        exp.hidden = false; t.classList.add("feito"); if (ok) t.classList.add("acertou"); atualizaPlacar();
      });
    });
  });
  atualizaPlacar();

  /* teste final: uma pergunta por vez */
  $$("[data-quiz]").forEach(function (q) {
    var itens = $$(".qz-item", q), dots = $$(".qz-dots i", q), n = q.querySelector("[data-qz-n]"),
        prox = q.querySelector("[data-qz-prox]"), fim = q.querySelector(".qz-fim"), lista = q.querySelector(".qz-lista"), i = 0;
    function mostra(k) {
      i = k; itens.forEach(function (it, j) { it.classList.toggle("atual", j === k); });
      dots.forEach(function (dd, j) { dd.classList.toggle("atual", j === k); });
      if (n) n.textContent = k + 1; prox.hidden = !itens[k].querySelector("[data-teste]").classList.contains("feito");
    }
    itens.forEach(function (it, j) {
      $$(".op", it).forEach(function (op) { op.addEventListener("click", function () {
        setTimeout(function () {
          var t = it.querySelector("[data-teste]"); dots[j].classList.add("feito"); if (t.classList.contains("acertou")) dots[j].classList.add("ok");
          prox.hidden = false; prox.firstChild.textContent = j === itens.length - 1 ? "Ver meu resultado" : "Próxima pergunta";
        }, 0);
      }); });
    });
    prox.addEventListener("click", function () {
      if (i < itens.length - 1) { mostra(i + 1); return; }
      var certas = itens.filter(function (it) { return it.querySelector(".acertou"); }).length;
      q.querySelector("[data-qz-certas]").textContent = certas;
      dots.forEach(function (dd) { dd.classList.remove("atual"); });
      lista.hidden = true; prox.hidden = true; fim.hidden = false; q.classList.add("terminou");
    });
    q.querySelector("[data-qz-refaz]").addEventListener("click", function () {
      itens.forEach(function (it) {
        var t = it.querySelector("[data-teste]"); t.classList.remove("feito", "acertou");
        $$(".op", it).forEach(function (o) { o.disabled = false; o.classList.remove("certa", "errada", "apagada"); });
        var e = it.querySelector(".teste-exp"); if (e) e.hidden = true;
      });
      dots.forEach(function (dd) { dd.classList.remove("feito", "ok"); });
      lista.hidden = false; fim.hidden = true; q.classList.remove("terminou"); prox.firstChild.textContent = "Próxima pergunta"; mostra(0);
    });
    mostra(0);
  });

  /* checklist */
  var CK = "ourofino-v5-checklist", est = {};
  try { est = JSON.parse(guarda(CK) || "{}") || {}; } catch (e) { est = {}; }
  var chks = $$(".chk input");
  function contaChk() {
    var n = chks.filter(function (c) { return c.checked; }).length;
    $$("[data-chk-txt]").forEach(function (t) { t.textContent = n + " de " + chks.length; });
    $$("[data-chk-barra]").forEach(function (t) { t.style.width = (chks.length ? n / chks.length * 100 : 0) + "%"; });
  }
  chks.forEach(function (c) {
    c.checked = !!est[c.getAttribute("data-k")];
    c.addEventListener("change", function () { est[c.getAttribute("data-k")] = c.checked; guarda(CK, JSON.stringify(est)); contaChk(); });
  });
  $$("[data-limpar]").forEach(function (x) { x.addEventListener("click", function () { est = {}; guarda(CK, "{}"); chks.forEach(function (c) { c.checked = false; }); contaChk(); }); });
  contaChk();

  /* glossário */
  var busca = d.querySelector(".g-busca input");
  if (busca) {
    var itens = $$(".g-item"), vazio = d.querySelector(".g-vazio");
    var norm = function (s) { return s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); };
    busca.addEventListener("input", function () {
      var q = norm(busca.value.trim()), vis = 0;
      itens.forEach(function (it) { var m = !q || norm(it.textContent).indexOf(q) > -1; it.hidden = !m; if (m) vis++; });
      if (vazio) vazio.hidden = vis > 0;
    });
  }
})();
