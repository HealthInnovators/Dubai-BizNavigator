/**
 * Workflow & Multi-Agent Trust Component
 * Interactive 4-step stepper with live agent previews and security/privacy callout grid.
 */

import { workflowStepperData } from '../data/content.js';

export function renderWorkflowSection() {
  const { steps, securityTrustGrid, sectionTitle, sectionSubtitle } = workflowStepperData;

  return `
    <section id="how-it-works" class="workflow-section" aria-labelledby="workflow-heading">
      <div class="container">
        <!-- Section Header -->
        <div class="section-header">
          <div class="section-tag">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
            Autonomous Agent Orchestration
          </div>
          <h2 id="workflow-heading">${sectionTitle}</h2>
          <p>${sectionSubtitle}</p>
        </div>

        <!-- 4-Step Stepper Tabs -->
        <div class="stepper-nav" role="tablist" aria-label="Workflow 4-step stepper">
          ${steps
            .map(
              (step, idx) => `
            <button
              type="button"
              class="stepper-tab ${idx === 0 ? 'active' : ''}"
              role="tab"
              aria-selected="${idx === 0 ? 'true' : 'false'}"
              aria-controls="panel-${step.id}"
              id="tab-${step.id}"
              data-step-index="${idx}"
            >
              <span class="stepper-tab-num">${step.number}</span>
              <span class="stepper-tab-label">${step.tabTitle}</span>
              ${idx === 2 ? '<span class="hitl-pill">HITL Gate</span>' : ''}
            </button>
          `
            )
            .join('')}
        </div>

        <!-- Stepper Panels Container -->
        <div class="stepper-panels-wrapper">
          ${steps.map((step, idx) => renderStepPanel(step, idx)).join('')}
        </div>

        <!-- Security & Privacy Callout Grid (Multi-Agent Trust) -->
        <div class="trust-grid-header">
          <div class="section-tag" style="margin-bottom: 0.5rem;">Sovereign Infrastructure</div>
          <h3>Enterprise Safety & Privacy Architecture</h3>
          <p>
            Automated intelligence with non-negotiable safety guardrails, client-side PII scrubbing, and local residency.
          </p>
        </div>

        <div class="security-privacy-grid" role="region" aria-label="Security and Privacy Architecture">
          ${securityTrustGrid
            .map(
              (item) => `
            <div class="trust-callout-card">
              <div class="trust-card-top">
                <div class="trust-icon-box" aria-hidden="true">
                  ${getTrustIcon(item.icon)}
                </div>
                <span class="trust-badge">${item.badge}</span>
              </div>
              <h4 class="trust-card-title">${item.title}</h4>
              <p class="trust-card-desc">${item.description}</p>
            </div>
          `
            )
            .join('')}
        </div>
      </div>
    </section>
  `;
}

function renderStepPanel(step, index) {
  const isFirst = index === 0;

  return `
    <div
      class="stepper-panel ${isFirst ? 'active' : ''}"
      id="panel-${step.id}"
      role="tabpanel"
      aria-labelledby="tab-${step.id}"
      data-panel-index="${index}"
      ${!isFirst ? 'hidden' : ''}
    >
      <div class="panel-layout">
        <!-- Left: Narrative & Deliverables -->
        <div class="panel-narrative">
          <div class="panel-agents-strip">
            ${step.agents
              .map(
                (ag) => `
              <span class="agent-tag" title="${ag.role}">
                <span class="agent-indicator"></span>
                <code>${ag.name}</code>
              </span>
            `
              )
              .join('')}
          </div>

          <h3 class="panel-title">${step.title}</h3>
          <p class="panel-desc">${step.shortDesc}</p>

          <div class="panel-deliverables">
            <h4 class="deliverables-heading">Deliverables & Agent Checks:</h4>
            <ul class="deliverables-list">
              ${step.points
                .map(
                  (pt) => `
                <li>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  <span>${pt}</span>
                </li>
              `
                )
                .join('')}
            </ul>
          </div>

          <div class="stepper-actions">
            <button
              type="button"
              class="btn btn-secondary btn-sm stepper-prev-btn"
              data-target-index="${index - 1}"
              ${index === 0 ? 'disabled style="opacity: 0.4; cursor: not-allowed;"' : ''}
            >
              &larr; Previous Step
            </button>
            <button
              type="button"
              class="btn btn-primary btn-sm stepper-next-btn"
              data-target-index="${index + 1}"
              ${index === 3 ? 'disabled style="opacity: 0.4; cursor: not-allowed;"' : ''}
            >
              ${index === 3 ? 'Final Stage' : 'Next Stage &rarr;'}
            </button>
          </div>
        </div>

        <!-- Right: Live Mock Preview Card -->
        <div class="panel-mockup">
          ${renderMockupByStep(step)}
        </div>
      </div>
    </div>
  `;
}

function renderMockupByStep(step) {
  if (step.id === 'step-1') {
    return `
      <div class="mockup-card">
        <div class="mockup-card-header">
          <span class="mockup-label">Intake Specification</span>
          <span class="mockup-status-dot"></span>
        </div>
        <div class="mockup-intake-body">
          <div class="intake-field">
            <span class="field-label">Target Industry:</span>
            <div class="field-value highlight-gold">${step.mockData.sector}</div>
          </div>
          <div class="intake-field">
            <span class="field-label">Commercial Market:</span>
            <div class="field-value">${step.mockData.market}</div>
          </div>
          <div class="intake-field">
            <span class="field-label">Visa Headcount:</span>
            <div class="field-value">${step.mockData.visas}</div>
          </div>
          <div class="intake-field">
            <span class="field-label">Physical Office Mandate:</span>
            <div class="field-value">${step.mockData.office}</div>
          </div>
        </div>
        <div class="mockup-footer-note">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          Mapped to UAE National Economic Register taxonomy in 0.8s
        </div>
      </div>
    `;
  }

  if (step.id === 'step-2') {
    return `
      <div class="mockup-card">
        <div class="mockup-card-header">
          <span class="mockup-label">Dual-Track Statutory Audit</span>
          <span class="agent-tag"><code>regulatory-researcher</code></span>
        </div>
        <div class="mockup-analysis-body">
          <div class="analysis-verdict">
            <strong>Result:</strong> ${step.mockData.recommendation}
          </div>
          <div class="citation-box">
            <div class="citation-header">Official Source Citations:</div>
            <ul class="citation-list">
              ${step.mockData.citations
                .map(
                  (c) => `
                <li>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                  </svg>
                  <span>${c}</span>
                </li>
              `
                )
                .join('')}
            </ul>
          </div>
        </div>
        <div class="mockup-footer-note">
          Corporate Tax Assessment: Qualifying Free Zone Person (QFZP) applicability analyzed
        </div>
      </div>
    `;
  }

  if (step.id === 'step-3') {
    return `
      <div class="mockup-card hitl-mockup">
        <div class="mockup-card-header">
          <span class="mockup-label">Form Pre-Fill Registry</span>
          <span class="human-approved-badge" id="hitl-preview-badge">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            HITL Gate Active
          </span>
        </div>
        <div class="mockup-hitl-body">
          <div class="form-preview-row">
            <span class="form-preview-label">Proposed Trade Name:</span>
            <span class="form-preview-val highlight-gold">${step.mockData.tradeName}</span>
          </div>
          <div class="form-preview-row">
            <span class="form-preview-label">DED Activity Codes:</span>
            <div class="tag-row">
              ${step.mockData.activityCodes
                .map((code) => `<span class="activity-code-chip">${code}</span>`)
                .join('')}
            </div>
          </div>
          <div class="form-preview-row">
            <span class="form-preview-label">Bilingual MOA Status:</span>
            <span class="form-preview-val" style="color: #38BDF8;">${step.mockData.moaStatus}</span>
          </div>

          <div class="hitl-gate-box" id="hitl-action-box">
            <div class="hitl-gate-status">
              <span class="pulse-indicator"></span>
              <strong id="hitl-gate-text">PAUSED: Explicit Founder Approval Required</strong>
            </div>
            <button type="button" class="btn btn-sm btn-primary" id="hitl-approve-toggle">
              Sign-off & Authorize Dossier
            </button>
          </div>
        </div>
        <div class="mockup-footer-note" style="color: #F8FAFC;">
          Zero unapproved submissions guaranteed by cryptographically signed audit trail.
        </div>
      </div>
    `;
  }

  // Step 4: Banking & Ongoing Monitoring
  return `
    <div class="mockup-card">
      <div class="mockup-card-header">
        <span class="mockup-label">Underwriting & Compliance Dossier</span>
        <span class="agent-tag"><code>banking-readiness-agent</code></span>
      </div>
      <div class="mockup-banking-body">
        <div class="banking-partner-row">
          <span class="partner-label">Pre-Formatted Bank KYC:</span>
          <div class="tag-row">
            ${step.mockData.banks
              .map((b) => `<span class="bank-pill">${b}</span>`)
              .join('')}
          </div>
        </div>
        <div class="banking-dossier-row">
          <span class="partner-label">Artifact Status:</span>
          <span class="highlight-gold" style="font-weight: 600;">${step.mockData.dossier}</span>
        </div>

        <div class="monitor-status-box">
          <div class="monitor-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
            </svg>
          </div>
          <div>
            <div class="monitor-title">Regulatory Watchdog Daemon</div>
            <div class="monitor-desc">${step.mockData.monitorStatus}</div>
          </div>
        </div>
      </div>
      <div class="mockup-footer-note">
        Automatic reminders scheduled for Corporate Tax registration & annual trade license renewal.
      </div>
    </div>
  `;
}

function getTrustIcon(type) {
  if (type === 'shield-alert') {
    return `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
    `;
  }
  if (type === 'eye-off') {
    return `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
        <line x1="1" y1="1" x2="23" y2="23"></line>
      </svg>
    `;
  }
  return `
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect>
      <rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect>
      <line x1="6" y1="6" x2="6.01" y2="6"></line>
      <line x1="6" y1="18" x2="6.01" y2="18"></line>
    </svg>
  `;
}

export function initWorkflowSection() {
  const tabs = document.querySelectorAll('.stepper-tab');
  const panels = document.querySelectorAll('.stepper-panel');

  const switchStep = (index) => {
    const targetIdx = parseInt(index, 10);
    if (isNaN(targetIdx) || targetIdx < 0 || targetIdx >= tabs.length) return;

    tabs.forEach((tab, i) => {
      const isSelected = i === targetIdx;
      tab.classList.toggle('active', isSelected);
      tab.setAttribute('aria-selected', String(isSelected));
    });

    panels.forEach((panel, i) => {
      const isSelected = i === targetIdx;
      panel.classList.toggle('active', isSelected);
      if (isSelected) {
        panel.removeAttribute('hidden');
      } else {
        panel.setAttribute('hidden', '');
      }
    });
  };

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      const idx = tab.getAttribute('data-step-index');
      switchStep(idx);
    });
  });

  // Action buttons (Next / Previous Step inside panel)
  document.querySelectorAll('.stepper-next-btn, .stepper-prev-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetIdx = btn.getAttribute('data-target-index');
      if (targetIdx !== null) switchStep(targetIdx);
    });
  });

  // Interactive HITL Approval button in Step 3
  const hitlBtn = document.getElementById('hitl-approve-toggle');
  const hitlStatusText = document.getElementById('hitl-gate-text');
  const hitlBadge = document.getElementById('hitl-preview-badge');

  if (hitlBtn && hitlStatusText && hitlBadge) {
    let approved = false;
    hitlBtn.addEventListener('click', () => {
      approved = !approved;
      if (approved) {
        hitlBtn.textContent = 'Filing Signed-Off ✓';
        hitlBtn.style.background = '#10B981';
        hitlBtn.style.borderColor = '#10B981';
        hitlBtn.style.color = '#0B132B';
        hitlStatusText.textContent = 'APPROVED: Ready for Authorized Submission';
        hitlStatusText.style.color = '#10B981';
        hitlBadge.innerHTML = `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          Founder Approved
        `;
      } else {
        hitlBtn.textContent = 'Sign-off & Authorize Dossier';
        hitlBtn.style.background = '';
        hitlBtn.style.borderColor = '';
        hitlBtn.style.color = '';
        hitlStatusText.textContent = 'PAUSED: Explicit Founder Approval Required';
        hitlStatusText.style.color = '';
        hitlBadge.innerHTML = `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          HITL Gate Active
        `;
      }
    });
  }
}
