# AIRA — Query Reference

All queries executed by the AI Platform Readiness Assessment workbook. This file is auto-generated from the workbook source by `scripts/build-workbook.py`.

**Total: 41 queries** (41 ARG).

## Foundry Inventory

| Query ID | Query Name | Type | Description |
|----------|-----------|------|-------------|
| FDY-001 | Foundry Accounts | ARG | Microsoft Foundry account inventory with identity, network, encryption, and auth configuration. |
| FDY-002 | Foundry Projects | ARG | Projects organize models, data, and agents within a Foundry account. |

## Data Management & Governance

| Query ID | Query Name | Type | Description |
|----------|-----------|------|-------------|
| DMG-001 | Purview Accounts | ARG | Microsoft Purview &#x2014; Unified data governance platform. |
| DMG-002 | Purview Scan Rulesets | ARG | Validate scan rulesets are configured for data discovery. |
| DMG-003 | Data Classification Rules | ARG | Cloud connector configurations enabling data classification. |
| DMG-004 | Data Lineage Enablement | ARG | Lineage endpoints for tracking data flow. |
| DMG-005 | Unity Catalog (Databricks) | ARG | Azure Databricks workspaces for unified analytics governance. |
| DMG-006 | Data Factory ETL | ARG | ADF instances with Git integration. |
| DMG-007 | Lakehouse Presence | ARG | ADLS Gen2, Databricks, or Microsoft Fabric for enterprise data lake. |
| DMG-008 | ADLS Lifecycle Policies | ARG | Retention and lifecycle management on ADLS Gen2. |

## Retrieval & Context Enablement

| Query ID | Query Name | Type | Description |
|----------|-----------|------|-------------|
| RCE-001 | AI Search | ARG | Azure AI Search &#x2014; Semantic and vector search capabilities. |
| RCE-002 | Redis Cache | ARG | Azure Cache for Redis &#x2014; Semantic / response caching. |
| RCE-003 | Cosmos DB / PostgreSQL | ARG | Databases used for retrieval-augmented generation patterns. |
| RCE-004 | Vector Stores | ARG | Vector store inventory: AI Search, Cosmos DB with vector search enabled, and PostgreSQL candidates for pgvector. |
| RCE-005 | Document Intelligence | ARG | Azure AI Document Intelligence &#x2014; OCR / document processing. |

## Responsible AI

| Query ID | Query Name | Type | Description |
|----------|-----------|------|-------------|
| RAI-001 | Foundry Guardrail Feature Coverage | ARG | Built-in safety features available on each Foundry account (jailbreak, prompt shield, groundedness, agent safety, etc.). |

## Identity & Access

| Query ID | Query Name | Type | Description |
|----------|-----------|------|-------------|
| IAM-001 | Foundry Account Authentication | ARG | Disable local auth (key-based) on Foundry accounts &#x2014; Entra ID only is recommended. |
| IAM-002 | Managed Identity Coverage | ARG | Foundry accounts, projects, AI Search, and APIM with managed identity. |
| IAM-003 | RBAC Role Assignments on Foundry | ARG | Counts of role assignments on Foundry accounts &#x2014; flag potential overprivileged access. |

## Network & Security

| Query ID | Query Name | Type | Description |
|----------|-----------|------|-------------|
| SEC-001 | Foundry Private Networking | ARG | Public access and private endpoint state on Foundry accounts and AI Search. |
| SEC-002 | Foundry Network Injection | ARG | Foundry account network injection mode (Allow internet / Approved-only outbound). |
| SEC-003 | Customer-Managed Keys (CMK) | ARG | Foundry accounts encrypted with a customer-managed Key Vault key. |
| SEC-004 | Key Vault Hardening | ARG | Centralized secret management with RBAC, soft delete, purge protection. |
| SEC-005 | Virtual Networks & Peering | ARG | VNets, subnets, and peering &#x2014; Foundry network landing zone footprint. |
| SEC-006 | Network Security Groups | ARG | NSGs enforcing inbound/outbound traffic policies. |
| SEC-007 | Azure Firewall | ARG | Centralized outbound traffic control and data exfiltration protection. |
| SEC-008 | Web Application Firewall | ARG | WAF on Application Gateway / Front Door for internet-facing AI workloads. |
| SEC-009 | Private DNS Zones for AI Services | ARG | Required for private endpoint name resolution to Foundry / AI Search / OpenAI. |
| SEC-010 | Azure Bastion | ARG | Secure RDP/SSH access to jumpboxes inside Foundry VNet without public IPs. |
| SEC-011 | API Management as AI Gateway | ARG | APIM for centralized AI API access control, throttling, and auth. |
| SEC-012 | Defender for Cloud Plans | ARG | Security posture and threat protection plans. |
| SEC-013 | Defender for AI Services | ARG | Threat protection specifically for AI workloads (prompt injection, model abuse). |
| SEC-014 | Microsoft Sentinel | ARG | SIEM/SOAR coverage on Log Analytics workspaces. |

## Policy & Compliance

| Query ID | Query Name | Type | Description |
|----------|-----------|------|-------------|
| POL-001 | Policy Assignments Targeting AI | ARG | Azure Policy assignments referencing Cognitive Services / Foundry / AI Search scopes. |
| POL-002 | Policy Compliance State | ARG | Non-compliant policy states across the subscription. |

## Cost & Operations

| Query ID | Query Name | Type | Description |
|----------|-----------|------|-------------|
| OPS-001 | Foundry Multi-Region Presence | ARG | Foundry accounts deployed across multiple regions for BCDR. |
| OPS-002 | Container Apps Dynamic Sessions | ARG | Isolated, ephemeral execution environments for AI agent code execution. |

## Monitoring & Operations

| Query ID | Query Name | Type | Description |
|----------|-----------|------|-------------|
| MON-001 | Application Insights | ARG | APM / tracing for Foundry-backed applications and agents. |
| MON-002 | Foundry Diagnostics Coverage | ARG | Diagnostic settings on Foundry accounts. |
| MON-003 | Metric Alert Rules | ARG | Metric alerts targeting Foundry / Cognitive Services. |
| MON-004 | Log Analytics Workspace Routing | ARG | Foundry / AI Search resources sending diagnostics to a workspace. |

