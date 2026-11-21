/**
 * Footer Component
 * Includes verified official Dubai resource directory, formal legal/advisory disclaimer,
 * platform navigation, and copyright notices.
 */

import { siteConfig, navLinks, officialDubaiResources } from '../data/content.js';

export function renderFooter() {
  const currentYear = new Date().getFullYear();

  return `
    <footer class="site-footer" role="contentinfo">
      <div class="container">
        <!-- Top Directory Columns -->
        <div class="footer-top">
          <!-- Brand & Mission Column -->
          <div class="footer-brand">
            <a href="#" class="nav-brand" style="margin-bottom: 0.75rem;">
              <div class="brand-icon" aria-hidden="true" style="width: 32px; height: 32px;">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polygon points="12 2 19 21 12 17 5 21 12 2"></polygon>
                </svg>
              </div>
              <span class="brand-text" style="font-size: 1.15rem;">
                ${siteConfig.wordmark.prefix} <span class="highlight">${siteConfig.wordmark.highlight}</span>
              </span>
            </a>
            <p>
              Autonomous business setup copilot, AI jurisdiction optimizer, and bank-ready preparation engine for founders expanding to the United Arab Emirates.
            </p>
          </div>

          <!-- Official Dubai Government & Authority Resources -->
          <div class="footer-col">
            <h4>Official Dubai Resources</h4>
            <ul class="official-links-list">
              ${officialDubaiResources
                .map(
                  (res) => `
                <li>
                  <a href="${res.url}" target="_blank" rel="noopener noreferrer" class="footer-ext-link">
                    <span>${res.name}</span>
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                      <polyline points="15 3 21 3 21 9"></polyline>
                      <line x1="10" y1="14" x2="21" y2="3"></line>
                    </svg>
                  </a>
                </li>
              `
                )
                .join('')}
            </ul>
          </div>

          <!-- Platform Navigation -->
          <div class="footer-col">
            <h4>Platform & Features</h4>
            <ul>
              ${navLinks
                .map(
                  (link) => `
                <li><a href="${link.href}">${link.label}</a></li>
              `
                )
                .join('')}
              <li><a href="#setup-preview">Setup Path Preview</a></li>
              <li><a href="#waitlist">Early Access Waitlist</a></li>
            </ul>
          </div>

          <!-- Sovereign Governance & Privacy -->
          <div class="footer-col">
            <h4>Sovereignty & Standards</h4>
            <ul>
              <li><a href="#security">UAE PDPL (Decree-Law No. 45/2021)</a></li>
              <li><a href="#security">Zero-Knowledge Langfuse Observability</a></li>
              <li><a href="#security">AES-256 Cloud Encryption</a></li>
              <li><a href="#faq">Human-in-the-Loop Safeguards</a></li>
            </ul>
          </div>
        </div>

        <!-- Prominent Legal / Advisory Disclaimer -->
        <div class="footer-disclaimer-box">
          <div class="disclaimer-header">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
            <strong>Regulatory & Legal Advisory Disclaimer</strong>
          </div>
          <p>
            Dubai BizNavigator is an autonomous artificial intelligence software preparation co-pilot and decision-support tool. Dubai BizNavigator does not provide licensed legal advice, render formal legal opinions, practice UAE law, or substitute for authorized legal practitioners, advocates, or registered Public Relations Officers (PROs). Trade license issuance, corporate tax registrations, visa approvals, and corporate bank account authorizations remain subject to final regulatory review and discretionary approval by the Dubai Department of Economy and Tourism (DET), relevant UAE Free Zone Authorities, the UAE Federal Tax Authority (FTA), the Ministry of Human Resources and Emiratisation (MOHRE), and participating financial institutions.
          </p>
        </div>

        <!-- Bottom Copyright Row -->
        <div class="footer-bottom">
          <div class="copyright-text">
            &copy; ${currentYear} ${siteConfig.name}. All rights reserved.
          </div>
          <div class="footer-bottom-links">
            <span>Sovereignty-Engineered in Dubai, United Arab Emirates</span>
            <span class="sep">•</span>
            <a href="#security">Data Privacy Policy</a>
            <span class="sep">•</span>
            <a href="#faq">Terms of Service</a>
          </div>
        </div>
      </div>
    </footer>
  `;
}
