/**
 * FAQ Accordion Component
 * Fully accessible accordion with aria-expanded, keyboard navigation,
 * and clear disclaimers regarding legal and filing safeguards.
 */

import { faqItems } from '../data/content.js';

export function renderFAQAccordion() {
  return `
    <section id="faq" class="faq-section" aria-labelledby="faq-section-title">
      <div class="container">
        <div class="section-header">
          <div class="section-tag">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
            Founder Advisory & Governance
          </div>
          <h2 id="faq-section-title">Frequently Asked Questions</h2>
          <p>
            Key insights on autonomous agent mechanics, Human-in-the-Loop filing safeguards, PII sovereignty, and our legal co-pilot scope.
          </p>
        </div>

        <div class="faq-list" role="region" aria-label="Frequently Asked Questions Accordion">
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
                <span class="faq-question-text">${item.question}</span>
                <span class="faq-icon-wrapper" aria-hidden="true">
                  <svg class="faq-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="6 9 12 15 18 9"></polyline>
                  </svg>
                </span>
              </button>
              <div
                class="faq-answer"
                id="faq-ans-${idx}"
                role="region"
                aria-labelledby="faq-btn-${idx}"
              >
                <div class="faq-answer-inner">
                  <p>${item.answer}</p>
                  ${
                    item.question.includes('lawyer') || item.question.includes('legal advice')
                      ? `
                    <div class="faq-legal-callout">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line>
                        <line x1="12" y1="17" x2="12.01" y2="17"></line>
                      </svg>
                      <span><strong>Notice:</strong> Dubai BizNavigator is an AI-powered preparation technology co-pilot. It does not provide legal opinions, practice UAE law, or replace registered attorneys.</span>
                    </div>
                  `
                      : ''
                  }
                </div>
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

export function initFAQAccordion() {
  const faqButtons = document.querySelectorAll('.faq-question');

  faqButtons.forEach((btn) => {
    const toggleAccordion = () => {
      const parent = btn.closest('.faq-item');
      if (!parent) return;

      const isExpanded = btn.getAttribute('aria-expanded') === 'true';

      // Accessible single-open or multi-open behavior:
      // Close other items for focused reading
      document.querySelectorAll('.faq-item').forEach((item) => {
        if (item !== parent) {
          item.classList.remove('active');
          const otherBtn = item.querySelector('.faq-question');
          if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
        }
      });

      if (isExpanded) {
        parent.classList.remove('active');
        btn.setAttribute('aria-expanded', 'false');
      } else {
        parent.classList.add('active');
        btn.setAttribute('aria-expanded', 'true');
      }
    };

    // Click trigger
    btn.addEventListener('click', toggleAccordion);

    // Keyboard accessibility: Enter or Space
    btn.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        toggleAccordion();
      }
    });
  });
}
