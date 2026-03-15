#!/usr/bin/env python3
"""
setup_sharepoint_list.py

Creates the "Safety Issue Log" SharePoint list with all columns and populates
it with realistic sample data for the Retail Warehouse Copilot Studio Demo.

Authentication: MSAL Device Code Flow
  - The script will print a URL and a code.
  - Open a PRIVATE / INCOGNITO browser window and go to the URL.
  - Enter the code and sign in with your demo tenant credentials.
  - The script resumes automatically once authenticated.
  - Credentials are cached in .token_cache.json so you won't be prompted again
    on subsequent runs (delete that file to force re-login).

Prerequisites:
  pip install msal requests

One-time App Registration (~2 minutes):
  1. Go to https://portal.azure.com (sign in with your demo tenant admin)
  2. Azure Active Directory -> App registrations -> New registration
       Name: Warehouse Demo Script
       Supported account types: Accounts in this organizational directory only
  3. Authentication -> Add a platform -> Mobile and desktop applications
       Redirect URI: https://login.microsoftonline.com/common/oauth2/nativeclient
       Enable: "Allow public client flows" -> Yes -> Save
  4. API permissions -> Add a permission -> SharePoint -> Delegated permissions
       Add: AllSites.Manage -> click "Grant admin consent for <tenant>" -> Yes
  5. Overview page -> copy "Application (client) ID" and "Directory (tenant) ID"
  6. Paste both values into the CONFIG section below and save.

Usage:
  python setup_sharepoint_list.py
"""

import json
import os
import sys
import random
from datetime import datetime, timedelta

import msal
import requests

# ── CONFIG ─────────────────────────────────────────────────────────────────────
TENANT_ID  = "2540c676-79f2-4c66-894b-0a60644507f0"   # Directory (tenant) ID from Azure AD
CLIENT_ID  = "165ce690-4aaf-4433-8d8e-205a5cb1f402"   # Application (client) ID from Azure AD
SITE_URL   = "https://m365x17959284.sharepoint.com/sites/RetailWarehouseDemo"
LIST_NAME  = "Safety Issue Log"
TOKEN_CACHE_FILE = ".token_cache.json"
# ───────────────────────────────────────────────────────────────────────────────

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SP_HOST   = SITE_URL.split("/sites/")[0]   # e.g. https://m365x17959284.sharepoint.com
SCOPES    = [f"{SP_HOST}/AllSites.Manage"]


# ── AUTHENTICATION ─────────────────────────────────────────────────────────────

def load_token_cache():
    cache = msal.SerializableTokenCache()
    if os.path.exists(TOKEN_CACHE_FILE):
        with open(TOKEN_CACHE_FILE) as f:
            cache.deserialize(f.read())
    return cache


def save_token_cache(cache):
    if cache.has_state_changed:
        with open(TOKEN_CACHE_FILE, "w") as f:
            f.write(cache.serialize())


def get_access_token():
    cache = load_token_cache()
    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)

    # Try silent (cached) first
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            save_token_cache(cache)
            print("  Using cached credentials (delete .token_cache.json to force re-login).")
            return result["access_token"]

    # Device code flow
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        raise RuntimeError(f"Failed to create device flow:\n{json.dumps(flow, indent=2)}")

    print()
    print("=" * 62)
    print("  ACTION REQUIRED")
    print("  Open a PRIVATE / INCOGNITO browser window and:")
    print(f"    1. Navigate to:  {flow['verification_uri']}")
    print(f"    2. Enter code:   {flow['user_code']}")
    print()
    print("  Sign in with your demo tenant credentials.")
    print("  This window will continue automatically once authenticated.")
    print("=" * 62)
    print()

    result = app.acquire_token_by_device_flow(flow)
    if "access_token" not in result:
        raise RuntimeError(
            f"Authentication failed: {result.get('error_description', result)}"
        )

    save_token_cache(cache)
    print("  Authentication successful.")
    return result["access_token"]


def make_session(token):
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Bearer {token}",
        "Accept": "application/json;odata=verbose",
        "Content-Type": "application/json;odata=verbose",
    })
    return s


# ── SHAREPOINT HELPERS ─────────────────────────────────────────────────────────

def get_form_digest(session):
    """Request digest value required for SharePoint write operations."""
    r = session.post(f"{SITE_URL}/_api/contextinfo")
    r.raise_for_status()
    return r.json()["d"]["GetContextWebInformation"]["FormDigestValue"]


def list_exists(session):
    r = session.get(f"{SITE_URL}/_api/web/lists/getbytitle('{LIST_NAME}')")
    return r.status_code == 200


def get_list_entity_type(session):
    """Returns the OData entity type name for list items (needed for POST payloads)."""
    r = session.get(
        f"{SITE_URL}/_api/web/lists/getbytitle('{LIST_NAME}')"
        "?$select=ListItemEntityTypeFullName"
    )
    r.raise_for_status()
    return r.json()["d"]["ListItemEntityTypeFullName"]


def create_list(session, digest):
    payload = {
        "__metadata": {"type": "SP.List"},
        "BaseTemplate": 100,
        "Title": LIST_NAME,
        "Description": (
            "Safety issue and near-miss log for Contoso Retail warehouse locations. "
            "Used by the Warehouse Assistant Copilot Studio agent."
        ),
    }
    r = session.post(
        f"{SITE_URL}/_api/web/lists",
        json=payload,
        headers={"X-RequestDigest": digest},
    )
    r.raise_for_status()


def add_field(session, digest, field_def):
    field_name = field_def.get("Title", "unknown")
    r = session.post(
        f"{SITE_URL}/_api/web/lists/getbytitle('{LIST_NAME}')/fields",
        json=field_def,
        headers={"X-RequestDigest": digest},
    )
    if r.status_code not in (200, 201):
        print(f"    [WARN] Could not add '{field_name}': {r.status_code} — {r.text[:120]}")
        return False
    return True


def add_field_to_view(session, digest, field_name):
    r = session.post(
        f"{SITE_URL}/_api/web/lists/getbytitle('{LIST_NAME}')"
        f"/defaultview/viewfields/addviewfield('{field_name}')",
        headers={"X-RequestDigest": digest},
    )
    return r.status_code in (200, 204)


def create_schema(session, digest):
    """Create all custom columns for the Safety Issue Log."""

    CHOICE = "SP.FieldChoice"
    TEXT   = "SP.FieldText"
    NOTE   = "SP.FieldMultiLineText"
    DATE   = "SP.FieldDateTime"

    def choices(values):
        return {
            "__metadata": {"type": "Collection(Edm.String)"},
            "results": values,
        }

    fields = [
        {
            "__metadata": {"type": DATE},
            "FieldTypeKind": 4,
            "Title": "DateReported",
            "DisplayFormat": 0,          # date only
        },
        {
            "__metadata": {"type": TEXT},
            "FieldTypeKind": 2,
            "Title": "ReporterName",
            "MaxLength": 255,
        },
        {
            "__metadata": {"type": CHOICE},
            "FieldTypeKind": 6,
            "Title": "WarehouseLocation",
            "EditFormat": 0,             # dropdown
            "Choices": choices([
                "CA-LAX-001 Los Angeles",
                "CA-SFO-002 Fresno",
                "NV-LV-001 Las Vegas",
                "NV-RNO-002 Reno",
                "AZ-PHX-001 Phoenix",
                "AZ-TUC-002 Tucson",
            ]),
        },
        {
            "__metadata": {"type": CHOICE},
            "FieldTypeKind": 6,
            "Title": "IssueType",
            "EditFormat": 0,
            "Choices": choices(["Equipment", "Environmental", "Process", "Near-Miss", "Other"]),
        },
        {
            "__metadata": {"type": NOTE},
            "FieldTypeKind": 3,
            "Title": "Description",
            "NumberOfLines": 6,
            "RichText": False,
        },
        {
            "__metadata": {"type": CHOICE},
            "FieldTypeKind": 6,
            "Title": "Severity",
            "EditFormat": 0,
            "Choices": choices(["Low", "Medium", "High", "Critical"]),
        },
        {
            "__metadata": {"type": CHOICE},
            "FieldTypeKind": 6,
            "Title": "Status",
            "EditFormat": 0,
            "DefaultValue": "Open",
            "Choices": choices(["Open", "In Progress", "Resolved"]),
        },
        # AssignedTo is a Person field (FieldTypeKind 20) and requires knowing
        # the user's SharePoint ID. Add it manually in the SharePoint list settings
        # after running this script if needed.
        {
            "__metadata": {"type": NOTE},
            "FieldTypeKind": 3,
            "Title": "ResolutionNotes",
            "NumberOfLines": 6,
            "RichText": False,
        },
    ]

    added = []
    for field in fields:
        name = field["Title"]
        print(f"    Adding column: {name} ...", end=" ", flush=True)
        ok = add_field(session, digest, field)
        if ok:
            add_field_to_view(session, digest, name)
            added.append(name)
            print("OK")
        else:
            print("skipped")

    return added


# ── SAMPLE DATA ────────────────────────────────────────────────────────────────

REPORTERS = [
    "Maria Garcia", "James Thompson", "Priya Patel", "Derek Williams",
    "Sarah Kim", "Luis Hernandez", "Keisha Johnson", "Tom Nguyen",
    "Amanda Foster", "Carlos Reyes", "Nadia Okafor", "Brian Mitchell",
]

LOCATIONS = [
    "CA-LAX-001 Los Angeles",
    "CA-SFO-002 Fresno",
    "NV-LV-001 Las Vegas",
    "NV-RNO-002 Reno",
    "AZ-PHX-001 Phoenix",
    "AZ-TUC-002 Tucson",
]

ISSUES = [
    {
        "IssueType": "Equipment", "Severity": "High",
        "Description": (
            "Dock leveler at Bay 3 is not locking into the raised position. "
            "Leveler dropped unexpectedly while a team member was positioned on it. "
            "No injuries, but this is a near-miss situation. Bay 3 has been coned off pending repair."
        ),
    },
    {
        "IssueType": "Environmental", "Severity": "Medium",
        "Description": (
            "Unmarked liquid spill (approximately 4x6 ft) on the main aisle between receiving "
            "and storage Zone B. Surface is slippery. Wet floor signs placed but full cleanup not yet complete."
        ),
    },
    {
        "IssueType": "Near-Miss", "Severity": "Critical",
        "Description": (
            "Forklift operator nearly struck a pedestrian team member in the crossover aisle near "
            "the charging station. Pedestrian was not wearing hi-vis vest. Operator braked in time — "
            "no contact made. Both employees interviewed."
        ),
    },
    {
        "IssueType": "Equipment", "Severity": "Low",
        "Description": (
            "Pallet jack PJ-07 has a slow air leak in the front wheel. Not an imminent safety risk "
            "but reducing maneuverability. Reported to maintenance for scheduling."
        ),
    },
    {
        "IssueType": "Process", "Severity": "Medium",
        "Description": (
            "Team members observed stacking pallets above the marked 8-foot height limit in Zone D. "
            "Overstacked pallets pose falling risk. Supervisor retrained team and restacked to compliant height."
        ),
    },
    {
        "IssueType": "Environmental", "Severity": "High",
        "Description": (
            "Ambient temperature in Zone C reached 97 degrees F during afternoon shift. Heat illness "
            "prevention plan activated — mandatory cool-down breaks every 30 minutes, water station "
            "replenished. Three team members reported dizziness; two monitored by first aid."
        ),
    },
    {
        "IssueType": "Equipment", "Severity": "Critical",
        "Description": (
            "Conveyor belt CB-02 emergency stop button unresponsive during monthly safety test. "
            "Belt was immediately locked out per LOTO procedure. Maintenance called for urgent repair. "
            "Belt out of service until independently certified."
        ),
    },
    {
        "IssueType": "Near-Miss", "Severity": "High",
        "Description": (
            "Unsecured load on a high-bay rack began shifting during replenishment operation. "
            "Team member noticed movement and moved clear before partial collapse. "
            "Two pallets fell to floor. Area cordoned off; rack inspection ordered."
        ),
    },
    {
        "IssueType": "Process", "Severity": "Low",
        "Description": (
            "New temporary worker observed operating a manual pallet jack without completing "
            "required equipment orientation. Worker directed to stop immediately. "
            "Training scheduled for next morning before return to duties."
        ),
    },
    {
        "IssueType": "Equipment", "Severity": "Medium",
        "Description": (
            "Forklift FL-04 seatbelt latch is worn and intermittently fails to engage. "
            "Unit tagged out of service and submitted to maintenance. Replacement latch on order; "
            "ETA 2 business days."
        ),
    },
    {
        "IssueType": "Environmental", "Severity": "Medium",
        "Description": (
            "Overhead light fixture in Aisle 7 is flickering and partially failed, creating "
            "reduced-visibility conditions. Temporary portable lighting added. "
            "Facilities ticket submitted for repair."
        ),
    },
    {
        "IssueType": "Process", "Severity": "High",
        "Description": (
            "LOTO (lockout/tagout) procedure not fully followed during conveyor belt maintenance — "
            "energy source was not completely locked out before technician began work. No injury occurred. "
            "Work stopped immediately; mandatory LOTO retraining conducted for all maintenance staff."
        ),
    },
    {
        "IssueType": "Near-Miss", "Severity": "Medium",
        "Description": (
            "Cardboard box fell from shelf at approximately 6 feet and narrowly missed a passing "
            "team member. Box had been improperly placed at shelf edge. Team member uninjured. "
            "Full shelf audit completed for that aisle."
        ),
    },
    {
        "IssueType": "Equipment", "Severity": "Low",
        "Description": (
            "Safety mirror at blind corner intersection of Aisles 3 and 5 is cracked, "
            "providing a distorted field of view. Replacement mirror requested from facilities. "
            "Additional spotter stationed at intersection during peak hours as interim measure."
        ),
    },
    {
        "IssueType": "Environmental", "Severity": "Low",
        "Description": (
            "Minor oil drip from Forklift FL-02 engine noticed on floor of charging area. "
            "Absorbent pads placed. Maintenance scheduled to inspect and repair seal. "
            "No slip hazard at current drip rate."
        ),
    },
    {
        "IssueType": "Process", "Severity": "Medium",
        "Description": (
            "Two team members found working in the dock area without required steel-toe footwear. "
            "Both were sent to retrieve proper PPE before returning to duties. "
            "PPE compliance spot-check audit scheduled for next week."
        ),
    },
    {
        "IssueType": "Near-Miss", "Severity": "High",
        "Description": (
            "Reverse alarm on Forklift FL-06 found disabled during pre-shift inspection. "
            "Near-miss had occurred on prior shift when FL-06 reversed without audible warning "
            "in a busy pedestrian area. Unit taken out of service; alarm repaired same day."
        ),
    },
    {
        "IssueType": "Equipment", "Severity": "Medium",
        "Description": (
            "Fire extinguisher at Station 4B is 18 months past its last annual inspection date. "
            "Flagged during monthly safety walk. Inspection company contacted for priority visit."
        ),
    },
    {
        "IssueType": "Environmental", "Severity": "Critical",
        "Description": (
            "Ammonia odor detected near refrigeration unit in cold storage corridor. "
            "Two team members evacuated with eye and throat irritation. Partial facility evacuation "
            "initiated. Hazmat team called. Refrigeration contractor on site within 2 hours; "
            "minor line leak identified and repaired."
        ),
    },
    {
        "IssueType": "Process", "Severity": "Low",
        "Description": (
            "Aisle floor markings throughout Zone A are significantly faded and difficult to distinguish "
            "under current lighting. Risk of vehicles and pedestrians inadvertently sharing lanes. "
            "Repainting scheduled for upcoming weekend maintenance window."
        ),
    },
]

RESOLUTION_NOTES = [
    "Maintenance completed repair. Unit tested and certified operational. Area reopened.",
    "Spill fully cleaned and neutralized. Surface confirmed non-slip. Signs removed.",
    "Both employees counseled. Mandatory refresher training completed. Camera coverage extended to cover area.",
    "Equipment serviced and returned to fleet. Confirmed safe for operation.",
    "Team briefed at huddle. Supervisor implementing weekly compliance spot-checks.",
    "HVAC inspection completed. Additional ventilation installed. Heat illness plan updated.",
    "Repair completed and independently certified. Returned to service after full safety test.",
    "Racking system inspected by certified vendor. Two beam connectors replaced. Load limits re-labeled.",
    "Worker completed required orientation. Signed acknowledgment on file. Cleared to operate.",
    "Part replaced. Unit returned to service following maintenance sign-off.",
    "Electrical repair completed. Normal lighting restored. Portable units removed.",
    "Root cause analysis completed. LOTO procedure updated and re-posted. All staff re-certified.",
]


def build_sample_items(count=20):
    random.seed(42)   # reproducible output
    today = datetime.utcnow()
    pool = ISSUES.copy()
    random.shuffle(pool)
    items = []

    for i in range(count):
        issue = pool[i % len(pool)]
        days_ago = random.randint(1, 90)
        date_str = (today - timedelta(days=days_ago)).strftime("%Y-%m-%dT00:00:00Z")

        # Older issues trend toward resolved; newer ones trend open
        if days_ago > 60:
            status = random.choices(["Resolved", "In Progress", "Open"], weights=[60, 30, 10])[0]
        elif days_ago > 25:
            status = random.choices(["Resolved", "In Progress", "Open"], weights=[30, 40, 30])[0]
        else:
            status = random.choices(["Resolved", "In Progress", "Open"], weights=[10, 30, 60])[0]

        resolution = random.choice(RESOLUTION_NOTES) if status == "Resolved" else ""

        items.append({
            "DateReported":      date_str,
            "ReporterName":      random.choice(REPORTERS),
            "WarehouseLocation": random.choice(LOCATIONS),
            "IssueType":         issue["IssueType"],
            "Description":       issue["Description"],
            "Severity":          issue["Severity"],
            "Status":            status,
            "ResolutionNotes":   resolution,
        })

    return items


def add_item(session, digest, entity_type, item):
    payload = {"__metadata": {"type": entity_type}, **item}
    r = session.post(
        f"{SITE_URL}/_api/web/lists/getbytitle('{LIST_NAME}')/items",
        json=payload,
        headers={"X-RequestDigest": digest},
    )
    if r.status_code not in (200, 201):
        raise RuntimeError(
            f"Failed to add item (HTTP {r.status_code}): {r.text[:300]}"
        )
    return r.json()["d"]["Id"]


# ── MAIN ───────────────────────────────────────────────────────────────────────

def main():
    print()
    print("=" * 62)
    print("  Contoso Retail — Safety Issue Log Setup")
    print(f"  Site: {SITE_URL}")
    print("=" * 62)

    if "YOUR_TENANT_ID" in TENANT_ID or "YOUR_CLIENT_ID" in CLIENT_ID:
        print()
        print("ERROR: TENANT_ID and CLIENT_ID are not configured.")
        print("  Edit the CONFIG section at the top of this script.")
        print("  See the docstring at the top for app registration steps.")
        print()
        sys.exit(1)

    # 1. Authenticate
    print("\n[1/4] Authenticating ...")
    token = get_access_token()
    session = make_session(token)

    # 2. Connect
    print("\n[2/4] Connecting to SharePoint ...")
    digest = get_form_digest(session)
    print("  Connected.")

    # 3. Create list + schema
    print(f"\n[3/4] Setting up list: '{LIST_NAME}' ...")
    if list_exists(session):
        print(f"  List already exists — skipping creation and schema.")
        print("  (Delete the list in SharePoint and re-run to recreate it.)")
    else:
        create_list(session, digest)
        print("  List created.")
        print("  Adding columns ...")
        cols = create_schema(session, digest)
        print(f"  {len(cols)} columns added: {', '.join(cols)}")
        print()
        print("  NOTE: The 'AssignedTo' Person column must be added manually")
        print("  in the SharePoint list settings (List settings -> Create column).")

    # 4. Populate sample data
    print(f"\n[4/4] Adding sample records ...")
    items = build_sample_items(20)

    # Refresh digest before writes (avoids expiry on slow connections)
    digest = get_form_digest(session)
    entity_type = get_list_entity_type(session)

    for idx, item in enumerate(items, 1):
        item_id = add_item(session, digest, entity_type, item)
        loc = item["WarehouseLocation"][:22]
        print(
            f"  [{idx:02d}/20] #{item_id:>3}  "
            f"{item['Severity']:<8}  {item['IssueType']:<14}  "
            f"{item['Status']:<11}  {loc}"
        )

    print()
    print(f"Done. {len(items)} records added to '{LIST_NAME}'.")
    print(
        f"View list: {SITE_URL}/Lists/"
        + LIST_NAME.replace(" ", "%20")
        + "/AllItems.aspx"
    )
    print()


if __name__ == "__main__":
    main()
