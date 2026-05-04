# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.0.0] - Unreleased

### Added

- **Foundry Inventory pillar** (FDY-001..004) — Foundry accounts, projects, and informational ARG-indexed connections/capability hosts for Standard tier
- **Identity & Access pillar** (IAM-001..007) — Foundry account auth (`disableLocalAuth`), managed identity coverage, RBAC role-assignment analysis on Foundry resources, manual callouts for Conditional Access, MFA, PIM, and Microsoft Entra Agent ID inventory
- **Network & Security expansion** (SEC-005..010, SEC-012, SEC-015) — Virtual networks, NSGs, Azure Firewall, WAF (App Gateway / Front Door), Private DNS zones for AI service private endpoints, Bastion, ACR, Sentinel
- **Policy & Compliance pillar** (POL-001..005) — AI-specific Azure Policy assignment detection, policy compliance state, Defender for Cloud recommendations on AI resources, manual callouts for Compliance Manager and regulatory initiatives
- **Cost & Operations pillar** (OPS-001..004) — Multi-region Foundry presence, Container Apps Dynamic Sessions, manual callouts for quotas / PTUs and budgets
- **Network injection mode** (SEC-002) — Detects Foundry network injection scenarios and approved-outbound mode
- **Customer-managed keys** (SEC-003) — Detects CMK encryption on Foundry accounts
- **Python workbook generator** (`scripts/build-workbook.py`) — Generates the `.workbook` source and `queries.md` from a single structured definition; eliminates manual JSON editing
- **Auto-generated query reference** — `queries.md` and `docs/QUERIES.md` are now produced from the workbook source and stay in sync

### Changed

- **Responsible AI pillar refocused on Foundry guardrails** — Lead check is now `RAI-001 Foundry Guardrail Policies` as a Manual/API callout because custom `raiPolicies` are not consistently indexed in Azure Resource Graph. Score signal is now `+2` for any Foundry account because Microsoft.Default applies automatically.
- **Foundry-only scope** — Workbook now exclusively assesses Microsoft Foundry (`microsoft.cognitiveservices/accounts` with `kind = AIServices`). Standalone Azure OpenAI account signals are no longer included in any score signal
- **Pillar count: 6 → 9** — Reorganised into Foundry Inventory, Data Management & Governance, Retrieval & Context Enablement, Responsible AI, Identity & Access, Network & Security, Policy & Compliance, Cost & Operations, Monitoring & Operations
- **Total queries: 39 → 60** (46 ARG + 14 Manual/API)
- **Maximum score: 36 → 50** with rebalanced pillar weights aligned to the Azure AI Landing Zone
- **Score signals** — Removed standalone OpenAI and legacy model-management compute signals; added Foundry project identity, network injection, CMK, Private DNS, Firewall, WAF, and Bastion signals
- **MDL-001..008 removed** — Model-related queries consolidated into the Foundry Inventory pillar; deployment-level signals are not assessed until they are reliably available through Azure Resource Graph or a supported workbook data source

### Removed

- **Legacy model-management workspace and compute checks** — Out of scope for Foundry-aligned assessment
- **Unavailable Foundry data-plane inventory callout** — Removed until this data is available through a supported workbook data source
- **Standalone OpenAI signal** — Score now requires `kind=AIServices` (Microsoft Foundry)
- **AI Search SKU heuristic** — All current AI Search SKUs (including `free` and `basic`) support vector search; the legacy SKU-based heuristic was producing false negatives

## [1.1.0] - 2026-04-03

### Added

- **RAI-002 Content Filtering Enabled** — Replaced manual Safety Evaluators check with ARG query that detects `RaiMonitor` capability on Azure OpenAI / AI Services accounts
- **RAI-004 Content Safety Feature Matrix** — New ARG query showing 10 content safety features per AI account: Jailbreak Detection, Prompt Shield, Protected Material, Groundedness Detection, Text/Image Moderation, RAI Policies, Content Provenance, Agent Safety, Custom Categories
- **AI Resource Landscape** — New informational summary section with bubble map and breakdown table showing AI resources by region and service category (does not affect scoring)
- **Release workflow** (`.github/workflows/release.yml`) — Tag-triggered GitHub Actions workflow that validates, packages, and creates a GitHub Release with versioned artifacts and Deploy-to-Azure button
- **Dependabot** (`.github/dependabot.yml`) — Weekly GitHub Actions version monitoring
- **CODEOWNERS** — Team-based auto-assignment for PR reviews
- **.editorconfig** — Consistent formatting across contributors
- **Branch protection guide** in CONTRIBUTING.md — Post-repo-creation setup instructions

### Changed

- Total queries: 36 → 37 (35 ARG + 2 manual)
- Manual checks reduced from 3 to 2 (RAI-002 is now automated)
- CI workflow (`validate.yml`) — Removed path filters, added ARM/workbook sync check, added PSScriptAnalyzer linting job
- ARM template (`azuredeploy.json`) — Added `metadata` block (description, author, version) and `tags` parameter
- Build script (`build-arm-template.ps1`) — Generates metadata and tags in ARM template
- `.gitignore` — Added `.env`, `.env.local`, `*.code-workspace` patterns
- README — Added maintainer callout for branch protection, updated repo structure, screenshot reference moved to TODO comment

### Fixed

- **RCE-003** — Renamed `extend kind = case(...)` to `extend dbKind = case(...)` to avoid overriding ARG built-in `kind` column

## [1.0.0] - 2026-04-02

### Added

- Initial release with 36 assessment queries across 6 pillars
- **Data Management & Governance (8 queries)**: Purview accounts, scan rulesets, data classification, lineage, Databricks Unity Catalog, ADF ETL, Lakehouse (ADLS/Databricks/Fabric), retention policies
- **Retrieval & Context Enablement (5 queries)**: AI Search, Redis Cache, Cosmos DB / PostgreSQL, vector stores inventory, Document Intelligence
- **Model Management (8 queries)**: Azure OpenAI / AI Services, Microsoft Foundry projects, online endpoints, model deployments, fine-tuned models, evaluation runs
- **Responsible AI (3 queries)**: Content Safety (ARG), safety evaluators (Manual/API), red teaming runs (Manual/API)
- **Security & Compliance (7 queries)**: Managed identities, Key Vault, private networking, Defender for Cloud, Defender for AI, model API authentication, APIM as AI gateway
- **Monitoring & Operations (5 queries)**: Application Insights, AI services diagnostics, metric alerts, Log Analytics workspace coverage, quality evaluators (Manual/API)
- Interactive HTML summary with pillar score bars and overall AI readiness ring
- ARM template (`azuredeploy.json`) for one-click deployment
- Deploy to Azure button
- GitHub Actions CI for JSON validation
