#!/usr/bin/env python3
"""
setup_dataverse_ppe_table.py

Creates the "PPE Kit Recommendation" Dataverse table with all columns and
populates it with 20 realistic PPE kit records for the Retail Warehouse
Copilot Studio Demo.

Authentication: MSAL Device Code Flow
  - The script will print a URL and a code.
  - Open a PRIVATE / INCOGNITO browser window and go to the URL.
  - Enter the code and sign in with your demo tenant credentials.
  - The script resumes automatically once authenticated.
  - Credentials are cached in .token_cache_dataverse.json so you won't be
    prompted again on subsequent runs (delete that file to force re-login).

Prerequisites:
  pip install msal requests

  Azure AD App Registration must have:
    API permissions > Dynamics CRM > Delegated > user_impersonation
    (Grant admin consent after adding)

Usage:
  python setup_dataverse_ppe_table.py
"""

import json
import os
import sys
import time

import msal
import requests

# ── CONFIG ─────────────────────────────────────────────────────────────────────
TENANT_ID  = "2540c676-79f2-4c66-894b-0a60644507f0"   # Directory (tenant) ID
CLIENT_ID  = "165ce690-4aaf-4433-8d8e-205a5cb1f402"   # Application (client) ID
DATAVERSE_URL    = "https://orgc1a3d9f4.crm.dynamics.com"
PUBLISHER_PREFIX = "cr"        # matches your solution publisher
TABLE_SCHEMA_NAME   = f"{PUBLISHER_PREFIX}_PPEKitRecommendation"
TABLE_LOGICAL_NAME  = TABLE_SCHEMA_NAME.lower()        # cr_ppekitrecommendation
TABLE_DISPLAY_NAME  = "PPE Kit Recommendation"
TABLE_PLURAL_NAME   = "PPE Kit Recommendations"
TABLE_SET_NAME      = f"{PUBLISHER_PREFIX}_ppekitrecommendations"  # entity set name
TOKEN_CACHE_FILE    = ".token_cache_dataverse.json"
# ───────────────────────────────────────────────────────────────────────────────

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES    = [f"{DATAVERSE_URL}/.default"]
API_BASE  = f"{DATAVERSE_URL}/api/data/v9.2"


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
            print("  Using cached credentials (delete .token_cache_dataverse.json to force re-login).")
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
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Prefer": "return=representation",
    })
    return s


# ── DATAVERSE HELPERS ──────────────────────────────────────────────────────────

def whoami(session):
    """Verify Dataverse connection via WhoAmI()."""
    r = session.get(f"{API_BASE}/WhoAmI()")
    r.raise_for_status()
    data = r.json()
    return data.get("UserId", "unknown")


def table_exists(session):
    """Check if the table already exists."""
    r = session.get(
        f"{API_BASE}/EntityDefinitions"
        f"?$filter=LogicalName eq '{TABLE_LOGICAL_NAME}'"
        f"&$select=LogicalName"
    )
    r.raise_for_status()
    return len(r.json().get("value", [])) > 0


def create_table(session):
    """Create the PPE Kit Recommendation table."""
    payload = {
        "@odata.type": "Microsoft.Dynamics.CRM.EntityMetadata",
        "SchemaName": TABLE_SCHEMA_NAME,
        "DisplayName": {
            "@odata.type": "Microsoft.Dynamics.CRM.Label",
            "LocalizedLabels": [{
                "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                "Label": TABLE_DISPLAY_NAME,
                "LanguageCode": 1033,
            }],
        },
        "DisplayCollectionName": {
            "@odata.type": "Microsoft.Dynamics.CRM.Label",
            "LocalizedLabels": [{
                "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                "Label": TABLE_PLURAL_NAME,
                "LanguageCode": 1033,
            }],
        },
        "Description": {
            "@odata.type": "Microsoft.Dynamics.CRM.Label",
            "LocalizedLabels": [{
                "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                "Label": "Role-based PPE kit recommendations for Contoso Retail warehouse workers. Used by the PPE Suggestion Agent.",
                "LanguageCode": 1033,
            }],
        },
        "OwnershipType": "UserOwned",
        "HasNotes": False,
        "HasActivities": False,
        "IsActivity": False,
        "PrimaryNameAttribute": f"{PUBLISHER_PREFIX}_ppekitname",
        "Attributes": [
            {
                "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
                "SchemaName": f"{PUBLISHER_PREFIX}_PPEKitName",
                "AttributeType": "String",
                "FormatName": {"Value": "Text"},
                "MaxLength": 200,
                "DisplayName": {
                    "@odata.type": "Microsoft.Dynamics.CRM.Label",
                    "LocalizedLabels": [{
                        "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                        "Label": "PPE Kit Name",
                        "LanguageCode": 1033,
                    }],
                },
                "Description": {
                    "@odata.type": "Microsoft.Dynamics.CRM.Label",
                    "LocalizedLabels": [{
                        "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                        "Label": "Primary name column — e.g., Dock Worker Kit",
                        "LanguageCode": 1033,
                    }],
                },
                "IsPrimaryName": True,
                "RequiredLevel": {"Value": "ApplicationRequired"},
            },
        ],
    }
    r = session.post(f"{API_BASE}/EntityDefinitions", json=payload)
    if r.status_code not in (200, 201, 204):
        raise RuntimeError(
            f"Failed to create table (HTTP {r.status_code}): {r.text[:500]}"
        )
    print(f"  Table '{TABLE_DISPLAY_NAME}' created.")


def add_string_column(session, schema_name, display_name, max_length=200, description=""):
    """Add a single-line text column."""
    payload = {
        "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
        "SchemaName": schema_name,
        "AttributeType": "String",
        "FormatName": {"Value": "Text"},
        "MaxLength": max_length,
        "DisplayName": {
            "@odata.type": "Microsoft.Dynamics.CRM.Label",
            "LocalizedLabels": [{
                "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                "Label": display_name,
                "LanguageCode": 1033,
            }],
        },
        "Description": {
            "@odata.type": "Microsoft.Dynamics.CRM.Label",
            "LocalizedLabels": [{
                "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                "Label": description,
                "LanguageCode": 1033,
            }],
        },
        "RequiredLevel": {"Value": "None"},
    }
    r = session.post(
        f"{API_BASE}/EntityDefinitions(LogicalName='{TABLE_LOGICAL_NAME}')/Attributes",
        json=payload,
    )
    if r.status_code not in (200, 201, 204):
        print(f"    [WARN] Could not add '{display_name}': {r.status_code} — {r.text[:200]}")
        return False
    return True


def add_memo_column(session, schema_name, display_name, max_length=2000, description=""):
    """Add a multi-line text (memo) column."""
    payload = {
        "@odata.type": "Microsoft.Dynamics.CRM.MemoAttributeMetadata",
        "SchemaName": schema_name,
        "AttributeType": "Memo",
        "FormatName": {"Value": "Text"},
        "MaxLength": max_length,
        "DisplayName": {
            "@odata.type": "Microsoft.Dynamics.CRM.Label",
            "LocalizedLabels": [{
                "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                "Label": display_name,
                "LanguageCode": 1033,
            }],
        },
        "Description": {
            "@odata.type": "Microsoft.Dynamics.CRM.Label",
            "LocalizedLabels": [{
                "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                "Label": description,
                "LanguageCode": 1033,
            }],
        },
        "RequiredLevel": {"Value": "None"},
    }
    r = session.post(
        f"{API_BASE}/EntityDefinitions(LogicalName='{TABLE_LOGICAL_NAME}')/Attributes",
        json=payload,
    )
    if r.status_code not in (200, 201, 204):
        print(f"    [WARN] Could not add '{display_name}': {r.status_code} — {r.text[:200]}")
        return False
    return True


def add_picklist_column(session, schema_name, display_name, options, description=""):
    """Add a choice (picklist) column with the given options."""
    option_items = []
    for i, label in enumerate(options):
        option_items.append({
            "Value": (i + 1) * 100000,   # 100000, 200000, 300000, ...
            "Label": {
                "@odata.type": "Microsoft.Dynamics.CRM.Label",
                "LocalizedLabels": [{
                    "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                    "Label": label,
                    "LanguageCode": 1033,
                }],
            },
        })
    payload = {
        "@odata.type": "Microsoft.Dynamics.CRM.PicklistAttributeMetadata",
        "SchemaName": schema_name,
        "AttributeType": "Picklist",
        "DisplayName": {
            "@odata.type": "Microsoft.Dynamics.CRM.Label",
            "LocalizedLabels": [{
                "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                "Label": display_name,
                "LanguageCode": 1033,
            }],
        },
        "Description": {
            "@odata.type": "Microsoft.Dynamics.CRM.Label",
            "LocalizedLabels": [{
                "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                "Label": description,
                "LanguageCode": 1033,
            }],
        },
        "RequiredLevel": {"Value": "None"},
        "OptionSet": {
            "@odata.type": "Microsoft.Dynamics.CRM.OptionSetMetadata",
            "IsGlobal": False,
            "OptionSetType": "Picklist",
            "Options": option_items,
        },
    }
    r = session.post(
        f"{API_BASE}/EntityDefinitions(LogicalName='{TABLE_LOGICAL_NAME}')/Attributes",
        json=payload,
    )
    if r.status_code not in (200, 201, 204):
        print(f"    [WARN] Could not add '{display_name}': {r.status_code} — {r.text[:200]}")
        return False
    return True


def create_columns(session):
    """Add all custom columns beyond the primary name column."""
    columns = [
        ("string", f"{PUBLISHER_PREFIX}_JobRole",     "Job Role",      200, "e.g., Dock Worker, Forklift Operator"),
        ("picklist", f"{PUBLISHER_PREFIX}_Department", "Department",    None, "Warehouse department"),
        ("memo",   f"{PUBLISHER_PREFIX}_RequiredPPE",  "Required PPE",  2000, "Mandatory PPE items with standards and specifications"),
        ("memo",   f"{PUBLISHER_PREFIX}_OptionalPPE",  "Optional PPE",  2000, "Recommended PPE items with conditions"),
        ("picklist", f"{PUBLISHER_PREFIX}_HazardLevel", "Hazard Level", None, "Low, Medium, or High"),
        ("memo",   f"{PUBLISHER_PREFIX}_Notes",        "Notes",         2000, "Zone assignments, certifications, safety warnings"),
    ]

    department_options = [
        "Receiving", "Staging", "Storage", "Pick & Pack",
        "Shipping", "Maintenance", "Management",
    ]
    hazard_options = ["Low", "Medium", "High"]

    added = []
    for col in columns:
        col_type, schema, display, size_or_none, desc = col
        print(f"    Adding column: {display} ...", end=" ", flush=True)

        if col_type == "string":
            ok = add_string_column(session, schema, display, size_or_none, desc)
        elif col_type == "memo":
            ok = add_memo_column(session, schema, display, size_or_none, desc)
        elif col_type == "picklist":
            opts = department_options if "Department" in display else hazard_options
            ok = add_picklist_column(session, schema, display, opts, desc)
        else:
            ok = False

        if ok:
            added.append(display)
            print("OK")
        else:
            print("skipped")

    return added


def get_picklist_map(session, attribute_logical_name):
    """Retrieve the picklist label-to-value mapping for a column."""
    r = session.get(
        f"{API_BASE}/EntityDefinitions(LogicalName='{TABLE_LOGICAL_NAME}')"
        f"/Attributes(LogicalName='{attribute_logical_name}')"
        f"/Microsoft.Dynamics.CRM.PicklistAttributeMetadata"
        f"?$select=LogicalName&$expand=OptionSet($select=Options)"
    )
    r.raise_for_status()
    options = r.json()["OptionSet"]["Options"]
    mapping = {}
    for opt in options:
        label = opt["Label"]["LocalizedLabels"][0]["Label"]
        mapping[label] = opt["Value"]
    return mapping


# ── SAMPLE DATA ────────────────────────────────────────────────────────────────

PPE_KITS = [
    {
        "name": "Dock Worker Kit",
        "role": "Dock Worker",
        "department": "Receiving",
        "hazard": "High",
        "required": (
            "Hi-visibility safety vest (ANSI/ISEA 107 Class 2, fluorescent yellow or orange with 2\" reflective strips, "
            "must be worn fully zipped over all outer garments); "
            "ASTM F2413-rated steel-toe or composite-toe boots (slip-resistant sole, ankle support, $100/yr reimbursement through HR); "
            "ANSI Z87.1+ impact-rated safety glasses (clear lens for indoor, tinted lens available for outdoor dock work); "
            "Heavy-duty leather or synthetic work gloves with reinforced grip (mandatory during all loading/unloading operations, "
            "remove before operating WMS terminals)"
        ),
        "optional": (
            "ANSI Z89.1 Type I Class E hard hat (required when overhead work is in progress or container unloading involves "
            "top-loaded freight); Foam or flanged earplugs (NRR 25+, recommended when truck engines are running at dock doors); "
            "Knee pads (recommended for floor-level pallet inspection)"
        ),
        "notes": (
            "Primary zones: A (Receiving Dock) and E (Outbound Dock). Hard hat transitions from optional to mandatory when "
            "overhead crane or elevated loading operations are active. Gloves must be removed near conveyor drive belts and "
            "rotating machinery due to entanglement risk. Loaner hi-vis vests available at Zone G security desk for temporary dock visitors."
        ),
    },
    {
        "name": "Forklift Operator Kit",
        "role": "Forklift Operator",
        "department": "Receiving",
        "hazard": "High",
        "required": (
            "Hi-visibility safety vest (ANSI/ISEA 107 Class 2); "
            "ASTM F2413-rated steel-toe boots (slip-resistant, ankle support); "
            "ANSI Z87.1+ safety glasses; "
            "Integrated forklift seatbelt (must be fastened before starting engine, inspect latch function during pre-shift checklist)"
        ),
        "optional": (
            "ANSI Z89.1 hard hat (required during container unloading with overhead exposure); "
            "Hearing protection NRR 25+ (recommended in high-noise dock areas); "
            "Leather work gloves (recommended for manual load adjustments, must be removed before operating forklift controls)"
        ),
        "notes": (
            "Zones A-E. Must hold valid Contoso Retail forklift certification per OSHA 29 CFR 1910.178 — certification requires "
            "8-hour classroom + practical evaluation, renewed every 3 years. Pre-shift inspection checklist (brakes, steering, mast, "
            "hydraulics, horn, lights, seatbelt) must be completed before EVERY shift. Seatbelt non-compliance is a Critical safety violation."
        ),
    },
    {
        "name": "Receiving Clerk Kit",
        "role": "Receiving Clerk",
        "department": "Receiving",
        "hazard": "Medium",
        "required": (
            "Hi-visibility safety vest (ANSI/ISEA 107 Class 2); "
            "ASTM F2413-rated steel-toe boots; "
            "ANSI Z87.1+ safety glasses"
        ),
        "optional": (
            "General-purpose work gloves (leather or synthetic, recommended when physically inspecting or handling freight); "
            "Hearing protection (recommended when working near active dock doors with truck engines)"
        ),
        "notes": (
            "Zone A office/dock interface role. Standard floor PPE required whenever on the warehouse floor. "
            "Gloves optional unless directly handling freight or assisting with dock operations. "
            "Safety glasses must be worn at all times on the floor, even during clipboard/paperwork activities at dock stations."
        ),
    },
    {
        "name": "Staging Associate Kit",
        "role": "Staging Associate",
        "department": "Staging",
        "hazard": "Medium",
        "required": (
            "Hi-visibility safety vest (ANSI/ISEA 107 Class 2); "
            "ASTM F2413-rated steel-toe boots (slip-resistant); "
            "ANSI Z87.1+ safety glasses"
        ),
        "optional": (
            "General-purpose work gloves (recommended for manual pallet handling); "
            "Back support belt (optional, available from PPE station in Zone F supply closet)"
        ),
        "notes": (
            "Zone B. Standard warehouse floor PPE package. Report any footwear that no longer meets safety standards "
            "(worn sole, cracked toe cap) to supervisor for early reimbursement eligibility. "
            "PPE replacement available at Zone F supply closet."
        ),
    },
    {
        "name": "Inventory Associate Kit",
        "role": "Inventory Associate",
        "department": "Storage",
        "hazard": "Medium",
        "required": (
            "Hi-visibility safety vest (ANSI/ISEA 107 Class 2); "
            "ASTM F2413-rated steel-toe boots; "
            "ANSI Z87.1+ safety glasses"
        ),
        "optional": (
            "ANSI Z89.1 hard hat (required when working near active high-bay replenishment operations or within 15 feet "
            "of reach truck activity); General-purpose gloves (recommended for physical inventory counts involving product handling); "
            "Knee pads (recommended for low-shelf counting)"
        ),
        "notes": (
            "Zone C. Hard hat requirement activates when reach trucks are operating in the same aisle — check with the "
            "shift supervisor before entering an active replenishment zone. Carry a two-way radio for communication "
            "with material handling equipment operators in storage aisles."
        ),
    },
    {
        "name": "Reach Truck Operator Kit",
        "role": "Reach Truck Operator",
        "department": "Storage",
        "hazard": "High",
        "required": (
            "Hi-visibility safety vest (ANSI/ISEA 107 Class 2); "
            "ASTM F2413-rated steel-toe boots; "
            "ANSI Z87.1+ safety glasses; "
            "Integrated reach truck seatbelt/operator restraint (must be engaged before operating); "
            "ANSI Z89.1 hard hat (mandatory for all high-bay operations above 12 feet)"
        ),
        "optional": (
            "Hearing protection NRR 25+ (recommended in narrow aisles with echo); "
            "Leather work gloves (for manual load adjustment, remove before operating controls)"
        ),
        "notes": (
            "Zone C high-bay. Requires separate Contoso Retail reach truck certification (not interchangeable with "
            "standard forklift cert). Hard hat is mandatory (not optional) for this role due to constant overhead exposure. "
            "Pre-shift inspection includes mast extension test, fork tilt check, and overhead guard integrity verification."
        ),
    },
    {
        "name": "Pick & Pack Associate Kit",
        "role": "Pick & Pack Associate",
        "department": "Pick & Pack",
        "hazard": "Medium",
        "required": (
            "Hi-visibility safety vest (ANSI/ISEA 107 Class 2); "
            "ASTM F2413-rated steel-toe boots; "
            "ANSI Z87.1+ safety glasses; "
            "Cut-resistant gloves ANSI A2 minimum (mandatory for all box cutting and blade operations — "
            "Contoso stocks Ansell HyFlex 11-840 or equivalent)"
        ),
        "optional": (
            "Ergonomic wrist support brace (available from PPE station, recommended for repetitive packing motions "
            "over 6+ hour shifts); Back support belt (optional, available from Zone F supply closet)"
        ),
        "notes": (
            "Zone D. Cut-resistant gloves are MANDATORY whenever using box cutters, utility knives, or razor blades. "
            "Gloves must NOT be worn near conveyor drive belts or rotating machinery (entanglement risk). "
            "Remove gloves before operating touch screen WMS terminals. Replace gloves immediately when holes, tears, "
            "or cut-through is observed — do not attempt to repair gloves."
        ),
    },
    {
        "name": "Order Picker (Elevated) Kit",
        "role": "Order Picker (Elevated)",
        "department": "Pick & Pack",
        "hazard": "High",
        "required": (
            "Hi-visibility safety vest (ANSI/ISEA 107 Class 2); "
            "ASTM F2413-rated steel-toe boots; "
            "ANSI Z87.1+ safety glasses; "
            "Full-body fall protection harness with shock-absorbing lanyard (ANSI Z359.1, mandatory for all elevated "
            "picking above 4 feet per OSHA 1910.28); "
            "ANSI Z89.1 hard hat"
        ),
        "optional": (
            "Cut-resistant gloves ANSI A2 (for box cutting at height); "
            "Knee pads (for kneeling picks on elevated platforms)"
        ),
        "notes": (
            "Zone D elevated picking. Fall protection harness must be inspected before each use — check webbing for fraying, "
            "stitching integrity, D-ring condition, and buckle function. Harness must be connected to an approved anchor point "
            "rated for 5,000 lbs. Fall protection training and annual re-certification required. Never use a harness that has "
            "arrested a fall — remove from service immediately and tag for inspection."
        ),
    },
    {
        "name": "Shipping Clerk Kit",
        "role": "Shipping Clerk",
        "department": "Shipping",
        "hazard": "Medium",
        "required": (
            "Hi-visibility safety vest (ANSI/ISEA 107 Class 2); "
            "ASTM F2413-rated steel-toe boots; "
            "ANSI Z87.1+ safety glasses"
        ),
        "optional": (
            "Heavy-duty work gloves with grip (recommended during physical loading assistance); "
            "Hearing protection (recommended when working near running truck engines at outbound dock doors)"
        ),
        "notes": (
            "Zone E. Same standard floor PPE as other floor roles. Gloves recommended but not mandatory unless directly "
            "handling freight. Safety glasses required at all times on the shipping floor, including at packing stations "
            "and label printers."
        ),
    },
    {
        "name": "Outbound Loader Kit",
        "role": "Outbound Loader",
        "department": "Shipping",
        "hazard": "High",
        "required": (
            "Hi-visibility safety vest (ANSI/ISEA 107 Class 2); "
            "ASTM F2413-rated steel-toe boots (slip-resistant sole critical for trailer floors); "
            "ANSI Z87.1+ safety glasses; "
            "Heavy-duty work gloves with textured grip (mandatory during all trailer loading/unloading operations — "
            "Contoso stocks Mechanix Wear M-Pact or equivalent)"
        ),
        "optional": (
            "Hearing protection NRR 25+ (required when truck engines are running at dock doors); "
            "ANSI Z89.1 hard hat (required when loading containers with overhead stacking); "
            "Knee pads (recommended for floor-level pallet positioning in trailers)"
        ),
        "notes": (
            "Zone E active loading. Full glove use is mandatory — not optional — during trailer loading operations. "
            "Slip-resistant boot soles are critical as trailer floors may be wet, oily, or have debris. "
            "Check dock leveler lock position before walking onto any leveler surface. "
            "Report dock leveler malfunctions immediately."
        ),
    },
    {
        "name": "Maintenance Technician Kit",
        "role": "Maintenance Technician",
        "department": "Maintenance",
        "hazard": "High",
        "required": (
            "Hi-visibility safety vest (ANSI/ISEA 107 Class 2, for floor transit); "
            "ASTM F2413-rated steel-toe boots; "
            "ANSI Z87.1+ safety glasses (minimum — upgrade to splash-proof goggles for fluid work); "
            "Task-specific gloves (see LOTO procedure card for each job — ranges from leather work gloves to "
            "chemical-resistant nitrile); "
            "Hearing protection NRR 25+ (mandatory near compressors, generators, and pneumatic tools)"
        ),
        "optional": (
            "ANSI Z89.1 hard hat (required for overhead work, racking installation, light fixture replacement); "
            "Full-face shield (for grinding, cutting, or fluid splash risk); "
            "Fall protection harness (required for any work above 4 feet); "
            "Chemical-resistant gloves and apron (for hydraulic fluid, coolant, or cleaning chemical work); "
            "Respirator with appropriate cartridges (for paint, solvent, or dust-generating tasks)"
        ),
        "notes": (
            "All zones. PPE requirements vary significantly by task — always consult the specific LOTO procedure card "
            "before beginning any maintenance job. The \"Required\" list above is the minimum for floor transit between jobs. "
            "Each work order should specify additional PPE beyond the baseline. Lockout/Tagout (LOTO) must be completed "
            "before any equipment maintenance — verify zero energy state before work begins."
        ),
    },
    {
        "name": "Battery Room Technician Kit",
        "role": "Battery Room Technician",
        "department": "Maintenance",
        "hazard": "High",
        "required": (
            "Chemical-resistant nitrile or neoprene gloves (minimum 15 mil thickness, elbow-length preferred for battery watering); "
            "Safety glasses with side shields (ANSI Z87.1+, mandatory — standard safety glasses without side shields are NOT acceptable "
            "in the battery room); Full-face shield (must be worn over safety glasses during battery charging, watering, and terminal cleaning); "
            "ASTM F2413-rated steel-toe boots (chemical-resistant sole material); "
            "Acid-resistant rubber apron (hip-length minimum, worn over work clothes)"
        ),
        "optional": (
            "Half-face respirator with acid gas cartridges (required if ventilation system is not meeting air quality standards — "
            "check H2 monitor readings); Emergency eyewash station access (not PPE, but must be verified functional before "
            "starting any battery work)"
        ),
        "notes": (
            "Battery charging station area only. Sulfuric acid and hydrogen gas exposure risks are present. Chemical-resistant gloves "
            "must be inspected before each use — replace immediately if any holes, tears, or degradation is observed. Face shield must "
            "be worn OVER safety glasses, not instead of them. Acid-resistant apron must cover from chest to below the knee. Emergency "
            "eyewash and safety shower must be within 10 seconds walking distance per ANSI Z358.1. Know the location of the nearest "
            "spill kit and neutralizing agent (sodium bicarbonate)."
        ),
    },
    {
        "name": "Janitorial / Housekeeping Kit",
        "role": "Janitorial Staff",
        "department": "Maintenance",
        "hazard": "Medium",
        "required": (
            "ASTM F2413-rated steel-toe boots (slip-resistant sole mandatory — janitorial staff work on wet surfaces regularly); "
            "ANSI Z87.1+ safety glasses; "
            "Chemical-resistant nitrile gloves (mandatory when handling any cleaning agents, disinfectants, or floor chemicals — "
            "check SDS for each product)"
        ),
        "optional": (
            "Hi-visibility safety vest (mandatory when working on the warehouse floor in Zones A-E, optional in offices and break rooms); "
            "Non-slip shoe covers (for freshly mopped areas); "
            "Dust mask or N95 respirator (recommended when sweeping high-dust areas or using aerosol cleaning products)"
        ),
        "notes": (
            "All zones. Chemical-resistant gloves are required whenever handling cleaning agents — check the Safety Data Sheet (SDS) "
            "for each product to confirm glove material compatibility (nitrile is suitable for most general cleaning chemicals, but "
            "some solvents require neoprene or butyl rubber). Hi-vis vest is required whenever on the warehouse floor but not needed "
            "in office areas or break rooms. Report any cleaning chemical containers with damaged or missing labels to the Safety "
            "Coordinator immediately."
        ),
    },
    {
        "name": "Floor Supervisor Kit",
        "role": "Floor Supervisor",
        "department": "Management",
        "hazard": "Medium",
        "required": (
            "Hi-visibility safety vest (ANSI/ISEA 107 Class 2); "
            "ASTM F2413-rated steel-toe boots; "
            "ANSI Z87.1+ safety glasses"
        ),
        "optional": (
            "ANSI Z89.1 hard hat (required when conducting walks in active dock areas or high-bay zones); "
            "Hearing protection (recommended during dock and maintenance area walkthroughs); "
            "Work gloves (recommended if physically assisting with operations)"
        ),
        "notes": (
            "All floor zones (A-E). Supervisors must wear the same PPE as their team members when on the warehouse floor — "
            "no exceptions. Responsible for conducting monthly PPE compliance audits and logging results in the safety inspection "
            "record. Must enforce PPE policy and issue verbal warnings for first-time violations, written warnings for repeat "
            "violations. Keep spare PPE (vests, glasses, gloves) in supervisor office for team members who need emergency replacements."
        ),
    },
    {
        "name": "Warehouse Manager Kit",
        "role": "Warehouse Manager",
        "department": "Management",
        "hazard": "Low",
        "required": (
            "Hi-visibility safety vest (ANSI/ISEA 107 Class 2); "
            "ASTM F2413-rated steel-toe boots; "
            "ANSI Z87.1+ safety glasses"
        ),
        "optional": (
            "ANSI Z89.1 hard hat (required if entering active dock or high-bay area during operations); "
            "Hearing protection (for extended time in high-noise zones)"
        ),
        "notes": (
            "PPE required whenever leaving Zone G (Office/Manager area) and entering any floor zone (A-E). Same PPE standards "
            "apply to managers as all other personnel — leadership by example is a core Contoso Retail safety value. $100/year "
            "footwear reimbursement applies to all employees including management. Keep a set of visitor PPE (loaner vest, safety "
            "glasses, shoe covers) in the manager's office for unplanned facility tours."
        ),
    },
    {
        "name": "Visitor / Contractor Kit",
        "role": "Visitor or Contractor",
        "department": "Management",
        "hazard": "Medium",
        "required": (
            "Hi-visibility safety vest (ANSI/ISEA 107 Class 2 loaner vest issued from Zone G security desk — must be returned upon exit); "
            "ANSI Z87.1+ safety glasses (disposable or loaner from security desk); "
            "Closed-toe shoes minimum (no sandals, flip-flops, or open-toe shoes permitted past the security desk)"
        ),
        "optional": (
            "Steel-toe overshoe covers (available at security desk for visitors without steel-toe footwear — strongly recommended "
            "for dock and floor areas); ANSI Z89.1 hard hat (required if visiting active dock or high-bay area); "
            "Hearing protection (provided if visiting high-noise zones)"
        ),
        "notes": (
            "All floor zones. All visitors and contractors must be escorted by a Contoso Retail employee at all times. Visitor PPE "
            "is checked out at the Zone G security desk and must be returned before leaving the facility. Contractors performing work "
            "(not just touring) must bring their own PPE meeting Contoso standards or will be denied floor access. Visitor log must "
            "be signed at security desk with arrival/departure times."
        ),
    },
    {
        "name": "Conveyor Belt Operator Kit",
        "role": "Conveyor Belt Operator",
        "department": "Shipping",
        "hazard": "Medium",
        "required": (
            "Hi-visibility safety vest (ANSI/ISEA 107 Class 2); "
            "ASTM F2413-rated steel-toe boots; "
            "ANSI Z87.1+ safety glasses; "
            "Hearing protection NRR 25+ (mandatory — conveyor systems generate sustained noise above 85 dB requiring "
            "protection per OSHA 1910.95)"
        ),
        "optional": (
            "Cut-resistant gloves ANSI A2 (ONLY for jam clearing when conveyor belt is fully locked out per LOTO procedure — "
            "never wear gloves near a running belt); Bump cap (lightweight head protection for low-clearance conveyor areas)"
        ),
        "notes": (
            "Zones D-E conveyor lines. CRITICAL SAFETY WARNING: Gloves must NEVER be worn near running conveyor belts, "
            "drive rollers, or any rotating machinery — entanglement risk is the #1 conveyor injury cause. Gloves are only "
            "permitted when the conveyor is locked out per LOTO procedure for jam clearing or maintenance. Know the location "
            "of all emergency stop buttons on your assigned conveyor line — test monthly per the safety calendar."
        ),
    },
    {
        "name": "Cold Storage Associate Kit",
        "role": "Cold Storage Associate",
        "department": "Storage",
        "hazard": "Medium",
        "required": (
            "Hi-visibility safety vest (ANSI/ISEA 107 Class 2, worn over insulated jacket); "
            "ASTM F2413-rated steel-toe boots (insulated version recommended for sustained cold exposure); "
            "ANSI Z87.1+ safety glasses (anti-fog coating required — standard lenses fog immediately in cold-to-warm transitions); "
            "Insulated work gloves rated for operating temperature (minimum -20 degrees F for freezer, 0-35 degrees F for cooler); "
            "Insulated jacket or cold-weather work coat"
        ),
        "optional": (
            "Balaclava or insulated face covering (recommended for freezer operations below 0 degrees F); "
            "Thermal moisture-wicking base layer (recommended under work clothes); "
            "Insulated thermal socks; Hand and toe warmers (disposable, available from PPE station)"
        ),
        "notes": (
            "Cold storage zones. Exposure time limits apply: for temperatures below 0 degrees F, maximum 30 minutes continuous "
            "exposure followed by a 10-minute warm-up break in a heated area. Anti-fog safety glasses are mandatory — do not enter "
            "cold storage with standard lenses as fogging creates an immediate vision hazard. Report any cold-related symptoms "
            "(numbness, tingling, shivering) immediately to your supervisor. Buddy system required for freezer entry — never enter alone."
        ),
    },
    {
        "name": "Hazmat Spill Responder Kit",
        "role": "Hazmat Spill Responder",
        "department": "Maintenance",
        "hazard": "High",
        "required": (
            "Chemical-resistant full-body suit (Tyvek 400 or equivalent, disposable, sized to fit over work clothes and boots); "
            "Chemical-resistant gloves (nitrile or neoprene, minimum 15 mil, double-gloved with inner nitrile liner recommended); "
            "Splash-proof chemical safety goggles (ANSI Z87.1+ indirect-vent, not standard safety glasses); "
            "Half-face respirator with combination OV/P100 cartridges (3M 6000 series or equivalent, must be fit-tested annually "
            "per OSHA 1910.134); "
            "Chemical-resistant steel-toe boots or boot covers (must create a sealed barrier with the suit)"
        ),
        "optional": (
            "Full-face powered air-purifying respirator (PAPR) for large spills or unknown chemicals; "
            "Self-contained breathing apparatus (SCBA) for ammonia leaks or oxygen-deficient environments; "
            "Chemical-resistant apron (additional splash protection over Tyvek suit)"
        ),
        "notes": (
            "Trained responders only. Must have current HAZWOPER 24-hour initial training or 8-hour annual refresher per "
            "OSHA 29 CFR 1910.120. This kit is stored in the Hazmat response locker at the Zone F supply area — not carried daily. "
            "Before responding to any chemical spill: identify the substance from the SDS, assess the spill size, ensure adequate "
            "ventilation, and confirm the correct PPE level (Level A through D). Call 911 for any spill involving ammonia, unknown "
            "chemicals, or quantities exceeding 5 gallons. Decontamination procedure must be followed before removing any PPE."
        ),
    },
    {
        "name": "Safety Coordinator / Trainer Kit",
        "role": "Safety Coordinator",
        "department": "Management",
        "hazard": "Low",
        "required": (
            "Hi-visibility safety vest (ANSI/ISEA 107 Class 2); "
            "ASTM F2413-rated steel-toe boots; "
            "ANSI Z87.1+ safety glasses"
        ),
        "optional": (
            "Complete demonstration PPE set for training sessions (includes: hard hat, all glove types, face shield, fall harness "
            "demo unit, respirator fit-test kit, hearing protection samples); Clipboard and PPE audit checklist forms"
        ),
        "notes": (
            "All zones. The Safety Coordinator carries demonstration PPE for new employee orientation and monthly safety training "
            "sessions — this is a training aid, not personal protection equipment. When on the warehouse floor, standard floor PPE "
            "applies. Responsible for: quarterly PPE compliance audits, managing the Zone F PPE supply closet inventory, processing "
            "$100/year footwear reimbursement requests, coordinating annual respirator fit-testing, and maintaining PPE inspection "
            "records. Hard hat replacement tracking: check manufacture date stamp inside shell — replace every 5 years from "
            "manufacture date or immediately after any impact."
        ),
    },
]


# ── MAIN ───────────────────────────────────────────────────────────────────────

def main():
    print()
    print("=" * 62)
    print("  Contoso Retail — PPE Kit Recommendation Table Setup")
    print(f"  Dataverse: {DATAVERSE_URL}")
    print("=" * 62)

    # 1. Authenticate
    print("\n[1/4] Authenticating ...")
    token = get_access_token()
    session = make_session(token)

    # 2. Connect — WhoAmI() check
    print("\n[2/4] Connecting to Dataverse ...")
    user_id = whoami(session)
    print(f"  Connected. User ID: {user_id}")

    # 3. Create table + columns
    print(f"\n[3/4] Setting up table: '{TABLE_DISPLAY_NAME}' ...")
    if table_exists(session):
        print(f"  Table already exists — skipping creation and schema.")
        print("  (Delete the table in Power Apps and re-run to recreate it.)")
    else:
        create_table(session)

        # Brief pause for Dataverse to propagate the new table
        print("  Waiting for table propagation ...", flush=True)
        time.sleep(5)

        print("  Adding columns ...")
        cols = create_columns(session)
        print(f"  {len(cols)} columns added: {', '.join(cols)}")

        # Publish the table so it's visible in Power Apps
        print("  Publishing customizations ...", flush=True)
        r = session.post(
            f"{API_BASE}/PublishAllXml",
            json={},
        )
        if r.status_code in (200, 204):
            print("  Published.")
        else:
            print(f"  [WARN] Publish returned HTTP {r.status_code} — table may need manual publish in Power Apps.")

    # 4. Populate sample data
    print(f"\n[4/4] Adding PPE kit records ...")

    # Retrieve picklist mappings to send integer values
    print("  Retrieving picklist mappings ...", flush=True)
    dept_map = get_picklist_map(session, f"{PUBLISHER_PREFIX}_department")
    hazard_map = get_picklist_map(session, f"{PUBLISHER_PREFIX}_hazardlevel")
    print(f"  Department options: {list(dept_map.keys())}")
    print(f"  Hazard Level options: {list(hazard_map.keys())}")

    for idx, kit in enumerate(PPE_KITS, 1):
        record = {
            f"{PUBLISHER_PREFIX}_ppekitname": kit["name"],
            f"{PUBLISHER_PREFIX}_jobrole":    kit["role"],
            f"{PUBLISHER_PREFIX}_department":  dept_map.get(kit["department"]),
            f"{PUBLISHER_PREFIX}_requiredppe": kit["required"],
            f"{PUBLISHER_PREFIX}_optionalppe": kit["optional"],
            f"{PUBLISHER_PREFIX}_hazardlevel": hazard_map.get(kit["hazard"]),
            f"{PUBLISHER_PREFIX}_notes":       kit["notes"],
        }

        r = session.post(f"{API_BASE}/{TABLE_SET_NAME}", json=record)
        if r.status_code not in (200, 201, 204):
            print(
                f"  [{idx:02d}/20] FAILED — HTTP {r.status_code}: {r.text[:200]}"
            )
        else:
            hazard = kit["hazard"]
            print(
                f"  [{idx:02d}/20]  {hazard:<6}  {kit['department']:<12}  {kit['name']}"
            )

    print()
    print(f"Done. {len(PPE_KITS)} records added to '{TABLE_DISPLAY_NAME}'.")
    print(f"View table: https://make.powerapps.com > Tables > {TABLE_DISPLAY_NAME}")
    print()


if __name__ == "__main__":
    main()
