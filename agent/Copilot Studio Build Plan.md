# Copilot Studio Agent Build Plan

Audience: Customer stakeholders
Scope: End-to-end order of operations for building the Warehouse Assistant agent, with space for screenshots.
Date: 2026-03-09

## 0) Prerequisites and inputs

- Access: Copilot Studio environment with permission to create agents, connect data, and publish.
- SharePoint:
  - Document library containing the generated policy docs with folders: General, States/CA, States/NV, States/AZ.
  - Safety Issue Log list created with the required columns.
- Tool access in Copilot Studio to create a custom action for list writeback.
- Ready-to-use artifacts in the `agent/` directory of this repo:
  - Agent instructions in Copilot Studio Agent Instructions.txt.
  - Tool guidance in Log Safety Issue - Tool Instructions.txt.
  - Demo prompts in demo_prompts.txt.

[Add screenshot: environment access + permissions confirmation]

## 1) Create the agent

Goal: Stand up the Warehouse Assistant shell and apply baseline instructions.

- Create a new agent named Warehouse Assistant.
- Paste the system instructions from Copilot Studio Agent Instructions.txt.
- Set tone to concise and direct (warehouse floor audience).
- Save and open the test chat to confirm the agent is responsive.

[Add screenshot: Agent creation screen]
[Add screenshot: Instructions pane with system prompt]

## 2) Connect knowledge sources

Goal: Ensure the agent can answer from policy docs and read from the Safety Issue Log list.

- Add the SharePoint document library as a knowledge source.
  - Include all folders: General, States/CA, States/NV, States/AZ.
- Add the Safety Issue Log list as a knowledge source (for read queries).
- Validate that general questions resolve from the General folder.
- Validate that state-specific questions pull from the correct state folder based on the user state.

[Add screenshot: Knowledge sources list]
[Add screenshot: SharePoint document library mapping]

## 3) Create tools (actions)

Goal: Enable writeback for logging new safety issues using a tool action and a topic.

- Create a tool action that creates a list item in Safety Issue Log.
- Name the action LogSafetyIssue and map fields:
  - ReporterName
  - WarehouseLocation
  - IssueType
  - Description
  - Severity
- Validate the tool returns success on a test submission.

[Add screenshot: Action definition]
[Add screenshot: Field mapping]

## 4) Create and modify topics

Goal: Add intent routing and slot-filling for safety issue logging.

- Create a Log Safety Issue topic.
  - Triggers: "log a safety issue", "report a safety concern", "near-miss", "incident report".
  - Collect required fields in order:
    1) Reporter name
    2) Warehouse location (choice list)
    3) Issue type (choice list)
    4) Description
    5) Severity (choice list)
  - Confirm details and call LogSafetyIssue.
  - Acknowledge submission and next steps.
- Create topic(s) for policy routing:
  - My State Regulations (state-scoped safety and labor law questions)
  - Shift and Schedule Help (general questions)
  - Emergency Procedures (general emergencies)

[Add screenshot: Topic triggers]
[Add screenshot: Slot-filling dialog]
[Add screenshot: Action call node]

## 5) Enhance instructions

Goal: Make routing behavior explicit and reduce hallucinations.

- Reconfirm state-specific filtering rules and non-switching behavior.
- Add knowledge source routing hints:
  - Policy docs for procedures and regulations.
  - Safety Issue Log list for issue status.
- Reinforce: do not guess or invent policy details.

[Add screenshot: Updated system prompt]

## 6) Test with demo prompts

Goal: Validate coverage across general, state, list read, and list write.

Use demo prompts from demo_prompts.txt:
- General knowledge: PPE, shift management, emergency procedures.
- State-specific: heat illness, labor law, hazard communication.
- Safety Issue Log read: open issues, severity filters, location views.
- Safety Issue Log write: log a safety issue (slot-filling).

Pass criteria:
- Answers cite the correct source and state scope.
- List reads include issue type, severity, status, date.
- Log Safety Issue collects all five fields and confirms before submit.

[Add screenshot: Test chat results]

## 7) Final review and handoff

Goal: Confirm readiness for the supervised build with the group.

- Verify all knowledge sources are connected.
- Verify LogSafetyIssue action works end-to-end.
- Confirm topics trigger reliably from natural language.
- Prepare a short demo script (5 to 7 minutes) using the prompts.

[Add screenshot: Publish screen]

## Appendix A: Field lists

Safety Issue Log fields:
- ReporterName
- WarehouseLocation: CA-LAX-001, CA-SFO-002, NV-LV-001, NV-RNO-002, AZ-PHX-001, AZ-TUC-002
- IssueType: Equipment, Environmental, Process, Near-Miss, Other
- Description
- Severity: Low, Medium, High, Critical

## Appendix B: References

All referenced files are co-located in this `agent/` directory:

- Copilot Studio Agent Instructions.txt
- Log Safety Issue - Tool Instructions.txt
- demo_prompts.txt
