/**
 * Waitlist Form Component
 * Dedicated inline early access intake form with client-side validation
 * and clean inline async confirmation.
 */

export function renderWaitlistForm() {
  return `
    <section id="waitlist" class="waitlist-section" aria-labelledby="waitlist-title">
      <div class="container">
        <div class="waitlist-container-card">
          <div class="waitlist-layout">
            <!-- Left: Value Proposition Column -->
            <div class="waitlist-info-col">
              <div class="section-tag">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <polygon points="12 2 19 21 12 17 5 21 12 2"></polygon>
                </svg>
                Private Founder Cohort
              </div>
              <h2 id="waitlist-title" class="waitlist-heading">
                Reserve Your Place in the <span class="text-gradient">Early Access Beta</span>
              </h2>
              <p class="waitlist-sub">
                Join international ventures and scaling entrepreneurs using autonomous agent intelligence to incorporate in Dubai with zero broker commissions and verified statutory compliance.
              </p>

              <div class="cohort-perks-list">
                <div class="perk-item">
                  <div class="perk-icon" aria-hidden="true">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                  </div>
                  <div>
                    <strong>AED 2,500 Fee Credit:</strong> Locked in for platform launch and trade license dossier creation.
                  </div>
                </div>

                <div class="perk-item">
                  <div class="perk-icon" aria-hidden="true">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                  </div>
                  <div>
                    <strong>Complimentary Structuring Review:</strong> 30-minute tailored evaluation with a licensed UAE corporate advisor.
                  </div>
                </div>

                <div class="perk-item">
                  <div class="perk-icon" aria-hidden="true">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                  </div>
                  <div>
                    <strong>Tier-1 Corporate Banking Fast-Track:</strong> Pre-cleared AML/KYC checklist for Wio, Emirates NBD, and Mashreq NeoBiz.
                  </div>
                </div>
              </div>
            </div>

            <!-- Right: Interactive Form / Confirmation Column -->
            <div class="waitlist-form-col">
              <div class="waitlist-form-wrapper" id="waitlist-form-wrapper">
                <div class="form-header-row">
                  <h3 class="form-title">Apply for Priority Access</h3>
                  <span class="cohort-tag">Cohort Q1 2025</span>
                </div>

                <form id="inline-waitlist-form" novalidate>
                  <!-- 1. Full Name -->
                  <div class="form-field-item">
                    <label for="wl-name" class="form-label">
                      Full Name <span class="required-mark">*</span>
                    </label>
                    <input
                      type="text"
                      id="wl-name"
                      name="fullName"
                      class="form-input"
                      placeholder="e.g. Tariq Al-Hashimi"
                      required
                      autocomplete="name"
                    />
                    <div class="form-error-msg" id="wl-name-error">Please enter your full name.</div>
                  </div>

                  <!-- 2. Work Email -->
                  <div class="form-field-item">
                    <label for="wl-email" class="form-label">
                      Work / Business Email <span class="required-mark">*</span>
                    </label>
                    <input
                      type="email"
                      id="wl-email"
                      name="email"
                      class="form-input"
                      placeholder="tariq@global-venture.io"
                      required
                      autocomplete="email"
                    />
                    <div class="form-error-msg" id="wl-email-error">Please enter a valid business email address.</div>
                  </div>

                  <!-- 3. Company / Startup Stage -->
                  <div class="form-field-item">
                    <label for="wl-stage" class="form-label">
                      Company / Startup Stage <span class="required-mark">*</span>
                    </label>
                    <select id="wl-stage" name="stage" class="form-select" required>
                      <option value="" disabled selected>Select Current Stage</option>
                      <option value="pre-seed">Idea / Pre-Seed (Evaluating Dubai Market)</option>
                      <option value="seed-funded">Seed / VC-Funded Venture</option>
                      <option value="established-sme">Established International SME / Foreign Branch</option>
                      <option value="ecosystem-partner">Free Zone / Accelerator / Advisory Partner</option>
                    </select>
                    <div class="form-error-msg" id="wl-stage-error">Please select your current company stage.</div>
                  </div>

                  <!-- 4. Target Expansion Timeline -->
                  <div class="form-field-item">
                    <label for="wl-timeline" class="form-label">
                      Target Expansion Timeline <span class="required-mark">*</span>
                    </label>
                    <select id="wl-timeline" name="timeline" class="form-select" required>
                      <option value="" disabled selected>Select Expected Launch Timeline</option>
                      <option value="immediate">Immediate (Next 30 Days)</option>
                      <option value="1-3-months">1 – 3 Months</option>
                      <option value="3-6-months">3 – 6 Months</option>
                      <option value="exploratory">Exploratory / Long-Term Expansion</option>
                    </select>
                    <div class="form-error-msg" id="wl-timeline-error">Please select your target expansion timeline.</div>
                  </div>

                  <div class="privacy-notice-text">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                      <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                    </svg>
                    <span>Complies with UAE PDPL (Federal Decree-Law No. 45/2021). Zero spam.</span>
                  </div>

                  <button type="submit" class="btn btn-primary btn-lg" id="wl-submit-btn" style="width: 100%;">
                    <span id="btn-text">Submit Early Access Application</span>
                    <svg id="btn-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                      <polyline points="12 5 19 12 12 19"></polyline>
                    </svg>
                  </button>
                </form>

                <!-- Clean Inline Confirmation State -->
                <div class="waitlist-confirmation-state" id="waitlist-confirmation-state" role="status" aria-live="polite">
                  <div class="confirmation-icon-box">
                    <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                      <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                  </div>
                  <h3 class="confirmation-title">Application Received!</h3>
                  <p class="confirmation-desc">
                    Thank you, <strong id="confirmed-applicant-name">Founder</strong>. We have registered your application under priority cohort status.
                  </p>
                  <div class="confirmation-details-box">
                    <div class="confirmation-detail-row">
                      <span class="c-label">Registered Email:</span>
                      <strong class="c-val" id="confirmed-email">email@domain.com</strong>
                    </div>
                    <div class="confirmation-detail-row">
                      <span class="c-label">Launch Voucher Credit:</span>
                      <strong class="c-val highlight-gold">AED 2,500 Reserved</strong>
                    </div>
                    <div class="confirmation-detail-row">
                      <span class="c-label">Queue Verification Status:</span>
                      <strong class="c-val" style="color: #10B981;">Priority Queue #142</strong>
                    </div>
                  </div>
                  <p class="confirmation-next-steps">
                    A verification link and onboarding invitation will be delivered to your inbox shortly.
                  </p>
                  <button type="button" class="btn btn-secondary btn-sm" id="btn-submit-another">
                    Submit Another Application
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  `;
}

export function initWaitlistForm() {
  const form = document.getElementById('inline-waitlist-form');
  const formWrapper = document.getElementById('waitlist-form-wrapper');
  const confirmationState = document.getElementById('waitlist-confirmation-state');
  const submitBtn = document.getElementById('wl-submit-btn');
  const btnText = document.getElementById('btn-text');
  const btnIcon = document.getElementById('btn-icon');
  const submitAnotherBtn = document.getElementById('btn-submit-another');

  if (!form) return;

  const nameInput = document.getElementById('wl-name');
  const emailInput = document.getElementById('wl-email');
  const stageSelect = document.getElementById('wl-stage');
  const timelineSelect = document.getElementById('wl-timeline');

  const nameError = document.getElementById('wl-name-error');
  const emailError = document.getElementById('wl-email-error');
  const stageError = document.getElementById('wl-stage-error');
  const timelineError = document.getElementById('wl-timeline-error');

  const confirmedName = document.getElementById('confirmed-applicant-name');
  const confirmedEmail = document.getElementById('confirmed-email');

  function clearErrors() {
    [nameError, emailError, stageError, timelineError].forEach((err) => {
      if (err) err.style.display = 'none';
    });
    [nameInput, emailInput, stageSelect, timelineSelect].forEach((input) => {
      if (input) input.classList.remove('input-invalid');
    });
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearErrors();

    let hasError = false;

    if (!nameInput.value.trim()) {
      nameError.style.display = 'block';
      nameInput.classList.add('input-invalid');
      if (!hasError) nameInput.focus();
      hasError = true;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailInput.value.trim() || !emailPattern.test(emailInput.value.trim())) {
      emailError.style.display = 'block';
      emailInput.classList.add('input-invalid');
      if (!hasError) emailInput.focus();
      hasError = true;
    }

    if (!stageSelect.value) {
      stageError.style.display = 'block';
      stageSelect.classList.add('input-invalid');
      if (!hasError) stageSelect.focus();
      hasError = true;
    }

    if (!timelineSelect.value) {
      timelineError.style.display = 'block';
      timelineSelect.classList.add('input-invalid');
      if (!hasError) timelineSelect.focus();
      hasError = true;
    }

    if (hasError) return;

    // Simulation of async API call (e.g. POST /api/v1/waitlist)
    submitBtn.disabled = true;
    btnText.textContent = 'Securing VIP Reservation...';
    btnIcon.style.display = 'none';

    try {
      // Realistic network latency simulation
      await new Promise((resolve) => setTimeout(resolve, 800));

      const payload = {
        fullName: nameInput.value.trim(),
        email: emailInput.value.trim(),
        stage: stageSelect.value,
        timeline: timelineSelect.value,
        timestamp: new Date().toISOString()
      };

      // Populate confirmation card
      if (confirmedName) confirmedName.textContent = payload.fullName;
      if (confirmedEmail) confirmedEmail.textContent = payload.email;

      // Show confirmation state with transition
      form.style.display = 'none';
      if (confirmationState) confirmationState.classList.add('active');
    } catch (err) {
      console.error('Waitlist submission error:', err);
      submitBtn.disabled = false;
      btnText.textContent = 'Submit Early Access Application';
      btnIcon.style.display = 'inline-block';
    }
  });

  if (submitAnotherBtn) {
    submitAnotherBtn.addEventListener('click', () => {
      form.reset();
      clearErrors();
      submitBtn.disabled = false;
      btnText.textContent = 'Submit Early Access Application';
      btnIcon.style.display = 'inline-block';
      if (confirmationState) confirmationState.classList.remove('active');
      form.style.display = 'block';
    });
  }
}
