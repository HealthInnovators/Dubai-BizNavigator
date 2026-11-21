/**
 * Security & Compliance Component
 * Highlights sovereignty protection, data security, and regulatory adherence.
 */

import { securityFeatures } from '../data/content.js';

function getIconSvg(type) {
  switch (type) {
    case 'shield':
      return `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          <polyline points="9 12 11 14 15 10"></polyline>
        </svg>
      `;
    case 'lock':
      return `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
          <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
        </svg>
      `;
    case 'database':
      return `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
          <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
          <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
        </svg>
      `;
    case 'file-check':
    default:
      return `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
          <polyline points="9 15 11 17 15 13"></polyline>
        </svg>
      `;
  }
}

export function renderSecurity() {
  return `
    <section id="security" aria-labelledby="security-title">
      <div class="container">
        <div class="section-header">
          <div class="section-tag">Institutional Trust</div>
          <h2 id="security-title">Enterprise Security & UAE Sovereignty</h2>
          <p>
            Your corporate documents, shareholder records, and financial projections are governed by rigorous privacy controls and bank-grade standards.
          </p>
        </div>

        <div class="security-grid">
          ${securityFeatures
            .map(
              (feat) => `
            <div class="security-card">
              <div class="security-icon-wrap" aria-hidden="true">
                ${getIconSvg(feat.icon)}
              </div>
              <h3>${feat.title}</h3>
              <p>${feat.description}</p>
            </div>
          `
            )
            .join('')}
        </div>
      </div>
    </section>
  `;
}
