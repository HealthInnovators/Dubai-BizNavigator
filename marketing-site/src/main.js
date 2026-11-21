/**
 * Dubai BizNavigator - Main Entry Point
 */

import './styles/tokens.css';
import './styles/main.css';

import { renderNavbar, initNavbar } from './components/navbar.js';
import { renderHero, initHeroInteractive } from './components/hero.js';
import { renderTrustStrip } from './components/trustStrip.js';
import {
  renderWorkflowSection,
  initWorkflowSection
} from './components/workflowSection.js';
import {
  renderSetupPreviewWidget,
  initSetupPreviewWidget
} from './components/setupPreviewWidget.js';
import {
  renderJurisdictionComparison,
  initJurisdictionComparison
} from './components/jurisdictionComparison.js';
import { renderPricingSection } from './components/pricingSection.js';
import { renderSecurity } from './components/security.js';
import {
  renderFAQAccordion,
  initFAQAccordion
} from './components/faqAccordion.js';
import {
  renderWaitlistForm,
  initWaitlistForm
} from './components/waitlistForm.js';
import {
  renderEarlyAccessModal,
  initEarlyAccessModal
} from './components/earlyAccessModal.js';
import { renderFooter } from './components/footer.js';

function bootstrapApp() {
  const appElement = document.getElementById('app');
  if (!appElement) {
    console.error('Root #app container not found.');
    return;
  }

  // Render semantic HTML layout
  appElement.innerHTML = `
    ${renderNavbar()}
    <main id="main-content">
      ${renderHero()}
      ${renderTrustStrip()}
      ${renderWorkflowSection()}
      ${renderSetupPreviewWidget()}
      ${renderJurisdictionComparison()}
      ${renderPricingSection()}
      ${renderSecurity()}
      ${renderFAQAccordion()}
      ${renderWaitlistForm()}
    </main>
    ${renderFooter()}
    ${renderEarlyAccessModal()}
  `;

  // Initialize interactive behaviors
  initNavbar();
  initHeroInteractive();
  initWorkflowSection();
  initSetupPreviewWidget();
  initJurisdictionComparison();
  initFAQAccordion();
  initWaitlistForm();
  initEarlyAccessModal();
}

// Ensure execution after DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrapApp);
} else {
  bootstrapApp();
}
