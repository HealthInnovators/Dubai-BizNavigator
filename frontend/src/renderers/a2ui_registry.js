/**
 * A2UI surface mounting and component catalog registry.
 */

export class A2UISurfaceMount {
  constructor(rootContainer) {
    this.rootContainer = rootContainer;
    this.catalog = new Map();
    this.registerStandardComponents();
  }

  register(componentName, renderFunction) {
    this.catalog.set(componentName, renderFunction);
  }

  registerStandardComponents() {
    this.register('ProgressTracker', (props) => {
      const container = document.createElement('div');
      container.className = 'a2ui-card';
      container.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h3 style="font-size: 1rem; color: #38bdf8;">${props.currentStep || 'Processing'}</h3>
          <span style="font-size: 0.85rem; color: #94a3b8;">${props.progress || 0}%</span>
        </div>
        <div class="progress-track">
          <div class="progress-bar" style="width: ${props.progress || 0}%;"></div>
        </div>
        <p style="font-size: 0.85rem; color: #cbd5e1;">${props.statusText || ''}</p>
      `;
      return container;
    });

    this.register('Card', (props) => {
      const card = document.createElement('div');
      card.className = 'a2ui-card';
      card.innerHTML = `
        <h3 style="font-size: 1.1rem; color: #f8fafc; margin-bottom: 0.25rem;">${props.title}</h3>
        <p style="font-size: 0.9rem; color: #cbd5e1; margin-bottom: 0.5rem;">${props.description}</p>
      `;
      return card;
    });
  }

  renderSurface(surfacePayload) {
    if (!surfacePayload || !surfacePayload.root) return;
    const { type, props } = surfacePayload.root;
    const renderer = this.catalog.get(type);

    if (renderer) {
      this.rootContainer.innerHTML = '';
      const element = renderer(props || {});
      this.rootContainer.appendChild(element);
    } else {
      console.warn(`[A2UI] No renderer registered for component type: ${type}`);
    }
  }
}
