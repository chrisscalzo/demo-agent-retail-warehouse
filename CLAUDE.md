# Retail Warehouse Copilot Studio Demo

## Project Purpose

Demo content and Microsoft Copilot Studio agent for retail warehouse workers (team members, supervisors, managers) at Contoso Retail. Showcases: general policy/procedure knowledge, state-specific safety content (CA/NV/AZ), NL queries against a SharePoint list, and safety issue logging via the agent.

## File Structure

```
agent-retail-warehouse-demo/
├── README.md                    ← quick-start entry point
├── CLAUDE.md
├── .gitignore
├── content/
│   ├── general/                 ← 10 general policy/procedure JSON files
│   └── states/
│       ├── ca/                  ← 5 CA-specific JSON files
│       ├── nv/                  ← 5 NV-specific JSON files
│       └── az/                  ← 5 AZ-specific JSON files
├── output/                      ← generated Word docs (mirrors SharePoint structure)
│   ├── General/
│   └── States/
│       ├── CA/
│       ├── NV/
│       └── AZ/
├── data/                        ← sample data (Safety Issue Log CSV)
├── scripts/                     ← all Python scripts + single requirements.txt
│   ├── generate_docs.py
│   ├── setup_sharepoint_list.py
│   ├── setup_dataverse_ppe_table.py
│   ├── markdown_to_docx.py
│   ├── deploy_weather_mcp_azure.ps1
│   └── requirements.txt        ← merged (python-docx + msal + requests)
├── agent/                       ← Copilot Studio config artifacts
│   ├── Copilot Studio Agent Instructions.txt
│   ├── PPE Suggestion Agent Instructions.txt
│   ├── Log Safety Issue - Tool Instructions.txt
│   ├── Copilot Studio Build Plan.md
│   └── demo_prompts.txt
├── workshop/                    ← workshop deliverables
│   ├── Prerequisites Setup Guide.md/.docx
│   ├── Copilot Studio Build Plan - Warehouse Assistant Agent.md/.docx
│   └── Weather MCP Server Audience Setup.md
└── mcp-weather-server/          ← self-contained Weather MCP server
```

## Current Status

- [x] content/general/ — all 10 JSON files complete
- [x] content/states/ca/ — all 5 complete
- [x] content/states/nv/ — all 5 complete
- [x] content/states/az/ — all 5 complete
- [x] scripts/generate_docs.py — complete (python-docx, dark blue #003A70 headings, orange #F26B00 accent)
- [x] scripts/requirements.txt — consolidated (python-docx + msal + requests)
- [x] output/ — 25 .docx files generated (zero errors, Python 3.14.3)
- [x] scripts/setup_sharepoint_list.py — complete (MSAL device code + SP REST API)
- [x] scripts/setup_dataverse_ppe_table.py — complete (MSAL device code + Dataverse Web API)
- [x] agent/PPE Suggestion Agent Instructions.txt — complete (child agent system prompt)
- [ ] Dataverse PPE Kit Recommendation table created (run scripts/setup_dataverse_ppe_table.py)
- [ ] SharePoint list created
- [ ] Copilot Studio agent built
- [ ] PPE Suggestion Agent (child agent) configured in Copilot Studio

## JSON Content Schema

Every content file must follow this exact schema:

```json
{
  "title": "Document Title",
  "version": "1.0",
  "category": "General | CA | NV | AZ",
  "audience": ["Team Member", "Supervisor", "Manager"],
  "sections": [
    {
      "heading": "Section Title",
      "level": 1,
      "content": [
        { "type": "paragraph", "text": "..." },
        { "type": "bullet_list", "items": ["...", "..."] },
        { "type": "numbered_list", "items": ["...", "..."] },
        { "type": "table", "headers": ["Col1", "Col2"], "rows": [["val", "val"]] }
      ]
    }
  ]
}
```

## Content Files Reference

### General (10 docs)

| File | Title |
|------|-------|
| warehouse_operations_overview.json | Warehouse Operations Overview |
| shift_management_policy.json | Shift Management Policy |
| holiday_busy_period_procedures.json | Holiday & Peak Season Procedures |
| new_employee_onboarding.json | New Employee Onboarding Guide |
| general_safety_handbook.json | General Safety Handbook |
| emergency_response_procedures.json | Emergency Response Procedures |
| equipment_safety_guidelines.json | Equipment Safety Guidelines |
| ppe_policy.json | PPE Policy |
| incident_reporting_policy.json | Incident & Near-Miss Reporting Policy |
| workplace_code_of_conduct.json | Workplace Code of Conduct |

### State-Specific (5 per state x 3 states = 15 docs)

Same 5 document types per state:
- `{state}_safety_regulations.json`
- `{state}_heat_illness_prevention.json`
- `{state}_labor_law_compliance.json`
- `{state}_workers_compensation.json`
- `{state}_hazard_communication.json`

### Key State Differentiators

**Safety Regulations:** CA = Cal/OSHA (state plan, DOSH); NV = Nevada OSHA (state plan, DIR); AZ = Federal OSHA (no state plan, AZ Industrial Commission)

**Heat Illness:** CA = Cal/OSHA §3395, shade at ≥80°F, mandatory written plan; NV = NAC 618, 90°F+ protocols, acclimatization; AZ = Federal OSHA Heat NPRM, 110°F+ extreme heat, monsoon hazard

**Labor Law:** CA = daily OT after 8hr, 10-min rest per 4hr, meal by hr 5, split-shift premium; NV = OT after 40hr/week, 10-min rest per 4hr, meal after 8hr; AZ = OT after 40hr/week, meal after 5hr continuous, no daily OT

**Workers Comp:** CA = CA DIR/State Fund, 1-day reporting, employee MPN doctor choice; NV = NV SIIS/private carriers, 7-day reporting, employer panel; AZ = AZ State Compensation Fund, 10-day reporting, employer-directed care first 90 days

**Hazard Communication:** CA = Cal/OSHA HazCom + Prop 65, bilingual labeling common; NV = NV Right-to-Know, annual training mandate; AZ = Federal HazCom 2012/GHS, training within 30 days of hire

## generate_docs.py Architecture

1. Walk `content/` directory tree
2. For each `.json` file, load content
3. Create a new `docx` Document
4. Apply styles:
   - Header block: "Contoso Retail" + document title + version/date
   - level 1 heading → Title style
   - level 2 heading → Heading 1 style
   - paragraphs → Normal style
   - bullet/numbered lists → List styles
   - tables → styled with header row shading
5. Write to matching path under `output/` (general → `output/General/`, states/ca → `output/States/CA/`, etc.)
6. Print summary of files generated

## SharePoint Safety Issue Log Schema

List name: **Safety Issue Log**

| Column | Type | Notes |
|--------|------|-------|
| Title (IssueID) | Auto | SP auto-generated |
| DateReported | Date/Time | Default: today |
| ReporterName | Single line text | |
| WarehouseLocation | Choice | CA-LAX-001 Los Angeles, CA-SFO-002 Fresno, NV-LV-001 Las Vegas, NV-RNO-002 Reno, AZ-PHX-001 Phoenix, AZ-TUC-002 Tucson |
| IssueType | Choice | Equipment / Environmental / Process / Near-Miss / Other |
| Description | Multi-line text | |
| Severity | Choice | Low / Medium / High / Critical |
| Status | Choice | Open / In Progress / Resolved |
| AssignedTo | Person | |
| ResolutionNotes | Multi-line text | |

## Dataverse PPE Kit Recommendation Table

Table name: **PPE Kit Recommendation** (logical: `cr_ppekitrecommendation`)

| Column | Type | Notes |
|--------|------|-------|
| cr_ppekitname | String (200) | Primary name — e.g., "Dock Worker Kit" |
| cr_jobrole | String (200) | e.g., "Dock Worker" |
| cr_department | Picklist | Receiving, Staging, Storage, Pick & Pack, Shipping, Maintenance, Management |
| cr_requiredppe | Memo (2000) | Mandatory PPE items with standards |
| cr_optionalppe | Memo (2000) | Recommended PPE items with conditions |
| cr_hazardlevel | Picklist | Low, Medium, High |
| cr_notes | Memo (2000) | Zone assignments, certifications, safety warnings |

20 records covering: Dock Worker, Forklift Operator, Receiving Clerk, Staging Associate, Inventory Associate, Reach Truck Operator, Pick & Pack Associate, Order Picker (Elevated), Shipping Clerk, Outbound Loader, Maintenance Technician, Battery Room Technician, Janitorial Staff, Floor Supervisor, Warehouse Manager, Visitor/Contractor, Conveyor Belt Operator, Cold Storage Associate, Hazmat Spill Responder, Safety Coordinator.

## PPE Suggestion Agent (Child Agent)

- Name: **PPE Suggestion Agent**
- Parent: Warehouse Assistant
- Tool: Dataverse MCP Server (queries PPE Kit Recommendation table)
- Trigger: AI-routed based on description (role-based PPE questions)
- Instructions: `agent/PPE Suggestion Agent Instructions.txt`
- Scope: Role/department PPE lookups only; defers zone-based, policy, and incident questions to parent

## Copilot Studio Agent Setup

Agent name: **Warehouse Assistant**

1. Create agent in Copilot Studio
2. Add SharePoint knowledge source (entire doc library, all folders)
3. State filtering via system prompt: "When answering safety questions, only use documents from the user's state folder. Ask the user which state their warehouse is in if not known."
4. SharePoint list read — knowledge source or Power Automate connector (NL queries)
5. SharePoint list write — Power Automate flow triggered by agent topic
6. Topics:
   - **Log Safety Issue** — slot-filling to collect all required fields, submit to list
   - **My State Regulations** — routes to state-specific content
   - **Shift & Schedule Help** — general shift queries
   - **Emergency Procedures** — surfaces emergency docs

## Implementation Order

0. Verify Python (`python --version`) and install deps (`pip install -r scripts/requirements.txt`)
1. Complete remaining JSON content files (ca_hazard_communication, all NV, all AZ)
2. Create `scripts/generate_docs.py` and `scripts/requirements.txt`
3. Run script → `python scripts/generate_docs.py` → verify 25 .docx files in `output/`
4. Upload to SharePoint in correct folder structure
5. Create SharePoint Safety Issue Log list
6. Walk through Copilot Studio agent setup

## Verification Checklist

- [ ] `python scripts/generate_docs.py` produces 25 .docx files in `output/`
- [ ] Open 2-3 docs and verify formatting, content realism, section structure
- [ ] SharePoint upload — folder structure mirrors `output/`
- [ ] Copilot Studio test: shift question → general doc answer
- [ ] Copilot Studio test: CA heat safety question → only CA doc cited
- [ ] Copilot Studio test: "what open safety issues are there?" → list query works
- [ ] Copilot Studio test: "I want to log a safety issue" → slot-filling collects all fields + submits
- [ ] `python scripts/setup_dataverse_ppe_table.py` creates table with 7 columns and 20 records
- [ ] Table visible in Power Apps with correct data
- [ ] PPE Suggestion Agent answers: "What PPE does a forklift operator need?" correctly
- [ ] Parent agent delegates: "I'm a dock worker, what PPE do I need?" to child agent
- [ ] Parent agent does NOT delegate: "What PPE is required in Zone A?" (answers from docs)
- [ ] Parent agent does NOT delegate: "How do I get reimbursed for safety boots?" (answers from docs)
