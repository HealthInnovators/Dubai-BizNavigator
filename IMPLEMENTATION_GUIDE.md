# Dubai BizNavigator — Developer Implementation Guide

> **Practical Recipes, Code Walkthroughs, and Implementation Instructions for Engineers Extending Dubai BizNavigator**

---

## Table of Contents
1. [Developer Setup & Environment Verification](#1-developer-setup--environment-verification)
2. [Recipe 1: Adding a New Specialized Subagent](#recipe-1-adding-a-new-specialized-subagent)
3. [Recipe 2: Adding a New A2UI Declarative Widget Component](#recipe-2-adding-a-new-a2ui-declarative-widget-component)
4. [Recipe 3: Integrating a New Corporate Banking Partner](#recipe-3-integrating-a-new-corporate-banking-partner)
5. [Recipe 4: Configuring Langfuse Cloud vs. Self-Hosted VPC](#recipe-4-configuring-langfuse-cloud-vs-self-hosted-vpc)
6. [Recipe 5: Extending the Scheduled Regulatory Monitor](#recipe-5-extending-the-scheduled-regulatory-monitor)
7. [Recipe 6: Running Automated Evaluation Quality Gates](#recipe-6-running-automated-evaluation-quality-gates)
8. [Recipe 7: Production Deployment & Containerization](#recipe-7-production-deployment--containerization)

---

## 1. Developer Setup & Environment Verification

### Prerequisites
- Python 3.11, 3.12, 3.13, or 3.14
- Node.js 20+ and npm 10+
- Git

### Quickstart Commands

```bash
# Clone and enter monorepo
git clone <repo-url>
cd DBN

# 1. Backend environment setup
cd backend
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -e .

# 2. Frontend environment setup
cd ../frontend
npm install --legacy-peer-deps

# 3. Verify clean baseline
cd ..
pytest backend/tests/
ruff check backend/
python backend/evals/run_langfuse_evals.py --dry-run
cd frontend && npm run build
```

---

## Recipe 1: Adding a New Specialized Subagent

To add a new subagent (for example, `tax-advisor` to calculate UAE Corporate Tax Qualifying Free Zone Person status and VAT liabilities), follow these four steps:

### Step 1.1: Create Subagent Specification in `backend/app/infrastructure/agents/subagents/`

Create `backend/app/infrastructure/agents/subagents/tax_advisor.py`:

```python
"""Tax Advisor Subagent for UAE Corporate Tax and VAT guidance."""

from collections.abc import Sequence
from typing import Any
from deepagents.middleware.subagents import SubAgent
from langchain_core.tools import BaseTool

TAX_ADVISOR_SYSTEM_PROMPT = """You are the Senior UAE Corporate Tax & VAT Advisor for Dubai BizNavigator.
Your mission is to inspect `/workspace/startup_profile.json` and determine:
1. Qualifying Free Zone Person (QFZP) eligibility under Federal Decree-Law No. 47 of 2022 (0% tax on qualifying income).
2. Mandatory vs Voluntary VAT registration under Federal Decree-Law No. 8 of 2017 (375,000 AED threshold).
3. Withholding tax and international double taxation treaty implications.

Persist your findings to `/workspace/tax_strategy.md` with official citations to https://tax.gov.ae.
"""

def get_tax_advisor_subagent(tools: Sequence[BaseTool | Any] | None = None) -> SubAgent:
    """Build the tax-advisor SubAgent specification for create_deep_agent."""
    return {
        "name": "tax-advisor",
        "description": (
            "Specialized UAE corporate tax and VAT strategist that determines QFZP 0% status, "
            "VAT registration thresholds, and writes /workspace/tax_strategy.md."
        ),
        "system_prompt": TAX_ADVISOR_SYSTEM_PROMPT,
        "tools": list(tools) if tools else [],
        "mode": "isolated",
    }
```

### Step 1.2: Register in Subagents Package (`__init__.py`)

In `backend/app/infrastructure/agents/subagents/__init__.py`, export the new factory function:

```python
from app.infrastructure.agents.subagents.tax_advisor import get_tax_advisor_subagent

__all__ = [
    # ... existing subagents
    "get_tax_advisor_subagent",
]
```

### Step 1.3: Register with the Lead Orchestrator

In `backend/app/infrastructure/agents/orchestrator.py`, add the subagent to `_build_subagents()`:

```python
def _build_subagents(self) -> Sequence[SubAgent]:
    from app.infrastructure.agents.subagents import (
        get_banking_readiness_agent_subagent,
        get_compliance_auditor_subagent,
        get_form_automation_agent_subagent,
        get_licensing_strategist_subagent,
        get_regulatory_researcher_subagent,
        get_tax_advisor_subagent,  # <-- Add here
    )
    return [
        get_licensing_strategist_subagent(),
        get_regulatory_researcher_subagent(),
        get_tax_advisor_subagent(),  # <-- Add here
        get_form_automation_agent_subagent(),
        get_banking_readiness_agent_subagent(),
        get_compliance_auditor_subagent(),
    ]
```

### Step 1.4: Update Frontend Timeline Roster

In `frontend/src/services/agentClient.js`, add the new agent to `KNOWN_SUBAGENTS`:

```javascript
export const KNOWN_SUBAGENTS = [
  // ... existing agents
  {
    id: 'tax-advisor',
    name: 'Tax & VAT Advisor',
    role: 'Corporate Tax QFZP & FTA Threshold Scorer',
    icon: '📊',
  },
];
```

---

## Recipe 2: Adding a New A2UI Declarative Widget Component

To add a new widget (for example, a `Slider` or `FinancialMetricBadge`):

### Step 2.1: Register Schema in Catalog (`catalog.py`)

In `backend/app/interfaces/a2ui/catalog.py`:

```python
# Add to ALLOWED_COMPONENTS
ALLOWED_COMPONENTS: frozenset[str] = frozenset({
    # ... existing
    "FinancialMetricBadge",
})

# In validate_a2ui_components():
elif comp_type == "FinancialMetricBadge":
    if "metric_label" not in comp or "metric_value" not in comp:
        raise DomainValidationError("FinancialMetricBadge requires 'metric_label' and 'metric_value'.")
```

### Step 2.2: Add Builder Method in `surface_builder.py`

In `backend/app/interfaces/a2ui/surface_builder.py`:

```python
def create_financial_metric_component(
    self, comp_id: str, label: str, value: str, change_pct: float | None = None
) -> dict[str, Any]:
    return {
        "id": comp_id,
        "component": "FinancialMetricBadge",
        "metric_label": label,
        "metric_value": value,
        "change_pct": change_pct,
    }
```

### Step 2.3: Implement Safe Native DOM Renderer in `frontend/src/renderers/a2uiHost.js`

In `frontend/src/renderers/a2uiHost.js`:

```javascript
_renderComponent(comp, surface) {
  switch (comp.component) {
    // ... existing components
    case 'FinancialMetricBadge':
      return this._renderFinancialMetricBadge(comp);
    default:
      return this._renderUnknown(comp);
  }
}

_renderFinancialMetricBadge(comp) {
  const card = document.createElement('div');
  card.className = 'a2ui-metric-badge';
  
  const lbl = document.createElement('span');
  lbl.className = 'metric-label';
  lbl.textContent = comp.metric_label;
  
  const val = document.createElement('span');
  val.className = 'metric-value';
  val.textContent = comp.metric_value;
  
  card.appendChild(lbl);
  card.appendChild(val);
  return card;
}
```

---

## Recipe 3: Integrating a New Corporate Banking Partner

### Step 3.1: Define API Contract in `corporate_banking_adapter.py`

In `backend/app/infrastructure/banking/corporate_banking_adapter.py`:

```python
class CorporateBankingAdapter(BankingWorkflowPort):
    def __init__(self, partner_configs: dict[str, Any] | None = None) -> None:
        self.partners = partner_configs or {
            "wio_bank": {
                "base_url": "https://api.wio.io/v1",
                "kyb_endpoint": "/corporate/applications",
            },
            "mashreq_neo": {
                "base_url": "https://api.mashreq.com/business",
                "kyb_endpoint": "/onboarding",
            },
        }

    async def submit_readiness_package(
        self, package: BankingReadinessPackage, partner_id: str
    ) -> dict[str, Any]:
        package.ensure_hitl_approved()
        config = self.partners.get(partner_id)
        if not config:
            raise DomainValidationError(f"Unknown bank partner: {partner_id}")
            
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{config['base_url']}{config['kyb_endpoint']}",
                json=package.model_dump(mode="json"),
                headers={
                    "Idempotency-Key": f"pkg_{package.id}",
                    "X-Partner-ID": partner_id,
                },
            )
            resp.raise_for_status()
            return resp.json()
```

### Step 3.2: Secure Asynchronous Webhooks with HMAC-SHA256

Incoming bank updates to `POST /v1/webhooks/banking` must be verified using HMAC-SHA256 signatures:

```python
import hmac
import hashlib

def verify_bank_webhook_signature(payload_bytes: bytes, signature_header: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)
```

---

## Recipe 4: Configuring Langfuse Cloud vs. Self-Hosted VPC

### Scenario A: Langfuse Cloud (Default)

Configure your `.env`:
```ini
LANGFUSE_PUBLIC_KEY="pk-lf-01234567-89ab-cdef-0123-456789abcdef"
LANGFUSE_SECRET_KEY="sk-lf-01234567-89ab-cdef-0123-456789abcdef"
LANGFUSE_BASE_URL="https://cloud.langfuse.com"

# Strictly disable competing LangSmith tracing
LANGSMITH_TRACING=false
LANGSMITH_OTEL_ENABLED=false
```

### Scenario B: Self-Hosted Langfuse in Private VPC

Add Langfuse services to `docker-compose.yml`:
```yaml
  langfuse-server:
    image: langfuse/langfuse:2
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/langfuse
      - NEXTAUTH_SECRET=my-high-entropy-secret
      - SALT=my-high-entropy-salt
      - NEXTAUTH_URL=http://localhost:3000
      - TELEMETRY_ENABLED=false
```
Then point your backend `.env` to the internal VPC address:
```ini
LANGFUSE_BASE_URL="http://langfuse-server:3000"
```

---

## Recipe 5: Extending the Scheduled Regulatory Monitor

In `backend/app/application/regulatory_monitor.py`:

```python
MONITORED_AUTHORITIES = [
    {
        "authority": "DET",
        "portal_url": "https://dubaidet.gov.ae/en/news-and-updates",
        "topic": "Instant License Ejari Exemptions & 100% Foreign Ownership",
    },
    {
        "authority": "FTA",
        "portal_url": "https://tax.gov.ae/en/legislation",
        "topic": "Corporate Tax Qualifying Free Zone Person (QFZP) Guidelines",
    },
]
```

When a content hash diverges from the stored database state:
1. An immutable `RegulatoryAlert` entity is instantiated.
2. The entity is saved to the PostgreSQL repository.
3. Connected active sessions receive an A2UI alert notification on their next turn.

---

## Recipe 6: Running Automated Evaluation Quality Gates

The quality gate evaluates 10 test cases in `backend/evals/dataset_dubai_setup.json`.

```bash
# Run evaluations in dry-run mode (suitable for offline development & CI)
python backend/evals/run_langfuse_evals.py --dry-run

# Run against live Langfuse Cloud with score ingestion
python backend/evals/run_langfuse_evals.py --upload-dataset
```

Expected output:
```
==========================================================================================
DUBAI BIZNAVIGATOR — LANGFUSE EVALUATION RESULTS
==========================================================================================
Overall Cases Evaluated:       10
Average Jurisdiction Accuracy: 100.0% (Quality Gate: >= 90.0%)
Average Citation Grounding:    98.0%
Average PII Masking Check:     100.0%
==========================================================================================
QUALITY GATE PASSED: Jurisdiction accuracy (100.0%) >= threshold (90.0%)
```

---

## Recipe 7: Production Deployment & Containerization

### Build & Run Containers with Docker Compose

```bash
# Build production images and start in background
docker-compose up --build -d

# View live backend logs
docker-compose logs -f backend

# Run health check
curl http://localhost:8000/health
# {"status":"ok","app":"Dubai BizNavigator","environment":"production"}
```
