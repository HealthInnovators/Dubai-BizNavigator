/**
 * Trust Strip Component
 * Presents 3 core value/metric callouts highlighting autonomous AI capabilities.
 */

import { siteConfig } from '../data/content.js';

export function renderTrustStrip() {
  const { callouts } = siteConfig.trustStrip;

  return `
    <section class="trust-strip-section" id="trust-strip" aria-label="Core Capabilities">
      <div class="container">
        <!-- 3 Concise Metric/Value Callouts -->
        <div class="value-callouts-grid" role="region" aria-label="Core AI Capabilities">
          ${callouts
            .map((item, index) => {
              let iconSvg = '';
              if (item.icon === 'compass') {
                iconSvg = `
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon>
                  </svg>
                `;
              } else if (item.icon === 'shield-check') {
                iconSvg = `
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                    <polyline points="9 12 11 14 15 10"></polyline>
                  </svg>
                `;
              } else {
                iconSvg = `
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                  </svg>
                `;
              }

              return `
                <div class="callout-card" data-index="${index}">
                  <div class="callout-icon-box" aria-hidden="true">
                    ${iconSvg}
                  </div>
                  <div class="callout-content">
                    <h4 class="callout-title">${item.title}</h4>
                    <p class="callout-desc">${item.description}</p>
                  </div>
                </div>
              `;
            })
            .join('')}
        </div>
      </div>
    </section>
  `;
}
