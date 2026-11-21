/**
 * Pricing & Access Tiers Component
 * 3 clean cards outlining the Founder Explorer, Launch Ready, and Ecosystem Partner tiers.
 */

import { pricingTiers } from '../data/content.js';

export function renderPricingSection() {
  return `
    <section id="pricing" class="pricing-section" aria-labelledby="pricing-title">
      <div class="container">
        <div class="section-header">
          <div class="section-tag">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
            </svg>
            Transparent Tiering
          </div>
          <h2 id="pricing-title">Access Plans & Partnership Tiers</h2>
          <p>
            Choose between public feasibility exploration, end-to-end autonomous formation with Human-in-the-Loop review, or white-label ecosystem API integration.
          </p>
        </div>

        <div class="pricing-grid">
          ${pricingTiers
            .map(
              (tier) => `
            <div class="pricing-card ${tier.highlight ? 'featured-card' : ''}" id="tier-${tier.id}">
              <div class="pricing-card-header">
                <span class="tier-badge ${tier.highlight ? 'gold-badge' : ''}">${tier.badge}</span>
                <h3 class="tier-name">${tier.name}</h3>
                <p class="tier-desc">${tier.description}</p>
                <div class="tier-price-box">
                  <span class="tier-price ${tier.highlight ? 'highlight-gold' : ''}">${tier.price}</span>
                  <span class="tier-period">${tier.period}</span>
                </div>
              </div>

              <div class="tier-features-section">
                <h4 class="features-label">Included Deliverables:</h4>
                <ul class="features-list">
                  ${tier.features
                    .map(
                      (feat) => `
                    <li>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                      <span>${feat}</span>
                    </li>
                  `
                    )
                    .join('')}
                </ul>
              </div>

              <div class="tier-card-footer">
                <a
                  href="${tier.ctaTarget}"
                  class="btn ${tier.highlight ? 'btn-primary' : 'btn-secondary'} tier-cta-btn ${tier.ctaTarget === '#waitlist' ? 'early-access-trigger' : ''}"
                >
                  ${tier.ctaText}
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                    <polyline points="12 5 19 12 12 19"></polyline>
                  </svg>
                </a>
              </div>
            </div>
          `
            )
            .join('')}
        </div>

        <div class="pricing-advisory-note">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
          <span>
            <strong>Early Access Notice:</strong> Commercial package pricing is locked in during early cohort onboarding. Waitlist applicants receive a guaranteed AED 2,500 voucher credit towards government filing and bank dossier compilation fees.
          </span>
        </div>
      </div>
    </section>
  `;
}
