/**
 * Dubai BizNavigator - Marketing Site Content & Data Repository
 */

export const siteConfig = {
  name: "Dubai BizNavigator",
  wordmark: {
    prefix: "Dubai",
    highlight: "BizNavigator",
    badge: "Enterprise AI"
  },
  tagline: "Navigate Dubai Business Setup with Algorithmic Precision",
  description: "The intelligent jurisdiction recommendation engine, instant fee estimator, and autonomous incorporation copilot for entrepreneurs expanding into the UAE.",
  hero: {
    headline: "Launch Your Dubai Business in Hours, Not Weeks",
    subheadline: "Dubai BizNavigator is an autonomous AI agent that analyzes your business model, recommends Free Zone vs. Mainland licensing, pre-fills registration forms, and prepares bank-ready business plans and compliance checklists.",
    primaryCTA: "Preview Your Setup Path",
    primaryTarget: "#setup-preview",
    secondaryCTA: "Request Early Access",
    secondaryTarget: "#waitlist"
  },
  mockA2UICard: {
    badge: "Human-Approved",
    activity: "Software & Digital Advisory",
    timestamp: "Real-time AI Recommendation",
    mainlandDET: {
      name: "Dubai Mainland (DET)",
      badge: "Top Recommendation",
      authority: "Department of Economy and Tourism",
      matchScore: "98% Fit",
      ownership: "100% Foreign Ownership",
      marketAccess: "Direct UAE Local & Federal Contracts",
      estCost: "AED 18,500/yr",
      officeRule: "Ejari lease required",
      speed: "24-48 Hours"
    },
    dmccFreeZone: {
      name: "DMCC Free Zone",
      badge: "Alternative Option",
      authority: "Dubai Multi Commodities Centre",
      matchScore: "93% Fit",
      ownership: "100% Foreign Ownership",
      marketAccess: "Global & Intra-Zone (Distributor for Local B2C)",
      estCost: "AED 16,900/yr",
      officeRule: "Flexi-desk eligible",
      speed: "3-5 Days"
    }
  },
  trustStrip: {
    chamberCompetition: {
      title: "Dubai Chamber of Digital Economy",
      initiative: "Create AI Agents Championship",
      category: "Best Business AI Agent Entrant",
      url: "https://www.dubaichamberdigital.com/en/create-ai-agents",
      badgeText: "Chamber AI Championship Entrant"
    },
    callouts: [
      {
        title: "Free Zone vs. DET Mainland Analysis",
        description: "Instant algorithmic benchmarking of 45+ Free Zones vs. Mainland DET commercial licenses.",
        icon: "compass"
      },
      {
        title: "Human-in-the-Loop Filing Safety",
        description: "Zero autonomous filing surprises. Every government submission is pre-screened and human-approved.",
        icon: "shield-check"
      },
      {
        title: "Bank-Ready KYC & Business Plans",
        description: "Pre-compiled corporate banking packets aligned with UAE Central Bank AML & Tier-1 bank KYC standards.",
        icon: "file-text"
      }
    ]
  },
  earlyAccessCTA: "Join Early Access",
  secondaryCTA: "Compare Jurisdictions",
  stats: [
    { value: "48 Hrs", label: "Average Setup Projection", sub: "vs 3-4 weeks manual broker" },
    { value: "100%", label: "Digital Workflow", sub: "Zero physical paperwork delays" },
    { value: "AED 18,500+", label: "Average Fee Savings", sub: "Eliminated hidden middleman fees" },
    { value: "45+", label: "Free Zones & Mainland", sub: "Cross-analyzed in real time" }
  ]
};

export const navLinks = [
  { label: "How It Works", href: "#how-it-works" },
  { label: "Free Zone vs. Mainland", href: "#comparison" },
  { label: "Pricing", href: "#pricing" },
  { label: "Security", href: "#security" },
  { label: "FAQ", href: "#faq" }
];

export const pricingTiers = [
  {
    id: "founder-explorer",
    name: "Founder Explorer",
    badge: "Free Public Preview",
    price: "AED 0",
    period: "Free preview access",
    description: "Designed for international entrepreneurs and researchers evaluating UAE feasibility before committing capital.",
    highlight: false,
    ctaText: "Start Free Preview",
    ctaTarget: "#setup-preview",
    features: [
      "Autonomous sector & business model intake",
      "Interactive Free Zone vs. Mainland comparison matrix",
      "Preliminary Total Cost of Ownership (TCO) simulation",
      "Direct links to official Dubai government portals",
      "Public UAE commercial activity database search"
    ]
  },
  {
    id: "launch-ready",
    name: "Launch Ready",
    badge: "Most Popular • Early Access",
    price: "Early Access — Join Waitlist",
    period: "Per incorporated entity",
    description: "End-to-end autonomous preparation package for founders actively incorporating their Dubai enterprise.",
    highlight: true,
    ctaText: "Request Early Access",
    ctaTarget: "#waitlist",
    features: [
      "Everything in Founder Explorer",
      "Automated trade name & DED activity codes pre-fill",
      "Mandatory Human-in-the-Loop (HITL) review gate & sign-off",
      "Bilingual Memorandum of Association (MOA) generation",
      "12-Month bank-ready business plan & financial forecast",
      "Tier-1 UAE bank KYC & onboarding dossier (Wio, ENBD)",
      "UAE PDPL-compliant statutory compliance checklist"
    ]
  },
  {
    id: "ecosystem-partner",
    name: "Ecosystem Partner",
    badge: "B2B2C & Institutional",
    price: "Early Access — Join Waitlist",
    period: "Custom partner licensing",
    description: "White-label & API integration for Free Zone authorities, incubators, legal firms, and banking partners.",
    highlight: false,
    ctaText: "Partner With Us",
    ctaTarget: "#waitlist",
    features: [
      "Everything in Launch Ready",
      "Headless REST API & MCP Server integration",
      "Embeddable A2UI jurisdiction recommendation widget",
      "White-label client onboarding & intake pipelines",
      "Custom regulatory rule sets for specialized Free Zones",
      "Dedicated background regulatory watchdog daemon",
      "Priority compliance SLA & technical integration support"
    ]
  }
];

export const officialDubaiResources = [
  {
    name: "Dubai Department of Economy & Tourism (DET)",
    url: "https://www.dubaidet.gov.ae",
    desc: "Official municipal authority for Dubai Mainland licensing and commercial permits."
  },
  {
    name: "Invest in Dubai (Official Portal)",
    url: "https://www.investindubai.gov.ae",
    desc: "Integrated digital platform for business establishment in Dubai."
  },
  {
    name: "Dubai Chamber of Digital Economy",
    url: "https://www.dubaichamberdigital.com",
    desc: "Government chamber driving Dubai's digital transformation & AI championships."
  },
  {
    name: "Dubai Multi Commodities Centre (DMCC)",
    url: "https://dmcc.ae",
    desc: "World's leading commodity Free Zone & premier business district."
  },
  {
    name: "UAE Federal Tax Authority (FTA)",
    url: "https://tax.gov.ae",
    desc: "Federal administration overseeing UAE Corporate Tax and VAT compliance."
  }
];

export const workflowStepperData = {
  sectionTitle: "Multi-Agent Autonomous Workflow",
  sectionSubtitle: "How specialized AI agents collaborate with Human-in-the-Loop governance to execute your Dubai company formation.",
  steps: [
    {
      id: "step-1",
      number: "01",
      tabTitle: "Business Model Intake",
      title: "Business Model & Operational Intake",
      shortDesc: "Share your sector, target market (UAE local vs. international), visa count, and office preference.",
      agents: [
        { name: "intake-orchestrator", role: "Autonomous Intake Coordinator" }
      ],
      points: [
        "Interactive sector intake (Tech, Trade, Consulting, Manufacturing)",
        "Target market classification: UAE domestic local vs. GCC & international export",
        "Visa headcount forecasting (1-10+ investor and employee visas)",
        "Office requirements: Virtual desk, flexi-coworking, or dedicated physical premises (Ejari)"
      ],
      mockData: {
        type: "intake",
        sector: "Cross-Border FinTech & Software",
        market: "UAE Domestic + Global International",
        visas: "3 Residence Visas",
        office: "Flexi-Desk with Ejari option"
      }
    },
    {
      id: "step-2",
      number: "02",
      tabTitle: "Jurisdiction & Compliance",
      title: "Jurisdiction & Statutory Compliance Analysis",
      shortDesc: "Specialized agents (licensing-strategist and regulatory-researcher) compare Dubai Mainland (DET) and Free Zones with official source citations.",
      agents: [
        { name: "licensing-strategist", role: "Jurisdiction Evaluator" },
        { name: "regulatory-researcher", role: "Statutory Law Citation Engine" }
      ],
      points: [
        "Dubai Mainland (DET) vs. 45+ Free Zones (DMCC, DIFC, IFZA, DAFZA) algorithmic benchmark",
        "Official statutory source citations: Federal Decree-Law No. 26/2020 & Corporate Tax Law (Decree-Law No. 47/2022)",
        "Qualifying Free Zone Person (QFZP) 0% corporate tax eligibility check",
        "Total Cost of Ownership (TCO) simulation covering licensing, visas, and annual renewal fees"
      ],
      mockData: {
        type: "analysis",
        recommendation: "Dual-Track Analysis: Dubai Mainland (DET) 98% vs. DMCC 93%",
        citations: [
          "Federal Decree-Law No. (26) of 2020 on Commercial Companies (100% Foreign Ownership)",
          "Cabinet Decision No. (139) of 2023 on Qualifying Free Zone Persons (Corporate Tax)",
          "Dubai DET Commercial Licensing Regulations (Order No. 13 of 2011)"
        ]
      }
    },
    {
      id: "step-3",
      number: "03",
      tabTitle: "Human-Approved Pre-Fill",
      title: "Human-Approved Form Pre-Fill & HITL Review",
      shortDesc: "form-automation-agent populates trade name, activity codes, and MOA inputs, pausing at a Human-in-the-Loop (HITL) gate for your explicit sign-off.",
      agents: [
        { name: "form-automation-agent", role: "Registry Synthesizer" },
        { name: "hitl-governance-gate", role: "Human Verification Guard" }
      ],
      points: [
        "Automated trade name clearance and official DED activity code mapping",
        "Bilingual Memorandum of Association (MOA) and Articles generation",
        "Mandatory Human-in-the-Loop (HITL) gate — execution pauses until founder approval",
        "Cryptographically signed audit receipt ensuring zero unapproved filing submissions"
      ],
      mockData: {
        type: "hitl",
        tradeName: "AlphaSphere Technologies LLC",
        activityCodes: ["620101 Software Development", "620201 IT Consultancy"],
        moaStatus: "Drafted & Formatted (Awaiting Founder Sign-off)",
        gateStatus: "PAUSED AT HITL CHECKPOINT"
      }
    },
    {
      id: "step-4",
      number: "04",
      tabTitle: "Banking & Monitoring",
      title: "Corporate Banking & Ongoing Monitoring",
      shortDesc: "banking-readiness-agent drafts your 12-month business plan and compliance checklist while a background monitor tracks UAE regulatory updates.",
      agents: [
        { name: "banking-readiness-agent", role: "Underwriting Dossier Compiler" },
        { name: "regulatory-monitor-daemon", role: "Continuous Law Watchdog" }
      ],
      points: [
        "12-month bankable financial projections and AML/KYC profile packaging",
        "Direct underwriting dossier ready for Tier-1 UAE institutions (Wio, Emirates NBD, Mashreq NeoBiz)",
        "Background monitor actively watching UAE Ministry of Finance & DET regulatory changes",
        "Automated compliance calendar for annual corporate tax filing and license renewal"
      ],
      mockData: {
        type: "banking",
        banks: ["Wio Bank Digital", "Emirates NBD", "Mashreq NeoBiz"],
        dossier: "12-Month Financial Plan & AML Dossier Ready",
        monitorStatus: "Active — Tracking UAE DET & FTA Corporate Tax Bulletins"
      }
    }
  ],
  securityTrustGrid: [
    {
      icon: "shield-alert",
      title: "Zero Unapproved Submissions (HITL Gates)",
      badge: "Mandatory Founder Sign-Off",
      description: "Agents cannot file or transmit documents autonomously. Every government submission halts at an immutable Human-in-the-Loop checkpoint requiring your explicit review and authorization."
    },
    {
      icon: "eye-off",
      title: "Automatic PII Redaction in Langfuse Traces",
      badge: "Zero-Knowledge Observability",
      description: "Passports, Emirates IDs, shareholder photos, and IBANs are scrubbed at the application perimeter with SHA-256 tokenization before traces are sent to Langfuse observability systems."
    },
    {
      icon: "server",
      title: "UAE-Compatible Data Residency",
      badge: "Federal Decree-Law No. 45/2021",
      description: "Architected to strictly comply with UAE Personal Data Protection Law (PDPL). Your corporate data stays sovereignty-protected with in-region encryption at rest and in transit."
    }
  ]
};

export const howItWorksSteps = [
  {
    step: "01",
    title: "Define Business Activities & Ownership",
    description: "Input your target industry, planned UAE commercial activities, shareholder structure, and initial visa requirements in under 3 minutes.",
    badge: "Intelligent Intake",
    points: [
      "2,000+ official UAE commercial activity classifications",
      "Instant multi-shareholder corporate structurer",
      "Visa quota and office allocation forecasting"
    ]
  },
  {
    step: "02",
    title: "AI Jurisdiction & Cost Optimization",
    description: "Our proprietary algorithm benchmarks your exact setup across Dubai Mainland (DED) and 45+ UAE Free Zones (DMCC, DIFC, IFZA, DAFZA, Meydan, and more).",
    badge: "Algorithmic Matching",
    points: [
      "Side-by-side total cost of ownership (TCO) breakdown",
      "Corporate tax (9%) & VAT (5%) applicability auditing",
      "Real-time physical vs. flexi-desk lease compliance"
    ]
  },
  {
    step: "03",
    title: "Automated Document Prep & Compliance Check",
    description: "Autogenerate MOAs, Articles of Association, board resolutions, and KYC packets formatted precisely to regulatory specifications.",
    badge: "Zero-Error Legal Ops",
    points: [
      "Strict UAE Federal Decree-Law No. 45/2021 (PDPL) compliance",
      "Pre-screened against AML/CFT sanctions & PEP lists",
      "Bilingual Arabic-English document synthesis"
    ]
  },
  {
    step: "04",
    title: "License Issuance & Corporate Banking Fast-Track",
    description: "Receive your verified trade license, register your corporate tax status, and connect directly with partner UAE digital and Tier-1 banks.",
    badge: "Direct Execution",
    points: [
      "Integrated corporate bank account readiness dossier",
      "Establishment card & investor residence visa assistance",
      "Continuous compliance & annual renewal monitoring"
    ]
  }
];

export const jurisdictionComparisonData = {
  categories: [
    { id: "all", label: "All Criteria" },
    { id: "ownership", label: "Ownership & Control" },
    { id: "market", label: "Market Access & Scope" },
    { id: "tax", label: "Banking, Tax & Setup" }
  ],
  items: [
    {
      category: "ownership",
      feature: "Foreign Ownership",
      freezone: "100% Foreign Ownership guaranteed across all permitted business activities.",
      mainland: "100% Foreign Ownership for 1,000+ commercial & industrial activities (Federal Decree No. 26/2020).",
      winner: "Tie (Both offer 100% foreign ownership)"
    },
    {
      category: "market",
      feature: "Local UAE Market Trading",
      freezone: "Can trade freely within the Free Zone and internationally. Mainland B2C sales require local distributor or Mainland branch.",
      mainland: "Unrestricted direct trading anywhere across Dubai, the UAE Mainland, and governmental entities.",
      winner: "Mainland (Direct local access)"
    },
    {
      category: "market",
      feature: "Government Contracting & Tenders",
      freezone: "Limited direct eligibility for federal and municipal government contracts.",
      mainland: "Directly eligible to bid on UAE municipal, Dubai Government, and federal contracts.",
      winner: "Mainland"
    },
    {
      category: "ownership",
      feature: "Physical Office Mandates",
      freezone: "Highly flexible: Virtual desk, flexi-desk, or dedicated physical office depending on visa quotas.",
      mainland: "Typically requires physical leased commercial premises registered with Ejari (minimum square footage rules apply).",
      winner: "Free Zone (Lower initial overhead)"
    },
    {
      category: "tax",
      feature: "Corporate Tax Treatment",
      freezone: "0% Corporate Tax on 'Qualifying Income' for Qualifying Free Zone Persons (QFZP); 9% on non-qualifying income.",
      mainland: "Standard UAE Corporate Tax: 0% up to AED 375,000 profit; 9% on taxable net profits exceeding AED 375,000.",
      winner: "Depends on Activity & QFZP status"
    },
    {
      category: "tax",
      feature: "Import & Customs Duties",
      freezone: "0% customs duties when importing goods into the designated Free Zone or transshipping internationally.",
      mainland: "Standard 5% UAE customs duty applies when importing goods directly into the UAE Mainland.",
      winner: "Free Zone"
    },
    {
      category: "tax",
      feature: "Corporate Bank Account Opening",
      freezone: "Standard approval cycle (2-6 weeks depending on substance, physical office, and shareholder profiles).",
      mainland: "Generally faster bank underwriting with UAE Tier-1 institutions due to established physical commercial substance.",
      winner: "Mainland"
    },
    {
      category: "ownership",
      feature: "Visa Allocation Flexibility",
      freezone: "Predictable visa packages tied to chosen flexi-desk or office package (1 to 6+ investor/employee visas).",
      mainland: "Visa quota strictly scales with leased square footage (e.g. 1 visa per 80-100 sq. ft. of Ejari space).",
      winner: "Free Zone (Capital-efficient)"
    }
  ]
};

export const securityFeatures = [
  {
    icon: "shield",
    title: "UAE PDPL Compliant",
    description: "Fully compliant with UAE Federal Decree-Law No. 45/2021 regarding Personal Data Protection. Your corporate records remain sovereignty-protected."
  },
  {
    icon: "lock",
    title: "AES-256 Military-Grade Encryption",
    description: "All shareholder passports, Emirates IDs, bank statements, and corporate resolutions are encrypted at rest and in transit via TLS 1.3."
  },
  {
    icon: "database",
    title: "Zero-Retention Biometric Policy",
    description: "Identity verifications are processed strictly via secure tokenized cryptographic hashes. Raw biometric scans are never stored on third-party servers."
  },
  {
    icon: "file-check",
    title: "Deterministic Audit Trails",
    description: "Every jurisdiction calculation, document generation step, and regulatory submission timestamp is cryptographically logged for full compliance traceability."
  }
];

export const faqItems = [
  {
    question: "How is BizNavigator different from a regular AI chatbot?",
    answer: "Generic chatbots hallucinate regulatory rules, lack statutory law citations, and cannot interact with corporate workflows. Dubai BizNavigator is an autonomous multi-agent system orchestrating specialized legal, tax, and banking agents. It calculates exact fee schedules, references verified UAE Federal Decrees and Cabinet Decisions, pre-fills official government forms, and pauses at deterministic Human-in-the-Loop (HITL) checkpoints before generating bank-ready dossiers."
  },
  {
    question: "Does BizNavigator submit government forms without my permission?",
    answer: "Never. BizNavigator enforces a non-negotiable Human-in-the-Loop (HITL) safety policy. The agent autonomously synthesizes trade name applications, activity code mappings, and Memorandum of Association (MOA) documents, but halts execution at an approval gate. No document or application is ever submitted to the Dubai Department of Economy and Tourism (DET) or any Free Zone authority without your explicit review and manual sign-off."
  },
  {
    question: "How is my passport and corporate banking data protected?",
    answer: "We implement defense-in-grade sovereignty and privacy controls. All shareholder passports, Emirates IDs, bank statements, and corporate resolutions are encrypted at rest using AES-256 and in transit via TLS 1.3. Sensitive Personally Identifiable Information (PII) is automatically redacted and replaced with cryptographic SHA-256 tokens before telemetry reaches Langfuse observability pipelines. Furthermore, our data architecture complies strictly with UAE Federal Decree-Law No. 45/2021 on Personal Data Protection (PDPL)."
  },
  {
    question: "Does BizNavigator replace a UAE lawyer or PRO?",
    answer: "No. Dubai BizNavigator is an intelligent AI preparation co-pilot designed to streamline research, cost modeling, document drafting, and bank readiness; it does NOT provide licensed legal advice or legal representation. While our agents reference official UAE statutes and DET regulations with high precision, users should consult a licensed UAE legal practitioner or certified corporate services firm for formal legal opinions and notarization."
  },
  {
    question: "What is the primary difference between a Free Zone and a Mainland company?",
    answer: "A Mainland company (licensed by the Dubai Department of Economy and Tourism - DET) permits unrestricted direct business across all UAE domestic markets and enables direct bidding on government tenders. A Free Zone company offers 100% foreign ownership with zero customs duties within designated zones, zero currency restrictions, and potential 0% Corporate Tax for Qualifying Free Zone Persons (QFZP), but B2C sales inside the UAE Mainland typically require a local commercial distributor or Mainland subsidiary."
  },
  {
    question: "How does UAE Corporate Tax (9%) apply to my new business?",
    answer: "Effective June 2023, the UAE levies a 9% federal corporate tax on net taxable business profits exceeding AED 375,000 (~$102,000 USD). Income up to AED 375,000 is taxed at 0%. Furthermore, qualifying micro-enterprises may benefit from Small Business Relief (SBR) up to AED 3,000,000 revenue. Certain Free Zone companies meeting Qualifying Free Zone Person (QFZP) criteria can maintain 0% tax on qualifying transactions."
  }
];

export const earlyAccessBenefits = [
  "Priority access to the AI Jurisdiction Cost Simulator",
  "Free personalized 30-minute UAE Corporate Structuring Consultation",
  "Exclusive AED 2,500 fee voucher upon official platform launch",
  "Pre-cleared expedited corporate bank account onboarding checklist"
];
