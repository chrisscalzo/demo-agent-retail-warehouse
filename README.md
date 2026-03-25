<div align="center">

# 🏭 Retail Warehouse Assistant — Copilot Studio Demo

**An end-to-end Microsoft Copilot Studio agent for warehouse operations, safety compliance, and shift planning**

[![Platform](https://img.shields.io/badge/Platform-Microsoft_Copilot_Studio-742774?style=for-the-badge&logo=microsoft&logoColor=white)](https://www.microsoft.com/en-us/copilot/microsoft-copilot-studio)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SharePoint](https://img.shields.io/badge/SharePoint-Online-038387?style=for-the-badge&logo=microsoftsharepoint&logoColor=white)](https://www.microsoft.com/en-us/microsoft-365/sharepoint/)
[![Dataverse](https://img.shields.io/badge/Dataverse-Power_Platform-742774?style=for-the-badge&logo=microsoft&logoColor=white)](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/)
[![MCP](https://img.shields.io/badge/MCP-Weather_Server-FF6F00?style=for-the-badge&logo=fastapi&logoColor=white)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

*A production-ready demo showcasing how Copilot Studio agents can serve frontline warehouse workers with knowledge retrieval, safety logging, role-based PPE recommendations, and real-time weather integration — all backed by SharePoint, Dataverse, and an MCP weather server.*

</div>

---

## 📋 Overview

This project provides everything you need to build, configure, and demo the **Warehouse Assistant** — a Microsoft Copilot Studio agent designed for **Contoso Retail** warehouse workers across California, Nevada, and Arizona.

The agent supports **team members, supervisors, and managers** by answering questions about warehouse operations, safety procedures, and labor law compliance. It retrieves answers from **25 policy documents** stored in SharePoint, queries a **Safety Issue Log** for real-time incident data, delegates **PPE kit recommendations** to a child agent backed by Dataverse, and can even factor in **live weather data** from an MCP server when planning shifts.

Whether you're running a workshop, delivering a customer demo, or exploring Copilot Studio's agentic capabilities — this repo has the content, scripts, agent configurations, and step-by-step guides to get you from zero to a working demo.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **Policy & Procedure Q&A** | Natural-language answers from 25 branded Word documents covering operations, safety, onboarding, equipment, and HR |
| 🗺️ **State-Specific Compliance** | Automatic scoping to CA, NV, or AZ regulations — heat illness, labor law, workers' comp, hazard communication |
| 📊 **Safety Issue Log Queries** | Read open/resolved incidents, filter by location or severity, spot trends — all from a SharePoint list |
| ✏️ **Safety Issue Logging** | Guided slot-filling flow to report new incidents with full field validation and confirmation |
| 🦺 **PPE Kit Recommendations** | Child agent queries a Dataverse table of 20 role-specific PPE kits with required/optional items and safety standards |
| 🌤️ **Weather-Aware Shift Planning** | MCP server provides real-time weather and 7-day forecasts to inform heat protocols and shift adjustments |
| 🔀 **Cross-State Comparisons** | Side-by-side answers for overtime rules, injury reporting deadlines, doctor choice policies across all three states |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Microsoft Copilot Studio                     │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Warehouse Assistant (Parent Agent)            │   │
│  │  • System instructions  • State filtering  • Slot-filling │   │
│  └──────┬──────────┬──────────┬──────────────┬──────────────┘   │
│         │          │          │              │                    │
│         ▼          ▼          ▼              ▼                    │
│   ┌──────────┐ ┌────────┐ ┌──────────┐ ┌─────────────────┐     │
│   │SharePoint│ │  SP    │ │   PPE    │ │  Weather MCP    │     │
│   │  Docs    │ │  List  │ │  Child   │ │  Server Action  │     │
│   │Knowledge │ │ Action │ │  Agent   │ │  (Connector)    │     │
│   └──────────┘ └────────┘ └────┬─────┘ └────────┬────────┘     │
└─────────────────────────────────┼────────────────┼──────────────┘
                                  │                │
                  ┌───────────────▼──┐    ┌───────▼───────────┐
                  │    Dataverse     │    │  Azure Container  │
                  │  PPE Kit Table   │    │  Apps (FastMCP)   │
                  │  (20 records)    │    │  Open-Meteo API   │
                  └──────────────────┘    └───────────────────┘

  ┌──────────────────┐   ┌──────────────────┐
  │  SharePoint Doc  │   │  SharePoint List  │
  │  Library (25     │   │  Safety Issue Log │
  │  policy docs)    │   │  (incidents data) │
  └──────────────────┘   └──────────────────┘
```

**How it works:**

1. **Knowledge Retrieval** — The parent agent uses SharePoint document knowledge to answer policy, safety, and HR questions. State-specific queries are automatically scoped to the correct folder (CA/NV/AZ).
2. **Safety Issue Log** — Supervisors query incident data from a SharePoint list; team members can log new issues through a guided slot-filling topic.
3. **PPE Delegation** — Role-based PPE questions are routed to the PPE Suggestion Agent, which queries Dataverse for the matching kit and returns required/optional items with safety standards.
4. **Weather Integration** — An MCP-compliant weather server (deployed to Azure Container Apps) provides current conditions and forecasts to support heat protocol decisions and shift planning.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Agent** | Microsoft Copilot Studio | Parent + child agent orchestration, topics, slot-filling |
| **Knowledge** | SharePoint Online (Document Library) | 25 branded policy/procedure Word documents |
| **Data** | SharePoint Online (List) | Safety Issue Log — incidents, near-misses, equipment issues |
| **Data** | Microsoft Dataverse | PPE Kit Recommendation table (20 role-specific records) |
| **MCP Server** | Python / FastMCP | Weather tools via streamable HTTP (`/mcp/` endpoint) |
| **Weather API** | Open-Meteo (no auth required) | Current conditions + daily forecast (geocoding + weather) |
| **Hosting** | Azure Container Apps | Docker container for the MCP weather server |
| **Scripts** | Python 3.10+ | Document generation, SharePoint list setup, Dataverse table setup |
| **Auth** | MSAL (Device Code Flow) | Script authentication to SharePoint and Dataverse APIs |
| **Deployment** | PowerShell / Azure CLI | Automated Azure Container Apps deployment |

---

## 📁 Project Structure

```
demo-agent-retail-warehouse/
│
├── 📄 README.md                           ← You are here
├── 📄 CLAUDE.md                           ← AI assistant context file
│
├── 📂 agent/                              ← Copilot Studio configuration
│   ├── Copilot Studio Agent Instructions.txt    ← Parent agent system prompt
│   ├── PPE Suggestion Agent Instructions.txt    ← Child agent system prompt
│   ├── Log Safety Issue - Tool Instructions.txt ← LogSafetyIssue action prompt
│   ├── Copilot Studio Build Plan.md             ← Concise build reference
│   └── demo_prompts.txt                         ← 105+ test prompts (8 sections)
│
├── 📂 content/                            ← Source content (JSON)
│   ├── general/                           ← 10 general policy docs
│   └── states/
│       ├── ca/                            ← 5 California-specific docs
│       ├── nv/                            ← 5 Nevada-specific docs
│       └── az/                            ← 5 Arizona-specific docs
│
├── 📂 output/                             ← Generated Word docs (upload to SharePoint)
│   ├── General/                           ← 10 .docx files
│   └── States/
│       ├── CA/                            ← 5 .docx files
│       ├── NV/                            ← 5 .docx files
│       └── AZ/                            ← 5 .docx files
│
├── 📂 data/                               ← Sample data
│   └── safety_issue_log_sample.csv        ← 25 sample incidents across 6 locations
│
├── 📂 scripts/                            ← Automation scripts
│   ├── generate_docs.py                   ← JSON → branded Word documents
│   ├── setup_sharepoint_list.py           ← Create Safety Issue Log + sample data
│   ├── setup_dataverse_ppe_table.py       ← Create PPE Kit table + 20 records
│   ├── markdown_to_docx.py               ← Markdown → Word conversion utility
│   ├── deploy_weather_mcp_azure.ps1       ← Azure Container Apps deployment
│   └── requirements.txt                   ← Python deps (python-docx, msal, requests)
│
├── 📂 mcp-weather-server/                 ← Self-contained MCP weather service
│   ├── server.py                          ← FastMCP server (get_current_weather, get_daily_forecast)
│   ├── Dockerfile                         ← Python 3.12-slim container
│   ├── requirements.txt                   ← mcp, requests
│   ├── copilot-studio-mcp-connector.yaml  ← Copilot Studio connector definition
│   └── weather-mcp-action.mcs.yml         ← MCS action manifest
│
└── 📂 workshop/                           ← Workshop & setup guides
    ├── Prerequisites Setup Guide.md       ← Full environment setup walkthrough
    ├── Prerequisites Setup Guide.docx
    ├── Copilot Studio Build Plan - Warehouse Assistant Agent.md
    ├── Copilot Studio Build Plan - Warehouse Assistant Agent.docx
    └── Weather MCP Server Audience Setup.md
```

---

## 📌 Prerequisites

Before you begin, ensure you have:

- [ ] **Python 3.10+** installed
- [ ] **Azure CLI** installed and authenticated (`az login`)
- [ ] **Microsoft 365 tenant** with SharePoint Online and Dataverse access
- [ ] **Microsoft Copilot Studio** license / trial
- [ ] **Azure subscription** (for deploying the MCP weather server)
- [ ] **Azure AD App Registration** with:
  - Public client / device code flow enabled
  - `SharePoint > AllSites.Manage` permission (admin-consented)
  - `Dataverse > user_impersonation` permission (admin-consented)

> 📖 See the **[Prerequisites Setup Guide](workshop/Prerequisites%20Setup%20Guide.md)** for detailed instructions on creating the app registration and obtaining all required IDs.

---

## 🚀 Getting Started

### Step 1 — Clone & Install Dependencies

```bash
git clone https://github.com/your-org/demo-agent-retail-warehouse.git
cd demo-agent-retail-warehouse
pip install -r scripts/requirements.txt
```

### Step 2 — Configure Environment Placeholders

Replace the placeholder values in the scripts and connector YAML with your environment details:

<details>
<summary><strong>📝 Click to expand placeholder reference</strong></summary>

| Placeholder | Where to Find It | Files to Update |
|---|---|---|
| `YOUR_TENANT_ID` | Azure AD → App registrations → Directory (tenant) ID | `scripts/setup_sharepoint_list.py`, `scripts/setup_dataverse_ppe_table.py` |
| `YOUR_CLIENT_ID` | Azure AD → App registrations → Application (client) ID | Same two scripts |
| `YOUR_TENANT.sharepoint.com/sites/YOUR_SITE` | Your SharePoint site URL | `scripts/setup_sharepoint_list.py` |
| `YOUR_ORG.crm.dynamics.com` | Power Platform Admin Center → Environments → URL | `scripts/setup_dataverse_ppe_table.py` |
| `YOUR_APP_NAME...azurecontainerapps.io` | Output of `deploy_weather_mcp_azure.ps1` | `mcp-weather-server/copilot-studio-mcp-connector.yaml` |

</details>

### Step 3 — Generate & Upload Policy Documents

```bash
python scripts/generate_docs.py
```

This creates **25 branded Word documents** in `output/`. Upload them to your SharePoint document library maintaining the folder structure:

```
SharePoint Document Library/
├── General/          ← 10 docs
└── States/
    ├── CA/           ← 5 docs
    ├── NV/           ← 5 docs
    └── AZ/           ← 5 docs
```

### Step 4 — Create the Safety Issue Log

```bash
python scripts/setup_sharepoint_list.py
```

Creates the **Safety Issue Log** SharePoint list with all required columns and populates it with **20 realistic sample incidents** across 6 warehouse locations.

### Step 5 — Create the Dataverse PPE Table

```bash
python scripts/setup_dataverse_ppe_table.py
```

Creates the **PPE Kit Recommendation** table in Dataverse with **20 role-specific records** covering roles from Dock Worker to Hazmat Spill Responder.

### Step 6 — Deploy the Weather MCP Server

```powershell
.\scripts\deploy_weather_mcp_azure.ps1
```

Deploys the FastMCP weather server to **Azure Container Apps**. The script handles resource group creation, container registry, image build/push, and app deployment. Copy the output URL for the next step.

### Step 7 — Build the Agent in Copilot Studio

Follow the **[Copilot Studio Build Plan](workshop/Copilot%20Studio%20Build%20Plan%20-%20Warehouse%20Assistant%20Agent.md)** to:

1. Create the **Warehouse Assistant** agent and paste the system instructions
2. Connect the **SharePoint document library** as a knowledge source
3. Connect the **Safety Issue Log** list
4. Create the **LogSafetyIssue** action with slot-filling
5. Create the **PPE Suggestion Agent** child agent with Dataverse connector
6. Add the **Weather MCP Server** connector ([setup guide](workshop/Weather%20MCP%20Server%20Audience%20Setup.md))

### Step 8 — Test with Demo Prompts

Use the **105+ curated prompts** in [`agent/demo_prompts.txt`](agent/demo_prompts.txt) to validate all agent capabilities.

---

## 🎯 Demo Scenarios

<details>
<summary><strong>1️⃣ General Policy & Procedure Q&A</strong> — 25 prompts</summary>

Ask about shift schedules, sick call procedures, onboarding milestones, PPE requirements, emergency assembly points, lockout/tagout, forklift certification, and more.

> *"What time does the AM shift start and end?"*
> *"How do I report a near-miss?"*
> *"Do I need certification to drive a forklift?"*

</details>

<details>
<summary><strong>2️⃣ State-Specific Safety Compliance</strong> — 25 prompts (auto-scoped to user's state)</summary>

Heat illness prevention, OSHA enforcement, labor law (overtime/breaks/meals), workers' compensation, and hazard communication — automatically filtered to CA, NV, or AZ.

> *"What temperature triggers enhanced heat protocols?"*
> *"How many rest breaks do I get on an 8-hour shift?"*
> *"Can I see my own doctor after a work injury?"*

</details>

<details>
<summary><strong>3️⃣ Explicit State & Cross-State Comparisons</strong> — 15 prompts</summary>

Override the default state or compare regulations across all three states.

> *"What are the overtime rules specifically in California?"*
> *"How does overtime differ between California, Nevada, and Arizona?"*
> *"Which state has the strictest heat illness requirements?"*

</details>

<details>
<summary><strong>4️⃣ Safety Issue Log Queries</strong> — 22 prompts (supervisor + team member)</summary>

Supervisors can view cross-location trends and severity breakdowns. Team members can check the status of specific reported issues.

> *"How many open safety issues are there across all locations?"*
> *"Show every Critical issue still open or in progress."*
> *"I reported a pallet jack problem last week — has it been fixed?"*

</details>

<details>
<summary><strong>5️⃣ Safety Issue Logging</strong> — 8 prompts</summary>

Guided slot-filling flow collects reporter name, location, issue type, description, and severity — then confirms and submits.

> *"I want to log a safety issue."*
> *"Forklift reverse alarm not making sound."*
> *"Temperature in Zone B is hitting 100 degrees and there's no extra water."*

</details>

<details>
<summary><strong>6️⃣ PPE Kit Recommendations</strong> — 10 prompts (delegated to child agent)</summary>

Role-based PPE lookups with required/optional items, safety standards, and hazard level warnings — powered by a Dataverse child agent.

> *"I'm a dock worker. What PPE do I need?"*
> *"What PPE kits are available for the Maintenance department?"*
> *"What PPE does a hazmat spill responder need?"*

</details>

<details>
<summary><strong>7️⃣ Weather-Aware Shift Planning</strong></summary>

Combine live weather data with safety policies to make informed decisions about shift adjustments and heat protocols.

> *"What is tomorrow's weather in Phoenix, AZ, and how should daytime shifts be adjusted?"*

</details>

---

## 🌤️ MCP Weather Server

The weather server is a standalone **FastMCP** service exposing two tools over streamable HTTP:

| Tool | Description |
|------|-------------|
| `get_current_weather(location)` | Current conditions — temperature, wind speed, humidity, weather code |
| `get_daily_forecast(location, days)` | 1–7 day forecast — high/low temps, precipitation, wind |

- **API**: [Open-Meteo](https://open-meteo.com/) (free, no auth required)
- **Transport**: Streamable HTTP at `/mcp/` endpoint
- **Caching**: LRU geocoding cache (128 entries)
- **Deployment**: Docker on Azure Container Apps (0.5 vCPU, 1 GiB RAM)

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes and commit (`git commit -m "Add my feature"`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

Please ensure any new content files follow the [JSON content schema](CLAUDE.md) documented in `CLAUDE.md`.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**Built with ❤️ for Microsoft Copilot Studio workshops and demos**

[Prerequisites Guide](workshop/Prerequisites%20Setup%20Guide.md) · [Build Plan](workshop/Copilot%20Studio%20Build%20Plan%20-%20Warehouse%20Assistant%20Agent.md) · [Demo Prompts](agent/demo_prompts.txt)

</div>
