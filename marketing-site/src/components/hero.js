/**
 * Hero Component
 * Displays high-converting headline, subheadline, CTAs, and
 * a clean CSS-styled interactive mock A2UI Licensing Recommendation Card.
 */

import { siteConfig } from '../data/content.js';

export function renderHero() {
  const { hero, mockA2UICard } = siteConfig;

  return `
    <section class="hero-section" id="hero">
      <div class="container">
        <div class="hero-grid">
          <!-- Left Column: Copy & Actions -->
          <div class="hero-copy">
            <div class="section-tag">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polygon points="12 2 19 21 12 17 5 21 12 2"></polygon>
              </svg>
              Autonomous UAE Incorporation Copilot
            </div>

            <h1 class="hero-title">
              Launch Your Dubai Business in <span class="text-gradient">Hours, Not Weeks</span>
            </h1>

            <p class="hero-subheadline">
              ${hero.subheadline}
            </p>

            <div class="hero-ctas">
              <a href="${hero.primaryTarget}" class="btn btn-primary btn-lg" id="hero-preview-cta">
                <span>${hero.primaryCTA}</span>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                  <polyline points="12 5 19 12 12 19"></polyline>
                </svg>
              </a>

              <a href="${hero.secondaryTarget}" class="btn btn-secondary btn-lg early-access-trigger" id="hero-waitlist-cta">
                <span>${hero.secondaryCTA}</span>
              </a>
            </div>

            <div class="hero-micro-trust">
              <div class="trust-indicator">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <span>Zero Broker Fees</span>
              </div>
              <div class="trust-indicator">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <span>100% Foreign Ownership Verified</span>
              </div>
              <div class="trust-indicator">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <span>UAE PDPL Compliant</span>
              </div>
            </div>
          </div>

          <!-- Right Column: Mock A2UI Licensing Recommendation Card -->
          <div class="hero-visual">
            <div class="a2ui-preview-card" id="a2ui-recommendation-card">
              <!-- Card Header -->
              <div class="a2ui-header">
                <div class="a2ui-badge-group">
                  <span class="a2ui-tag">A2UI Autonomous Inference</span>
                  <div class="human-approved-badge" title="Verified by licensed UAE legal specialist">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                      <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                    <span>${mockA2UICard.badge}</span>
                  </div>
                </div>
                <div class="a2ui-profile-pill">
                  <span class="dot"></span>
                  <span>Target: ${mockA2UICard.activity}</span>
                </div>
              </div>

              <!-- Recommendation Comparison Matrix -->
              <div class="a2ui-comparison-body">
                <!-- Option 1: Dubai Mainland DET (Primary) -->
                <div class="a2ui-option-card selected" id="option-mainland" data-target="mainland">
                  <div class="option-header">
                    <div class="option-title-wrap">
                      <span class="option-name">${mockA2UICard.mainlandDET.name}</span>
                      <span class="option-badge top-badge">${mockA2UICard.mainlandDET.badge}</span>
                    </div>
                    <span class="match-score">${mockA2UICard.mainlandDET.matchScore}</span>
                  </div>
                  <div class="option-authority">${mockA2UICard.mainlandDET.authority}</div>

                  <div class="option-specs">
                    <div class="spec-row">
                      <span class="spec-label">Market Access:</span>
                      <span class="spec-value highlight-gold">${mockA2UICard.mainlandDET.marketAccess}</span>
                    </div>
                    <div class="spec-row">
                      <span class="spec-label">Ownership:</span>
                      <span class="spec-value">${mockA2UICard.mainlandDET.ownership}</span>
                    </div>
                    <div class="spec-row">
                      <span class="spec-label">Physical Office:</span>
                      <span class="spec-value">${mockA2UICard.mainlandDET.officeRule}</span>
                    </div>
                    <div class="spec-row">
                      <span class="spec-label">Est. Gov Fee:</span>
                      <span class="spec-value fee-tag">${mockA2UICard.mainlandDET.estCost}</span>
                    </div>
                  </div>
                </div>

                <!-- Option 2: DMCC Free Zone -->
                <div class="a2ui-option-card" id="option-dmcc" data-target="dmcc">
                  <div class="option-header">
                    <div class="option-title-wrap">
                      <span class="option-name">${mockA2UICard.dmccFreeZone.name}</span>
                      <span class="option-badge">${mockA2UICard.dmccFreeZone.badge}</span>
                    </div>
                    <span class="match-score muted">${mockA2UICard.dmccFreeZone.matchScore}</span>
                  </div>
                  <div class="option-authority">${mockA2UICard.dmccFreeZone.authority}</div>

                  <div class="option-specs">
                    <div class="spec-row">
                      <span class="spec-label">Market Access:</span>
                      <span class="spec-value">${mockA2UICard.dmccFreeZone.marketAccess}</span>
                    </div>
                    <div class="spec-row">
                      <span class="spec-label">Ownership:</span>
                      <span class="spec-value">${mockA2UICard.dmccFreeZone.ownership}</span>
                    </div>
                    <div class="spec-row">
                      <span class="spec-label">Physical Office:</span>
                      <span class="spec-value">${mockA2UICard.dmccFreeZone.officeRule}</span>
                    </div>
                    <div class="spec-row">
                      <span class="spec-label">Est. Gov Fee:</span>
                      <span class="spec-value fee-tag">${mockA2UICard.dmccFreeZone.estCost}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Interactive Controls & Generated Artifacts Strip -->
              <div class="a2ui-artifacts-strip">
                <div class="artifact-pill active">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  <span>DET Form Pre-filled</span>
                </div>
                <div class="artifact-pill active">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  <span>Bank KYC Dossier (Wio & ENBD)</span>
                </div>
                <div class="artifact-pill">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  <span>MoA Template Ready</span>
                </div>
              </div>

              <!-- Card Action Bar -->
              <div class="a2ui-card-footer">
                <div class="a2ui-agent-meta">
                  <span class="meta-label">Agent:</span> <code>dbn-a2ui-v2</code>
                  <span class="separator">•</span>
                  <span class="meta-label">Latency:</span> <code>1.4s</code>
                </div>
                <button type="button" class="btn btn-sm btn-primary a2ui-demo-btn early-access-trigger">
                  Select & Pre-fill Forms
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  `;
}

export function initHeroInteractive() {
  const options = document.querySelectorAll('.a2ui-option-card');
  options.forEach((opt) => {
    opt.addEventListener('click', () => {
      options.forEach((o) => o.classList.remove('selected'));
      opt.classList.add('selected');
    });
  });
}
