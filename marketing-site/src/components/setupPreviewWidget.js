/**
 * Setup Path Preview Widget Component
 * Client-side interactive widget modeling jurisdiction pathways and trade-offs.
 */

export const officialPortalLinks = [
  {
    name: "Dubai DET Business Licensing",
    url: "https://www.dubaidet.gov.ae/en/licences-and-permits/business-licensing",
    description: "Official Dubai Department of Economy and Tourism portal"
  },
  {
    name: "Invest in Dubai Mainland Guide",
    url: "https://www.investindubai.gov.ae/en/business-setup/mainland-companies",
    description: "Official government business setup platform"
  },
  {
    name: "DMCC Mainland vs. Free Zone Analysis",
    url: "https://dmcc.ae/blog/difference-between-dubai-mainland-freezone-companies",
    description: "DMCC authority breakdown of jurisdiction distinctions"
  }
];

export function renderSetupPreviewWidget() {
  return `
    <section id="setup-preview" class="setup-preview-section" aria-labelledby="setup-preview-title">
      <div class="container">
        <div class="section-header">
          <div class="section-tag">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polygon points="12 2 19 21 12 17 5 21 12 2"></polygon>
            </svg>
            Interactive Decision Model
          </div>
          <h2 id="setup-preview-title">Setup Path Preview Widget</h2>
          <p>
            Configure your commercial profile to preview immediate jurisdiction recommendations, operational trade-offs, and official government portal pathways.
          </p>
        </div>

        <div class="preview-widget-grid">
          <!-- Left: Input Controls Card -->
          <div class="widget-controls-card">
            <h3 class="widget-card-heading">
              <span class="step-num-pill">1</span>
              Configure Business Parameters
            </h3>

            <!-- 1. Primary Market Toggle -->
            <div class="widget-field-group">
              <label class="widget-field-label" id="market-label">
                Primary Target Market
              </label>
              <div class="toggle-switch-group" role="radiogroup" aria-labelledby="market-label">
                <button
                  type="button"
                  class="toggle-btn active"
                  role="radio"
                  aria-checked="true"
                  data-market="international"
                  id="btn-market-intl"
                >
                  <span class="radio-indicator"></span>
                  <span>International / B2B</span>
                </button>
                <button
                  type="button"
                  class="toggle-btn"
                  role="radio"
                  aria-checked="false"
                  data-market="mainland"
                  id="btn-market-mainland"
                >
                  <span class="radio-indicator"></span>
                  <span>Direct UAE Local Market</span>
                </button>
              </div>
            </div>

            <!-- 2. Visa Quota Select/Slider -->
            <div class="widget-field-group">
              <div class="field-label-row">
                <label for="visa-quota-select" class="widget-field-label">
                  Visa Quota Requirement
                </label>
                <span class="field-helper" id="visa-badge">0–2 Visas</span>
              </div>
              <select id="visa-quota-select" class="form-select widget-select" aria-label="Select visa quota range">
                <option value="0-2" selected>0–2 Visas (Solopreneur / Core Partners)</option>
                <option value="3-6">3–6 Visas (Growing Team & Key Staff)</option>
                <option value="7+">7+ Visas (Enterprise / Scaled Operations)</option>
              </select>
            </div>

            <!-- 3. Office Preference Toggle -->
            <div class="widget-field-group">
              <label class="widget-field-label" id="office-label">
                Office Preference
              </label>
              <div class="toggle-switch-group" role="radiogroup" aria-labelledby="office-label">
                <button
                  type="button"
                  class="toggle-btn active"
                  role="radio"
                  aria-checked="true"
                  data-office="flexi"
                  id="btn-office-flexi"
                >
                  <span class="radio-indicator"></span>
                  <span>Flexi-Desk / Virtual</span>
                </button>
                <button
                  type="button"
                  class="toggle-btn"
                  role="radio"
                  aria-checked="false"
                  data-office="physical"
                  id="btn-office-physical"
                >
                  <span class="radio-indicator"></span>
                  <span>Physical Office (Ejari)</span>
                </button>
              </div>
            </div>

            <div class="widget-note-strip">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
              <span>Instant client-side inference powered by Dubai BizNavigator rule matrix.</span>
            </div>
          </div>

          <!-- Right: Live Output Card -->
          <div class="widget-output-card" id="widget-output-container">
            <!-- Dynamically populated via updateWidgetOutput() -->
          </div>
        </div>
      </div>
    </section>
  `;
}

export function calculateSetupPath(state) {
  const { market, visas, office } = state;

  if (market === 'mainland') {
    if (office === 'flexi' && visas === '0-2') {
      return {
        pathway: 'Dubai Mainland (DET) Instant Licence',
        badge: 'Recommended for Quick Local Market Entry',
        hub: 'Dubai Department of Economy and Tourism (DET)',
        fitScore: '96% Fit',
        estSetupTime: '24–48 Hours',
        estAnnualFee: 'AED 15,500 – 19,000',
        tradeOffs: [
          {
            title: 'Direct UAE Local Trading',
            desc: 'Unrestricted commercial activity across all 7 UAE Emirates, B2B/B2C, and government entity tenders.',
            favorable: true
          },
          {
            title: 'Physical Office Flexibility',
            desc: 'Instant Licence waives the requirement for an Ejari lease for the 1st year (up to 4 residence visas allowed).',
            favorable: true
          },
          {
            title: 'Year-2 Ejari Mandate',
            desc: 'Must secure a physical commercial lease (Ejari) upon year-2 license renewal to maintain visa quotas.',
            favorable: false
          },
          {
            title: 'Corporate Tax Scope',
            desc: 'Standard 9% UAE Corporate Tax applies on net taxable profits exceeding AED 375,000 (Small Business Relief available up to AED 3M revenue).',
            favorable: false
          }
        ],
        regulatoryNote: 'Regulated under Federal Decree-Law No. (26) of 2020 on Commercial Companies.'
      };
    }

    return {
      pathway: 'Dubai Mainland (DET) Standard Commercial Licence',
      badge: 'Recommended for Direct Local Operations & Scaled Team',
      hub: 'Dubai Department of Economy and Tourism (DET)',
      fitScore: '98% Fit',
      estSetupTime: '3–5 Business Days',
      estAnnualFee: 'AED 18,500 – 26,000',
      tradeOffs: [
        {
          title: 'Direct Local Market Access',
          desc: 'Direct trading with mainland consumers and corporations without local distributor commissions or intermediary agents.',
          favorable: true
        },
        {
          title: 'Government Contract Eligibility',
          desc: 'Direct entitlement to register with Dubai Government e-Supply portal and bid on municipal and federal contracts.',
          favorable: true
        },
        {
          title: 'Physical Ejari Lease Required',
          desc: 'Requires an active commercial tenancy contract (Ejari). Visa quotas scale strictly with leased square footage (approx. 1 visa per 80 sq. ft.).',
          favorable: false
        },
        {
          title: 'No Free Zone Transshipment Privileges',
          desc: 'Mainland customs rules apply; standard 5% customs duty on goods imported into the mainland.',
          favorable: false
        }
      ],
      regulatoryNote: 'Governed by DET Commercial Licensing Regulations & Executive Council Resolution No. (13) of 2011.'
    };
  }

  // International / B2B market
  if (office === 'flexi' && visas === '0-2') {
    return {
      pathway: 'Dubai Free Zone (e.g. DMCC, IFZA, or DIC)',
      badge: 'Optimal for Capital Efficiency & International Reach',
      hub: 'Dubai Multi Commodities Centre (DMCC) / IFZA / TECOM (DIC)',
      fitScore: '97% Fit',
      estSetupTime: '3–5 Business Days',
      estAnnualFee: 'AED 14,900 – 18,500',
      tradeOffs: [
        {
          title: '100% Foreign Ownership & Low Overhead',
          desc: 'Complete ownership with flexi-desk or virtual office package; lowest capital expenditure for initial launch.',
          favorable: true
        },
        {
          title: 'Potential 0% Corporate Tax (QFZP)',
          desc: 'Qualifying Free Zone Persons (QFZP) can maintain 0% tax on qualifying transactions with foreign entities and designated zones.',
          favorable: true
        },
        {
          title: 'Mainland B2C Selling Constraint',
          desc: 'Cannot trade directly with UAE mainland retail consumers without engaging a licensed mainland distributor or opening a DET branch.',
          favorable: false
        },
        {
          title: 'Capped Flexi-Desk Visa Quota',
          desc: 'Flexi-desk packages are typically capped at 1–3 visas. Scaling to 4+ visas necessitates upgrading to dedicated office premises.',
          favorable: false
        }
      ],
      regulatoryNote: 'Compliant with Cabinet Decision No. (139) of 2023 regarding Qualifying Free Zone Income.'
    };
  }

  return {
    pathway: 'Dubai Free Zone (e.g. DMCC or DIFC Hub)',
    badge: 'Recommended for Global Enterprise & Dedicated Infrastructure',
    hub: 'DMCC (Commodities & Tech Hub) / DIFC (Financial District)',
    fitScore: '95% Fit',
    estSetupTime: '5–8 Business Days',
    estAnnualFee: 'AED 22,000 – 35,000+',
    tradeOffs: [
      {
        title: 'Tier-1 Banking Underwriting Credibility',
        desc: 'Dedicated physical premises in established Free Zones significantly accelerate KYC approval with Tier-1 UAE banks (Emirates NBD, Mashreq).',
        favorable: true
      },
      {
        title: 'High Visa Quota Scalability',
        desc: 'Dedicated office footprint allows expanding team visas without artificial package caps.',
        favorable: true
      },
      {
        title: 'Premium Lease Overhead',
        desc: 'Higher annual commercial real estate commitments in prime business districts (JLT, Downtown, DIFC).',
        favorable: false
      },
      {
        title: 'Domestic Mainland Trading Restrictions',
        desc: 'Selling directly to non-freezone UAE clients requires mainland branch registration or local commercial agent.',
        favorable: false
      }
    ],
    regulatoryNote: 'Governed by DMCC Company Regulations 2020 and UAE Federal Commercial Law.'
  };
}

export function initSetupPreviewWidget() {
  const container = document.getElementById('widget-output-container');
  if (!container) return;

  const state = {
    market: 'international',
    visas: '0-2',
    office: 'flexi'
  };

  const marketBtns = document.querySelectorAll('[data-market]');
  const officeBtns = document.querySelectorAll('[data-office]');
  const visaSelect = document.getElementById('visa-quota-select');
  const visaBadge = document.getElementById('visa-badge');

  function renderOutput() {
    const res = calculateSetupPath(state);

    container.innerHTML = `
      <div class="output-header">
        <div class="output-top-row">
          <span class="output-badge">${res.badge}</span>
          <span class="output-score">${res.fitScore}</span>
        </div>
        <h3 class="output-pathway-title">${res.pathway}</h3>
        <div class="output-authority-text">
          <span class="bullet-dot"></span>
          <span>Authority: <strong>${res.hub}</strong></span>
        </div>
      </div>

      <!-- Quick Metrics Strip -->
      <div class="output-metrics-strip">
        <div class="output-metric">
          <span class="metric-label">Estimated Setup Speed:</span>
          <span class="metric-val highlight-gold">${res.estSetupTime}</span>
        </div>
        <div class="output-metric">
          <span class="metric-label">Est. Annual Gov & License Fee:</span>
          <span class="metric-val">${res.estAnnualFee}</span>
        </div>
      </div>

      <!-- Trade-offs Breakdown -->
      <div class="tradeoffs-container">
        <h4 class="tradeoffs-heading">Key Operational Trade-offs & Permit Rules:</h4>
        <div class="tradeoffs-grid">
          ${res.tradeOffs
            .map(
              (to) => `
            <div class="tradeoff-item ${to.favorable ? 'favorable' : 'restrictive'}">
              <div class="tradeoff-header">
                <span class="tradeoff-icon">
                  ${
                    to.favorable
                      ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>'
                      : '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>'
                  }
                </span>
                <span class="tradeoff-title">${to.title}</span>
              </div>
              <p class="tradeoff-desc">${to.desc}</p>
            </div>
          `
            )
            .join('')}
        </div>
      </div>

      <!-- Official Portal Verification Links -->
      <div class="official-portals-section">
        <h4 class="portals-heading">Verified UAE Government & Authority Portals:</h4>
        <div class="portals-list">
          ${officialPortalLinks
            .map(
              (p) => `
            <a
              href="${p.url}"
              target="_blank"
              rel="noopener noreferrer"
              class="portal-link-item"
              aria-label="Visit ${p.name} (opens in new tab)"
            >
              <div class="portal-link-content">
                <span class="portal-name">${p.name}</span>
                <span class="portal-sub">${p.description}</span>
              </div>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                <polyline points="15 3 21 3 21 9"></polyline>
                <line x1="10" y1="14" x2="21" y2="3"></line>
              </svg>
            </a>
          `
            )
            .join('')}
        </div>
      </div>

      <!-- Illustrative Disclaimer Note -->
      <div class="illustrative-disclaimer">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="16" x2="12" y2="12"></line>
          <line x1="12" y1="8" x2="12.01" y2="8"></line>
        </svg>
        <span>
          <strong>Illustrative Preview:</strong> This widget demonstrates preliminary jurisdiction fit based on general guidelines. The full Dubai BizNavigator multi-agent engine conducts live statutory verification against 2,000+ DET activity classifications and current Cabinet Decisions.
        </span>
      </div>

      <div class="output-cta-row">
        <button type="button" class="btn btn-primary btn-sm early-access-trigger" style="width: 100%;">
          Run Full Autonomous Analysis for this Profile
        </button>
      </div>
    `;
  }

  // Setup event listeners for Market toggle
  marketBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      marketBtns.forEach((b) => {
        b.classList.remove('active');
        b.setAttribute('aria-checked', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-checked', 'true');
      state.market = btn.getAttribute('data-market');
      renderOutput();
    });
  });

  // Setup event listeners for Office toggle
  officeBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      officeBtns.forEach((b) => {
        b.classList.remove('active');
        b.setAttribute('aria-checked', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-checked', 'true');
      state.office = btn.getAttribute('data-office');
      renderOutput();
    });
  });

  // Setup event listener for Visa select
  if (visaSelect) {
    visaSelect.addEventListener('change', (e) => {
      state.visas = e.target.value;
      if (visaBadge) {
        if (state.visas === '0-2') visaBadge.textContent = '0–2 Visas';
        else if (state.visas === '3-6') visaBadge.textContent = '3–6 Visas';
        else visaBadge.textContent = '7+ Visas';
      }
      renderOutput();
    });
  }

  // Initial render
  renderOutput();
}
