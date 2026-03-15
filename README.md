# Retail Warehouse Copilot Studio Demo

Demo content and Microsoft Copilot Studio agent for retail warehouse workers (team members, supervisors, managers) at Contoso Retail. Covers general policy/procedure knowledge, state-specific safety content (CA/NV/AZ), natural-language queries against a SharePoint list, safety issue logging, and PPE kit recommendations via a child agent backed by Dataverse.

## Folder Structure

| Folder | Contents |
|--------|----------|
| `content/` | 25 JSON source files (10 general + 5 per state) |
| `output/` | Generated Word docs ready for SharePoint upload |
| `data/` | Sample data (Safety Issue Log CSV) |
| `scripts/` | Python scripts and consolidated `requirements.txt` |
| `agent/` | Copilot Studio agent instructions, tool guidance, build plan, demo prompts |
| `workshop/` | Workshop deliverables (slide decks, setup guides) |
| `mcp-weather-server/` | Self-contained Weather MCP server (own requirements.txt) |

## Important: Configuration Required

The Python scripts and MCP connector YAML ship with placeholder values that you **must** replace with your own environment details before running anything:

| Placeholder | Where to get it | Files |
|-------------|-----------------|-------|
| `YOUR_TENANT_ID` | Azure AD > App registrations > Overview > Directory (tenant) ID | `scripts/setup_sharepoint_list.py`, `scripts/setup_dataverse_ppe_table.py` |
| `YOUR_CLIENT_ID` | Azure AD > App registrations > Overview > Application (client) ID | Same two scripts |
| `YOUR_TENANT.sharepoint.com/sites/YOUR_SITE` | Your SharePoint site URL | `scripts/setup_sharepoint_list.py` |
| `YOUR_ORG.crm.dynamics.com` | Power Platform admin center > Environments > Environment URL | `scripts/setup_dataverse_ppe_table.py` |
| `YOUR_APP_NAME...azurecontainerapps.io` | Output of `scripts/deploy_weather_mcp_azure.ps1` | `mcp-weather-server/copilot-studio-mcp-connector.yaml`, `workshop/Weather MCP Server Audience Setup.md` |

See the [Prerequisites Setup Guide](workshop/Prerequisites%20Setup%20Guide.md) for full details on creating the app registration and obtaining these values.

## Quick Start

1. **Configure**: Replace the placeholder values listed above with your environment details.
2. **Prerequisites**: Follow `workshop/Prerequisites Setup Guide.md` to set up the Azure AD app registration, SharePoint site, document library, Safety Issue Log list, and Dataverse PPE table.
3. **Build the agent**: Follow `workshop/Copilot Studio Build Plan - Warehouse Assistant Agent.md` to create and configure the Copilot Studio agent.
4. **Test**: Use the demo prompts in `agent/demo_prompts.txt` to validate all capabilities.

## Key Files

| File | Purpose |
|------|---------|
| `workshop/Prerequisites Setup Guide.md` | End-to-end environment setup (SharePoint, Dataverse, scripts) |
| `workshop/Copilot Studio Build Plan - Warehouse Assistant Agent.md` | Step-by-step agent build instructions |
| `agent/Copilot Studio Agent Instructions.txt` | Parent agent system instructions |
| `agent/PPE Suggestion Agent Instructions.txt` | Child agent system instructions |
| `agent/Log Safety Issue - Tool Instructions.txt` | LogSafetyIssue action description |
| `agent/Copilot Studio Build Plan.md` | Concise build plan (internal reference) |
| `agent/demo_prompts.txt` | 8 sections of test prompts |
