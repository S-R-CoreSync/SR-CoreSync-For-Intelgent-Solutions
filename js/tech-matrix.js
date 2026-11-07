// ---------------------------------------------------------------
// tech-matrix.js – Interactive Tech Comparison Matrix
// ---------------------------------------------------------------
// This script builds a dynamic comparison table, adds filtering, sorting,
// difference highlighting, a simple cost‑savings calculator and a PDF export.
// It is pure vanilla JavaScript – no external libs – to keep the project
// self‑contained and compatible with the existing build pipeline.

/* -----------------------------------------------------------------
   Sample data – in a real project this would be fetched from a JSON file
   or an API. Each entry represents a product / solution.
   Fields:
   • name        – Display name
   • size        – "startup" | "mid" | "enterprise"
   • price       – Monthly price (USD) – used for the savings calculator
   • features    – Object where key = feature name, value = true/false or a value
   ----------------------------------------------------------------- */
const TechData = [
  {
    name: "CoreSync Starter",
    size: "startup",
    price: 199,
    features: {
      "التحكم السحابي": true,
      "تحليل AI": false,
      "تعدد اللغات": true,
      "دعم 24/7": false,
      "تكامل ERP": "محدود",
      "وقت الاستجابة": "5 ث",
    },
  },
  {
    name: "CoreSync Business",
    size: "mid",
    price: 499,
    features: {
      "التحكم السحابي": true,
      "تحليل AI": true,
      "تعدد اللغات": true,
      "دعم 24/7": true,
      "تكامل ERP": "متوسط",
      "وقت الاستجابة": "2 ث",
    },
  },
  {
    name: "CoreSync Enterprise",
    size: "enterprise",
    price: 1199,
    features: {
      "التحكم السحابي": true,
      "تحليل AI": true,
      "تعدد اللغات": true,
      "دعم 24/7": true,
      "تكامل ERP": "متكامل",
      "وقت الاستجابة": "1 ث",
    },
  },
];

// -----------------------------------------------------------------
// Utility helpers
// -----------------------------------------------------------------
function $(selector) {
  return document.querySelector(selector);
}
function $$(selector) {
  return Array.from(document.querySelectorAll(selector));
}

// -----------------------------------------------------------------
// Core object exposed globally as `TechMatrix`
// -----------------------------------------------------------------
const TechMatrix = {
  data: TechData,
  filteredData: TechData.slice(),
  currentSort: { col: null, asc: true },

  init() {
    this.renderHeader();
    this.renderBody();
    this.updateCostSavings();
  },

  // -----------------------------------------------------------------
  // Render table header – each feature becomes a sortable column
  // -----------------------------------------------------------------
  renderHeader() {
    const headerRow = $('#matrixHeader');
    headerRow.innerHTML = '';
    // First column for product names
    const thName = document.createElement('th');
    thName.textContent = 'المنتج / النظام';
    thName.dataset.key = 'name';
    thName.addEventListener('click', () => this.sortBy('name'));
    headerRow.appendChild(thName);

    // Collect all distinct feature keys (order preserved by first product)
    const featureKeys = Object.keys(this.data[0].features);
    featureKeys.forEach((key) => {
      const th = document.createElement('th');
      th.textContent = key;
      th.dataset.key = key;
      th.addEventListener('click', () => this.sortBy(key));
      headerRow.appendChild(th);
    });
    // Price column (always last)
    const thPrice = document.createElement('th');
    thPrice.textContent = 'السعر (USD)';
    thPrice.dataset.key = 'price';
    thPrice.addEventListener('click', () => this.sortBy('price'));
    headerRow.appendChild(thPrice);
  },

  // -----------------------------------------------------------------
  // Render table body based on `filteredData`
  // -----------------------------------------------------------------
  renderBody() {
    const tbody = $('#matrixBody');
    tbody.innerHTML = '';
    this.filteredData.forEach((item) => {
      const tr = document.createElement('tr');
      // Product name cell
      const tdName = document.createElement('td');
      tdName.textContent = item.name;
      tr.appendChild(tdName);
      // Feature cells
      const featureKeys = Object.keys(this.data[0].features);
      featureKeys.forEach((key) => {
        const td = document.createElement('td');
        const val = item.features[key];
        if (typeof val === 'boolean') {
          td.textContent = val ? '✔️' : '✖️';
        } else {
          td.textContent = val;
        }
        tr.appendChild(td);
      });
      // Price cell
      const tdPrice = document.createElement('td');
      tdPrice.textContent = item.price.toLocaleString('ar-EG') + ' $';
      tr.appendChild(tdPrice);
      tbody.appendChild(tr);
    });
    // After drawing body, apply difference highlighting
    this.highlightDifferences();
  },

  // -----------------------------------------------------------------
  // Sort by a column (feature key or name / price)
  // -----------------------------------------------------------------
  sortBy(key) {
    const asc = this.currentSort.col === key ? !this.currentSort.asc : true;
    this.currentSort = { col: key, asc };
    this.filteredData.sort((a, b) => {
      let aVal = a[key];
      let bVal = b[key];
      // For features we compare boolean/value representations
      if (typeof aVal === 'object' && aVal !== null) aVal = JSON.stringify(aVal);
      if (typeof bVal === 'object' && bVal !== null) bVal = JSON.stringify(bVal);
      if (aVal < bVal) return asc ? -1 : 1;
      if (aVal > bVal) return asc ? 1 : -1;
      return 0;
    });
    this.renderBody();
  },

  // -----------------------------------------------------------------
  // Filter by company size (startup / mid / enterprise / all)
  // -----------------------------------------------------------------
  filterBySize() {
    const filter = $('#sizeFilter').value;
    if (filter === 'all') {
      this.filteredData = this.data.slice();
    } else {
      this.filteredData = this.data.filter((it) => it.size === filter);
    }
    // Reset sorting after filter
    this.currentSort = { col: null, asc: true };
    this.renderBody();
    this.updateCostSavings();
  },

  // -----------------------------------------------------------------
  // Highlight cells that differ from the cheapest product in the current view
  // -----------------------------------------------------------------
  highlightDifferences() {
    if (this.filteredData.length === 0) return;
    // Find the reference (cheapest) product for price comparison
    const reference = this.filteredData.reduce((prev, cur) => (cur.price < prev.price ? cur : prev), this.filteredData[0]);
    const tbodyRows = $$('#matrixBody tr');
    const featureKeys = Object.keys(this.data[0].features);
    tbodyRows.forEach((tr, rowIndex) => {
      const product = this.filteredData[rowIndex];
      // Skip the reference row – no highlight needed
      if (product === reference) return;
      // Iterate over feature cells (skip first name cell)
      const cells = tr.querySelectorAll('td');
      featureKeys.forEach((key, colIdx) => {
        const refVal = reference.features[key];
        const curVal = product.features[key];
        if (refVal !== curVal) {
          // Highlight the cell
          cells[colIdx + 1].classList.add('diff-highlight'); // +1 because first cell is name
        }
      });
    });
  },

  // -----------------------------------------------------------------
  // Simple cost‑savings calculator – shows how much cheaper each option is
  // relative to the most expensive one in the current view.
  // -----------------------------------------------------------------
  updateCostSavings() {
    if (this.filteredData.length === 0) {
      $('#costSavings').textContent = '';
      return;
    }
    const maxPrice = Math.max(...this.filteredData.map((p) => p.price));
    const lines = this.filteredData.map((p) => {
      const saved = maxPrice - p.price;
      return `${p.name}: توفير ${saved.toLocaleString('ar-EG')} $`; 
    });
    $('#costSavings').innerHTML = lines.join('<br>');
  },

  // -----------------------------------------------------------------
  // Export current table view as PDF using `window.print()` on a hidden clone.
  // -----------------------------------------------------------------
  exportPDF() {
    // Clone the table into a temporary full‑screen container
    const clone = document.createElement('div');
    clone.style.position = 'fixed';
    clone.style.top = '0';
    clone.style.left = '0';
    clone.style.width = '100%';
    clone.style.height = '100%';
    clone.style.background = '#fff';
    clone.style.zIndex = '9999';
    clone.style.overflow = 'auto';
    clone.innerHTML = `<h1 style="text-align:center;margin:20px 0;">
      مصفوفة المقارنات التقنية – نسخة طباعة
    </h1>` + document.getElementById('matrixTable').outerHTML;
    document.body.appendChild(clone);
    // Give the browser a moment to render the clone before printing
    setTimeout(() => {
      window.print();
      document.body.removeChild(clone);
    }, 500);
  },
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  TechMatrix.init();
});
