/* sr-anchor-jump.js — البند 27أ: هبوط فوري ونظيف على أقسام الجذر.
   المشكلة: مراسٍ صفرية الارتفاع على حافة الأقسام + منطقة ميتة داخل كل قسم
   (padding علوي + ظل داخلي أسود ~120px) فالهبوط الافتراضي يعرض فراغاً قبل
   المحتوى، والتمرير المتحرك العام يجعل القفزة بطيئة في صفحة ثقيلة.
   الحل: قياس أول كتلة محتوى مرئية داخل القسم الهدف وقت النقر (صفر أرقام
   سحرية — يبقى دقيقاً بعد أي تعديل مستقبلي) والهبوط عندها فوراً. */
(function () {
  "use strict";
  if (window.__SR_ANCHOR_JUMP__) return;
  window.__SR_ANCHOR_JUMP__ = true;

  var RESPIRE = 12; /* تنفس أسفل الهيدر الثابت */

  function headerHeight() {
    var h = document.querySelector("header");
    return h ? Math.max(h.offsetHeight, 0) : 90;
  }

  /* أول أبناء الحاوية بارتفاع حقيقي — يتجاوز padding القسم والظل الداخلي
     وعناصر المرسى صفرية الارتفاع. */
  function contentTop(section) {
    var root = section.querySelector(".container") || section;
    var kids = root.children;
    for (var i = 0; i < kids.length; i++) {
      var k = kids[i];
      if (k.classList && k.classList.contains("section-scroll-anchor")) continue;
      var r = k.getBoundingClientRect();
      if (r.height > 8 && r.width > 8) return r.top;
    }
    return section.getBoundingClientRect().top;
  }

  function jumpTo(hash) {
    if (!hash || hash === "#") return false;
    var id;
    try { id = decodeURIComponent(hash.slice(1)); } catch (e) { id = hash.slice(1); }
    if (!id) return false;
    var target = document.getElementById(id);
    if (!target) return false;
    /* مرسى صفرية؟ القسم الفعلي هو الشقيق التالي لها */
    var section = (target.classList && target.classList.contains("section-scroll-anchor"))
      ? (target.nextElementSibling || target.parentElement)
      : target;
    if (!section || !section.getBoundingClientRect) return false;
    var top = contentTop(section) + window.pageYOffset - headerHeight() - RESPIRE;
    window.scrollTo(0, Math.max(top, 0));
    if (window.history && history.pushState) history.pushState(null, "", hash);
    return true;
  }

  document.addEventListener("click", function (e) {
    if (e.defaultPrevented || e.button !== 0) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = (e.target && e.target.closest) ? e.target.closest('a[href^="#"]') : null;
    if (!a || a.target === "_blank") return;
    var href = a.getAttribute("href");
    if (!href || href === "#") return;
    if (jumpTo(href)) e.preventDefault();
  }, false);

  window.addEventListener("hashchange", function () {
    jumpTo(location.hash);
  }, false);

  /* الفتح البارد بالهاش (مثل /#service): بعد اكتمال التحميل واستقرار التخطيط */
  window.addEventListener("load", function () {
    if (!location.hash) return;
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { jumpTo(location.hash); });
    });
  }, false);
})();
