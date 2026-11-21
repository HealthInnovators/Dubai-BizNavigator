/**
 * Navbar Component
 * Sticky top navigation bar with Dubai BizNavigator wordmark,
 * section links, and "Join Early Access" CTA button.
 */

import { siteConfig, navLinks } from '../data/content.js';

export function renderNavbar() {
  return `
    <header class="navbar" id="top-navbar" role="banner">
      <div class="container navbar-inner">
        <a href="#" class="nav-brand" aria-label="Dubai BizNavigator Home">
          <div class="brand-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="12 2 19 21 12 17 5 21 12 2"></polygon>
            </svg>
          </div>
          <span class="brand-text">
            ${siteConfig.wordmark.prefix} <span class="highlight">${siteConfig.wordmark.highlight}</span>
            <span class="brand-badge">${siteConfig.wordmark.badge}</span>
          </span>
        </a>

        <nav class="nav-links" aria-label="Primary Navigation">
          ${navLinks
            .map(
              (link) => `
            <a href="${link.href}" class="nav-link" data-nav-target="${link.href}">
              ${link.label}
            </a>
          `
            )
            .join('')}
        </nav>

        <div class="nav-actions">
          <button type="button" class="btn btn-primary btn-sm early-access-trigger" id="nav-cta-btn">
            ${siteConfig.earlyAccessCTA}
          </button>

          <button type="button" class="mobile-toggle" id="mobile-toggle-btn" aria-label="Toggle navigation menu" aria-expanded="false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile Menu Dropdown -->
      <div class="mobile-menu" id="mobile-menu" aria-hidden="true">
        ${navLinks
          .map(
            (link) => `
          <a href="${link.href}" class="nav-link mobile-nav-link" data-nav-target="${link.href}">
            ${link.label}
          </a>
        `
          )
          .join('')}
        <button type="button" class="btn btn-primary early-access-trigger" style="margin-top: 1rem; width: 100%;">
          ${siteConfig.earlyAccessCTA}
        </button>
      </div>
    </header>
  `;
}

export function initNavbar() {
  const toggleBtn = document.getElementById('mobile-toggle-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  const mobileLinks = document.querySelectorAll('.mobile-nav-link');

  if (toggleBtn && mobileMenu) {
    toggleBtn.addEventListener('click', () => {
      const isOpen = mobileMenu.classList.toggle('open');
      toggleBtn.setAttribute('aria-expanded', String(isOpen));
      mobileMenu.setAttribute('aria-hidden', String(!isOpen));
    });

    mobileLinks.forEach((link) => {
      link.addEventListener('click', () => {
        mobileMenu.classList.remove('open');
        toggleBtn.setAttribute('aria-expanded', 'false');
        mobileMenu.setAttribute('aria-hidden', 'true');
      });
    });
  }

  // Active link highlight on scroll
  const sections = document.querySelectorAll('section[id]');
  const desktopLinks = document.querySelectorAll('.nav-links .nav-link');

  const onScroll = () => {
    const scrollPos = window.scrollY + 120;
    sections.forEach((section) => {
      const top = section.offsetTop;
      const height = section.offsetHeight;
      const id = section.getAttribute('id');
      if (scrollPos >= top && scrollPos < top + height) {
        desktopLinks.forEach((link) => {
          if (link.getAttribute('href') === `#${id}`) {
            link.classList.add('active');
          } else {
            link.classList.remove('active');
          }
        });
      }
    });
  };

  window.addEventListener('scroll', onScroll, { passive: true });
}
