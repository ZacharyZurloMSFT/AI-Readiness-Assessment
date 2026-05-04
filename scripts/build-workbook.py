#!/usr/bin/env python3
"""
Generates workbook/ai-readiness-assessment.workbook from a structured definition.

Scope: Microsoft Foundry only (kind=AIServices). Excludes standalone Azure OpenAI
and generic Cognitive Services accounts other than ContentSafety / Document Intelligence,
which are explicitly assessed.
"""
from __future__ import annotations
import json, pathlib, copy

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "workbook" / "ai-readiness-assessment.workbook"

# ---------------------------------------------------------------------------
# Helpers to build workbook items
# ---------------------------------------------------------------------------

SUBSCRIPTION_RESOURCES = ["{Subscription}"]


def html_block(text: str, name: str) -> dict:
    return {"type": 1, "content": {"json": text}, "name": name}


def query_header(qid: str, title: str, subtitle: str) -> dict:
    html = (
        "<div style='margin:16px 0 4px 0;border-bottom:1px solid #edebe9;padding-bottom:4px'>"
        f"<span style='font-size:11px;font-weight:600;color:#0078d4;text-transform:uppercase;letter-spacing:.5px'>{qid}</span>"
        "&nbsp;&nbsp;"
        f"<span style='font-size:14px;font-weight:600;color:#323130'>{title}</span>"
        f"<span style='font-size:12px;color:#605e5c;margin-left:8px'>{subtitle}</span>"
        "</div>"
    )
    return html_block(html, f"{qid.lower()}-header")


def manual_callout(qid: str, title: str, subtitle: str, body: str) -> dict:
    html = (
        "<div style='margin:16px 0 4px 0;border-bottom:1px solid #edebe9;padding-bottom:4px'>"
        f"<span style='font-size:11px;font-weight:600;color:#0078d4;text-transform:uppercase;letter-spacing:.5px'>{qid}</span>"
        "&nbsp;&nbsp;"
        f"<span style='font-size:14px;font-weight:600;color:#323130'>{title}</span>"
        f"<span style='font-size:12px;color:#605e5c;margin-left:8px'>Manual/API &#x2014; {subtitle}</span>"
        "</div>"
        "<div style='margin:4px 0 8px 0;padding:8px 12px;background:#fff4ce;border-left:3px solid #ffb900;border-radius:3px;font-size:12px;color:#323130'>"
        f"<strong>&#x26A0; Manual Check Required:</strong> {body}"
        "</div>"
    )
    return html_block(html, f"{qid.lower()}-header")


def arg_query(
    qid: str,
    title: str,
    query: str,
    visualization: str = "table",
    formatters: list | None = None,
    no_data: str = "No resources found in the selected subscription(s).",
    extra: dict | None = None,
) -> dict:
    item = {
        "type": 3,
        "content": {
            "version": "KqlItem/1.0",
            "query": query,
            "size": 3,
            "title": title,
            "queryType": 1,
            "resourceType": "microsoft.resourcegraph/resources",
            "crossComponentResources": SUBSCRIPTION_RESOURCES,
            "visualization": visualization,
            "noDataMessage": no_data,
            "noDataMessageStyle": 4,
        },
        "name": f"{qid.lower()}-query",
    }
    if formatters:
        item["content"]["gridSettings"] = {"formatters": formatters}
    if extra:
        item["content"].update(extra)
    return item


def threshold_icon_formatter(column: str, success_value: str, default_repr: str = "warning",
                             success_text: str = "Yes", default_text: str = "No") -> dict:
    return {
        "columnMatch": column,
        "formatter": 18,
        "formatOptions": {
            "thresholdsOptions": "icons",
            "thresholdsGrid": [
                {"operator": "==", "thresholdValue": success_value, "representation": "success", "text": success_text},
                {"operator": "Default", "representation": default_repr, "text": default_text},
            ],
        },
    }


def heat_formatter(column: str, palette: str = "greenRed") -> dict:
    return {
        "columnMatch": column,
        "formatter": 8,
        "formatOptions": {"palette": palette},
    }


def group_section(title: str, items: list, expanded: bool = False, name: str | None = None) -> dict:
    return {
        "type": 12,
        "content": {
            "version": "NotebookGroup/1.0",
            "groupType": "editable",
            "title": title,
            "expandable": True,
            "expanded": expanded,
            "items": items,
        },
        "name": name or (title.lower().replace(" & ", "-").replace(" ", "-") + "-group"),
    }


# ---------------------------------------------------------------------------
# Top-level summary parameters: score ring + pillar bars
# ---------------------------------------------------------------------------

# Common signal aggregation used by both summary parameters.
# All Foundry-related counts use kind=~'AIServices' (Foundry account).
SIGNAL_AGG = """resources
| summarize
    purview=countif(type=='microsoft.purview/accounts'),
    databricks=countif(type=='microsoft.databricks/workspaces'),
    adf=countif(type=='microsoft.datafactory/factories'),
    adf_git=countif(type=='microsoft.datafactory/factories' and isnotnull(properties.repoConfiguration.repositoryName)),
    adls=countif(type=='microsoft.storage/storageaccounts' and tobool(properties.isHnsEnabled)==true),
    aisearch=countif(type=='microsoft.search/searchservices'),
    redis=countif(type in ('microsoft.cache/redis','microsoft.cache/redisenterprise')),
    cosmos=countif(type=='microsoft.documentdb/databaseaccounts'),
    docint=countif(type=='microsoft.cognitiveservices/accounts' and kind in ('FormRecognizer','DocumentIntelligence')),
    foundry=countif(type=='microsoft.cognitiveservices/accounts' and kind=~'AIServices'),
    foundry_id=countif(type=='microsoft.cognitiveservices/accounts' and kind=~'AIServices' and isnotnull(identity)),
    foundry_nokey=countif(type=='microsoft.cognitiveservices/accounts' and kind=~'AIServices' and tobool(properties.disableLocalAuth)==true),
    foundry_cmk=countif(type=='microsoft.cognitiveservices/accounts' and kind=~'AIServices' and isnotnull(properties.encryption.keyVaultProperties)),
    foundry_regions=dcountif(location, type=='microsoft.cognitiveservices/accounts' and kind=~'AIServices'),
    fproject=countif(type=~'microsoft.cognitiveservices/accounts/projects'),
    fproject_id=countif(type=~'microsoft.cognitiveservices/accounts/projects' and isnotnull(identity.principalId)),
    capability_host=countif(type=~'microsoft.cognitiveservices/accounts/capabilityhosts' or type=~'microsoft.cognitiveservices/accounts/projects/capabilityhosts'),
    fconnection=countif(type=~'microsoft.cognitiveservices/accounts/connections' or type=~'microsoft.cognitiveservices/accounts/projects/connections'),
    contentsafety=countif(type=='microsoft.cognitiveservices/accounts' and kind=~'ContentSafety'),
    custom_rai=countif(type=~'microsoft.cognitiveservices/accounts/raipolicies'),
    keyvault=countif(type=='microsoft.keyvault/vaults'),
    kv_hardened=countif(type=='microsoft.keyvault/vaults' and tobool(properties.enableRbacAuthorization)==true and tobool(properties.enableSoftDelete)==true and tobool(properties.enablePurgeProtection)==true),
    foundry_pe=countif(type=='microsoft.cognitiveservices/accounts' and kind=~'AIServices' and array_length(properties.privateEndpointConnections) > 0),
    apim=countif(type=='microsoft.apimanagement/service'),
    apim_mi=countif(type=='microsoft.apimanagement/service' and isnotnull(identity)),
    appinsights=countif(type=='microsoft.insights/components'),
    vnet=countif(type=='microsoft.network/virtualnetworks'),
    nsg=countif(type=='microsoft.network/networksecuritygroups'),
    firewall=countif(type=='microsoft.network/azurefirewalls'),
    appgw_waf=countif(type=='microsoft.network/applicationgateways' and isnotnull(properties.webApplicationFirewallConfiguration)),
    bastion=countif(type=='microsoft.network/bastionhosts'),
    pdz_aiservices=countif(type=='microsoft.network/privatednszones' and (name has 'cognitiveservices' or name has 'openai' or name has 'azure-api'))
"""

# Score formula building. Each pillar has component scores summed and a max.
# Pillar definitions (label|sortOrder|max|expression)
PILLAR_DEFS = [
    ("Foundry Inventory", 1, 8,
     "iff(foundry>0,2,0) + iff(foundry_id>0,1,0) + iff(fproject>0,2,0) + iff(fproject_id>0,1,0) + iff(fconnection>0,1,0) + iff(capability_host>0,1,0)"),
    ("Data Management & Governance", 2, 7,
     "iff(purview>0,3,0) + iff(databricks>0,2,0) + iff(adf_git>0,2,iff(adf>0,1,0))"),
    ("Retrieval & Context Enablement", 3, 5,
     "iff(aisearch>0,2,0) + iff(redis>0,1,0) + iff(cosmos>0,1,0) + iff(docint>0,1,0)"),
    ("Responsible AI", 4, 5,
     "iff(foundry>0,2,0) + iff(custom_rai>0,3,0)"),
    ("Identity & Access", 5, 5,
     "iff(foundry_id>0,2,0) + iff(apim_mi>0,1,iff(apim>0,0,0)) + iff(foundry_nokey>0,2,0)"),
    ("Network & Security", 6, 12,
     "iff(kv_hardened>0,3,iff(keyvault>0,1,0)) + iff(foundry_pe>0,2,0) + iff(apim>0,2,0) + iff(pdz_aiservices>0,1,0) + iff(firewall>0,1,0) + iff(appgw_waf>0,1,0) + iff(bastion>0,1,0) + iff(foundry_cmk>0,1,0)"),
    ("Policy & Compliance", 7, 3,
     "iff(foundry_pe>0,1,0) + iff(kv_hardened>0,1,0) + iff(foundry_cmk>0,1,0)"),
    ("Cost & Operations", 8, 5,
     "iff(foundry_regions>=2,2,iff(foundry>0,1,0)) + iff(appinsights>0,2,0) + iff(apim>0,1,0)"),
    ("Monitoring & Operations", 9, 5,
     "iff(appinsights>0,3,0) + iff(foundry_id>0,2,0)"),
]
TOTAL_MAX = sum(p[2] for p in PILLAR_DEFS)  # = 55


def build_pillar_pack_array() -> str:
    parts = []
    for label, order, mx, expr in PILLAR_DEFS:
        parts.append(f"strcat('{label}|{order}|{mx}|', tostring({expr}))")
    return ",\n        ".join(parts)


def build_total_expression() -> str:
    return " + ".join(f"({expr})" for _, _, _, expr in PILLAR_DEFS)


PILLAR_BARS_QUERY = SIGNAL_AGG + f"""| extend Pillars = pack_array(
        {build_pillar_pack_array()})
| mv-expand Pillars to typeof(string)
| extend parts = split(Pillars, '|')
| extend Pillar=tostring(parts[0]), SortOrder=toint(parts[1]), MaxScore=toint(parts[2]), WeightedScore=toint(parts[3])
| extend ScorePercent=toint(round(100.0*WeightedScore/MaxScore, 0))
| order by SortOrder asc
| extend BarColor=iff(ScorePercent>=75, '#00b294', iff(ScorePercent>=40, '#ff8c00', '#e81123'))
| extend row=strcat('<div style="display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid #f3f2f1"><div style="min-width:240px;font-size:13px;color:#0078d4;font-weight:600">', Pillar, '</div><div style="flex:1;height:12px;background:#edebe9;border-radius:2px;overflow:hidden;min-width:120px"><div style="height:100%;width:', tostring(ScorePercent), '%;background:', BarColor, ';border-radius:2px"></div></div><span style="min-width:44px;text-align:right;font-size:13px;font-weight:600;color:#323130">', tostring(ScorePercent), '%</span></div>')
| summarize allrows=strcat_array(make_list(row), '')
| project allrows"""


SCORE_CARD_QUERY = SIGNAL_AGG + f"""| extend TotalWeighted = {build_total_expression()}
| extend MaxTotal = {TOTAL_MAX}
| extend S = toint(round(100.0 * TotalWeighted / MaxTotal, 0))
| extend ScoreColor=iff(S>=80, '#107c10', iff(S>=50, '#d69900', '#d13438'))
| extend RingPct = S * 2.51327
| extend html=strcat('<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:12px 8px"><div style="font-size:13px;font-weight:600;color:#605e5c;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px">AI Readiness Score</div><div style="position:relative;width:160px;height:160px"><svg viewBox="0 0 100 100" style="transform:rotate(-90deg)"><circle cx="50" cy="50" r="40" fill="none" stroke="#edebe9" stroke-width="8"/><circle cx="50" cy="50" r="40" fill="none" stroke="', ScoreColor, '" stroke-width="8" stroke-dasharray="', tostring(RingPct), ' 251.327" stroke-linecap="round"/></svg><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center"><div style="font-size:38px;font-weight:700;color:', ScoreColor, ';line-height:1">', tostring(S), '%</div></div></div></div>')
| project html"""


# ---------------------------------------------------------------------------
# Build pillar groups
# ---------------------------------------------------------------------------

def foundry_inventory_group() -> dict:
    items: list = [html_block(
        "<div style='margin:8px 0;font-size:12px;color:#605e5c'>Inventory of Microsoft Foundry resources, projects, model deployments, connections, and agent service capability hosts. Foundry is identified as <code>microsoft.cognitiveservices/accounts</code> with <code>kind = AIServices</code>.</div>",
        "fdy-description")]

    items += [
        query_header("FDY-001", "Foundry Accounts",
                     "Microsoft Foundry account inventory with identity, network, encryption, and auth configuration."),
        arg_query("FDY-001", "Foundry Accounts",
                  """resources
| where type == 'microsoft.cognitiveservices/accounts' and kind =~ 'AIServices'
| extend hasIdentity = isnotnull(identity),
         disableLocalAuth = tobool(properties.disableLocalAuth),
         publicAccess = tostring(properties.publicNetworkAccess),
         cmkEnabled = isnotnull(properties.encryption.keyVaultProperties),
         networkInjection = tostring(properties.networkInjections),
         peCount = array_length(properties.privateEndpointConnections)
| project name, location, hasIdentity, disableLocalAuth, publicAccess, cmkEnabled, peCount, networkInjection, subscriptionId""",
                  formatters=[
                      threshold_icon_formatter("hasIdentity", "true"),
                      threshold_icon_formatter("disableLocalAuth", "true",
                                               success_text="Disabled", default_text="Enabled"),
                      threshold_icon_formatter("cmkEnabled", "true",
                                               success_text="Yes (CMK)", default_text="MMK"),
                  ]),

        query_header("FDY-002", "Foundry Projects",
                     "Projects organize models, data, agents, and evaluations within a Foundry account."),
        arg_query("FDY-002", "Foundry Projects",
                  """resources
| where type =~ 'microsoft.cognitiveservices/accounts/projects'
| extend hasIdentity = isnotnull(identity.principalId),
         endpoint = tostring(properties.endpoints)
| project name, location, hasIdentity, endpoint, subscriptionId""",
                  formatters=[threshold_icon_formatter("hasIdentity", "true")]),

        query_header("FDY-003", "Foundry Connections",
                     "Connections wire Foundry projects to AI Search, Storage, Cosmos, OpenAI, Bing, and other resources."),
        arg_query("FDY-003", "Foundry Connections",
                  """resources
| where type =~ 'microsoft.cognitiveservices/accounts/connections'
    or type =~ 'microsoft.cognitiveservices/accounts/projects/connections'
| extend category = tostring(properties.category),
         target = tostring(properties.target),
         authType = tostring(properties.authType)
| project name, category, target, authType, subscriptionId
| order by category asc, name asc""",
                  no_data="No Foundry connections found. Connections are required for RAG, agent tools, and external data integration."),

        query_header("FDY-004", "Capability Hosts (Agent Service)",
                     "Capability hosts indicate Foundry Agent Service is configured (storage + thread + vector store wiring)."),
        arg_query("FDY-004", "Capability Hosts",
                  """resources
| where type =~ 'microsoft.cognitiveservices/accounts/capabilityhosts'
    or type =~ 'microsoft.cognitiveservices/accounts/projects/capabilityhosts'
| extend storageConn = tostring(properties.storageConnections),
         vectorStoreConn = tostring(properties.vectorStoreConnections),
         threadConn = tostring(properties.threadStorageConnections),
         capabilityKind = tostring(properties.capabilityHostKind),
         provisioningState = tostring(properties.provisioningState)
| project name, capabilityKind, provisioningState, storageConn, vectorStoreConn, threadConn, subscriptionId""",
                  no_data="No capability hosts found. Foundry Agent Service has not been configured for any project."),

        manual_callout("FDY-005", "Model Deployments, Agents, Evaluations, Threads",
                       "Foundry deployments and data-plane resources are not reliably exposed to Azure Resource Graph.",
                       "Use the Azure Cognitive Services management API to list model deployments, and the Foundry data-plane REST API for agents, evaluations, and threads. <br/>"
                       "<code>GET https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{account}/deployments?api-version=2024-10-01</code><br/>"
                       "<code>GET https://{account}.services.ai.azure.com/api/projects/{project}/agents?api-version=2025-05-01</code><br/>"
                       "<code>GET https://{account}.services.ai.azure.com/api/projects/{project}/evaluations?api-version=2025-05-01</code><br/>"
                       "<code>GET https://{account}.services.ai.azure.com/api/projects/{project}/threads?api-version=2025-05-01</code>"),
    ]

    return group_section("Foundry Inventory", items, expanded=True, name="foundry-inventory-group")


def landscape_group() -> dict:
    landscape_query = """resources
| where type in~ (
    'microsoft.cognitiveservices/accounts',
    'microsoft.cognitiveservices/accounts/projects',
    'microsoft.search/searchservices',
    'microsoft.cache/redis',
    'microsoft.cache/redisenterprise',
    'microsoft.documentdb/databaseaccounts',
    'microsoft.purview/accounts',
    'microsoft.databricks/workspaces',
    'microsoft.datafactory/factories',
    'microsoft.apimanagement/service',
    'microsoft.insights/components'
  )
| where type !~ 'microsoft.cognitiveservices/accounts'
    or kind in~ ('AIServices','ContentSafety','FormRecognizer','DocumentIntelligence')
| summarize resourceCount = count() by location
| order by resourceCount desc"""

    items = [
        html_block(
            "<div style='margin:8px 0;font-size:12px;color:#605e5c'>Geographic distribution of Foundry-relevant resources across selected subscriptions. Informational; does not affect the score.</div>",
            "landscape-description"),
        {
            "type": 3,
            "content": {
                "version": "KqlItem/1.0",
                "query": landscape_query,
                "size": 3,
                "title": "AI Resources by Region",
                "queryType": 1,
                "resourceType": "microsoft.resourcegraph/resources",
                "crossComponentResources": SUBSCRIPTION_RESOURCES,
                "visualization": "map",
                "mapSettings": {
                    "locInfo": "AzureLoc",
                    "locInfoColumn": "location",
                    "sizeSettings": "resourceCount",
                    "sizeAggregation": "Sum",
                    "legendMetric": "resourceCount",
                    "legendAggregation": "Sum",
                    "itemColorSettings": {
                        "nodeColorField": "resourceCount",
                        "colorAggregation": "Sum",
                        "type": "heatmap",
                        "heatmapPalette": "greenRed",
                    },
                },
                "noDataMessage": "No AI resources found in the selected subscription(s).",
                "noDataMessageStyle": 4,
            },
            "name": "landscape-map",
        },
    ]
    return group_section("AI Resource Landscape", items, expanded=False, name="landscape-group")


def dmg_group() -> dict:
    items = [
        query_header("DMG-001", "Purview Accounts",
                     "Microsoft Purview &#x2014; Unified data governance platform."),
        arg_query("DMG-001", "Purview Accounts",
                  """resources
| where type == 'microsoft.purview/accounts'
| project name, location, subscriptionId, properties"""),

        query_header("DMG-002", "Purview Scan Rulesets",
                     "Validate scan rulesets are configured for data discovery."),
        arg_query("DMG-002", "Purview Scan Rulesets",
                  """resources
| where type == 'microsoft.purview/accounts'
| where isnotnull(properties.scanRulesets)
| project name, location, subscriptionId, scanRulesets=properties.scanRulesets"""),

        query_header("DMG-003", "Data Classification Rules",
                     "Cloud connector configurations enabling data classification."),
        arg_query("DMG-003", "Data Classification Rules",
                  """resources
| where type == 'microsoft.purview/accounts'
| where isnotnull(properties.cloudConnectors)
| project name, location, subscriptionId, properties"""),

        query_header("DMG-004", "Data Lineage Enablement",
                     "Lineage endpoints for tracking data flow."),
        arg_query("DMG-004", "Data Lineage Enablement",
                  """resources
| where type == 'microsoft.purview/accounts'
| extend lineageEndpoint = tostring(properties.endpoints.lineage)
| where isnotnull(lineageEndpoint)
| project name, lineageEndpoint, location, subscriptionId"""),

        query_header("DMG-005", "Unity Catalog (Databricks)",
                     "Azure Databricks workspaces for unified analytics governance."),
        arg_query("DMG-005", "Databricks Workspaces",
                  """resources
| where type == 'microsoft.databricks/workspaces'
| extend unityCatalog = properties.parameters.enableNoPublicIp
| project name, location, subscriptionId, properties"""),

        query_header("DMG-006", "Data Factory ETL",
                     "ADF instances with Git integration."),
        arg_query("DMG-006", "Data Factories",
                  """resources
| where type == 'microsoft.datafactory/factories'
| extend gitConfigured = isnotnull(properties.repoConfiguration.repositoryName),
         globalParams = array_length(bag_keys(properties.globalParameters))
| project name, location, subscriptionId, gitConfigured, globalParams""",
                  formatters=[threshold_icon_formatter("gitConfigured", "true")]),

        query_header("DMG-007", "Lakehouse Presence",
                     "ADLS Gen2, Databricks, or Microsoft Fabric for enterprise data lake."),
        arg_query("DMG-007", "Lakehouse Presence",
                  """resources
| where type in (
    'microsoft.storage/storageaccounts',
    'microsoft.databricks/workspaces',
    'microsoft.fabric/capacities'
  )
| extend layer = case(
    type == 'microsoft.storage/storageaccounts' and properties.isHnsEnabled == true, 'ADLS Gen2',
    type == 'microsoft.databricks/workspaces', 'Databricks',
    type == 'microsoft.fabric/capacities', 'Microsoft Fabric',
    'Other'
  )
| where layer != 'Other'
| project name, layer, location, subscriptionId"""),

        query_header("DMG-008", "ADLS Lifecycle Policies",
                     "Retention and lifecycle management on ADLS Gen2."),
        arg_query("DMG-008", "ADLS Gen2 Lifecycle Policies",
                  """resources
| where type == 'microsoft.storage/storageaccounts'
| where kind == 'StorageV2' and properties.isHnsEnabled == true
| extend lifecyclePolicy = isnotnull(properties.managementPolicies)
| project name, location, subscriptionId, lifecyclePolicy"""),
    ]
    return group_section("Data Management & Governance", items, name="dmg-group")


def rce_group() -> dict:
    items = [
        query_header("RCE-001", "AI Search",
                     "Azure AI Search &#x2014; Semantic and vector search capabilities."),
        arg_query("RCE-001", "AI Search Services",
                  """resources
| where type == 'microsoft.search/searchservices'
| extend sku = tostring(sku.name),
         semanticSearch = tostring(properties.semanticSearch),
         replicaCount = toint(properties.replicaCount),
         partitionCount = toint(properties.partitionCount),
         publicAccess = properties.publicNetworkAccess,
         status = tostring(properties.status)
| project name, sku, semanticSearch, replicaCount, partitionCount, publicAccess, status, subscriptionId""",
                  formatters=[
                      threshold_icon_formatter("status", "running",
                                               default_repr="error", success_text="Running", default_text="{0}"),
                  ]),

        query_header("RCE-002", "Redis Cache",
                     "Azure Cache for Redis &#x2014; Semantic / response caching."),
        arg_query("RCE-002", "Redis Cache",
                  """resources
| where type == 'microsoft.cache/redis' or type == 'microsoft.cache/redisenterprise'
| extend sku = tostring(sku.name), capacity = toint(sku.capacity)
| project name, sku, capacity, location, subscriptionId"""),

        query_header("RCE-003", "Cosmos DB / PostgreSQL",
                     "Databases used for retrieval-augmented generation patterns."),
        arg_query("RCE-003", "Cosmos DB / PostgreSQL",
                  """resources
| where type == 'microsoft.documentdb/databaseaccounts'
    or (type == 'microsoft.dbforpostgresql/flexibleservers')
| extend dbKind = case(
    type == 'microsoft.documentdb/databaseaccounts', 'Cosmos DB',
    type == 'microsoft.dbforpostgresql/flexibleservers', 'PostgreSQL Flexible',
    'Other')
| extend cosmosVectorEnabled = properties.capabilities has 'EnableNoSQLVectorSearch'
| extend vectorStatus = case(
    type == 'microsoft.documentdb/databaseaccounts' and cosmosVectorEnabled, 'NoSQL vector search enabled',
    type == 'microsoft.documentdb/databaseaccounts', 'NoSQL vector search not enabled',
    type == 'microsoft.dbforpostgresql/flexibleservers', 'Verify pgvector extension in database',
    'Unknown')
| project name, dbKind, vectorStatus, location, subscriptionId"""),

        query_header("RCE-004", "Vector Stores",
                     "Vector store inventory: AI Search, Cosmos DB with vector search enabled, and PostgreSQL candidates for pgvector."),
        arg_query("RCE-004", "Vector Stores",
                  """resources
| where type == 'microsoft.search/searchservices'
    or (type == 'microsoft.documentdb/databaseaccounts' and properties.capabilities has 'EnableNoSQLVectorSearch')
    or (type == 'microsoft.dbforpostgresql/flexibleservers')
| extend storeType = case(
    type == 'microsoft.search/searchservices', 'AI Search',
    type == 'microsoft.documentdb/databaseaccounts', 'Cosmos DB (vector)',
    type == 'microsoft.dbforpostgresql/flexibleservers', 'PostgreSQL (pgvector)',
    'Other')
| extend vectorStatus = case(
    type == 'microsoft.search/searchservices', 'Native vector search',
    type == 'microsoft.documentdb/databaseaccounts', 'NoSQL vector search enabled',
    type == 'microsoft.dbforpostgresql/flexibleservers', 'Verify pgvector extension in database',
    'Unknown')
| project name, storeType, vectorStatus, location, subscriptionId"""),

        query_header("RCE-005", "Document Intelligence",
                     "Azure AI Document Intelligence &#x2014; OCR / document processing."),
        arg_query("RCE-005", "Document Intelligence",
                  """resources
| where type == 'microsoft.cognitiveservices/accounts'
| where kind == 'FormRecognizer' or kind == 'DocumentIntelligence'
| extend sku = tostring(sku.name), publicAccess = properties.publicNetworkAccess
| project name, kind, sku, publicAccess, location, subscriptionId"""),
    ]
    return group_section("Retrieval & Context Enablement", items, name="rce-group")


def rai_group() -> dict:
    items = [
        html_block(
            "<div style='margin:8px 0;font-size:12px;color:#605e5c'>"
            "Microsoft Foundry guardrails are <strong>RAI policies</strong> that wrap every model deployment and agent. Every Foundry deployment automatically inherits the built-in <code>Microsoft.Default</code> policy "
            "(Hate, Sexual, Self-Harm, Violence at medium severity, plus Jailbreak and Indirect-Attack shields). Custom policies layer additional controls "
            "(Protected Material, Groundedness, Custom Categories, etc.) and tighter severity thresholds. This pillar checks that those Foundry-native guardrails are present and customised; the standalone Content Safety service is shown for reference only."
            "</div>",
            "rai-description"),

        query_header("RAI-001", "Foundry Guardrail Policies",
                     "Custom RAI (guardrail) policies defined on Foundry accounts &#x2014; layered on top of Microsoft.Default."),
        arg_query("RAI-001", "Foundry Guardrail Policies",
                  """resources
| where type =~ 'microsoft.cognitiveservices/accounts/raipolicies'
| extend parentAccount = tostring(split(id, '/')[8]),
         mode = tostring(properties.mode),
         basePolicyName = tostring(properties.basePolicyName),
         policyType = tostring(properties.type)
| project parentAccount, policyName=name, mode, basePolicyName, policyType, subscriptionId
| order by parentAccount asc, policyName asc""",
                  no_data="No custom guardrail policies found. All Foundry deployments are using the built-in Microsoft.Default policy only. Consider adding custom policies to enforce Protected Material, Groundedness, or Custom Categories."),

        query_header("RAI-002", "Foundry Content Filter Capability",
                     "Foundry accounts with the RaiMonitor capability available (required for guardrail enforcement at runtime)."),
        arg_query("RAI-002", "Foundry Content Filter Capability",
                  """resources
| where type =~ 'microsoft.cognitiveservices/accounts' and kind =~ 'AIServices'
| extend caps = properties.capabilities
| mv-expand cap = caps
| where tostring(cap.name) == 'RaiMonitor'
| project name, kind, resourceGroup, subscriptionId, raiMonitor = 'Available'""",
                  no_data="No Foundry accounts expose the RaiMonitor capability. Default Microsoft.Default guardrails still apply at the model API level."),

        query_header("RAI-003", "Foundry Guardrail Feature Coverage",
                     "Built-in safety features available on each Foundry account (jailbreak, prompt shield, groundedness, agent safety, etc.)."),
        arg_query("RAI-003", "Foundry Guardrail Features",
                  """resources
| where type =~ 'microsoft.cognitiveservices/accounts'
| where kind =~ 'AIServices'
| extend rules = properties.callRateLimit.rules
| mv-expand rule = rules
| extend ruleKey = tostring(rule.key)
| where ruleKey in (
    'ContentSafety.TextJailbreak',
    'ContentSafety.TextShieldPrompt',
    'ContentSafety.TextProtectedMaterial',
    'ContentSafety.TextGroundedDetection',
    'ContentSafety.Text',
    'ContentSafety.Image',
    'ContentSafety.RaiPoliciesAPI',
    'ContentSafety.Provenance.Detect',
    'ContentSafety.AgentTaskAdherence',
    'ContentSafety.TextCustomCategories'
  )
| extend feature = case(
    ruleKey == 'ContentSafety.TextJailbreak', 'Jailbreak Detection',
    ruleKey == 'ContentSafety.TextShieldPrompt', 'Prompt Shield',
    ruleKey == 'ContentSafety.TextProtectedMaterial', 'Protected Material',
    ruleKey == 'ContentSafety.TextGroundedDetection', 'Groundedness Detection',
    ruleKey == 'ContentSafety.Text', 'Text Moderation',
    ruleKey == 'ContentSafety.Image', 'Image Moderation',
    ruleKey == 'ContentSafety.RaiPoliciesAPI', 'RAI Policies',
    ruleKey == 'ContentSafety.Provenance.Detect', 'Content Provenance',
    ruleKey == 'ContentSafety.AgentTaskAdherence', 'Agent Safety',
    ruleKey == 'ContentSafety.TextCustomCategories', 'Custom Categories',
    '')
| project foundryAccount=name, feature, subscriptionId
| order by foundryAccount asc, feature asc""",
                  no_data="No Foundry guardrail features detected."),

        manual_callout("RAI-004", "Per-Deployment Guardrail Assignment",
                       "Verify which guardrail policy is bound to each model deployment and agent.",
                       "Model deployments are not reliably indexed in Azure Resource Graph. Use the management API per Foundry account:<br/>"
                       "<code>GET https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{account}/deployments?api-version=2024-10-01</code><br/>"
                       "Inspect <code>properties.raiPolicyName</code> on each deployment. <code>Microsoft.Default</code> = built-in; anything else = custom guardrail. "
                       "Agents inherit the policy from the underlying model deployment unless overridden in the agent definition."),

        manual_callout("RAI-005", "Guardrail Policy Controls Detail",
                       "Inspect the actual risks, severity thresholds, and intervention points configured on each custom policy.",
                       "<code>GET https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{account}/raiPolicies/{policy}?api-version=2024-10-01</code><br/>"
                       "Review <code>properties.contentFilters</code> for filter category (Hate, Sexual, Violence, Self-Harm, Jailbreak, Protected Material, Groundedness, Custom Categories), <code>severityThreshold</code>, "
                       "and <code>source</code> (Prompt vs Completion)."),

        manual_callout("RAI-006", "Red Teaming Runs",
                       "Check for completed red teaming runs and Attack Success Rate (ASR) metrics.",
                       "Use Foundry portal or API to verify red teaming runs.<br/>"
                       "<code>GET https://{account}.services.ai.azure.com/api/projects/{project}/redteams/runs?api-version=2025-05-01</code>"),

        query_header("RAI-007", "Standalone Content Safety Services",
                     "Dedicated Content Safety service instances &#x2014; informational only; Foundry guardrails are the primary control plane."),
        arg_query("RAI-007", "Standalone Content Safety",
                  """resources
| where type =~ 'microsoft.cognitiveservices/accounts'
| where kind =~ 'ContentSafety'
| extend sku = tostring(sku.name), publicAccess = tostring(properties.publicNetworkAccess)
| project name, sku, publicAccess, location, resourceGroup, subscriptionId""",
                  no_data="No standalone Content Safety services found. This is expected when Foundry guardrails are used; the Foundry-embedded Content Safety capability covers the same features."),
    ]
    return group_section("Responsible AI", items, name="rai-group")


def iam_group() -> dict:
    items = [
        html_block(
            "<div style='margin:8px 0;font-size:12px;color:#605e5c'>Identity and access posture for Foundry resources. Includes RBAC analysis, key-based auth detection, and manual callouts for Conditional Access, MFA, PIM, and Entra Agent ID inventory.</div>",
            "iam-description"),

        query_header("IAM-001", "Foundry Account Authentication",
                     "Disable local auth (key-based) on Foundry accounts &#x2014; Entra ID only is recommended."),
        arg_query("IAM-001", "Foundry Account Auth",
                  """resources
| where type == 'microsoft.cognitiveservices/accounts' and kind =~ 'AIServices'
| extend disableLocalAuth = tobool(properties.disableLocalAuth),
         publicAccess = tostring(properties.publicNetworkAccess)
| project name, disableLocalAuth, publicAccess, location, subscriptionId""",
                  formatters=[threshold_icon_formatter("disableLocalAuth", "true",
                                                       success_text="Entra-only", default_text="Keys allowed")]),

        query_header("IAM-002", "Managed Identity Coverage",
                     "Foundry accounts, projects, AI Search, and APIM with managed identity."),
        arg_query("IAM-002", "Managed Identity Coverage",
                  """resources
| where (type == 'microsoft.cognitiveservices/accounts' and kind =~ 'AIServices')
    or type =~ 'microsoft.cognitiveservices/accounts/projects'
    or type == 'microsoft.search/searchservices'
    or type == 'microsoft.apimanagement/service'
| extend hasManagedIdentity = isnotnull(identity)
| extend resourceType = case(
    type == 'microsoft.cognitiveservices/accounts', 'Foundry Account',
    type =~ 'microsoft.cognitiveservices/accounts/projects', 'Foundry Project',
    type == 'microsoft.search/searchservices', 'AI Search',
    type == 'microsoft.apimanagement/service', 'APIM',
    'Other')
| summarize Total=count(), WithManagedIdentity=countif(hasManagedIdentity == true) by resourceType""",
                  formatters=[heat_formatter("WithManagedIdentity")]),

        query_header("IAM-003", "RBAC Role Assignments on Foundry",
                     "Counts of role assignments on Foundry accounts &#x2014; flag potential overprivileged access."),
        arg_query("IAM-003", "Foundry RBAC Assignments",
                  """authorizationresources
| where type =~ 'microsoft.authorization/roleassignments'
| extend scope = tolower(tostring(properties.scope))
| where scope contains '/providers/microsoft.cognitiveservices/accounts/'
| extend roleDefinitionId = tolower(tostring(properties.roleDefinitionId))
| extend roleType = case(
    roleDefinitionId endswith '8e3af657-a8ff-443c-a75c-2fe8c4bcb635', 'Owner',
    roleDefinitionId endswith 'b24988ac-6180-42a0-ab88-20f7382dd24c', 'Contributor',
    roleDefinitionId endswith 'acdd72a7-3385-48ef-bd42-f606fba81ae7', 'Reader',
    roleDefinitionId endswith '64702f94-c441-49e6-a78b-ef80e0188fee', 'Azure AI Developer',
    roleDefinitionId endswith 'a97b65f3-24c7-4388-baec-2e87135dc908', 'Cognitive Services User',
    roleDefinitionId endswith '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd', 'Cognitive Services OpenAI User',
    roleDefinitionId endswith 'a001fd3d-188f-4b5d-821b-7da978bf7442', 'Cognitive Services OpenAI Contributor',
    'Other')
| summarize Assignments=count() by roleType
| order by Assignments desc""",
                  no_data="No Foundry RBAC assignments visible (requires Reader on the management group/subscription)."),

        manual_callout("IAM-004", "Conditional Access Policies",
                       "Risk-based Conditional Access for Foundry portal and APIs.",
                       "Conditional Access state lives in Microsoft Entra ID and is not surfaced in Azure Resource Graph. "
                       "Review via Entra portal or Microsoft Graph:<br/>"
                       "<code>GET https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies</code>"),

        manual_callout("IAM-005", "Multi-Factor Authentication",
                       "MFA enforcement for users accessing Foundry.",
                       "Verify via Microsoft Graph sign-in logs and authentication strength policies:<br/>"
                       "<code>GET https://graph.microsoft.com/v1.0/policies/authenticationStrengthPolicies</code>"),

        manual_callout("IAM-006", "Privileged Identity Management",
                       "Just-in-time elevation for Foundry administrative roles.",
                       "Inspect PIM eligible / active assignments for Cognitive Services Contributor / Azure AI Developer:<br/>"
                       "<code>GET https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignmentScheduleInstances</code>"),

        manual_callout("IAM-007", "Microsoft Entra Agent ID Inventory",
                       "Centralized AI agent identity catalog.",
                       "List all AI agents created via Foundry / Copilot Studio:<br/>"
                       "<code>GET https://graph.microsoft.com/v1.0/servicePrincipals?$filter=tags/any(t:t eq 'WindowsAzureActiveDirectoryIntegratedApp') and tags/any(t:t eq 'AzureAIAgent')</code>"),
    ]
    return group_section("Identity & Access", items, name="iam-group")


def network_security_group() -> dict:
    items = [
        html_block(
            "<div style='margin:8px 0;font-size:12px;color:#605e5c'>Network architecture and security controls for Foundry workloads. Covers private endpoints, network injection, Key Vault hardening, Defender, APIM, and Azure landing zone network components (VNets, NSGs, Firewall, WAF, Bastion, Private DNS).</div>",
            "sec-description"),

        query_header("SEC-001", "Foundry Private Networking",
                     "Public access and private endpoint state on Foundry accounts and AI Search."),
        arg_query("SEC-001", "Foundry Private Networking",
                  """resources
| where (type == 'microsoft.cognitiveservices/accounts' and kind in~ ('AIServices','ContentSafety','FormRecognizer','DocumentIntelligence'))
    or type == 'microsoft.search/searchservices'
    or type == 'microsoft.storage/storageaccounts'
    or type == 'microsoft.cache/redis'
| extend publicAccess = tostring(properties.publicNetworkAccess),
         peCount = array_length(properties.privateEndpointConnections),
         peState = tostring(properties.privateEndpointConnections[0].properties.privateLinkServiceConnectionState.status)
| project name, type, kind, publicAccess, peCount, peState, location, subscriptionId""",
                  formatters=[
                      threshold_icon_formatter("publicAccess", "Disabled",
                                               success_text="Disabled", default_text="{0}"),
                      threshold_icon_formatter("peState", "Approved",
                                               default_repr="2", success_text="Approved", default_text="{0}"),
                  ]),

        query_header("SEC-002", "Foundry Network Injection",
                     "Foundry account network injection mode (Allow internet / Approved-only outbound)."),
        arg_query("SEC-002", "Network Injection Mode",
                  """resources
| where type == 'microsoft.cognitiveservices/accounts' and kind =~ 'AIServices'
| extend injectionScenarios = tostring(properties.networkInjections),
         restrictOutbound = tobool(properties.restrictOutboundNetworkAccess),
         allowedFqdns = array_length(properties.allowedFqdnList)
| project name, injectionScenarios, restrictOutbound, allowedFqdns, location, subscriptionId""",
                  no_data="No Foundry accounts found."),

        query_header("SEC-003", "Customer-Managed Keys (CMK)",
                     "Foundry accounts encrypted with a customer-managed Key Vault key."),
        arg_query("SEC-003", "CMK Encryption",
                  """resources
| where type == 'microsoft.cognitiveservices/accounts' and kind =~ 'AIServices'
| extend cmk = isnotnull(properties.encryption.keyVaultProperties),
         keyVaultUri = tostring(properties.encryption.keyVaultProperties.keyVaultUri),
         keyName = tostring(properties.encryption.keyVaultProperties.keyName)
| project name, cmk, keyVaultUri, keyName, subscriptionId""",
                  formatters=[threshold_icon_formatter("cmk", "true",
                                                       success_text="CMK", default_text="MMK")]),

        query_header("SEC-004", "Key Vault Hardening",
                     "Centralized secret management with RBAC, soft delete, purge protection."),
        arg_query("SEC-004", "Key Vault Security",
                  """resources
| where type == 'microsoft.keyvault/vaults'
| extend softDelete = properties.enableSoftDelete,
         purgeProtection = properties.enablePurgeProtection,
         rbac = properties.enableRbacAuthorization
| project name, location, subscriptionId, softDelete, purgeProtection, rbac""",
                  formatters=[
                      threshold_icon_formatter("softDelete", "true", default_repr="error"),
                      threshold_icon_formatter("purgeProtection", "true", default_repr="error"),
                      threshold_icon_formatter("rbac", "true", default_repr="error"),
                  ]),

        query_header("SEC-005", "Virtual Networks & Peering",
                     "VNets, subnets, and peering &#x2014; Foundry network landing zone footprint."),
        arg_query("SEC-005", "VNet Inventory",
                  """resources
| where type == 'microsoft.network/virtualnetworks'
| extend addressSpace = tostring(properties.addressSpace.addressPrefixes),
         subnetCount = array_length(properties.subnets),
         peeringCount = array_length(properties.virtualNetworkPeerings)
| project name, addressSpace, subnetCount, peeringCount, location, subscriptionId"""),

        query_header("SEC-006", "Network Security Groups",
                     "NSGs enforcing inbound/outbound traffic policies."),
        arg_query("SEC-006", "NSG Inventory",
                  """resources
| where type == 'microsoft.network/networksecuritygroups'
| extend customRules = array_length(properties.securityRules),
         attachedSubnets = array_length(properties.subnets),
         attachedNICs = array_length(properties.networkInterfaces)
| project name, customRules, attachedSubnets, attachedNICs, location, subscriptionId"""),

        query_header("SEC-007", "Azure Firewall",
                     "Centralized outbound traffic control and data exfiltration protection."),
        arg_query("SEC-007", "Azure Firewall",
                  """resources
| where type == 'microsoft.network/azurefirewalls'
| extend tier = tostring(properties.sku.tier),
         policy = tostring(properties.firewallPolicy.id)
| project name, tier, policy, location, subscriptionId""",
                  no_data="No Azure Firewall instances found. Required for approved-outbound mode and FQDN egress filtering."),

        query_header("SEC-008", "Web Application Firewall",
                     "WAF on Application Gateway / Front Door for internet-facing AI workloads."),
        arg_query("SEC-008", "WAF Status",
                  """resources
| where type == 'microsoft.network/applicationgateways'
    or type == 'microsoft.network/frontdoorwebapplicationfirewallpolicies'
| extend wafEnabled = case(
    type == 'microsoft.network/applicationgateways' and isnotnull(properties.webApplicationFirewallConfiguration), true,
    type == 'microsoft.network/frontdoorwebapplicationfirewallpolicies', true,
    false),
   sku = tostring(coalesce(properties.sku.name, sku.name))
| project name, type, sku, wafEnabled, location, subscriptionId""",
                  formatters=[threshold_icon_formatter("wafEnabled", "true",
                                                       success_text="WAF on", default_text="No WAF")]),

        query_header("SEC-009", "Private DNS Zones for AI Services",
                     "Required for private endpoint name resolution to Foundry / AI Search / OpenAI."),
        arg_query("SEC-009", "Private DNS Zones (AI)",
                  """resources
| where type == 'microsoft.network/privatednszones'
| where name has 'cognitiveservices' or name has 'openai' or name has 'azure-api'
    or name has 'search.windows' or name has 'documents.azure' or name has 'blob.core'
    or name has 'vault.azure' or name has 'redis.cache'
| extend recordCount = toint(properties.numberOfRecordSets),
         vnetLinks = toint(properties.numberOfVirtualNetworkLinks)
| project name, recordCount, vnetLinks, subscriptionId
| order by name asc""",
                  no_data="No private DNS zones for AI service private endpoints found."),

        query_header("SEC-010", "Azure Bastion",
                     "Secure RDP/SSH access to jumpboxes inside Foundry VNet without public IPs."),
        arg_query("SEC-010", "Bastion Hosts",
                  """resources
| where type == 'microsoft.network/bastionhosts'
| extend sku = tostring(sku.name)
| project name, sku, location, subscriptionId"""),

        query_header("SEC-011", "API Management as AI Gateway",
                     "APIM for centralized AI API access control, throttling, and auth."),
        arg_query("SEC-011", "API Management",
                  """resources
| where type == 'microsoft.apimanagement/service'
| extend sku = tostring(sku.name),
         identityType = tostring(identity.type)
| project name, sku, identityType, location, subscriptionId"""),

        query_header("SEC-012", "Azure Container Registry",
                     "ACR for Foundry custom container images and managed online endpoint deployments."),
        arg_query("SEC-012", "Azure Container Registry",
                  """resources
| where type == 'microsoft.containerregistry/registries'
| extend sku = tostring(sku.name),
         publicAccess = tostring(properties.publicNetworkAccess),
         peCount = array_length(properties.privateEndpointConnections)
| project name, sku, publicAccess, peCount, location, subscriptionId"""),

        query_header("SEC-013", "Defender for Cloud Plans",
                     "Security posture and threat protection plans."),
        arg_query("SEC-013", "Defender Plans",
                  """securityresources
| where type == 'microsoft.security/pricings'
| where name in ('CloudPosture', 'Containers', 'VirtualMachines', 'StorageAccounts', 'Api', 'KeyVaults')
| project name, tier=tostring(properties.pricingTier)""",
                  formatters=[threshold_icon_formatter("tier", "Standard",
                                                       success_text="Standard", default_text="Free")]),

        query_header("SEC-014", "Defender for AI Services",
                     "Threat protection specifically for AI workloads (prompt injection, model abuse)."),
        arg_query("SEC-014", "Defender for AI",
                  """securityresources
| where type == 'microsoft.security/pricings'
| where name == 'AI'
| project name, tier=tostring(properties.pricingTier)""",
                  formatters=[threshold_icon_formatter("tier", "Standard",
                                                       success_text="Standard", default_text="Free")]),

        query_header("SEC-015", "Microsoft Sentinel",
                     "SIEM/SOAR coverage on Log Analytics workspaces."),
        arg_query("SEC-015", "Sentinel Workspaces",
                  """resources
| where type =~ 'microsoft.operationsmanagement/solutions'
| where name startswith 'SecurityInsights'
| extend workspaceId = tostring(properties.workspaceResourceId)
| project name, workspaceId, location, subscriptionId""",
                  no_data="No Microsoft Sentinel deployments found on any Log Analytics workspace."),
    ]
    return group_section("Network & Security", items, name="net-sec-group")


def policy_compliance_group() -> dict:
    items = [
        html_block(
            "<div style='margin:8px 0;font-size:12px;color:#605e5c'>Azure Policy enforcement and Defender posture findings against Foundry resources.</div>",
            "pol-description"),

        query_header("POL-001", "Policy Assignments Targeting AI",
                     "Azure Policy assignments referencing Cognitive Services / Foundry / AI Search scopes."),
        arg_query("POL-001", "AI Policy Assignments",
                  """policyresources
| where type == 'microsoft.authorization/policyassignments'
| extend displayName = tostring(properties.displayName),
         scope = tolower(tostring(properties.scope)),
         policyDefId = tolower(tostring(properties.policyDefinitionId))
| where displayName contains 'OpenAI' or displayName contains 'AI Services' or displayName contains 'Cognitive'
    or displayName contains 'AI Search' or displayName contains 'Foundry'
    or policyDefId contains 'cognitive' or policyDefId contains 'openai'
    or policyDefId contains 'enforce-guardrails'
| project displayName, scope, subscriptionId""",
                  no_data="No AI-specific Azure Policy assignments detected. Apply Enforce-Guardrails initiatives for OpenAI / Cognitive Services."),

        query_header("POL-002", "Policy Compliance State",
                     "Non-compliant policy states across the subscription."),
        arg_query("POL-002", "Policy Compliance",
                  """policyresources
| where type == 'microsoft.policyinsights/policystates'
| summarize total=count(), nonCompliant=countif(properties.complianceState=='NonCompliant') by tostring(properties.policyAssignmentName)
| where nonCompliant > 0
| order by nonCompliant desc
| top 25 by nonCompliant""",
                  no_data="No non-compliant policy states found (or policyinsights data not yet available)."),

        query_header("POL-003", "Defender Recommendations on AI",
                     "Open Defender for Cloud recommendations targeting Foundry / Cognitive Services / Search."),
        arg_query("POL-003", "Defender AI Recommendations",
                  """securityresources
| where type =~ 'microsoft.security/assessments'
| extend status = tostring(properties.status.code),
         resourceId = tolower(tostring(properties.resourceDetails.id)),
         displayName = tostring(properties.displayName),
         severity = tostring(properties.metadata.severity)
| where resourceId contains 'cognitiveservices'
    or resourceId contains 'searchservices' or resourceId contains 'apimanagement'
| where status != 'Healthy'
| summarize Count=count() by displayName, severity
| order by Count desc""",
                  no_data="No open Defender recommendations on AI resources (or Defender plans are not enabled)."),

        manual_callout("POL-004", "Compliance Manager State",
                       "Microsoft Purview Compliance Manager assessment scores.",
                       "Compliance Manager scores live in Microsoft Purview / Microsoft 365 admin center, not in Azure Resource Graph. "
                       "Review at <code>https://compliance.microsoft.com/compliancemanager</code> and align AI workloads to relevant assessments "
                       "(ISO/IEC 23053, NIST AI RMF, EU AI Act, HIPAA, etc.)."),

        manual_callout("POL-005", "Regulatory Compliance Initiatives",
                       "ISO/IEC 23053:2022, NIST AI RMF, EU AI Act alignment.",
                       "Apply the regulatory compliance initiatives in Azure Policy for your industry. "
                       "Available at: <code>Microsoft.Authorization/policySetDefinitions</code> with category 'Regulatory Compliance'."),
    ]
    return group_section("Policy & Compliance", items, name="pol-group")


def cost_ops_group() -> dict:
    items = [
        html_block(
            "<div style='margin:8px 0;font-size:12px;color:#605e5c'>Operational resilience and cost-related signals: regional distribution, agent execution isolation, and manual callouts for quotas / PTUs / budgets.</div>",
            "ops-description"),

        query_header("OPS-001", "Foundry Multi-Region Presence",
                     "Foundry accounts deployed across multiple regions for BCDR."),
        arg_query("OPS-001", "Foundry Regions",
                  """resources
| where type == 'microsoft.cognitiveservices/accounts' and kind =~ 'AIServices'
| summarize accountCount = count() by location
| order by accountCount desc"""),

        query_header("OPS-002", "Container Apps Dynamic Sessions",
                     "Isolated, ephemeral execution environments for AI agent code execution."),
        arg_query("OPS-002", "Container Apps Session Pools",
                  """resources
| where type =~ 'microsoft.app/sessionpools'
| extend containerType = tostring(properties.containerType),
         poolMgmtType = tostring(properties.poolManagementType)
| project name, containerType, poolMgmtType, location, subscriptionId""",
                  no_data="No Container Apps session pools found. Use Dynamic Sessions for sandboxed agent code execution."),

        manual_callout("OPS-003", "Foundry Quotas & PTU Usage",
                       "Provisioned Throughput Units and rate limits.",
                       "Quota and PTU usage are exposed via the Cognitive Services usage REST API:<br/>"
                       "<code>GET https://management.azure.com/subscriptions/{sub}/providers/Microsoft.CognitiveServices/locations/{region}/usages?api-version=2024-10-01</code>"),

        manual_callout("OPS-004", "Cost Tracking & Budgets",
                       "Subscription / resource group budgets and AI cost allocation.",
                       "Cost data is exposed via the Cost Management API:<br/>"
                       "<code>GET https://management.azure.com/subscriptions/{sub}/providers/Microsoft.Consumption/budgets?api-version=2023-05-01</code><br/>"
                       "Generative AI Gateway capabilities in APIM can track per-client token spend."),
    ]
    return group_section("Cost & Operations", items, name="ops-group")


def monitoring_group() -> dict:
    items = [
        query_header("MON-001", "Application Insights",
                     "APM / tracing for Foundry-backed applications and agents."),
        arg_query("MON-001", "Application Insights",
                  """resources
| where type == 'microsoft.insights/components'
| project name, applicationId=properties.ApplicationId, ingestionMode=properties.IngestionMode, subscriptionId"""),

        query_header("MON-002", "Foundry Diagnostics Coverage",
                     "Diagnostic settings on Foundry accounts."),
        arg_query("MON-002", "Foundry Diagnostics",
                  """resources
| where type == 'microsoft.cognitiveservices/accounts' and kind =~ 'AIServices'
| project resourceName=name, resourceId=id, subscriptionId
| join kind=leftouter (
    resources
    | where type == 'microsoft.insights/diagnosticsettings'
    | extend targetId = tostring(split(id, '/providers/microsoft.insights')[0])
    | project targetId, diagName=name, workspaceId=properties.workspaceId
) on $left.resourceId == $right.targetId
| summarize Total=count(), WithDiagnostics=countif(isnotnull(diagName))""",
                  formatters=[heat_formatter("WithDiagnostics")]),

        query_header("MON-003", "Metric Alert Rules",
                     "Metric alerts targeting Foundry / Cognitive Services."),
        arg_query("MON-003", "Foundry Metric Alerts",
                  """resources
| where type == 'microsoft.insights/metricalerts'
| where properties.scopes has 'microsoft.cognitiveservices'
| extend severity = toint(properties.severity), enabled = tobool(properties.enabled)
| project name, severity, enabled, location, subscriptionId""",
                  formatters=[threshold_icon_formatter("enabled", "true",
                                                       success_text="Enabled", default_text="Disabled")]),

        query_header("MON-004", "Log Analytics Workspace Routing",
                     "Foundry / AI Search resources sending diagnostics to a workspace."),
        arg_query("MON-004", "LAW Coverage",
                  """resources
| where (type == 'microsoft.cognitiveservices/accounts' and kind =~ 'AIServices')
    or type == 'microsoft.search/searchservices'
| project resourceId=id, resourceName=name, type, subscriptionId
| join kind=leftouter (
    resources
    | where type == 'microsoft.insights/diagnosticsettings'
    | extend targetId = tostring(split(id, '/providers/microsoft.insights')[0])
    | project targetId, workspaceId=tostring(properties.workspaceId)
) on $left.resourceId == $right.targetId
| extend hasWorkspace = isnotnull(workspaceId)
| summarize Total=count(), RoutingToWorkspace=countif(hasWorkspace == true) by type""",
                  formatters=[heat_formatter("RoutingToWorkspace")]),

        manual_callout("MON-005", "Foundry Quality Evaluators",
                       "Groundedness, relevance, coherence, fluency evaluators on Foundry agents.",
                       "Use Foundry data plane API:<br/>"
                       "<code>GET https://{account}.services.ai.azure.com/api/projects/{project}/evaluations?api-version=2025-05-01</code>"),

        manual_callout("MON-006", "Continuous / Online Evaluation",
                       "Production-time evaluation runs on Foundry deployments.",
                       "<code>GET https://{account}.services.ai.azure.com/api/projects/{project}/evaluations/runs?api-version=2025-05-01</code>"),
    ]
    return group_section("Monitoring & Operations", items, name="mon-group")


# ---------------------------------------------------------------------------
# Top-level workbook
# ---------------------------------------------------------------------------

def build_workbook() -> dict:
    header = html_block(
        "<div style='padding:16px 20px;background:#eff6fc;border-left:3px solid #0078d4;border-radius:6px;margin-bottom:8px'>"
        "<h2 style='margin:0 0 4px 0;color:#0078d4;font-size:18px'>Microsoft Foundry Readiness Assessment</h2>"
        "<p style='margin:0;font-size:13px;color:#605e5c'>Evaluates your Azure environment for Microsoft Foundry-based AI workloads "
        "across nine readiness pillars aligned with the Azure AI Landing Zone. Select subscription(s) to run the assessment.</p>"
        "</div>",
        "header")

    parameters_item = {
        "type": 9,
        "content": {
            "version": "KqlParameterItem/1.0",
            "parameters": [
                {
                    "id": "subscription",
                    "version": "KqlParameterItem/1.0",
                    "name": "Subscription",
                    "type": 6,
                    "isRequired": True,
                    "multiSelect": True,
                    "quote": "'",
                    "delimiter": ",",
                    "typeSettings": {
                        "additionalResourceOptions": ["value::all"],
                        "includeAll": True,
                        "showDefault": False,
                    },
                    "defaultValue": "value::all",
                },
                {
                    "id": "pillar-bars-param",
                    "version": "KqlParameterItem/1.0",
                    "name": "PillarBarsHtml",
                    "type": 1,
                    "query": PILLAR_BARS_QUERY,
                    "isHiddenWhenLocked": True,
                    "queryType": 1,
                    "resourceType": "microsoft.resourcegraph/resources",
                    "crossComponentResources": SUBSCRIPTION_RESOURCES,
                },
                {
                    "id": "score-card-param",
                    "version": "KqlParameterItem/1.0",
                    "name": "ScoreCardHtml",
                    "type": 1,
                    "query": SCORE_CARD_QUERY,
                    "isHiddenWhenLocked": True,
                    "queryType": 1,
                    "resourceType": "microsoft.resourcegraph/resources",
                    "crossComponentResources": SUBSCRIPTION_RESOURCES,
                },
            ],
            "style": "pills",
        },
        "name": "parameters",
    }

    summary_group = {
        "type": 12,
        "content": {
            "version": "NotebookGroup/1.0",
            "groupType": "editable",
            "title": "Assessment Summary",
            "items": [
                {
                    "type": 1,
                    "content": {
                        "json": "<div style=\"border:1px solid #edebe9;border-radius:8px;background:#fff;box-shadow:0 2px 8px rgba(0,0,0,0.08);height:100%\">{ScoreCardHtml}</div>"
                    },
                    "customWidth": "25",
                    "name": "overall-score-tile",
                },
                {
                    "type": 1,
                    "content": {
                        "json": "<div style=\"padding:0 4px\">\r\n\r\n**Readiness by Pillar**\r\n\r\n{PillarBarsHtml}\r\n</div>"
                    },
                    "customWidth": "75",
                    "name": "pillar-grid",
                },
            ],
        },
        "name": "summary-group",
    }

    footer = html_block(
        "<div style='margin-top:24px;padding:12px 16px;background:#f3f2f1;border-radius:4px;font-size:12px;color:#605e5c;display:flex;justify-content:center;align-items:center;gap:6px'>"
        "<a href='https://github.com/Azure/ai-readiness-assessment' style='color:#24292f;text-decoration:none;display:flex;align-items:center;gap:6px'>"
        "<svg height='16' width='16' viewBox='0 0 16 16' fill='#24292f'><path d='M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z'/></svg>"
        "View on GitHub</a></div>",
        "footer")

    return {
        "version": "Notebook/1.0",
        "items": [
            header,
            parameters_item,
            summary_group,
            landscape_group(),
            foundry_inventory_group(),
            dmg_group(),
            rce_group(),
            rai_group(),
            iam_group(),
            network_security_group(),
            policy_compliance_group(),
            cost_ops_group(),
            monitoring_group(),
            footer,
        ],
        "fallbackResourceIds": ["Azure Monitor"],
        "$schema": "https://github.com/Microsoft/Application-Insights-Workbooks/blob/master/schema/workbook.json",
    }


def write_query_reference(wb: dict) -> None:
    """Extract query metadata from headers and emit queries.md + docs/QUERIES.md."""
    import re

    queries = []

    def walk(items, pillar=None):
        for it in items:
            t = it.get("type")
            c = it.get("content", {})
            if t == 12:
                walk(c.get("items", []), c.get("title", "Other"))
            elif t == 1:
                j = c.get("json", "")
                m = re.search(
                    r"<span[^>]*>([A-Z]{3}-\d{3})</span>.*?<span[^>]*>([^<]+)</span>(?:<span[^>]*>([^<]+)</span>)?",
                    j, re.S)
                if m:
                    qid, title, sub = m.group(1), m.group(2).strip(), (m.group(3) or "").strip()
                    sub = sub.replace("Manual/API &#x2014; ", "")
                    kind = "Manual/API" if "Manual Check Required" in j else "ARG"
                    queries.append({"pillar": pillar, "qid": qid, "title": title,
                                    "subtitle": sub, "kind": kind})

    walk(wb["items"])

    pillar_order = [p[0] for p in PILLAR_DEFS]
    by_pillar: dict = {}
    for q in queries:
        by_pillar.setdefault(q["pillar"], []).append(q)

    arg_count = sum(1 for q in queries if q["kind"] == "ARG")
    manual_count = sum(1 for q in queries if q["kind"] == "Manual/API")

    lines = [
        "# AIRA \u2014 Query Reference",
        "",
        "All queries executed by the AI Platform Readiness Assessment workbook. "
        "This file is auto-generated from the workbook source by `scripts/build-workbook.py`.",
        "",
        f"**Total: {len(queries)} queries** ({arg_count} ARG, {manual_count} Manual/API).",
        "",
    ]
    for p in pillar_order:
        if p not in by_pillar:
            continue
        lines += [f"## {p}", "",
                  "| Query ID | Query Name | Type | Description |",
                  "|----------|-----------|------|-------------|"]
        for q in by_pillar[p]:
            lines.append(f"| {q['qid']} | {q['title']} | {q['kind']} | {q['subtitle']} |")
        lines.append("")

    content = "\n".join(lines) + "\n"
    (ROOT / "queries.md").write_text(content, encoding="utf-8")
    (ROOT / "docs" / "QUERIES.md").write_text(content, encoding="utf-8")
    print(f"Wrote queries.md and docs/QUERIES.md ({len(queries)} queries)")


def main() -> None:
    wb = build_workbook()
    OUT.write_text(json.dumps(wb, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    write_query_reference(wb)
    print(f"Total max score: {TOTAL_MAX}")
    for label, _, mx, _ in PILLAR_DEFS:
        print(f"  {label}: max {mx}")


if __name__ == "__main__":
    main()
