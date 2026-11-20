/**
 * Dubai BizNavigator — Main Frontend Controller
 * Integrates AgentClient (FastAPI/SSE) and A2UIHost (@a2ui/web_core, @a2ui/lit, @a2ui/markdown-it)
 */

import { AgentClient, KNOWN_SUBAGENTS } from './services/agentClient.js';
import { A2UIHost, getDefaultIntakeMessages } from './renderers/a2uiHost.js';

document.addEventListener('DOMContentLoaded', async () => {
  // DOM Elements
  const alertsBtn = document.getElementById('alerts-btn');
  const alertsBadge = document.getElementById('alerts-badge');
  const alertsModal = document.getElementById('alerts-modal');
  const closeAlertsModalBtn = document.getElementById('close-alerts-modal-btn');
  const alertsModalContent = document.getElementById('alerts-modal-content');
  const refreshAlertsBtn = document.getElementById('refresh-alerts-btn');

  const sessionIdDisplay = document.getElementById('session-id-display');
  const systemStatusPill = document.getElementById('system-status');
  const systemStatusText = document.getElementById('system-status-text');

  const subagentTimelineEl = document.getElementById('subagent-timeline');
  const eventsLogEl = document.getElementById('events-log');
  const clearEventsBtn = document.getElementById('clear-events-btn');

  const surfaceTitleEl = document.getElementById('surface-title');
  const surfaceRootEl = document.getElementById('a2ui-surface-root');
  const exportArtifactsBtn = document.getElementById('export-artifacts-btn');
  const artifactsModal = document.getElementById('artifacts-modal');
  const closeArtifactsModalBtn = document.getElementById('close-artifacts-modal-btn');
  const artifactsModalContent = document.getElementById('artifacts-modal-content');

  const chatForm = document.getElementById('chat-form');
  const userInput = document.getElementById('user-input');
  const sendBtn = document.getElementById('send-btn');
  const quickPromptBtns = document.querySelectorAll('.quick-btn');

  // Core Instances
  const client = new AgentClient();
  let a2uiHost = null;
  let isStreaming = false;

  // Initialize A2UI Host
  a2uiHost = new A2UIHost(surfaceRootEl, {
    onAction: handleA2UIAction,
  });

  // Render Subagents Timeline Cards
  renderSubagentTimeline();

  // Initialize Session
  await initializeSession();

  // Wire Events
  wireEventListeners();

  /**
   * Initialize Session with backend
   */
  async function initializeSession() {
    try {
      updateSystemStatus('connecting', 'Connecting to Gateway...');
      const sessionData = await client.createSession();
      sessionIdDisplay.textContent = sessionData.workspace_id || sessionData.session_id;
      sessionIdDisplay.title = `Session: ${sessionData.session_id}\nWorkspace: ${sessionData.workspace_id}`;
      updateSystemStatus('online', 'Connected • UAE DET & Free Zones');
      logEvent('system', `Session created: ${sessionData.session_id.substring(0, 8)}... (Workspace: ${sessionData.workspace_id})`);

      // Render initial Startup Profile intake form via A2UI
      const intakeMessages = getDefaultIntakeMessages();
      for (const msg of intakeMessages) {
        a2uiHost.processMessage(msg);
      }
      surfaceTitleEl.textContent = 'Startup Profile & Formation Intake';

      // Load active regulatory alerts
      await checkRegulatoryAlerts();
    } catch (err) {
      console.error('Session initialization error:', err);
      updateSystemStatus('offline', 'Backend Offline');
      sessionIdDisplay.textContent = 'Offline';
      logEvent('system', `Failed to initialize session: ${err.message}`);

      // Fallback: render default intake surface anyway
      const intakeMessages = getDefaultIntakeMessages();
      for (const msg of intakeMessages) {
        a2uiHost.processMessage(msg);
      }
    }
  }

  /**
   * Render Subagent timeline cards
   */
  function renderSubagentTimeline() {
    subagentTimelineEl.innerHTML = '';
    KNOWN_SUBAGENTS.forEach((agent) => {
      const card = document.createElement('div');
      card.className = 'agent-timeline-item';
      card.id = `subagent-card-${agent.id}`;

      card.innerHTML = `
        <div class="agent-icon-box">${agent.icon}</div>
        <div class="agent-info">
          <div class="agent-header-row">
            <span class="agent-name">${agent.name}</span>
            <span class="agent-status-tag status-idle" id="tag-${agent.id}">IDLE</span>
          </div>
          <p class="agent-role">${agent.role}</p>
        </div>
      `;
      subagentTimelineEl.appendChild(card);
    });
  }

  /**
   * Update individual subagent visual state
   */
  function updateSubagentStatus(agentId, status, message = '') {
    if (!agentId) return;
    const normalizedId = agentId.toLowerCase().trim();
    const card = document.getElementById(`subagent-card-${normalizedId}`);
    const tag = document.getElementById(`tag-${normalizedId}`);

    if (!card || !tag) return;

    // Reset classes
    card.classList.remove('active');
    tag.className = 'agent-status-tag';

    const normalizedStatus = (status || 'idle').toLowerCase();
    switch (normalizedStatus) {
      case 'running':
      case 'working':
      case 'active':
        card.classList.add('active');
        tag.classList.add('status-running');
        tag.textContent = 'WORKING';
        break;
      case 'completed':
      case 'success':
      case 'ready':
        tag.classList.add('status-completed');
        tag.textContent = 'COMPLETED';
        break;
      case 'interrupted':
      case 'waiting_hitl':
        tag.classList.add('status-interrupted');
        tag.textContent = 'HITL GATE';
        break;
      default:
        tag.classList.add('status-idle');
        tag.textContent = 'IDLE';
        break;
    }

    if (message) {
      card.title = `${message}`;
    }
  }

  /**
   * Reset all subagent statuses
   */
  function resetAllSubagents() {
    KNOWN_SUBAGENTS.forEach((agent) => {
      updateSubagentStatus(agent.id, 'idle');
    });
  }

  /**
   * Update top status pill
   */
  function updateSystemStatus(state, text) {
    systemStatusPill.className = `pill-btn status-pill status-${state}`;
    systemStatusText.textContent = text;
  }

  /**
   * Append formatted entry to live event feed
   */
  function logEvent(type, text) {
    const entry = document.createElement('div');
    entry.className = `event-entry event-${type}`;

    const now = new Date();
    const timeStr = now.toTimeString().split(' ')[0];

    entry.innerHTML = `
      <span class="event-time">${timeStr}</span>
      <span class="event-body">${escapeHtml(text)}</span>
    `;

    eventsLogEl.prepend(entry);
    // Keep max 100 entries
    while (eventsLogEl.children.length > 100) {
      eventsLogEl.removeChild(eventsLogEl.lastChild);
    }
  }

  /**
   * Check Regulatory Alerts from backend
   */
  async function checkRegulatoryAlerts() {
    try {
      const data = await client.fetchWorkspaceAlerts();
      const count = data.alert_count || (data.alerts ? data.alerts.length : 0);
      alertsBadge.textContent = String(count);

      if (count > 0) {
        alertsBtn.classList.add('has-alerts');
        logEvent('progress', `Regulatory Monitor: ${count} active UAE legal/tax alert(s) detected.`);
      }

      // If A2UI surface returned in alerts response
      if (data.a2ui_surface && Array.isArray(data.a2ui_surface) && data.a2ui_surface.length > 0) {
        data.a2ui_surface.forEach((msg) => a2uiHost.processMessage(msg));
      }
    } catch (err) {
      console.warn('Regulatory alerts check failed:', err);
    }
  }

  /**
   * Handle user action triggered from A2UI widgets
   */
  async function handleA2UIAction(action, payload) {
    if (isStreaming) {
      logEvent('system', 'Workflow currently active. Please wait...');
      return;
    }

    let eventType = typeof action === 'string' ? action : action.event;

    logEvent('surface', `A2UI Action Triggered: ${eventType}`);

    if (eventType === 'submit_intake_profile') {
      const formData = payload.formData || {};
      const companyName = formData.company_name || 'My UAE Business';
      const prompt = `Analyze optimal licensing pathways (Mainland DET vs Free Zone) and draft registration payload for startup: ${JSON.stringify(formData)}`;

      logEvent('progress', `Submitting formation profile for "${companyName}"...`);
      await dispatchAgentStream(prompt);
    } else if (eventType === 'hitl_approve' || eventType === 'approve_hitl_filing') {
      logEvent('hitl', 'User confirmed Human-in-the-Loop decision gate: Approved & Submitted.');
      await dispatchHITLResume('hitl_approve', payload);
    } else if (eventType === 'hitl_reject' || eventType === 'request_edits') {
      logEvent('hitl', 'User requested edits on Human-in-the-Loop decision gate.');
      await dispatchHITLResume('hitl_reject', payload);
    } else if (eventType === 'download_artifact') {
      await downloadWorkspaceArtifact(payload.filename || payload.path || 'business_plan.md');
    } else if (eventType === 'select_jurisdiction') {
      const pathway = payload.pathway || 'DET_Mainland';
      await dispatchAgentStream(`User selected jurisdiction pathway: ${pathway}. Proceed with filing payload generation and compliance audit.`);
    }
  }

  /**
   * Dispatch streaming user instruction to agent
   */
  async function dispatchAgentStream(messageText) {
    if (!messageText || isStreaming) return;
    setStreamingState(true);

    try {
      await client.sendUserMessage(client.currentSessionId, messageText, {
        onAgentProgress: (evt) => {
          const agent = evt.agent_name || evt.agent || 'coordinator';
          const status = evt.status || 'running';
          const message = evt.message || (typeof evt.data === 'string' ? evt.data : JSON.stringify(evt.data || ''));

          updateSubagentStatus(agent, status, message);
          logEvent('progress', `[${agent}] ${message}`);

          if (evt.artifact_updated) {
            logEvent('progress', `📁 Artifact saved to workspace: ${evt.artifact_updated}`);
          }
        },

        onA2UISurface: (surfaceMsg) => {
          if (Array.isArray(surfaceMsg)) {
            surfaceMsg.forEach((m) => a2uiHost.processMessage(m));
          } else {
            a2uiHost.processMessage(surfaceMsg);
          }

          // Update header title if identifiable
          if (surfaceMsg.updateComponents) {
            const comps = surfaceMsg.updateComponents.components || [];
            const titleComp = comps.find((c) => c.variant === 'title' || c.id?.includes('title'));
            if (titleComp && titleComp.text) {
              surfaceTitleEl.textContent = titleComp.text;
            }
          }
        },

        onHitlInterrupt: (hitlEvt) => {
          updateSubagentStatus(hitlEvt.agent_name || 'form-automation-agent', 'interrupted');
          logEvent('hitl', `⏸️ HITL Interrupt: ${hitlEvt.message || 'Verification required before external API submission.'}`);
          surfaceTitleEl.textContent = '🔒 Human-in-the-Loop Decision Gate';
        },

        onComplete: (data) => {
          logEvent('system', 'Agentic workflow execution completed.');
          setStreamingState(false);
          checkRegulatoryAlerts();
        },

        onError: (err) => {
          logEvent('system', `Stream error: ${err.message}`);
          setStreamingState(false);
        },
      });
    } catch (err) {
      logEvent('system', `Execution failed: ${err.message}`);
      setStreamingState(false);
    }
  }

  /**
   * Resume HITL decision gate
   */
  async function dispatchHITLResume(actionType, updates) {
    setStreamingState(true);
    try {
      await client.approveHITL(
        client.currentSessionId,
        {
          action: actionType,
          payloadUpdates: updates,
        },
        {
          onAgentProgress: (evt) => {
            const agent = evt.agent_name || 'coordinator';
            updateSubagentStatus(agent, evt.status || 'running', evt.message);
            logEvent('progress', `[${agent}] ${evt.message || ''}`);
          },
          onA2UISurface: (surfaceMsg) => {
            if (Array.isArray(surfaceMsg)) {
              surfaceMsg.forEach((m) => a2uiHost.processMessage(m));
            } else {
              a2uiHost.processMessage(surfaceMsg);
            }
          },
          onComplete: () => {
            logEvent('system', 'HITL Gate processed. Workflow execution resumed and completed.');
            setStreamingState(false);
          },
          onError: (err) => {
            logEvent('system', `HITL error: ${err.message}`);
            setStreamingState(false);
          },
        }
      );
    } catch (err) {
      logEvent('system', `Failed to resume HITL: ${err.message}`);
      setStreamingState(false);
    }
  }

  /**
   * Download workspace artifact helper
   */
  async function downloadWorkspaceArtifact(filename) {
    try {
      logEvent('progress', `Fetching workspace artifact: ${filename}...`);
      const artifacts = await client.fetchWorkspaceArtifacts();
      if (!artifacts) throw new Error('No artifacts available.');

      let content = '';
      const cleanName = filename.replace(/^\/workspace\//, '');

      if (cleanName.includes('licensing') && artifacts.licensing_matrix_md) {
        content = artifacts.licensing_matrix_md;
      } else if (cleanName.includes('business') && artifacts.business_plan_md) {
        content = artifacts.business_plan_md;
      } else if (cleanName.includes('compliance') && artifacts.compliance_checklist_md) {
        content = artifacts.compliance_checklist_md;
      } else if (cleanName.includes('registration') && artifacts.registration_payload_json) {
        content = JSON.stringify(artifacts.registration_payload_json, null, 2);
      } else if (artifacts.files && artifacts.files[cleanName]) {
        content = artifacts.files[cleanName];
      } else {
        content = `# Dubai BizNavigator Artifact: ${cleanName}\n\nGenerated for session ${client.currentSessionId}.`;
      }

      // Trigger browser download
      const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = cleanName.endsWith('.md') || cleanName.endsWith('.json') ? cleanName : `${cleanName}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      logEvent('progress', `Downloaded ${a.download}`);
    } catch (err) {
      logEvent('system', `Artifact download failed: ${err.message}`);
    }
  }

  /**
   * Set streaming visual state
   */
  function setStreamingState(active) {
    isStreaming = active;
    sendBtn.disabled = active;
    userInput.disabled = active;
    if (active) {
      sendBtn.querySelector('.btn-text').textContent = 'Thinking...';
      sendBtn.querySelector('.btn-icon').textContent = '⏳';
    } else {
      sendBtn.querySelector('.btn-text').textContent = 'Send';
      sendBtn.querySelector('.btn-icon').textContent = '➔';
    }
  }

  /**
   * Wire UI events
   */
  function wireEventListeners() {
    // Chat form submit
    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = userInput.value.trim();
      if (!text || isStreaming) return;
      userInput.value = '';
      logEvent('system', `User: "${text}"`);
      await dispatchAgentStream(text);
    });

    // Enter to submit in textarea
    userInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit', { cancelable: true }));
      }
    });

    // Quick prompt buttons
    quickPromptBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        const prompt = btn.dataset.prompt;
        if (prompt && !isStreaming) {
          userInput.value = prompt;
          userInput.focus();
        }
      });
    });

    // Clear event feed
    clearEventsBtn.addEventListener('click', () => {
      eventsLogEl.innerHTML = '';
      logEvent('system', 'Event stream cleared.');
    });

    // Alerts Modal open/close
    alertsBtn.addEventListener('click', async () => {
      await showRegulatoryAlertsModal();
    });
    refreshAlertsBtn.addEventListener('click', async () => {
      await checkRegulatoryAlerts();
      await showRegulatoryAlertsModal();
    });
    closeAlertsModalBtn.addEventListener('click', () => {
      alertsModal.classList.add('hidden');
    });
    alertsModal.addEventListener('click', (e) => {
      if (e.target === alertsModal) alertsModal.classList.add('hidden');
    });

    // Artifacts Modal open/close
    exportArtifactsBtn.addEventListener('click', async () => {
      await showArtifactsModal();
    });
    closeArtifactsModalBtn.addEventListener('click', () => {
      artifactsModal.classList.add('hidden');
    });
    artifactsModal.addEventListener('click', (e) => {
      if (e.target === artifactsModal) artifactsModal.classList.add('hidden');
    });
  }

  /**
   * Show Regulatory Alerts Modal
   */
  async function showRegulatoryAlertsModal() {
    alertsModal.classList.remove('hidden');
    alertsModalContent.innerHTML = '<p class="text-muted">Loading UAE regulatory updates...</p>';

    try {
      const data = await client.fetchWorkspaceAlerts();
      const alerts = data.alerts || [];

      if (alerts.length === 0) {
        alertsModalContent.innerHTML = `
          <div class="alert-item">
            <div class="alert-item-header">
              <span class="alert-authority">UAE Ministry of Economy / DET</span>
              <span class="alert-date">Compliant</span>
            </div>
            <p class="alert-summary">
              No regulatory changes impacting your chosen business activities or jurisdiction have been published since the last check.
            </p>
          </div>
        `;
        return;
      }

      alertsModalContent.innerHTML = '';
      alerts.forEach((alert) => {
        const item = document.createElement('div');
        item.className = 'alert-item';
        item.innerHTML = `
          <div class="alert-item-header">
            <span class="alert-authority">${escapeHtml(alert.authority || 'UAE Authority')}</span>
            <span class="alert-date">${escapeHtml(alert.effective_date || '')}</span>
          </div>
          <p class="alert-summary">${escapeHtml(alert.change_summary || '')}</p>
          ${alert.source_url ? `<a href="${escapeHtml(alert.source_url)}" target="_blank" rel="noopener" class="source-link">View Official Gazette ↗</a>` : ''}
        `;
        alertsModalContent.appendChild(item);
      });
    } catch (err) {
      alertsModalContent.innerHTML = `<p class="text-danger">Failed to fetch alerts: ${err.message}</p>`;
    }
  }

  /**
   * Show Workspace Artifacts Modal
   */
  async function showArtifactsModal() {
    artifactsModal.classList.remove('hidden');
    artifactsModalContent.innerHTML = '<p class="text-muted">Loading workspace artifacts...</p>';

    try {
      const artifacts = await client.fetchWorkspaceArtifacts();
      if (!artifacts) {
        artifactsModalContent.innerHTML = '<p class="text-muted">No artifacts generated in this workspace yet.</p>';
        return;
      }

      const listContainer = document.createElement('div');
      listContainer.className = 'artifacts-list';

      const items = [
        { name: 'licensing_matrix.md', label: 'Licensing Pathway Matrix (Mainland vs Free Zone)', content: artifacts.licensing_matrix_md },
        { name: 'registration_payload.json', label: 'Official Registration Payload & MOA Structure', content: artifacts.registration_payload_json },
        { name: 'business_plan.md', label: '12-Month Financial Projections & Market Entry Plan', content: artifacts.business_plan_md },
        { name: 'compliance_checklist.md', label: 'Corporate Banking & Zero-PII Compliance Checklist', content: artifacts.compliance_checklist_md },
      ];

      items.forEach((item) => {
        const box = document.createElement('div');
        box.className = 'alert-item';
        const hasContent = item.content !== undefined && item.content !== null;

        box.innerHTML = `
          <div class="alert-item-header">
            <span class="alert-authority">${item.name}</span>
            <span class="alert-date">${hasContent ? 'Available' : 'Pending'}</span>
          </div>
          <p class="alert-summary">${item.label}</p>
          <div style="margin-top: 0.5rem;">
            <button class="a2ui-btn a2ui-btn-secondary ${!hasContent ? 'disabled' : ''}" data-file="${item.name}">
              📥 Download File
            </button>
          </div>
        `;

        if (hasContent) {
          box.querySelector('button').addEventListener('click', () => {
            downloadWorkspaceArtifact(item.name);
          });
        }
        listContainer.appendChild(box);
      });

      artifactsModalContent.innerHTML = '';
      artifactsModalContent.appendChild(listContainer);
    } catch (err) {
      artifactsModalContent.innerHTML = `<p class="text-danger">Failed to load artifacts: ${err.message}</p>`;
    }
  }

  function escapeHtml(text) {
    if (!text) return '';
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});
