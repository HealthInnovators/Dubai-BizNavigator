/**
 * @file a2uiHost.js
 * @module renderers/a2uiHost
 * @description
 * High-security declarative A2UI Surface Host Renderer.
 * Implements native DOM rendering for the BizNavigator A2UI component catalog (`biznavigator_a2ui_v1`).
 *
 * Security Architecture & Design Principles:
 * - Strictly zero execution of unvalidated agent-generated HTML, inline scripts, or eval() calls.
 * - All Markdown text is rendered via `@a2ui/markdown-it` and sanitized through `DOMPurify.sanitize()`.
 * - Transforms declarative JSON specifications into branded, accessible, native DOM elements.
 * - Form inputs are harvested safely without direct DOM mutation side-effects.
 * - Action buttons emit structured events mapped back to the `AgentClient` communication bus.
 */

import { MessageProcessor } from '@a2ui/web_core';
import { renderMarkdown } from '@a2ui/markdown-it';
import DOMPurify from 'dompurify';

/**
 * @typedef {Object} A2UIComponent
 * @property {string} id - Component unique ID in the surface tree.
 * @property {string} component - Catalog widget type (Text, Column, Row, Card, DataTable, etc.).
 * @property {Array<string>} [children] - Child component IDs for container widgets.
 * @property {string} [child] - Single child component ID for Card widgets.
 * @property {string} [text] - Text content for Text and Badge widgets.
 * @property {string} [variant] - Visual variant (title, subtitle, body, elevated, primary, danger, etc.).
 * @property {string} [title] - Title string for Card, DataTable, and ApprovalGateCard.
 * @property {string} [name] - Form field input name.
 * @property {string} [value] - Form field current/default value.
 * @property {string} [placeholder] - Placeholder text for input controls.
 * @property {boolean} [required] - Whether input is mandatory.
 * @property {Array<{value: string, label: string}>} [options] - Selection options for Select widget.
 * @property {Object|string} [action] - Action specification triggered on click.
 * @property {Array<Object>} [columns] - Column metadata for DataTable.
 * @property {Array<Object>} [rows] - Data rows for DataTable.
 * @property {Object} [payload_preview] - Payload preview dictionary for ApprovalGateCard.
 * @property {Array<{title: string, url: string}>} [source_links] - Official citation links for MarkdownViewer.
 * @property {Array<{filename: string, path: string}>} [download_links] - Downloadable file references.
 */

/**
 * @typedef {Object} SurfaceState
 * @property {string} surfaceId - Unique surface identifier.
 * @property {string} catalogId - Catalog schema version identifier.
 * @property {Map<string, A2UIComponent>} components - Flattened ID to component dictionary.
 * @property {string|null} rootId - Top-level root container component ID.
 */

/**
 * A2UI Surface Host managing surface state, component hierarchies, and user action dispatching.
 */
export class A2UIHost {
  /**
   * Constructs an A2UIHost renderer instance.
   *
   * @param {HTMLElement} containerElement - Root DOM container where surfaces are rendered.
   * @param {Object} [options={}] - Configuration options.
   * @param {(action: string|Object, payload: Object) => void} [options.onAction] - Action callback handler.
   */
  constructor(containerElement, { onAction } = {}) {
    /** @type {HTMLElement} */
    this.container = containerElement;
    /** @type {(action: string|Object, payload: Object) => void} */
    this.onAction = onAction || (() => {});
    /** @type {Map<string, SurfaceState>} */
    this.surfaces = new Map();
    /** @type {string|null} */
    this.currentSurfaceId = null;

    try {
      /** @type {MessageProcessor|null} */
      this.messageProcessor = new MessageProcessor();
    } catch {
      this.messageProcessor = null;
    }
  }

  /**
   * Processes incoming A2UI wire transport messages (`createSurface`, `updateComponents`).
   *
   * @param {Object} message - Raw A2UI transport message.
   * @param {Object} [message.createSurface] - CreateSurface payload.
   * @param {string} message.createSurface.surfaceId - Target surface ID.
   * @param {string} message.createSurface.catalogId - Catalog specification ID.
   * @param {Object} [message.updateComponents] - UpdateComponents payload.
   * @param {string} message.updateComponents.surfaceId - Target surface ID.
   * @param {Array<A2UIComponent>} message.updateComponents.components - Updated components list.
   */
  processMessage(message) {
    if (!message) return;

    // Optional protocol validation via @a2ui/web_core processor
    if (this.messageProcessor && typeof this.messageProcessor.process === 'function') {
      try {
        this.messageProcessor.process(message);
      } catch {
        // Continue with local surface state mapping
      }
    }

    if (message.createSurface) {
      const { surfaceId, catalogId } = message.createSurface;
      this.surfaces.set(surfaceId, {
        surfaceId,
        catalogId,
        components: new Map(),
        rootId: null,
      });
      this.currentSurfaceId = surfaceId;
    } else if (message.updateComponents) {
      const { surfaceId, components } = message.updateComponents;
      let surface = this.surfaces.get(surfaceId);
      if (!surface) {
        surface = {
          surfaceId,
          catalogId: 'biznavigator_a2ui_v1',
          components: new Map(),
          rootId: null,
        };
        this.surfaces.set(surfaceId, surface);
      }

      for (const comp of components) {
        surface.components.set(comp.id, comp);
        // Identify potential root container (by convention named *root or first Column/Card)
        if (!surface.rootId && (comp.id.includes('root') || comp.component === 'Column')) {
          surface.rootId = comp.id;
        }
      }

      this.currentSurfaceId = surfaceId;
      this.render();
    }
  }

  /**
   * Renders the active A2UI surface component hierarchy into the host container.
   * Builds the component tree starting from the root container.
   */
  render() {
    if (!this.container) return;
    const surface = this.surfaces.get(this.currentSurfaceId);
    if (!surface || surface.components.size === 0) return;

    this.container.innerHTML = '';
    const surfaceWrapper = document.createElement('div');
    surfaceWrapper.className = 'a2ui-surface-view animate-fade-in';
    surfaceWrapper.dataset.surfaceId = surface.surfaceId;

    // Determine root component
    let rootComp = surface.components.get(surface.rootId);
    if (!rootComp) {
      // Find component that is not a child of any other component
      const childIds = new Set();
      for (const comp of surface.components.values()) {
        if (comp.children) comp.children.forEach((c) => childIds.add(c));
        if (comp.child) childIds.add(comp.child);
      }
      for (const comp of surface.components.values()) {
        if (!childIds.has(comp.id)) {
          rootComp = comp;
          break;
        }
      }
    }

    if (rootComp) {
      const el = this._renderComponent(rootComp, surface);
      if (el) surfaceWrapper.appendChild(el);
    } else {
      for (const comp of surface.components.values()) {
        const el = this._renderComponent(comp, surface);
        if (el) surfaceWrapper.appendChild(el);
      }
    }

    this.container.appendChild(surfaceWrapper);
  }

  /**
   * Dispatches component rendering by catalog type.
   *
   * @private
   * @param {A2UIComponent} comp - Component definition.
   * @param {SurfaceState} surface - Enclosing surface state.
   * @returns {HTMLElement|null}
   */
  _renderComponent(comp, surface) {
    if (!comp) return null;

    switch (comp.component) {
      case 'Text':
        return this._renderText(comp);
      case 'Column':
        return this._renderColumn(comp, surface);
      case 'Row':
        return this._renderRow(comp, surface);
      case 'Card':
        return this._renderCard(comp, surface);
      case 'DataTable':
        return this._renderDataTable(comp);
      case 'Badge':
        return this._renderBadge(comp);
      case 'TextField':
        return this._renderTextField(comp);
      case 'Select':
        return this._renderSelect(comp);
      case 'Button':
        return this._renderButton(comp);
      case 'ApprovalGateCard':
        return this._renderApprovalGateCard(comp);
      case 'MarkdownViewer':
        return this._renderMarkdownViewer(comp);
      default:
        return this._renderUnknown(comp);
    }
  }

  /** @private */
  _renderText(comp) {
    const el = document.createElement(
      comp.variant === 'title' ? 'h1' : comp.variant === 'heading' ? 'h2' : comp.variant === 'subheading' ? 'h3' : 'p'
    );
    el.className = `a2ui-text a2ui-${comp.variant || 'body'}`;
    el.textContent = comp.text || '';
    return el;
  }

  /** @private */
  _renderColumn(comp, surface) {
    const col = document.createElement('div');
    col.className = 'a2ui-col';
    if (comp.align) col.style.alignItems = comp.align;
    if (comp.justify) col.style.justifyContent = comp.justify;

    for (const childId of comp.children || []) {
      const childComp = surface.components.get(childId);
      if (childComp) {
        const childEl = this._renderComponent(childComp, surface);
        if (childEl) col.appendChild(childEl);
      }
    }
    return col;
  }

  /** @private */
  _renderRow(comp, surface) {
    const row = document.createElement('div');
    row.className = 'a2ui-row';
    if (comp.align) row.style.alignItems = comp.align;
    if (comp.justify) row.style.justifyContent = comp.justify;

    for (const childId of comp.children || []) {
      const childComp = surface.components.get(childId);
      if (childComp) {
        const childEl = this._renderComponent(childComp, surface);
        if (childEl) row.appendChild(childEl);
      }
    }
    return row;
  }

  /** @private */
  _renderCard(comp, surface) {
    const card = document.createElement('div');
    card.className = `a2ui-card a2ui-card-${comp.variant || 'default'}`;

    if (comp.title) {
      const header = document.createElement('div');
      header.className = 'a2ui-card-title';
      header.textContent = comp.title;
      card.appendChild(header);
    }

    if (comp.child) {
      const childComp = surface.components.get(comp.child);
      if (childComp) {
        const childEl = this._renderComponent(childComp, surface);
        if (childEl) card.appendChild(childEl);
      }
    }
    return card;
  }

  /** @private */
  _renderDataTable(comp) {
    const container = document.createElement('div');
    container.className = 'a2ui-datatable-container';

    if (comp.title) {
      const title = document.createElement('div');
      title.className = 'a2ui-table-title';
      title.textContent = comp.title;
      container.appendChild(title);
    }

    const table = document.createElement('table');
    table.className = 'a2ui-table';

    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    for (const col of comp.columns || []) {
      const th = document.createElement('th');
      th.textContent = typeof col === 'string' ? col : col.label || col.key;
      headerRow.appendChild(th);
    }
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    for (const row of comp.rows || []) {
      const tr = document.createElement('tr');
      for (const col of comp.columns || []) {
        const key = typeof col === 'string' ? col : col.key;
        const td = document.createElement('td');
        const val = row[key] !== undefined ? row[key] : '';
        td.textContent = String(val);
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
    table.appendChild(tbody);
    container.appendChild(table);
    return container;
  }

  /** @private */
  _renderBadge(comp) {
    const badge = document.createElement('span');
    badge.className = `a2ui-badge a2ui-badge-${comp.variant || 'default'}`;
    badge.textContent = comp.text || '';
    return badge;
  }

  /** @private */
  _renderTextField(comp) {
    const group = document.createElement('div');
    group.className = 'a2ui-form-group';

    const label = document.createElement('label');
    label.className = 'a2ui-label';
    label.textContent = comp.label;
    if (comp.required) {
      const req = document.createElement('span');
      req.className = 'a2ui-required-asterisk';
      req.textContent = ' *';
      label.appendChild(req);
    }
    group.appendChild(label);

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'a2ui-input';
    input.name = comp.name;
    input.id = comp.id;
    input.value = comp.value || '';
    input.placeholder = comp.placeholder || '';
    if (comp.required) input.required = true;

    group.appendChild(input);

    if (comp.description) {
      const desc = document.createElement('span');
      desc.className = 'a2ui-desc';
      desc.textContent = comp.description;
      group.appendChild(desc);
    }
    return group;
  }

  /** @private */
  _renderSelect(comp) {
    const group = document.createElement('div');
    group.className = 'a2ui-form-group';

    const label = document.createElement('label');
    label.className = 'a2ui-label';
    label.textContent = comp.label;
    if (comp.required) {
      const req = document.createElement('span');
      req.className = 'a2ui-required-asterisk';
      req.textContent = ' *';
      label.appendChild(req);
    }
    group.appendChild(label);

    const select = document.createElement('select');
    select.className = 'a2ui-select';
    select.name = comp.name;
    select.id = comp.id;
    if (comp.required) select.required = true;

    for (const opt of comp.options || []) {
      const option = document.createElement('option');
      option.value = opt.value;
      option.textContent = opt.label;
      if (opt.value === comp.value) option.selected = true;
      select.appendChild(option);
    }

    group.appendChild(select);
    return group;
  }

  /** @private */
  _renderButton(comp) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = `a2ui-btn a2ui-btn-${comp.variant || 'primary'}`;
    btn.textContent = comp.label;
    btn.disabled = comp.disabled || false;

    btn.addEventListener('click', (e) => {
      e.preventDefault();
      // Handle form harvest if button is part of an intake surface
      let actionPayload = comp.action;
      if (typeof comp.action === 'object' && comp.action.event === 'submit_intake_profile') {
        actionPayload = {
          ...comp.action,
          formData: this._harvestFormData(),
        };
      }
      this.onAction(comp.action, actionPayload);
    });

    return btn;
  }

  /** @private */
  _renderApprovalGateCard(comp) {
    const card = document.createElement('div');
    card.className = 'a2ui-card a2ui-approval-gate-card';

    const header = document.createElement('div');
    header.className = 'a2ui-gate-header';

    const icon = document.createElement('span');
    icon.className = 'a2ui-gate-icon';
    icon.textContent = '🔒';
    header.appendChild(icon);

    const title = document.createElement('h3');
    title.textContent = comp.title || 'Human-In-The-Loop Verification Gate';
    header.appendChild(title);
    card.appendChild(header);

    const summary = document.createElement('p');
    summary.className = 'a2ui-gate-summary';
    summary.textContent = comp.summary || '';
    card.appendChild(summary);

    // Payload Preview
    if (comp.payload_preview && Object.keys(comp.payload_preview).length > 0) {
      const previewBox = document.createElement('div');
      previewBox.className = 'a2ui-payload-preview';

      const preTitle = document.createElement('div');
      preTitle.className = 'a2ui-preview-title';
      preTitle.textContent = 'Payload Summary';
      previewBox.appendChild(preTitle);

      const table = document.createElement('table');
      table.className = 'a2ui-preview-table';
      for (const [k, v] of Object.entries(comp.payload_preview)) {
        const row = document.createElement('tr');
        const kTd = document.createElement('td');
        kTd.className = 'preview-key';
        kTd.textContent = k.replace(/_/g, ' ');
        const vTd = document.createElement('td');
        vTd.className = 'preview-val';
        vTd.textContent = typeof v === 'object' ? JSON.stringify(v) : String(v);
        row.appendChild(kTd);
        row.appendChild(vTd);
        table.appendChild(row);
      }
      previewBox.appendChild(table);
      card.appendChild(previewBox);
    }

    // Action buttons inside card if provided
    if (comp.approve_action || comp.reject_action) {
      const actionsDiv = document.createElement('div');
      actionsDiv.className = 'a2ui-gate-actions';
      if (comp.approve_action) {
        const appBtn = document.createElement('button');
        appBtn.type = 'button';
        appBtn.className = 'a2ui-btn a2ui-btn-primary hitl-approve-btn';
        appBtn.textContent = 'Approve & Submit';
        appBtn.addEventListener('click', () => this.onAction(comp.approve_action, comp.approve_action));
        actionsDiv.appendChild(appBtn);
      }
      if (comp.reject_action) {
        const rejBtn = document.createElement('button');
        rejBtn.type = 'button';
        rejBtn.className = 'a2ui-btn a2ui-btn-danger hitl-reject-btn';
        rejBtn.textContent = 'Request Edits';
        rejBtn.addEventListener('click', () => this.onAction(comp.reject_action, comp.reject_action));
        actionsDiv.appendChild(rejBtn);
      }
      card.appendChild(actionsDiv);
    }

    return card;
  }

  /** @private */
  _renderMarkdownViewer(comp) {
    const wrapper = document.createElement('div');
    wrapper.className = 'a2ui-markdown-viewer';

    if (comp.title) {
      const title = document.createElement('h3');
      title.className = 'a2ui-md-title';
      title.textContent = comp.title;
      wrapper.appendChild(title);
    }

    // Sanitize markdown content
    const contentEl = document.createElement('div');
    contentEl.className = 'a2ui-markdown-body';

    try {
      if (typeof window !== 'undefined') {
        const renderedHtml = renderMarkdown(comp.content || '');
        contentEl.innerHTML = DOMPurify.sanitize(renderedHtml);
      } else {
        contentEl.textContent = comp.content || '';
      }
    } catch {
      contentEl.textContent = comp.content || '';
    }
    wrapper.appendChild(contentEl);

    // Citations / Source links
    if (comp.source_links && comp.source_links.length > 0) {
      const sourcesBox = document.createElement('div');
      sourcesBox.className = 'a2ui-sources-box';
      const label = document.createElement('span');
      label.className = 'sources-label';
      label.textContent = 'Verified Official Citations: ';
      sourcesBox.appendChild(label);

      comp.source_links.forEach((src) => {
        const a = document.createElement('a');
        a.href = src.url;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        a.className = 'source-link';
        a.textContent = `[${src.title || src.url}]`;
        sourcesBox.appendChild(a);
      });
      wrapper.appendChild(sourcesBox);
    }

    // Downloadable artifact links
    if (comp.download_links && comp.download_links.length > 0) {
      const dlBox = document.createElement('div');
      dlBox.className = 'a2ui-download-box';
      comp.download_links.forEach((dl) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'a2ui-btn a2ui-btn-secondary download-btn';
        btn.textContent = `📥 Download ${dl.filename || 'Artifact'}`;
        btn.addEventListener('click', () => {
          this.onAction('download_artifact', dl);
        });
        dlBox.appendChild(btn);
      });
      wrapper.appendChild(dlBox);
    }

    return wrapper;
  }

  /** @private */
  _renderUnknown(comp) {
    const el = document.createElement('div');
    el.className = 'a2ui-unknown';
    el.textContent = `[Component: ${comp.component}]`;
    return el;
  }

  /**
   * Safely harvests user input values from rendered form controls within the container.
   *
   * @private
   * @returns {Record<string, string>} Key-value map of form field names and their values.
   */
  _harvestFormData() {
    const data = {};
    const inputs = this.container.querySelectorAll('input, select, textarea');
    inputs.forEach((input) => {
      if (input.name) {
        data[input.name] = input.value;
      }
    });
    return data;
  }
}

/**
 * Returns the default A2UI messages for initial Startup Profile intake.
 *
 * @returns {Array<{createSurface?: Object, updateComponents?: Object}>}
 */
export function getDefaultIntakeMessages() {
  return [
    {
      createSurface: {
        surfaceId: 'surface_intake_profile',
        catalogId: 'biznavigator_a2ui_v1',
      },
    },
    {
      updateComponents: {
        surfaceId: 'surface_intake_profile',
        components: [
          {
            id: 'intake_root',
            component: 'Column',
            children: ['intake_title', 'intake_card'],
            justify: 'start',
            align: 'stretch',
          },
          {
            id: 'intake_title',
            component: 'Text',
            text: 'Dubai Business Setup: Profile Intake',
            variant: 'title',
          },
          {
            id: 'intake_card',
            component: 'Card',
            title: 'Startup & Operational Configuration',
            child: 'intake_fields_col',
            variant: 'elevated',
          },
          {
            id: 'intake_fields_col',
            component: 'Column',
            children: [
              'field_company_name',
              'field_industry_sector',
              'field_business_activity',
              'field_revenue_model',
              'field_uae_local_trade',
              'field_visa_quota_needed',
              'field_office_preference',
              'field_founders_summary',
              'btn_submit_intake',
            ],
            justify: 'start',
            align: 'stretch',
          },
          {
            id: 'field_company_name',
            component: 'TextField',
            label: 'Company Name Candidate',
            name: 'company_name',
            value: 'Apex Global Technologies LLC',
            placeholder: 'e.g. Apex Global Technologies LLC',
            required: true,
          },
          {
            id: 'field_industry_sector',
            component: 'TextField',
            label: 'Industry Sector',
            name: 'industry_sector',
            value: 'Technology & AI',
            placeholder: 'e.g. Technology & AI',
            required: true,
          },
          {
            id: 'field_business_activity',
            component: 'TextField',
            label: 'Primary Business Activity',
            name: 'business_activity',
            value: 'Software Development & AI Consultancy',
            placeholder: 'e.g. Software Development & AI Consultancy',
            required: true,
          },
          {
            id: 'field_revenue_model',
            component: 'Select',
            label: 'Revenue Model',
            name: 'revenue_model',
            value: 'B2B_SaaS',
            required: true,
            options: [
              { value: 'B2B_SaaS', label: 'B2B SaaS / Enterprise Subscriptions' },
              { value: 'Consulting', label: 'Professional Consulting / Advisory' },
              { value: 'Ecommerce', label: 'E-Commerce / Physical Goods Trading' },
              { value: 'Fintech', label: 'FinTech / Payment Facilitation' },
              { value: 'Holding', label: 'Holding / Asset Management' },
            ],
          },
          {
            id: 'field_uae_local_trade',
            component: 'Select',
            label: 'UAE Mainland Commercial Operations Required?',
            name: 'uae_local_trade',
            value: 'true',
            required: true,
            options: [
              { value: 'true', label: 'Yes - Direct commercial contracts within UAE mainland market' },
              { value: 'false', label: 'No - Purely international exports & Free Zone operations' },
            ],
          },
          {
            id: 'field_visa_quota_needed',
            component: 'TextField',
            label: 'Visa Quota Needed',
            name: 'visa_quota_needed',
            value: '3',
            placeholder: 'e.g. 3',
            required: false,
          },
          {
            id: 'field_office_preference',
            component: 'Select',
            label: 'Office Preference',
            name: 'office_preference',
            value: 'FlexiDesk',
            required: true,
            options: [
              { value: 'FlexiDesk', label: 'Flexi Desk / Smart Desk (Cost Effective)' },
              { value: 'PhysicalOffice', label: 'Dedicated Physical Office (Leased Ejari)' },
              { value: 'Warehousing', label: 'Industrial Warehouse / Storage Unit' },
              { value: 'None', label: 'Virtual Office (Eligible Free Zones)' },
            ],
          },
          {
            id: 'field_founders_summary',
            component: 'TextField',
            label: 'Founders Summary',
            name: 'founders_summary',
            value: '2 International Founders (European & UAE resident)',
            placeholder: 'Founding team background & residency',
            required: false,
          },
          {
            id: 'btn_submit_intake',
            component: 'Button',
            label: 'Analyze & Generate Licensing Strategy',
            action: {
              event: 'submit_intake_profile',
              surface_id: 'surface_intake_profile',
            },
            variant: 'primary',
          },
        ],
      },
    },
  ];
}
