/**
 * FAQ Component
 * Accessible interactive accordion answering core Dubai company formation queries.
 */

import { faqItems } from '../data/content.js';

export function renderFAQ() {
  return `
    <section id="faq" aria-labelledby="faq-title">
      <div class="container">
        <div class="section-header">
          <div class="section-tag">Frequently Answered</div>
          <h2 id="faq-title">Clarifying UAE Incorporation</h2>
          <p>
            Key insights on jurisdiction rules, 100% foreign ownership, banking hurdles, and corporate tax regulations.
          </p>
        </div>

        <div class="faq-list" role="region" aria-label="FAQ Accordion">
          ${faqItems
            .map(
              (item, idx) => `
            <div class="faq-item" id="faq-item-${idx}">
              <button
                type="button"
                class="faq-question"
                id="faq-btn-${idx}"
                aria-expanded="false"
                aria-controls="faq-ans-${idx}"
              >
                <span>${item.question}</span>
                <svg class="faq-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </button>
              <div
                class="faq-answer"
                id="faq-ans-${idx}"
                role="region"
                aria-labelledby="faq-btn-${idx}"
              >
                <p>${item.answer}</p>
              </div>
            </div>
          `
            )
            .join('')}
        </div>
      </div>
    </section>
  `;
}

export function initFAQ() {
  const faqButtons = document.querySelectorAll('.faq-question');

  faqButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const parent = btn.closest('.faq-item');
      if (!parent) return;

      const isExpanded = btn.getAttribute('aria-expanded') === 'true';

      // Optionally close other items for single-open accordion behavior
      document.querySelectorAll('.faq-item').forEach((item) => {
        if (item !== parent) {
          item.classList.remove('active');
          const otherBtn = item.querySelector('.faq-question');
          if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
        }
      });

      // Toggle current
      if (isExpanded) {
        parent.classList.remove('active');
        btn.setAttribute('aria-expanded', 'false');
      } else {
        parent.classList.add('active');
        btn.setAttribute('aria-expanded', 'true');
      }
    });
  });
}
