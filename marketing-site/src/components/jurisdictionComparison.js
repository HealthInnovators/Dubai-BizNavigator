/**
 * Free Zone vs. Mainland Comparison Component
 * Interactive matrix enabling founders to filter and compare legal structures.
 */

import { jurisdictionComparisonData } from '../data/content.js';

export function renderJurisdictionComparison() {
  return `
    <section id="comparison" aria-labelledby="comparison-title">
      <div class="container">
        <div class="section-header">
          <div class="section-tag">Strategic Decision Engine</div>
          <h2 id="comparison-title">Free Zone vs. Mainland Architecture</h2>
          <p>
            Understand the legal, tax, and operational trade-offs to choose the optimal framework for your Dubai entity.
          </p>
        </div>

        <!-- Filter Controls -->
        <div class="comparison-filters" role="tablist" aria-label="Comparison categories">
          ${jurisdictionComparisonData.categories
            .map(
              (cat, idx) => `
            <button
              type="button"
              class="filter-btn ${idx === 0 ? 'active' : ''}"
              role="tab"
              aria-selected="${idx === 0 ? 'true' : 'false'}"
              data-category="${cat.id}"
            >
              ${cat.label}
            </button>
          `
            )
            .join('')}
        </div>

        <!-- Comparison Table Container -->
        <div class="comparison-table-wrapper" role="region" aria-label="Jurisdiction Comparison Table" tabindex="0">
          <table class="comparison-table">
            <thead>
              <tr>
                <th class="col-feature" scope="col">Decision Criteria</th>
                <th class="col-freezone" scope="col">
                  <span>Dubai Free Zone</span>
                  <div style="font-size: 0.75rem; font-weight: normal; color: var(--color-white-subtle); margin-top: 4px;">
                    e.g., DMCC, IFZA, DIFC, DAFZA
                  </div>
                </th>
                <th class="col-mainland" scope="col">
                  <span>Dubai Mainland (DED)</span>
                  <div style="font-size: 0.75rem; font-weight: normal; color: var(--color-white-subtle); margin-top: 4px;">
                    Department of Economy & Tourism
                  </div>
                </th>
              </tr>
            </thead>
            <tbody id="comparison-tbody">
              ${renderComparisonRows('all')}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  `;
}

function renderComparisonRows(activeCategory) {
  const filtered =
    activeCategory === 'all'
      ? jurisdictionComparisonData.items
      : jurisdictionComparisonData.items.filter((item) => item.category === activeCategory);

  return filtered
    .map(
      (item) => `
    <tr data-category="${item.category}">
      <td>
        <div class="comparison-feature-name">${item.feature}</div>
        <div class="comparison-winner">${item.winner}</div>
      </td>
      <td>
        ${item.freezone}
      </td>
      <td>
        ${item.mainland}
      </td>
    </tr>
  `
    )
    .join('');
}

export function initJurisdictionComparison() {
  const filterBtns = document.querySelectorAll('.comparison-filters .filter-btn');
  const tbody = document.getElementById('comparison-tbody');

  if (!filterBtns.length || !tbody) return;

  filterBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      filterBtns.forEach((b) => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });

      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');

      const category = btn.getAttribute('data-category') || 'all';
      tbody.innerHTML = renderComparisonRows(category);
    });
  });
}
