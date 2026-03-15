# Warehouse Assistant Agent - Prerequisites Setup Guide

Complete these steps before building the Copilot Studio agent. Each section can be done independently, but all must be finished before you start the agent build plan.

## 1) Install Python Dependencies

All scripts share a single requirements file.

- Open a terminal in the project root directory.
- Run: pip install -r scripts/requirements.txt
- This installs python-docx, msal, and requests.
- Requires Python 3.10 or later.

## 2) Azure AD App Registration

Both SharePoint and Dataverse scripts authenticate using MSAL Device Code Flow. You need one app registration that covers both.

1. Sign in to https://portal.azure.com with your tenant admin account.
2. Go to Azure Active Directory, then App registrations, then New registration.
3. Name: Warehouse Demo Script
4. Supported account types: Accounts in this organizational directory only
5. Register, then go to Authentication.
6. Add a platform: Mobile and desktop applications.
7. Redirect URI: https://login.microsoftonline.com/common/oauth2/nativeclient
8. Enable "Allow public client flows" and save.

### Add API Permissions

- SharePoint: Add a permission, then Microsoft APIs, then SharePoint, then Delegated permissions. Add AllSites.Manage.
- Dataverse: Add a permission, then APIs my organization uses, then search Dynamics CRM, then Delegated permissions. Add user_impersonation.
- Click "Grant admin consent" for your tenant after adding both permissions.

### Copy IDs

- From the Overview page, copy the Application (client) ID and Directory (tenant) ID.
- You will paste these into the CONFIG section of each script before running it.

## 3) Create the SharePoint Site

You need a SharePoint site with a document library and a list.

### Option A: Create via SharePoint Admin Center

1. Go to https://admin.microsoft.com and navigate to SharePoint admin center.
2. Create a new Team site or Communication site (e.g., "Retail Warehouse Demo").
3. Note the full site URL (e.g., https://yourtenant.sharepoint.com/sites/RetailWarehouseDemo).

### Option B: Use an Existing Site

- You can use any SharePoint site you have permission to manage. Just note the site URL.

## 4) Upload Policy Documents to SharePoint

The generated Word documents need to be in a SharePoint document library so the Copilot Studio agent can use them as a knowledge source.

### Generate the Documents (if not already done)

- Run: python scripts/generate_docs.py
- This creates 25 .docx files in the output/ folder.

### Upload to SharePoint

1. Open your SharePoint site and navigate to the Documents library (or create a new one).
2. Create the following folder structure in the library:
   - General/
   - States/CA/
   - States/NV/
   - States/AZ/
3. Upload the files from output/ matching each subfolder:
   - output/General/*.docx into the General/ folder
   - output/States/CA/*.docx into States/CA/
   - output/States/NV/*.docx into States/NV/
   - output/States/AZ/*.docx into States/AZ/
4. Verify all 25 documents are uploaded and accessible.

## 5) Create the Safety Issue Log SharePoint List

The Safety Issue Log list stores reported safety issues. The agent reads from this list to answer questions and writes to it when users log new issues.

### Update Script Configuration

1. Open scripts/setup_sharepoint_list.py in a text editor.
2. In the CONFIG section near the top, update:
   - TENANT_ID: your Directory (tenant) ID from the app registration
   - CLIENT_ID: your Application (client) ID from the app registration
   - SITE_URL: your SharePoint site URL (e.g., https://yourtenant.sharepoint.com/sites/RetailWarehouseDemo)
3. Save the file.

### Run the Script

- Run: python scripts/setup_sharepoint_list.py
- The script will display a URL and a device code.
- Open a private/incognito browser window, go to the URL, and enter the code.
- Sign in with your tenant credentials.
- The script will:
  - Create the Safety Issue Log list with all required columns
  - Populate it with realistic sample data
- On success it will print a summary of created columns and sample records.

### Verify

- Open the Safety Issue Log list in SharePoint.
- Confirm the columns exist: DateReported, ReporterName, WarehouseLocation, IssueType, Description, Severity, Status, AssignedTo, ResolutionNotes.
- Confirm sample data rows are present.

## 6) Create the Dataverse PPE Kit Recommendation Table

The PPE Kit Recommendation table in Dataverse is used by the PPE Suggestion child agent to look up role-specific PPE requirements.

### Update Script Configuration

1. Open scripts/setup_dataverse_ppe_table.py in a text editor.
2. In the CONFIG section near the top, update:
   - TENANT_ID: your Directory (tenant) ID
   - CLIENT_ID: your Application (client) ID
   - DATAVERSE_URL: your Dataverse environment URL (find this in the Power Platform admin center under Environments, then your environment, then Environment URL)
   - PUBLISHER_PREFIX: your solution publisher prefix (default is "cr")
3. Save the file.

### Run the Script

- Run: python scripts/setup_dataverse_ppe_table.py
- Authenticate the same way (device code flow in a private browser).
- The script will:
  - Create the PPE Kit Recommendation table with 7 columns
  - Populate it with 20 PPE kit records covering all warehouse roles
- On success it will print a summary of the table and record count.

### Verify

- Open Power Apps (make.powerapps.com) and navigate to Tables.
- Find PPE Kit Recommendation and open it.
- Confirm 20 records are present with data for roles like Dock Worker, Forklift Operator, Cold Storage Associate, etc.

## 7) Checklist

Before starting the agent build:

- Python dependencies installed
- App registration created with SharePoint and Dynamics CRM permissions
- SharePoint site created
- 25 policy documents uploaded to SharePoint document library
- Safety Issue Log list created with sample data
- PPE Kit Recommendation Dataverse table created with 20 records
- You have the SharePoint site URL, document library URL, and list URL handy

Once all items are confirmed, proceed to the Copilot Studio Agent Build Plan (workshop/Copilot Studio Build Plan - Warehouse Assistant Agent.docx).
