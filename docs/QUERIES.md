# AIRA — Query Reference

All queries executed by the AI Platform Readiness Assessment workbook. This file is auto-generated from the workbook source by `scripts/build-workbook.py`.

**Total: 62 queries** (48 ARG, 14 Manual/API).

## Foundry Inventory

| Query ID | Query Name | Type | Description |
|----------|-----------|------|-------------|
| FDY-001 | Foundry Accounts | ARG | Microsoft Foundry account inventory with identity, network, encryption, and auth configuration. |
| FDY-002 | Foundry Projects | ARG | Projects organize models, data, agents, and evaluations within a Foundry account. |
| FDY-003 | Foundry Connections | ARG | Connections wire Foundry projects to AI Search, Storage, Cosmos, OpenAI, Bing, and other resources. |
| FDY-004 | Capability Hosts (Agent Service) | ARG | Capability hosts indicate Foundry Agent Service is configured (storage + thread + vector store wiring). |
| FDY-005 | Model Deployments, Agents, Evaluations, Threads | Manual/API | Foundry deployments and data-plane resources are not reliably exposed to Azure Resource Graph. |

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
| RCE-003 | Cosmos DB / PostgreSQL | ARG | Vector-capable databases for RAG patterns. |
| RCE-004 | Vector Stores | ARG | All vector-capable stores: AI Search, Cosmos DB, PostgreSQL. |
| RCE-005 | Document Intelligence | ARG | Azure AI Document Intelligence &#x2014; OCR / document processing. |

## Responsible AI

| Query ID | Query Name | Type | Description |
|----------|-----------|------|-------------|
| RAI-001 | Foundry Guardrail Policies | ARG | Custom RAI (guardrail) policies defined on Foundry accounts &#x2014; layered on top of Microsoft.Default. |
| RAI-002 | Foundry Content Filter Capability | ARG | Foundry accounts with the RaiMonitor capability available (required for guardrail enforcement at runtime). |
| RAI-003 | Foundry Guardrail Feature Coverage | ARG | Built-in safety features available on each Foundry account (jailbreak, prompt shield, groundedness, agent safety, etc.). |
| RAI-004 | Per-Deployment Guardrail Assignment | Manual/API | Verify which guardrail policy is bound to each model deployment and agent. |
| RAI-005 | Guardrail Policy Controls Detail | Manual/API | Inspect the actual risks, severity thresholds, and intervention points configured on each custom policy. |
| RAI-006 | Red Teaming Runs | Manual/API | Check for completed red teaming runs and Attack Success Rate (ASR) metrics. |
| RAI-007 | Standalone Content Safety Services | ARG | Dedicated Content Safety service instances &#x2014; informational only; Foundry guardrails are the primary control plane. |

## Identity & Access

| Query ID | Query Name | Type | Description |
|----------|-----------|------|-------------|
| IAM-001 | Foundry Account Authentication | ARG | Disable local auth (key-based) on Foundry accounts &#x2014; Entra ID only is recommended. |
| IAM-002 | Managed Identity Coverage | ARG | Foundry accounts, projects, AI Search, and APIM with managed identity. |
| IAM-003 | RBAC Role Assignments on Foundry | ARG | Counts of role assignments on Foundry accounts &#x2014; flag potential overprivileged access. |
| IAM-004 | Conditional Access Policies | Manual/API | Risk-based Conditional Access for Foundry portal and APIs. |
| IAM-005 | Multi-Factor Authentication | Manual/API | MFA enforcement for users accessing Foundry. |
| IAM-006 | Privileged Identity Management | Manual/API | Just-in-time elevation for Foundry administrative roles. |
| IAM-007 | Microsoft Entra Agent ID Inventory | Manual/API | Centralized AI agent identity catalog. |

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
| SEC-012 | Azure Container Registry | ARG | ACR for Foundry custom container images and managed online endpoint deployments. |
| SEC-013 | Defender for Cloud Plans | ARG | Security posture and threat protection plans. |
| SEC-014 | Defender for AI Services | ARG | Threat protection specifically for AI workloads (prompt injection, model abuse). |
| SEC-015 | Microsoft Sentinel | ARG | SIEM/SOAR coverage on Log Analytics workspaces. |

## Policy & Compliance

| Query ID | Query Name | Type | Description |
|----------|-----------|------|-------------|
| POL-001 | Policy Assignments Targeting AI | ARG | Azure Policy assignments referencing Cognitive Services / Foundry / ML scopes. |
| POL-002 | Policy Compliance State | ARG | Non-compliant policy states across the subscription. |
| POL-003 | Defender Recommendations on AI | ARG | Open Defender for Cloud recommendations targeting Foundry / Cognitive Services / ML / Search. |
| POL-004 | Compliance Manager State | Manual/API | Microsoft Purview Compliance Manager assessment scores. |
| POL-005 | Regulatory Compliance Initiatives | Manual/API | ISO/IEC 23053:2022, NIST AI RMF, EU AI Act alignment. |

## Cost & Operations

| Query ID | Query Name | Type | Description |
|----------|-----------|------|-------------|
| OPS-001 | Foundry Multi-Region Presence | ARG | Foundry accounts deployed across multiple regions for BCDR. |
| OPS-002 | Container Apps Dynamic Sessions | ARG | Isolated, ephemeral execution environments for AI agent code execution. |
| OPS-003 | Foundry Quotas & PTU Usage | Manual/API | Provisioned Throughput Units and rate limits. |
| OPS-004 | Cost Tracking & Budgets | Manual/API | Subscription / resource group budgets and AI cost allocation. |

## Monitoring & Operations

| Query ID | Query Name | Type | Description |
|----------|-----------|------|-------------|
| MON-001 | Application Insights | ARG | APM / tracing for Foundry-backed applications and agents. |
| MON-002 | Foundry Diagnostics Coverage | ARG | Diagnostic settings on Foundry accounts. |
| MON-003 | Metric Alert Rules | ARG | Metric alerts targeting Foundry / Cognitive Services. |
| MON-004 | Log Analytics Workspace Routing | ARG | Foundry / AI Search resources sending diagnostics to a workspace. |
| MON-005 | Foundry Quality Evaluators | Manual/API | Groundedness, relevance, coherence, fluency evaluators on Foundry agents. |
| MON-006 | Continuous / Online Evaluation | Manual/API | Production-time evaluation runs on Foundry deployments. |

