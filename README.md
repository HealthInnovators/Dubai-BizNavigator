# Dubai BizNavigator (DBN)

> **Autonomous Multi-Agent UAE Corporate Formation, Trade Licensing & Banking Orchestration**

Dubai BizNavigator is an enterprise-grade agentic platform built using **Clean Architecture** and strict separation of concerns. It guides international founders and enterprises through incorporation across **Dubai Mainland (Department of Economy and Tourism - DET)** and major **UAE Free Zones (DIFC, DMCC, IFZA, Dubai CommerCity, DIC)**.

---

## 📚 Comprehensive Documentation Guides

For in-depth architectural details, implementation recipes, and protocol references:

1. **[Architectural Blueprint (ARCHITECTURE.md)](ARCHITECTURE.md)**:
   - Clean Architecture concentric circle boundaries & dependency rule.
   - Domain invariants, validation models, and entity lifecycles.
   - DeepAgents Virtual Filesystem & LangGraph checkpointer state graph.
   - A2UI Declarative Interface Protocol and wire transport serialization.
   - Observability architecture (Langfuse v3+, zero OTLP collisions, PII masking).
   - Regulatory Change Monitor and Corporate Banking Partner integration architectures.

2. **[Developer Implementation Guide (IMPLEMENTATION_GUIDE.md)](IMPLEMENTATION_GUIDE.md)**:
   - Step-by-step developer implementation instructions.
   - **Recipe 1**: Adding a new specialized subagent (e.g. `tax-advisor`).
   - **Recipe 2**: Adding a new A2UI widget component.
   - **Recipe 3**: Integrating a new corporate banking partner with HMAC-SHA256 webhooks.
   - **Recipe 4**: Setting up Langfuse Cloud vs. private VPC self-hosting.
   - **Recipe 5**: Extending the autonomous regulatory change monitor.
   - **Recipe 6**: Running automated evaluation quality gates.

3. **[API & Protocol Reference (API_REFERENCE.md)](API_REFERENCE.md)**:
   - Complete REST endpoints specification (`/health`, `/v1/sessions`, `/v1/sessions/{id}/approve`, `/v1/workspaces/{id}/artifacts`, `/v1/workspaces/{id}/alerts`).
   - Server-Sent Events (SSE) multiplexed stream format and event payloads (`POST /v1/sessions/{id}/messages`).
   - HMAC-SHA256 signature verification for corporate banking partner webhooks.
   - A2UI JSON wire transport specifications (`createSurface`, `updateComponents`, and actions).

---

## 🏛️ System Architecture

The monorepo enforces strict architectural boundaries:

```
Dubai-BizNavigator/
├── backend/
│   ├── app/
│   │   ├── domain/          # Pure Python entities, value objects, ports, exceptions (NO frameworks)
│   │   ├── application/     # Use cases, DTOs, regulatory change monitor, workflow services
│   │   ├── infrastructure/  # DeepAgents/LangGraph orchestrator, Langfuse v3+, PostgreSQL, Banking API
│   │   └── interfaces/      # FastAPI REST/SSE endpoints, A2UI surface builder & catalog, DI container
│   ├── evals/               # Langfuse dataset evaluation pipelines & quality gates (10 realistic cases)
│   └── tests/               # 116 passing unit and integration tests (pytest)
├── frontend/
│   ├── src/
│   │   ├── renderers/       # A2UI Host (@a2ui/web_core, @a2ui/markdown-it, DOMPurify sanitization)
│   │   ├── services/        # AgentClient for multiplexed SSE streaming & HITL gate resolution
│   │   ├── styles/          # Executive Dubai luxury theme (gold accents, dark slate, responsive)
│   │   └── main.js          # Swarm timeline, A2UI event listeners, and chat bar controller
│   └── index.html           # 3-Panel executive dashboard
├── .github/workflows/ci.yml # GitHub Actions CI: Ruff, Pytest, Langfuse Eval Gate, Frontend Build
└── docker-compose.yml       # Production/Local orchestration (PostgreSQL, Backend, Frontend)
```

---

## 🤖 Specialized DeepAgents Subagent Swarm

1. **Licensing Strategist** (`licensing-strategist`): Evaluates Dubai Mainland (DET Normal vs Instant Licence) against Free Zones (DIFC, DMCC, IFZA), calculating visa quotas and costs.
2. **Regulatory Researcher** (`regulatory-researcher`): Queries authoritative UAE portals (`dubaidet.gov.ae`, `investindubai.gov.ae`, `difc.com`, `dmcc.ae`) for up-to-date fees and tax rules.
3. **Form Automation Agent** (`form-automation-agent`): Maps startup profile into structured registration payloads and triggers **Human-in-the-Loop (HITL)** approval gates.
4. **Banking Readiness Agent** (`banking-readiness-agent`): Compiles corporate KYB packages, drafts 12-month financial projections, and coordinates with banking APIs.
5. **Compliance Auditor** (`compliance-auditor`): Independent critique agent with read-only sandbox enforcing zero-PII leakage and regulatory compliance.

---

## 🛡️ Observability: Langfuse (Zero OTLP Conflicts)

To guarantee conflict-free telemetry and complete multi-tenant trace isolation:
- **LangSmith Tracing Strictly Disabled**:
  ```ini
  LANGSMITH_TRACING=false
  LANGSMITH_OTEL_ENABLED=false
  ```
- **Langfuse SDK v3+**:
  - Direct integration via `langfuse.get_client()` and `langfuse.langchain.CallbackHandler`.
  - No competing OpenTelemetry exporters (`opentelemetry-exporter-otlp-proto-http`) targeting LangSmith are loaded.
  - Multi-tenant trace isolation using `propagate_attributes(user_id=..., session_id=..., tags=...)`.
  - Automatic recursive PII masking for Emirates IDs (`784-XXXX-XXXXXXX-X`), Passports, and UAE IBANs.

---

## 🚀 Quickstart & Local Development

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL (optional for local dev; MemorySaver fallback enabled)

### 1. Backend Setup
```bash
# Navigate to backend and install dependencies in editable mode
cd backend
pip install -e .

# Configure environment
cp ../.env.example .env

# Run FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be available at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
# Navigate to frontend and install dependencies
cd frontend
npm install --legacy-peer-deps

# Start Vite development server
npm run dev
```
Dashboard will be available at `http://localhost:5173`.

---

## 🐳 Docker Compose Deployment

To run the complete stack including PostgreSQL, FastAPI, and Vite:

```bash
docker-compose up --build
```

- **Frontend UI**: `http://localhost:5173`
- **Backend API**: `http://localhost:8000`
- **PostgreSQL**: `localhost:5432`

---

## 🧪 Testing & Automated Evaluation Gates

### Run Backend Unit & Integration Tests
```bash
pytest backend/tests/
# 116 passed in ~8s
```

### Run Code Formatting & Linting
```bash
ruff check backend/
```

### Run Langfuse Dataset Evaluation Quality Gate
```bash
python backend/evals/run_langfuse_evals.py --dry-run
```
The evaluator scores all 10 Dubai business formation test cases across:
- **Jurisdiction Accuracy**: Exact match and legal rationale (threshold: >= 90%).
- **Citation Grounding**: Verified official UAE government sources (`dubaidet.gov.ae`, etc.).
- **PII Masking Check**: Zero unredacted passport, Emirates ID, or IBAN strings.

---

## 🔑 Production Environment Variables Checklist

For live production deployment, configure the following keys in your environment:

| Variable | Description | Example / Note |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `LANGFUSE_PUBLIC_KEY` | Langfuse Cloud / VPC public key | `pk-lf-...` |
| `LANGFUSE_SECRET_KEY` | Langfuse Cloud / VPC secret key | `sk-lf-...` |
| `LANGFUSE_BASE_URL` | Langfuse host URL | `https://cloud.langfuse.com` or self-hosted VPC |
| `LANGSMITH_TRACING` | Must remain `false` | `false` |
| `LANGSMITH_OTEL_ENABLED` | Must remain `false` | `false` |
| `ANTHROPIC_API_KEY` | Anthropic Claude 3.5 Sonnet key | `sk-ant-...` |
| `TAVILY_API_KEY` | Tavily search API key for UAE queries | `tvly-...` |
| `BANKING_WEBHOOK_SECRET` | HMAC-SHA256 signature verification secret | High-entropy hex string |
