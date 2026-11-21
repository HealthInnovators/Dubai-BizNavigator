/**
 * Trust & Competition Strip Component
 * Highlights alignment with the Dubai Chamber of Digital Economy AI Championship
 * and presents 3 core value/metric callouts.
 */

import { siteConfig } from '../data/content.js';

export function renderTrustStrip() {
  const { chamberCompetition, callouts } = siteConfig.trustStrip;

  return `
    <section class="trust-strip-section" id="trust-strip" aria-label="Trust and Competition Alignment">
      <div class="container">
        <!-- Chamber Competition Alignment Banner -->
        <div class="chamber-alignment-card">
          <div class="chamber-crest-col">
            <div class="chamber-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="8" r="7"></circle>
                <polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline>
              </svg>
            </div>
            <div class="chamber-text-content">
              <div class="chamber-badge">${chamberCompetition.badgeText}</div>
              <h3 class="chamber-title">
                Aligned with the <span>${chamberCompetition.title}</span>
              </h3>
              <p class="chamber-subtitle">
                Official Entrant: <strong>${chamberCompetition.initiative}</strong> &mdash; <em>${chamberCompetition.category}</em>
              </p>
            </div>
          </div>

          <div class="chamber-action-col">
            <a
              href="${chamberCompetition.url}"
              target="_blank"
              rel="noopener noreferrer"
              class="chamber-link-btn"
              aria-label="View Dubai Chamber of Digital Economy Create AI Agents Championship (opens in new tab)"
            >
              <span>Explore Championship</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                <polyline points="15 3 21 3 21 9"></polyline>
                <line x1="10" y1="14" x2="21" y2="3"></line>
              </svg>
            </a>
          </div>
        </div>

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
