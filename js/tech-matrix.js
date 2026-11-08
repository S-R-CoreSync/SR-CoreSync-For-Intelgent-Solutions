/**
 * S&R CoreSync Sovereign Tech Comparison Matrix Engine
 * (c) 2026 S&R CoreSync For Intelligent Solutions — The Netherlands
 */

const TechData = [
  {
    name: "CoreSync Starter • انطلاقة سحابية",
    size: "startup",
    price: 199,
    features: {
      "التحكم السحابي": true,
      "تحليل AI": false,
      "تعدد اللغات": true,
      "دعم 24/7": false,
      "تكامل ERP": "أساسي",
      "وقت الاستجابة": "0.4 ثانية",
    },
  },
  {
    name: "CoreSync Business • منظومة الشركات",
    size: "mid",
    price: 499,
    features: {
      "التحكم السحابي": true,
      "تحليل AI": true,
      "تعدد اللغات": true,
      "دعم 24/7": true,
      "تكامل ERP": "متوسط",
      "وقت الاستجابة": "0.15 ثانية",
    },
  },
  {
    name: "CoreSync Enterprise • باقة سيادية متكاملة",
    size: "enterprise",
    price: 1199,
    features: {
      "التحكم السحابي": true,
      "تحليل AI": true,
      "تعدد اللغات": true,
      "دعم 24/7": true,
      "تكامل ERP": "سيادي 100%",
      "وقت الاستجابة": "0.05 ثانية (Edge)",
    },
  },
];

function $(selector) {
  return document.querySelector(selector);
}
function $$(selector) {
  return Array.from(document.querySelectorAll(selector));
}

const TechMatrix = {
  data: TechData,
  filteredData: TechData.slice(),
  currentSort: { col: null, asc: true },
  diffOnly: false,

  init() {
    this.renderHeader();
    this.renderBody();
    this.updateCostSavings();
  },

  renderHeader() {
    const headerRow = $('#matrixHeader');
    if (!headerRow) return;
    headerRow.innerHTML = '';

    const thName = document.createElement('th');
    thName.innerHTML = 'المنظومة / الباقة <span>⇅</span>';
    thName.dataset.key = 'name';
    thName.addEventListener('click', () => this.sortBy('name'));
    headerRow.appendChild(thName);

    const featureKeys = Object.keys(this.data[0].features);
    featureKeys.forEach((key) => {
      const th = document.createElement('th');
      th.innerHTML = `${key} <span style="font-size:0.75rem;opacity:0.6;">⇅</span>`;
      th.dataset.key = key;
      th.addEventListener('click', () => this.sortBy(key));
      headerRow.appendChild(th);
    });

    const thPrice = document.createElement('th');
    thPrice.innerHTML = 'الاستثمار الشهري <span>⇅</span>';
    thPrice.dataset.key = 'price';
    thPrice.addEventListener('click', () => this.sortBy('price'));
    headerRow.appendChild(thPrice);
  },

  renderBody() {
    const tbody = $('#matrixBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    this.filteredData.forEach((item) => {
      const tr = document.createElement('tr');
      const tdName = document.createElement('td');
      tdName.className = 'feature-cell';
      tdName.textContent = item.name;
      tr.appendChild(tdName);

      const featureKeys = Object.keys(this.data[0].features);
      featureKeys.forEach((key) => {
        const td = document.createElement('td');
        const val = item.features[key];
        if (typeof val === 'boolean') {
          td.innerHTML = val
            ? '<span class="feature-included">✓ مشمول</span>'
            : '<span class="feature-excluded">✕ غير متاح</span>';
        } else {
          td.innerHTML = `<span style="font-weight:600; color:#f8fafc;">${val}</span>`;
        }
        tr.appendChild(td);
      });

      const tdPrice = document.createElement('td');
      tdPrice.style.direction = 'ltr';
      tdPrice.style.fontWeight = 'bold';
      tdPrice.style.color = 'var(--sr-gold-light)';
      tdPrice.textContent = `€ ${item.price} / شهر`;
      tr.appendChild(tdPrice);
      tbody.appendChild(tr);
    });

    this.highlightDifferences();
  },

  sortBy(key) {
    const asc = this.currentSort.col === key ? !this.currentSort.asc : true;
    this.currentSort = { col: key, asc };
    this.filteredData.sort((a, b) => {
      let aVal = a[key];
      let bVal = b[key];
      if (typeof aVal === 'object' && aVal !== null) aVal = JSON.stringify(aVal);
      if (typeof bVal === 'object' && bVal !== null) bVal = JSON.stringify(bVal);
      if (aVal < bVal) return asc ? -1 : 1;
      if (aVal > bVal) return asc ? 1 : -1;
      return 0;
    });
    this.renderBody();
  },

  filterBySize() {
    const filterEl = $('#sizeFilter');
    const filter = filterEl ? filterEl.value : 'all';
    if (filter === 'all') {
      this.filteredData = this.data.slice();
    } else {
      this.filteredData = this.data.filter((it) => it.size === filter);
    }
    this.currentSort = { col: null, asc: true };
    this.renderBody();
    this.updateCostSavings();
  },

  toggleDiff() {
    this.diffOnly = !this.diffOnly;
    const btn = $('#btnDiff');
    if (btn) btn.classList.toggle('active', this.diffOnly);
    this.highlightDifferences();
  },

  highlightDifferences() {
    if (this.filteredData.length === 0) return;
    const reference = this.filteredData[0];
    const tbodyRows = $$('#matrixBody tr');
    const featureKeys = Object.keys(this.data[0].features);

    tbodyRows.forEach((tr, rowIndex) => {
      const product = this.filteredData[rowIndex];
      const cells = tr.querySelectorAll('td');

      featureKeys.forEach((key, colIdx) => {
        const refVal = reference.features[key];
        const curVal = product.features[key];
        const cell = cells[colIdx + 1];
        if (!cell) return;

        if (refVal !== curVal) {
          cell.classList.add('diff-highlight');
        } else {
          cell.classList.remove('diff-highlight');
        }
      });
    });
  },

  updateCostSavings() {
    const costBox = $('#costSavings');
    if (!costBox) return;

    if (this.filteredData.length === 0) {
      costBox.textContent = '';
      return;
    }
    const maxPrice = Math.max(...this.filteredData.map((p) => p.price));
    const lines = this.filteredData.map((p) => {
      const annualSaved = (maxPrice - p.price) * 12;
      return `<span><strong>${p.name}:</strong> توفير سنوي مباشر بقيمة € ${annualSaved.toLocaleString('en-US')}</span>`;
    });
    costBox.innerHTML = lines.join('<br>');
  },

  openSocialCard() {
    if (typeof SRSocialCard === 'undefined') return;
    SRSocialCard.open({
      title: 'مصفوفة المقارنات الفنية والتقنية للأنظمة السحابية',
      subtitle: 'تحليل ومقارنة شاملة لحلول الذكاء الاصطناعي وباقات الأنظمة السيادية',
      badge: 'مقارنات الأنظمة ⚖️',
      url: window.location.href,
      metrics: [
        { label: 'باقة الشركات الكبرى Enterprise', val: '€ 1,199', sub: 'تكامل سيادي ERP 100%', color: '#c5a880' },
        { label: 'زمن الاستجابة السحابية', val: '0.05s', sub: 'أداء Edge فائق السرعة', color: '#10b981' },
        { label: 'التوفير السنوي المقدر ROI', val: '€ 14,800', sub: 'توفير تكاليف الصيانة', color: '#38bdf8' }
      ]
    });
  },

  openAdvisor() {
    const modal = $('#srAdvisorModal');
    if (modal) modal.classList.add('active');
  },

  closeAdvisor() {
    const modal = $('#srAdvisorModal');
    if (modal) modal.classList.remove('active');
  },

  selectAdvisorOption(el) {
    const type = el.dataset.type;
    const parent = el.parentElement;
    parent.querySelectorAll('.advisor-option-btn').forEach(btn => btn.classList.remove('selected'));
    el.classList.add('selected');
  },

  advisorRecommendation: null,

  calcRecommendation() {
    const selectedSize = document.querySelector('.advisor-option-btn.selected[data-type="size"]')?.dataset.val || 'startup';
    const selectedPriority = document.querySelector('.advisor-option-btn.selected[data-type="priority"]')?.dataset.val || 'cloud';

    let planKey = 'startup';
    let planName = 'CoreSync Starter • انطلاقة سحابية';
    let matchScore = 95;
    let reason = 'توصية مثالية للمشاريع الناشئة لبناء بنية سحابية متينة بأقل تكلفة مع دعم التوسع المستقبلي.';
    let savings = 'توفير سنوي مباشر يقدر بـ € 4,800';

    if (selectedSize === 'enterprise' || selectedPriority === 'erp') {
      planKey = 'enterprise';
      planName = 'CoreSync Enterprise • باقة سيادية متكاملة';
      matchScore = 99;
      reason = 'المؤسسات ذات المتطلبات المتقدمة والربط المالي الشامل تحتاج منظومة ERP متكاملة مع استجابة Edge فائقة ودعم 24/7.';
      savings = 'توفير سنوي استثماري يقدر بـ € 18,200';
    } else if (selectedSize === 'mid' || selectedPriority === 'ai') {
      planKey = 'mid';
      planName = 'CoreSync Business • منظومة الشركات';
      matchScore = 97;
      reason = 'توازن هندسي رائد يدمج محركات تحليل الذكاء الاصطناعي مع الأداء السحابي السريع والتكامل المؤسسي.';
      savings = 'توفير سنوي مباشر يقدر بـ € 9,600';
    }

    this.advisorRecommendation = { planKey, planName };

    const resultCard = $('#advisorResultCard');
    const recTitle = $('#advisorRecTitle');
    const recScore = $('#advisorRecScore');
    const recReason = $('#advisorRecReason');
    const recSavings = $('#advisorRecSavings');

    if (recTitle) recTitle.textContent = planName;
    if (recScore) recScore.textContent = `نسبة المطابقة: ${matchScore}%`;
    if (recReason) recReason.textContent = reason;
    if (recSavings) recSavings.textContent = savings;
    if (resultCard) resultCard.classList.add('active');
  },

  applyAdvisorPlan() {
    if (!this.advisorRecommendation) return;
    const filterEl = $('#sizeFilter');
    if (filterEl) {
      filterEl.value = this.advisorRecommendation.planKey;
      this.filterBySize();
    }
    this.closeAdvisor();
    const table = $('#matrixTable');
    if (table) {
      table.scrollIntoView({ behavior: 'smooth', block: 'center' });
      table.style.boxShadow = '0 0 35px rgba(16, 185, 129, 0.5)';
      setTimeout(() => { table.style.boxShadow = ''; }, 2500);
    }
  },

  exportPDF() {
    const printWin = window.open('', '_blank');
    if (!printWin) {
      alert('يرجى السماح بالنوافذ المنبثقة لطباعة مصفوفة المقارنة');
      return;
    }
    const printHtml = `<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>مصفوفة المقارنات الفنية والتقنية • S&R CoreSync</title>
  <style>
    body { font-family: 'Segoe UI', Tahoma, Arial, sans-serif; direction: rtl; background: #fff; color: #0f172a; padding: 40px; margin: 0; }
    .header { border-bottom: 2px solid #c5a880; padding-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
    .title { font-size: 22px; font-weight: bold; color: #0b192c; }
    table { width: 100%; border-collapse: collapse; margin: 25px 0; }
    th, td { border: 1px solid #cbd5e1; padding: 12px; text-align: right; }
    th { background: #0b192c; color: #fff; font-weight: bold; }
    .footer { margin-top: 40px; border-top: 1px solid #e2e8f0; padding-top: 15px; font-size: 11px; color: #64748b; text-align: center; }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <div class="title">S&R CoreSync For Intelligent Solutions</div>
      <div>مصفوفة المقارنات الفنية والتقنية للأنظمة والباقات</div>
    </div>
    <div style="font-size:12px; color:#64748b;">${new Date().toLocaleDateString('ar-EG', { dateStyle: 'full' })}</div>
  </div>
  ${document.getElementById('matrixTable').outerHTML}
  <div style="background:#f8fafc; border:1px solid #cbd5e1; padding:15px; border-radius:6px; margin-top:20px;">
    <strong>تقدير الجدوى والتوفير المالي:</strong>
    <div style="margin-top:8px;">${document.getElementById('costSavings').innerHTML}</div>
  </div>
  <div class="footer">
    تم تصدير هذا التقرير رسمياً بواسطة بوابة مصفوفة المقارنات لشركة S&R CoreSync For Intelligent Solutions — هولندا
  </div>
</body>
</html>`;

    printWin.document.open();
    printWin.document.write(printHtml);
    printWin.document.close();
    setTimeout(() => {
      printWin.print();
    }, 400);
  },
};

document.addEventListener('DOMContentLoaded', () => {
  TechMatrix.init();
});
