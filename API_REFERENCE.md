# Dubai BizNavigator — API & Protocol Reference Manual

> **Complete Technical Specification of REST Endpoints, SSE Streaming Protocols, Webhook Handlers, and A2UI Wire Formats**

---

## Table of Contents
1. [Overview & Standards](#1-overview--standards)
2. [REST API Endpoints](#2-rest-api-endpoints)
   - [Health Check: `GET /health`](#get-health)
   - [Create Setup Session: `POST /v1/sessions`](#post-v1sessions)
   - [Agent Workflow SSE Stream: `POST /v1/sessions/{session_id}/messages`](#post-v1sessionssession_idmessages)
   - [Resolve HITL Gate: `POST /v1/sessions/{session_id}/approve`](#post-v1sessionssession_idapprove)
   - [Retrieve Workspace Artifacts: `GET /v1/workspaces/{workspace_id}/artifacts`](#get-v1workspacesworkspace_idartifacts)
   - [Retrieve Regulatory Alerts: `GET /v1/workspaces/{workspace_id}/alerts`](#get-v1workspacesworkspace_idalerts)
   - [Corporate Banking Webhook: `POST /v1/webhooks/banking`](#post-v1webhooksbanking)
3. [SSE Wire Format & Event Types](#3-sse-wire-format--event-types)
4. [A2UI Declarative Transport Protocol](#4-a2ui-declarative-transport-protocol)
5. [Error Handling & Standard Error Envelopes](#5-error-handling--standard-error-envelopes)

---

## 1. Overview & Standards

- **Base URL**: `http://localhost:8000` (Local) / `https://api.biznavigator.dubai` (Production)
- **Data Interchange**: JSON (`application/json; charset=utf-8`) for standard request/response payloads; `text/event-stream; charset=utf-8` for agent execution streams.
- **Authentication**: Bearer tokens or Session-based tenancy headers (`X-Tenant-ID`).
- **Idempotency**: External mutations support `Idempotency-Key` HTTP headers.

---

## 2. REST API Endpoints

### `GET /health`
Returns system operational status and active runtime environment.

#### Response (`200 OK`)
```json
{
  "status": "ok",
  "app": "Dubai BizNavigator",
  "environment": "development"
}
```

---

### `POST /v1/sessions`
Initializes a new Dubai incorporation workspace, assigns a durable LangGraph checkpointer thread, and pre-populates the virtual workspace.

#### Request Body
```json
{
  "company_name": "Apex Global Technologies LLC",
  "industry_sector": "Technology",
  "business_activity": "Software Development and AI Consulting",
  "revenue_model": "B2B_SaaS",
  "uae_local_trade": false,
  "visa_quota_needed": 3,
  "office_preference": "FlexiDesk",
  "founders_summary": "Two international founders from UK & Germany.",
  "tenant_id": "tenant_dubai_01"
}
```

#### Response (`201 Created`)
```json
{
  "session_id": "sess_4bd148d210d0",
  "workspace_id": "ws_4bd148d210d0",
  "tenant_id": "tenant_dubai_01",
  "status": "created",
  "created_at": "2026-11-20T22:30:00Z",
  "profile": {
    "company_name": "Apex Global Technologies LLC",
    "industry_sector": "Technology",
    "business_activity": "Software Development and AI Consulting",
    "revenue_model": "B2B_SaaS",
    "uae_local_trade": false,
    "visa_quota_needed": 3,
    "office_preference": "FlexiDesk"
  }
}
```

---

### `POST /v1/sessions/{session_id}/messages`
Dispatches user instructions to the lead coordinator agent and streams multiplexed subagent progress events and declarative A2UI surfaces via **Server-Sent Events (SSE)**.

#### Path Parameters
- `session_id` (string, required): Active session identifier.

#### Request Body
```json
{
  "message": "Evaluate DET Mainland vs IFZA Free Zone for my startup.",
  "workspace_id": "ws_4bd148d210d0",
  "tenant_id": "tenant_dubai_01"
}
```

#### Response Stream (`text/event-stream`)
```http
HTTP/1.1 200 OK
Content-Type: text/event-stream; charset=utf-8
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no

id: evt_1
event: agent_progress
data: {"agent_name": "coordinator", "status": "started", "message": "Initialized setup workspace."}

id: evt_2
event: agent_progress
data: {"agent_name": "licensing-strategist", "status": "running", "message": "Analyzing DET vs Free Zones..."}

id: evt_3
event: a2ui_surface
data: {"createSurface": {"surfaceId": "surface_licensing_3", "catalogId": "biznavigator_a2ui_v1"}}

id: evt_4
event: a2ui_surface
data: {"updateComponents": {"surfaceId": "surface_licensing_3", "components": [...]}}

id: evt_5
event: hitl_interrupt
data: {"agent_name": "form-automation-agent", "status": "interrupted", "surface_id": "surface_hitl_5", "message": "Verification required."}

id: evt_6
event: stream_complete
data: {"status": "completed", "total_events": 6}
```

---

### `POST /v1/sessions/{session_id}/approve`
Submits a Human-in-the-Loop (HITL) approval decision, unpausing the durable LangGraph checkpointer thread.

#### Request Body
```json
{
  "action": "hitl_approve",
  "workspace_id": "ws_4bd148d210d0",
  "tenant_id": "tenant_dubai_01",
  "payload_updates": {
    "target_authority": "DET",
    "confirmed_trade_name": "Apex Global Technologies LLC"
  }
}
```

#### Response Stream (`text/event-stream`)
Streams subsequent agent progress (`banking-readiness-agent`, `compliance-auditor`) and emits final business plan and compliance checklist surfaces.

---

### `GET /v1/workspaces/{workspace_id}/artifacts`
Retrieves generated markdown reports and JSON payloads from the virtual workspace.

#### Response (`200 OK`)
```json
{
  "workspace_id": "ws_4bd148d210d0",
  "licensing_matrix_md": "# Dubai Licensing Strategy Matrix\n\n...",
  "registration_payload_json": {
    "target_authority": "DET",
    "licence_category": "Commercial",
    "trade_name_candidates": ["Apex Global Technologies LLC"],
    "shareholding_structure": [{"partner": "Founding Partner", "share": "100%"}]
  },
  "business_plan_md": "# Executive Business Plan & Market Entry\n\n...",
  "compliance_checklist_md": "# UAE Corporate Banking & Regulatory Compliance Checklist\n\n..."
}
```

---

### `GET /v1/workspaces/{workspace_id}/alerts`
Fetches detected regulatory updates or legal changes impacting the workspace's designated jurisdiction and activities.

#### Response (`200 OK`)
```json
{
  "workspace_id": "ws_4bd148d210d0",
  "alert_count": 1,
  "alerts": [
    {
      "id": "alert_99a81c",
      "authority": "DET",
      "change_summary": "Cabinet Decision No. 10/2026 updates Instant License eligibility for commercial software.",
      "effective_date": "2026-06-01",
      "source_url": "https://dubaidet.gov.ae/en/gazette/2026-10",
      "detected_at": "2026-11-20T10:00:00Z"
    }
  ],
  "a2ui_surface": []
}
```

---

### `POST /v1/webhooks/banking`
Receives asynchronous corporate bank account status updates (KYC approval, account opening voucher, IBAN issuance).

#### Headers
- `X-Signature-SHA256`: Hexadecimal HMAC-SHA256 signature of request body using shared partner secret.

#### Request Body
```json
{
  "event_id": "evt_bank_9921",
  "partner_id": "wio_bank",
  "application_id": "app_uae_5541",
  "workspace_id": "ws_4bd148d210d0",
  "status": "APPROVED",
  "iban": "AE070331234567890123456",
  "currency": "AED",
  "approved_at": "2026-11-20T15:30:00Z"
}
```

#### Response (`200 OK`)
```json
{
  "status": "received",
  "event_id": "evt_bank_9921",
  "verified": true
}
```

---

## 3. SSE Wire Format & Event Types

Every SSE chunk conforms to standard MIME type `text/event-stream`:

| Event Name | Purpose | Data Payload Schema |
|---|---|---|
| `agent_progress` | Subagent status update | `{"agent_name": str, "status": str, "message": str, "artifact_updated": str \| null}` |
| `a2ui_surface` | Declarative UI update | A2UI Transport Message (`CreateSurface` or `UpdateComponents`) |
| `hitl_interrupt` | Human gate pause | `{"agent_name": str, "status": "interrupted", "surface_id": str, "message": str}` |
| `stream_complete`| Successful termination | `{"status": "completed", "total_events": int}` |
| `stream_error` | Unexpected failure | `{"status": "error", "message": str}` |

---

## 4. A2UI Declarative Transport Protocol

A2UI messages are emitted in two structural forms:

### Message Type 1: `createSurface`
Initializes a new visual surface bound to a validated catalog:
```json
{
  "createSurface": {
    "surfaceId": "surface_licensing_matrix",
    "catalogId": "biznavigator_a2ui_v1"
  }
}
```

### Message Type 2: `updateComponents`
Supplies or mutates the component tree:
```json
{
  "updateComponents": {
    "surfaceId": "surface_licensing_matrix",
    "components": [
      {
        "id": "licensing_root",
        "component": "Column",
        "children": ["title_text", "comparison_table"],
        "justify": "start",
        "align": "stretch"
      },
      {
        "id": "title_text",
        "component": "Text",
        "text": "Dubai Jurisdiction & Licensing Comparison Matrix",
        "variant": "title"
      },
      {
        "id": "comparison_table",
        "component": "DataTable",
        "title": "Evaluated Pathways",
        "columns": [
          {"key": "pathway", "label": "Pathway"},
          {"key": "authority", "label": "Authority"},
          {"key": "cost_range", "label": "Est. Cost (AED)"}
        ],
        "rows": [
          {"pathway": "Mainland_DET", "authority": "DET", "cost_range": "18,000 - 35,000"},
          {"pathway": "FreeZone", "authority": "IFZA", "cost_range": "12,500 - 22,000"}
        ]
      }
    ]
  }
}
```

---

## 5. Error Handling & Standard Error Envelopes

All HTTP errors return standard JSON payloads with diagnostic details:

```json
{
  "detail": {
    "code": "DOMAIN_VALIDATION_ERROR",
    "message": "visa_quota_needed cannot be negative.",
    "field": "visa_quota_needed"
  }
}
```

### Standard Error Codes

| HTTP Status | Error Code | Description |
|---|---|---|
| `400 Bad Request` | `DOMAIN_VALIDATION_ERROR` | Schema constraint or invariant violation |
| `401 Unauthorized` | `INVALID_HMAC_SIGNATURE` | Webhook signature verification failure |
| `404 Not Found` | `WORKSPACE_NOT_FOUND` | Specified workspace ID does not exist |
| `409 Conflict` | `HITL_APPROVAL_REQUIRED` | Attempted submission without user confirmation |
| `502 Bad Gateway` | `BANKING_PARTNER_ERROR` | Upstream banking API timeout or error |
