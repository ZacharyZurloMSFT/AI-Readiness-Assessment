# AI Platform Readiness Assessment

[![Validate](https://github.com/krishna-sunkavalli/ai-platform-readiness-assessment/actions/workflows/validate.yml/badge.svg)](https://github.com/krishna-sunkavalli/ai-platform-readiness-assessment/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Assess your Azure environment's readiness for **Microsoft Foundry**-based AI workloads. This [Azure Monitor Workbook](https://learn.microsoft.com/azure/azure-monitor/visualize/workbooks-overview) evaluates resources across **9 capability pillars** aligned with the [Azure AI Landing Zone](https://learn.microsoft.com/azure/cloud-adoption-framework/scenarios/ai/platform/landing-zones) using **Azure Resource Graph** queries and presents an interactive, shareable dashboard — no agents, no code, no external dependencies.

> **Scope:** This assessment is focused on **Microsoft Foundry** (`microsoft.cognitiveservices/accounts` with `kind = AIServices`). Standalone Azure OpenAI accounts and classic AI Hub workspaces (`microsoft.machinelearningservices/workspaces`) are intentionally excluded — Microsoft Foundry is the unified successor.

Some data-plane signals (agents, evaluation runs, threads, Conditional Access, MFA, PIM, quota/PTU usage, budgets) are **not exposed via Azure Resource Graph** and are surfaced as Manual/API checks with the exact REST call documented in the workbook.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fkrishna-sunkavalli%2Fai-platform-readiness-assessment%2Fmain%2Fworkbook%2Fazuredeploy.json)

<!-- TODO: Add screenshot — save as docs/screenshot.png -->

## What It Assesses

| # | Pillar | Max | Queries | Coverage |
|:-:|--------|:---:|:-------:|----------|
| 1 | **Foundry Inventory** | 8 | 5 | Foundry accounts, projects, connections, capability hosts (agent service), manual callout for model deployments / agents / evaluations |
| 2 | **Data Management & Governance** | 7 | 8 | Purview, Databricks (Unity Catalog), Data Factory + Git, ADLS Gen2, Microsoft Fabric, lifecycle policies |
| 3 | **Retrieval & Context Enablement** | 5 | 5 | AI Search, Redis, Cosmos DB / PostgreSQL pgvector, Document Intelligence |
| 4 | **Responsible AI** | 5 | 7 | **Foundry guardrails (RAI policies)**, RaiMonitor capability, guardrail feature coverage (jailbreak, prompt shield, groundedness, agent safety), per-deployment guardrail assignment (manual), policy controls detail (manual), red teaming (manual), standalone Content Safety (informational) |
| 5 | **Identity & Access** | 5 | 7 | Disable local auth, Managed Identity coverage, RBAC analysis, Conditional Access / MFA / PIM / Entra Agent ID (manual) |
| 6 | **Network & Security** | 12 | 15 | Private endpoints, network injection mode, CMK, Key Vault hardening, VNets, NSGs, Firewall, WAF, Private DNS, Bastion, ACR, APIM, Defender, Sentinel |
| 7 | **Policy & Compliance** | 3 | 5 | AI policy assignments, compliance state, Defender on AI recommendations, Compliance Manager, regulatory initiatives |
| 8 | **Cost & Operations** | 5 | 4 | Multi-region foundry, Container Apps Dynamic Sessions, quotas / PTUs (manual), budgets (manual) |
| 9 | **Monitoring & Operations** | 5 | 6 | App Insights, diagnostics coverage, metric alerts, LAW routing, quality / online evaluators |
|   | **Total** | **55** | **62** | 48 automated ARG queries + 14 Manual/API checks |

For the full list of queries with their IDs and descriptions, see [queries.md](queries.md).

### Scoring Logic

Each pillar score is computed by summing weighted points from a fixed Foundry-aligned signal set, then normalising to a percentage of the pillar's maximum. The overall score is the sum of weighted points divided by **55**.

| Signal | Pillar | Points | Trigger |
|--------|:------:|:------:|---------|
| Foundry account exists | FDY | 2 | `kind=AIServices` present |
| Foundry account has identity | FDY | +1 | Managed identity assigned |
| Foundry project exists | FDY | 2 | `accounts/projects` present |
| Project identity | FDY | +1 | Project principalId set |
| Foundry connections | FDY | 1 | Any connection configured |
| Capability host (agent service) | FDY | 1 | `capabilityHosts` present |
| Foundry default guardrails | RAI | 2 | Any Foundry account (Microsoft.Default policy is automatic) |
| Custom guardrail policy | RAI | 3 | Custom `raiPolicies` defined on Foundry |
| Purview | DMG | 3 | Account present |
| Databricks | DMG | 2 | Workspace present |
| Data Factory | DMG | 1–2 | +1 base, +1 if Git configured |
| AI Search | RCE | 2 | Service present |
| Redis | RCE | 1 | Cache present |
| Cosmos DB | RCE | 1 | Account present |
| Document Intelligence | RCE | 1 | Account present |
| Foundry identity | IAM | 2 | Identity on Foundry account |
| APIM with identity | IAM | 1 | APIM + managed identity |
| Foundry no-key auth | IAM | 2 | `disableLocalAuth=true` |
| Key Vault hardened | SEC | 3 | RBAC + soft delete + purge protection |
| Foundry private endpoint | SEC | 2 | PE attached |
| APIM | SEC | 2 | Service present |
| Private DNS for AI | SEC | 1 | Zones for cognitiveservices/openai/etc. |
| Azure Firewall | SEC | 1 | Firewall present |
| WAF | SEC | 1 | App Gateway WAF or Front Door WAF |
| Bastion | SEC | 1 | Host present |
| Foundry CMK | SEC | 1 | CMK encryption enabled |
| Foundry private endpoint | POL | 1 | PE attached |
| KV hardened | POL | 1 | Hardened |
| Foundry CMK | POL | 1 | CMK enabled |
| Multi-region foundry | OPS | 1–2 | +1 if 1 region, +2 if ≥2 regions |
| App Insights | OPS | 2 | Component present |
| APIM | OPS | 1 | Service present |
| App Insights | MON | 3 | Component present |
| Foundry identity | MON | 2 | Identity on Foundry account |

**Per-pillar score** = pillar weighted points ÷ pillar max × 100%. **Overall AI Readiness Score** = total weighted points ÷ 55 × 100%.

| Score Range | Color | Status |
|:-----------:|:-----:|--------|
| ≥ 80% | Green | Ready |
| 50–79% | Yellow | Partial |
| < 50% | Red | Needs Attention |

## Getting Started

### Prerequisites

- An Azure subscription with **Reader** role
- No additional software required — the workbook runs entirely in the Azure Portal

### Option 1: Deploy to Azure (recommended)

Click the button above, or use the direct link:

```
https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fkrishna-sunkavalli%2Fai-platform-readiness-assessment%2Fmain%2Fworkbook%2Fazuredeploy.json
```

### Option 2: Azure CLI

```bash
az group create --name rg-ai-readiness --location eastus

az deployment group create \
  --resource-group rg-ai-readiness \
  --template-file workbook/azuredeploy.json \
  --parameters workbookDisplayName="AI Platform Readiness Assessment"
```

### Option 3: Azure PowerShell

```powershell
New-AzResourceGroup -Name "rg-ai-readiness" -Location "eastus"

New-AzResourceGroupDeployment `
  -ResourceGroupName "rg-ai-readiness" `
  -TemplateFile "workbook/azuredeploy.json" `
  -workbookDisplayName "AI Platform Readiness Assessment"
```

### Option 4: Manual Import

1. Open **Azure Portal** → **Monitor** → **Workbooks**
2. Click **+ New** → **Advanced Editor** (`</>` icon)
3. Paste the contents of [`workbook/ai-readiness-assessment.workbook`](workbook/ai-readiness-assessment.workbook)
4. Click **Apply** → **Done Editing** → **Save**

## Using the Workbook

1. **Select Subscriptions** — Use the picker at the top to scope the assessment
2. **Review Summary** — The top section shows the overall score ring and per-pillar progress bars
3. **Expand Pillars** — Click each pillar section to see detailed query results
4. **Check Status Icons** — ✅ Compliant, ⚠️ Warning, ❌ Missing

## Repository Structure

```
├── workbook/
│   ├── ai-readiness-assessment.workbook   # The Azure Workbook (auto-generated source of truth)
│   └── azuredeploy.json                   # ARM template for deployment (auto-generated)
├── docs/
│   └── QUERIES.md                         # Full query reference by pillar (auto-generated)
├── scripts/
│   ├── build-workbook.py                  # Generates the .workbook + queries.md from a structured definition
│   ├── build-arm-template.ps1             # Embeds workbook into ARM template
│   └── validate-queries.ps1               # Test all ARG queries against live Azure
├── .github/
│   ├── workflows/
│   │   ├── validate.yml             # CI: JSON validation & linting
│   │   └── release.yml              # Tag-triggered release packaging
│   ├── ISSUE_TEMPLATE/                    # Bug report & feature request templates
│   └── PULL_REQUEST_TEMPLATE/             # PR template with checklist
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── SECURITY.md
└── SUPPORT.md
```

## Contributing

This project welcomes contributions and suggestions. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Most contributions require you to agree to a Contributor License Agreement (CLA). For details, visit https://cla.opensource.microsoft.com.

> **Maintainers:** After creating the repo, [configure branch protection](CONTRIBUTING.md#repository-setup-maintainers) on `main` to require CI checks and code review before merging.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general). Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party's policies.

## License

[MIT](LICENSE)
