/**
 * @file agentClient.js
 * @module services/agentClient
 * @description
 * High-performance HTTP and Server-Sent Events (SSE) streaming client for Dubai BizNavigator.
 * Communicates with the FastAPI application layer, parses multiplexed typed stream events,
 * tracks live subagent states, and dispatches Human-in-the-Loop (HITL) approval decisions.
 *
 * Architecture Notes:
 * - Operates as the frontend interface adapter between the A2UIHost renderer and FastAPI backend.
 * - Parses `text/event-stream` chunks natively via `ReadableStream` (`getReader()`).
 * - Decodes typed SSE events: `agent_progress`, `a2ui_surface`, `hitl_interrupt`, `stream_complete`, `stream_error`.
 * - Strictly avoids executing raw backend strings; dispatches structured payloads to A2UIHost.
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

/**
 * @typedef {Object} SubagentDefinition
 * @property {string} id - Unique identifier matching the LangGraph subagent name.
 * @property {string} name - Display title formatted for the executive dashboard.
 * @property {string} role - Functional description of the specialist's responsibilities.
 * @property {string} icon - High-contrast emoji/icon representing the domain.
 */

/**
 * Roster of the 5 specialized autonomous DeepAgents subagents orchestrated by LangGraph.
 * @type {ReadonlyArray<SubagentDefinition>}
 */
export const KNOWN_SUBAGENTS = [
  {
    id: 'licensing-strategist',
    name: 'Licensing Strategist',
    role: 'DET Mainland vs Free Zone Pathway Scorer',
    icon: '🏛️',
  },
  {
    id: 'regulatory-researcher',
    name: 'Regulatory Researcher',
    role: 'Tax, VAT, and UBO Regulatory Verification',
    icon: '🔍',
  },
  {
    id: 'form-automation-agent',
    name: 'Form Automation Agent',
    role: 'Registration Payload & MOA Preparation',
    icon: '📝',
  },
  {
    id: 'banking-readiness-agent',
    name: 'Banking Readiness Agent',
    role: 'Corporate KYB Dossier & Financial Modeling',
    icon: '🏦',
  },
  {
    id: 'compliance-auditor',
    name: 'Compliance Auditor',
    role: 'Read-Only Critique & Zero-PII Verification',
    icon: '🛡️',
  },
];

/**
 * @typedef {Object} SseCallbacks
 * @property {(event: Object) => void} [onAgentProgress] - Fired on subagent transitions, thoughts, or tool calls.
 * @property {(surfaceMessage: Object|Array<Object>) => void} [onA2UISurface] - Fired when declarative A2UI surfaces update.
 * @property {(interruptData: Object) => void} [onHitlInterrupt] - Fired when LangGraph checkpointer pauses for human confirmation.
 * @property {(completionData: Object) => void} [onComplete] - Fired when workflow completes successfully.
 * @property {(error: Error) => void} [onError] - Fired on stream or network failure.
 */

/**
 * Service class managing session initialization, multiplexed SSE stream consumption,
 * and Human-in-the-Loop gate execution.
 */
export class AgentClient {
  /**
   * Constructs a new AgentClient instance.
   * @param {string} [baseUrl=API_BASE] - FastAPI gateway base URL.
   */
  constructor(baseUrl = API_BASE) {
    /** @type {string} */
    this.baseUrl = baseUrl.replace(/\/+$/, '');
    /** @type {string|null} */
    this.currentSessionId = null;
    /** @type {string|null} */
    this.currentWorkspaceId = null;
    /** @type {ReadableStreamDefaultReader<Uint8Array>|null} */
    this.activeReader = null;
  }

  /**
   * Initializes a new Dubai business formation workspace and session.
   * Calls `POST /v1/sessions` on the FastAPI backend.
   *
   * @async
   * @param {Object} [profileData={}] - Initial startup parameters (company name, sector, etc.).
   * @returns {Promise<{session_id: string, workspace_id: string, status: string, profile: Object}>}
   * @throws {Error} If HTTP response status is not 2xx.
   *
   * @example
   * const client = new AgentClient();
   * const session = await client.createSession({ company_name: 'Apex AI LLC' });
   * console.log('Session ID:', session.session_id);
   */
  async createSession(profileData = {}) {
    const res = await fetch(`${this.baseUrl}/v1/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profileData),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Session creation failed: ${res.statusText}`);
    }

    const data = await res.json();
    this.currentSessionId = data.session_id;
    this.currentWorkspaceId = data.workspace_id;
    return data;
  }

  /**
   * Fetches active regulatory alerts detected for the current or specified workspace.
   * Calls `GET /v1/workspaces/{workspace_id}/alerts`.
   *
   * @async
   * @param {string} [workspaceId=this.currentWorkspaceId] - Target workspace identifier.
   * @returns {Promise<{workspace_id: string, alert_count: number, alerts: Array<Object>, a2ui_surface: Array<Object>}>}
   * @throws {Error} If the HTTP request fails.
   */
  async fetchWorkspaceAlerts(workspaceId = this.currentWorkspaceId) {
    if (!workspaceId) return { alerts: [], alert_count: 0, a2ui_surface: [] };
    const res = await fetch(`${this.baseUrl}/v1/workspaces/${workspaceId}/alerts`);
    if (!res.ok) {
      throw new Error(`Failed to fetch alerts: ${res.statusText}`);
    }
    return res.json();
  }

  /**
   * Fetches all generated markdown reports and JSON payloads from the virtual workspace.
   * Calls `GET /v1/workspaces/{workspace_id}/artifacts`.
   *
   * @async
   * @param {string} [workspaceId=this.currentWorkspaceId] - Target workspace identifier.
   * @returns {Promise<{workspace_id: string, licensing_matrix_md: string, registration_payload_json: Object, business_plan_md: string, compliance_checklist_md: string}|null>}
   * @throws {Error} If the HTTP request fails.
   */
  async fetchWorkspaceArtifacts(workspaceId = this.currentWorkspaceId) {
    if (!workspaceId) return null;
    const res = await fetch(`${this.baseUrl}/v1/workspaces/${workspaceId}/artifacts`);
    if (!res.ok) {
      throw new Error(`Failed to fetch artifacts: ${res.statusText}`);
    }
    return res.json();
  }

  /**
   * Sends user intent or instructions to the lead orchestrator and streams multiplexed SSE events.
   * Calls `POST /v1/sessions/{session_id}/messages` with `text/event-stream` consumption.
   *
   * @async
   * @param {string} sessionId - Active session identifier.
   * @param {string} message - User instruction or prompt text.
   * @param {SseCallbacks} [callbacks={}] - Typed callback handlers.
   * @returns {Promise<void>} Resolves when the SSE stream completes or terminates.
   * @throws {Error} If no session ID is available or if initial connection fails.
   */
  async sendUserMessage(sessionId, message, callbacks = {}) {
    const targetSessionId = sessionId || this.currentSessionId;
    if (!targetSessionId) {
      throw new Error('No active session ID provided.');
    }

    const response = await fetch(`${this.baseUrl}/v1/sessions/${targetSessionId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        workspace_id: this.currentWorkspaceId,
      }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Message stream failed: ${response.statusText}`);
    }

    return this._consumeSseStream(response.body, callbacks);
  }

  /**
   * Transmits Human-in-the-Loop (HITL) approval decisions to unpause the LangGraph checkpointer.
   * Calls `POST /v1/sessions/{session_id}/approve` and streams subsequent agent progression.
   *
   * @async
   * @param {string} sessionId - Active session identifier.
   * @param {Object} options - Decision options.
   * @param {'hitl_approve'|'hitl_reject'} [options.action='hitl_approve'] - Approved or Request Edits.
   * @param {Object|null} [options.payloadUpdates=null] - User-confirmed parameter overrides.
   * @param {SseCallbacks} [callbacks={}] - Typed callback handlers.
   * @returns {Promise<void>} Resolves when resumed stream finishes.
   * @throws {Error} If response is non-2xx.
   */
  async approveHITL(sessionId, { action = 'hitl_approve', payloadUpdates = null }, callbacks = {}) {
    const targetSessionId = sessionId || this.currentSessionId;
    if (!targetSessionId) {
      throw new Error('No active session ID provided.');
    }

    const response = await fetch(`${this.baseUrl}/v1/sessions/${targetSessionId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action,
        workspace_id: this.currentWorkspaceId,
        payload_updates: payloadUpdates,
      }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `HITL approval failed: ${response.statusText}`);
    }

    return this._consumeSseStream(response.body, callbacks);
  }

  /**
   * Internal streaming loop that parses raw `text/event-stream` chunks into typed domain events.
   *
   * @private
   * @async
   * @param {ReadableStream<Uint8Array>|null} streamBody - Readable body stream from Fetch response.
   * @param {SseCallbacks} callbacks - Event dispatch callbacks.
   * @returns {Promise<void>}
   */
  async _consumeSseStream(streamBody, callbacks) {
    const { onAgentProgress, onA2UISurface, onHitlInterrupt, onComplete, onError } = callbacks;

    if (!streamBody) {
      if (onComplete) onComplete({ status: 'completed' });
      return;
    }

    const reader = streamBody.getReader();
    this.activeReader = reader;
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split('\n\n');
        buffer = events.pop() || ''; // Preserve incomplete trailing chunk in buffer

        for (const rawEvent of events) {
          if (!rawEvent.trim()) continue;

          let eventName = 'message';
          let eventData = '';

          const lines = rawEvent.split('\n');
          for (const line of lines) {
            if (line.startsWith('event: ')) {
              eventName = line.substring(7).trim();
            } else if (line.startsWith('data: ')) {
              eventData += line.substring(6);
            }
          }

          if (!eventData) continue;

          let parsedPayload;
          try {
            parsedPayload = JSON.parse(eventData);
          } catch {
            parsedPayload = eventData;
          }

          switch (eventName) {
            case 'agent_progress':
              if (onAgentProgress) onAgentProgress(parsedPayload);
              break;

            case 'a2ui_surface':
              if (onA2UISurface) onA2UISurface(parsedPayload);
              break;

            case 'hitl_interrupt':
              if (onHitlInterrupt) onHitlInterrupt(parsedPayload);
              break;

            case 'stream_complete':
              if (onComplete) onComplete(parsedPayload);
              break;

            case 'stream_error':
              if (onError) onError(new Error(parsedPayload.message || 'Stream error'));
              break;

            default:
              if (onAgentProgress && typeof parsedPayload === 'object') {
                onAgentProgress(parsedPayload);
              }
              break;
          }
        }
      }

      if (onComplete) onComplete({ status: 'completed' });
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error('SSE Read Error:', err);
        if (onError) onError(err);
      }
    } finally {
      this.activeReader = null;
    }
  }

  /**
   * Cancels the active SSE stream reader, terminating the connection cleanly.
   */
  cancelActiveStream() {
    if (this.activeReader) {
      this.activeReader.cancel().catch(() => {});
      this.activeReader = null;
    }
  }
}
