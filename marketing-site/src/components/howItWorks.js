/**
 * How It Works Component
 * Visualizes the 4-step streamlined incorporation workflow.
 */

import { howItWorksSteps } from '../data/content.js';

export function renderHowItWorks() {
  return `
    <section id="how-it-works" aria-labelledby="how-it-works-title">
      <div class="container">
        <div class="section-header">
          <div class="section-tag">Autonomous Workflow</div>
          <h2 id="how-it-works-title">From Concept to Active Trade License</h2>
          <p>
            Eliminate traditional bureaucratic delays, opaque consultancy markups, and repetitive paperwork through an automated 4-stage pipeline.
          </p>
        </div>

        <div class="how-it-works-grid">
          ${howItWorksSteps
            .map(
              (step) => `
            <div class="card step-card" data-step="${step.step}">
              <div class="step-card-header">
                <div class="step-number">${step.step}</div>
                <span class="step-badge">${step.badge}</span>
              </div>
              <h3>${step.title}</h3>
              <p>${step.description}</p>
              <ul class="step-points">
                ${step.points
                  .map(
                    (point) => `
                  <li>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                    <span>${point}</span>
                  </li>
                `
                  )
                  .join('')}
              </ul>
            </div>
          `
            )
            .join('')}
        </div>
      </div>
    </section>
  `;
}
