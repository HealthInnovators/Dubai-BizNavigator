/**
 * Early Access Modal Component
 * Interactive lead capture modal with form validation & animated confirmation.
 */

import { siteConfig } from '../data/content.js';

export function renderEarlyAccessModal() {
  return `
    <div class="modal-backdrop" id="early-access-modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div class="modal-card">
        <button type="button" class="modal-close" id="modal-close-btn" aria-label="Close early access modal">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        <div id="modal-form-content">
          <div class="modal-header">
            <div class="section-tag" style="margin-bottom: 0.5rem;">VIP Access</div>
            <h3 id="modal-title">Join the Private Beta</h3>
            <p>
              Be the first to access the AI jurisdiction simulator, receive a complimentary UAE structuring review, and lock in AED 2,500 in launch credits.
            </p>
          </div>

          <form id="early-access-form" novalidate>
            <div class="form-group">
              <label for="founder-name" class="form-label">Full Name</label>
              <input
                type="text"
                id="founder-name"
                name="name"
                class="form-input"
                placeholder="e.g., Sarah Al-Mansoor"
                required
              />
            </div>

            <div class="form-group">
              <label for="founder-email" class="form-label">Business / Work Email</label>
              <input
                type="email"
                id="founder-email"
                name="email"
                class="form-input"
                placeholder="sarah@innovate-tech.ae"
                required
              />
            </div>

            <div class="form-group">
              <label for="target-jurisdiction" class="form-label">Target Jurisdiction Interest</label>
              <select id="target-jurisdiction" name="jurisdiction" class="form-select">
                <option value="undecided">Not Sure — Need AI Recommendation</option>
                <option value="freezone">Dubai Free Zone (e.g. DMCC, IFZA, DIFC)</option>
                <option value="mainland">Dubai Mainland (DED - 100% Foreign Ownership)</option>
                <option value="dual">Dual License (Free Zone + Mainland Branch)</option>
              </select>
            </div>

            <div class="form-group">
              <label for="setup-timeline" class="form-label">Planned Launch Timeline</label>
              <select id="setup-timeline" name="timeline" class="form-select">
                <option value="immediate">Immediate (Within 30 Days)</option>
                <option value="q1">1 - 3 Months</option>
                <option value="q2">3 - 6 Months</option>
                <option value="researching">Just Researching for Future Expansion</option>
              </select>
            </div>

            <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1rem;" id="submit-waitlist-btn">
              Secure My Beta Invitation
            </button>
          </form>
        </div>

        <!-- Success Feedback State -->
        <div class="modal-success-state" id="modal-success-state">
          <div class="success-icon" aria-hidden="true">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>
          <h3>You're on the Priority List!</h3>
          <p style="margin-top: 0.5rem; margin-bottom: 1.5rem;">
            Thank you for registering. Our team has reserved your AED 2,500 fee credit and will send your private platform credentials shortly.
          </p>
          <button type="button" class="btn btn-secondary" id="modal-done-btn" style="width: 100%;">
            Return to Overview
          </button>
        </div>
      </div>
    </div>
  `;
}

export function initEarlyAccessModal() {
  const modal = document.getElementById('early-access-modal');
  const closeBtn = document.getElementById('modal-close-btn');
  const doneBtn = document.getElementById('modal-done-btn');
  const form = document.getElementById('early-access-form');
  const formContent = document.getElementById('modal-form-content');
  const successState = document.getElementById('modal-success-state');
  const triggers = document.querySelectorAll('.early-access-trigger');

  if (!modal) return;

  const openModal = () => {
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
    const firstInput = document.getElementById('founder-name');
    if (firstInput) setTimeout(() => firstInput.focus(), 100);
  };

  const closeModal = () => {
    modal.classList.remove('open');
    document.body.style.overflow = '';
  };

  triggers.forEach((trigger) => {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      openModal();
    });
  });

  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (doneBtn) doneBtn.addEventListener('click', closeModal);

  // Close on backdrop click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeModal();
    }
  });

  // Close on Escape key
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('open')) {
      closeModal();
    }
  });

  // Handle form submission
  if (form && formContent && successState) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const emailInput = document.getElementById('founder-email');
      const nameInput = document.getElementById('founder-name');

      if (!nameInput.value.trim()) {
        nameInput.focus();
        return;
      }
      if (!emailInput.value.trim() || !emailInput.checkValidity()) {
        emailInput.focus();
        return;
      }

      // Simulate instantaneous submission & transition to success
      formContent.style.display = 'none';
      successState.classList.add('active');
    });
  }
}
