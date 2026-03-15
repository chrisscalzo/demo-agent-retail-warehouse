# Copilot Studio Build Plan - Warehouse Assistant Agent

## Overview

This document walks through building the Warehouse Assistant agent in Microsoft Copilot Studio from start to finish. Complete the Prerequisites Setup Guide before starting here.

The Warehouse Assistant helps retail warehouse workers (team members, supervisors, managers) at Contoso Retail with:

- General policy and procedure questions (shift management, onboarding, code of conduct)
- State-specific safety and labor law content for California, Nevada, and Arizona
- Querying the Safety Issue Log (SharePoint list) using natural language
- Logging new safety issues through guided conversation
- PPE kit recommendations by job role (via a child agent backed by Dataverse)

## Before You Begin

Confirm all prerequisites are complete:

- 25 policy documents uploaded to a SharePoint document library (General, States/CA, States/NV, States/AZ folders)
- Safety Issue Log SharePoint list created with sample data
- PPE Kit Recommendation Dataverse table created with 20 records
- Reference files ready in the agent/ folder of this repo

## Step 1: Create the Agent

Goal: Stand up the Warehouse Assistant shell and apply baseline instructions.

1. Open Copilot Studio and create a new agent.
2. Name it Warehouse Assistant.
3. Open the agent instructions pane.
4. Paste the full contents of agent/Copilot Studio Agent Instructions.txt as the system instructions.
5. Set the tone to concise and direct (this agent serves a warehouse floor audience).
6. Save and open the test chat to confirm the agent responds.

[Add screenshot: Agent creation screen]

[Add screenshot: Instructions pane with system prompt]

## Step 2: Connect Knowledge Sources

Goal: Give the agent access to policy documents and the Safety Issue Log.

### SharePoint Document Library

1. Go to Knowledge Sources and add a new SharePoint source.
2. Point it to the document library containing the uploaded policy docs.
3. Include all folders: General, States/CA, States/NV, States/AZ.

### Safety Issue Log List

1. Add the Safety Issue Log SharePoint list as a second knowledge source.
2. This allows the agent to answer natural-language queries about open issues, severity, location, etc.

### Validate

- Ask a general question (e.g., "What is the PPE policy?") and confirm the answer comes from the General folder.
- Ask a state-specific question (e.g., "What are the heat illness rules in California?") and confirm the answer cites a CA document.

[Add screenshot: Knowledge sources list]

[Add screenshot: SharePoint document library mapping]

## Step 3: Create Tools (Actions)

Goal: Enable the agent to write new items to the Safety Issue Log.

1. Create a new tool action that creates a list item in the Safety Issue Log SharePoint list.
2. Name the action LogSafetyIssue.
3. In the action description, paste the contents of agent/Log Safety Issue - Tool Instructions.txt.
4. Map the following input fields:
   - ReporterName (text)
   - WarehouseLocation (choice: CA-LAX-001, CA-SFO-002, NV-LV-001, NV-RNO-002, AZ-PHX-001, AZ-TUC-002)
   - IssueType (choice: Equipment, Environmental, Process, Near-Miss, Other)
   - Description (text)
   - Severity (choice: Low, Medium, High, Critical)
5. Test the action with sample data and confirm a new row appears in the SharePoint list.

[Add screenshot: Action definition]

[Add screenshot: Field mapping]

## Step 4: Create and Modify Topics

Goal: Add intent routing and slot-filling for safety issue logging.

### Log Safety Issue Topic

1. Create a new topic named Log Safety Issue.
2. Add trigger phrases: "log a safety issue", "report a safety concern", "near-miss", "incident report".
3. Add question nodes to collect required fields in order:
   - Reporter name (open text)
   - Warehouse location (choice list)
   - Issue type (choice list)
   - Description (open text)
   - Severity (choice list)
4. Add a confirmation message summarizing the collected details.
5. Call the LogSafetyIssue action with the collected values.
6. Add a closing message acknowledging the submission and advising that a supervisor will follow up.

### Policy Routing Topics (Optional)

These are optional if generative orchestration handles routing well on its own:

- My State Regulations: routes state-scoped safety and labor law questions
- Shift and Schedule Help: routes general shift management queries
- Emergency Procedures: routes emergency-related questions

[Add screenshot: Topic triggers]

[Add screenshot: Slot-filling dialog]

[Add screenshot: Action call node]

## Step 5: Configure the PPE Suggestion Child Agent

Goal: Add a child agent that answers role-based PPE questions using the Dataverse table.

1. In Copilot Studio, create a new child agent named PPE Suggestion Agent.
2. Paste the contents of agent/PPE Suggestion Agent Instructions.txt as the system instructions.
3. Connect the Dataverse MCP Server or add a Dataverse action that queries the PPE Kit Recommendation table.
4. Configure the parent (Warehouse Assistant) to delegate role-based PPE questions to this child agent.
5. The parent agent instructions already include delegation rules; confirm they match.

### Validate Delegation

- "What PPE does a forklift operator need?" should route to the child agent and return Dataverse data.
- "What PPE is required in Zone A?" should stay with the parent and answer from documents.
- "How do I get reimbursed for safety boots?" should stay with the parent and answer from documents.

[Add screenshot: Child agent configuration]

## Step 6: Enhance Instructions

Goal: Fine-tune routing behavior and reduce hallucinations.

1. Review the system instructions and confirm state-specific filtering rules are clear.
2. Add knowledge source routing hints if needed:
   - Policy docs for procedures and regulations.
   - Safety Issue Log list for issue status queries.
   - PPE Kit Recommendation table (via child agent) for role-based PPE.
3. Reinforce: the agent must not guess or invent policy details.

[Add screenshot: Updated system prompt]

## Step 7: Test with Demo Prompts

Goal: Validate coverage across all capabilities.

Open agent/demo_prompts.txt and work through each section:

- Section 1 - General knowledge: PPE, shift management, emergency procedures
- Section 2 - State-specific: heat illness, labor law, hazard communication
- Section 3 - Cross-state comparison questions
- Section 4 - Safety Issue Log reads: open issues, severity filters, location views
- Section 5 - Safety Issue Log writes: log a safety issue (slot-filling flow)
- Section 6 - Role and audience scoping
- Section 7 - Edge cases and guardrails
- Section 8 - PPE Suggestion Agent prompts

### Pass Criteria

- Answers cite the correct source document and respect state scope.
- List read queries include issue type, severity, status, and date.
- Log Safety Issue flow collects all five fields and confirms before submitting.
- PPE queries for specific roles return data from Dataverse (not from documents).
- The agent declines to answer questions outside its scope.

[Add screenshot: Test chat results]

## Step 8: Publish and Review

Goal: Confirm the agent is ready for use.

1. Verify all knowledge sources are connected and returning results.
2. Verify the LogSafetyIssue action works end-to-end.
3. Confirm topics trigger reliably from natural language.
4. Confirm the PPE child agent delegation works correctly.
5. Publish the agent.
6. Test in the published channel to confirm behavior matches the test chat.

[Add screenshot: Publish screen]

## Appendix A: Safety Issue Log Fields

- ReporterName: Full name of the person reporting
- WarehouseLocation: CA-LAX-001 Los Angeles, CA-SFO-002 Fresno, NV-LV-001 Las Vegas, NV-RNO-002 Reno, AZ-PHX-001 Phoenix, AZ-TUC-002 Tucson
- IssueType: Equipment, Environmental, Process, Near-Miss, Other
- Description: Free text
- Severity: Low, Medium, High, Critical

## Appendix B: Reference Files

All located in the agent/ directory of this repo:

- Copilot Studio Agent Instructions.txt: Parent agent system instructions
- PPE Suggestion Agent Instructions.txt: Child agent system instructions
- Log Safety Issue - Tool Instructions.txt: LogSafetyIssue action description
- demo_prompts.txt: 8 sections of test prompts
