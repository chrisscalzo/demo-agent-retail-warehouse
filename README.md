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

## Quick Start

1. **Prerequisites**: Follow `workshop/Prerequisites Setup Guide.md` to set up the Azure AD app registration, SharePoint site, document library, Safety Issue Log list, and Dataverse PPE table.
2. **Build the agent**: Follow `workshop/Copilot Studio Build Plan - Warehouse Assistant Agent.md` to create and configure the Copilot Studio agent.
3. **Test**: Use the demo prompts in `agent/demo_prompts.txt` to validate all capabilities.

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
