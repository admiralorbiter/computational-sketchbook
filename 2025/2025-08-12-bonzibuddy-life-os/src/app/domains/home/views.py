from flask import Blueprint, jsonify, render_template, request, make_response
from ...core.db import get_session
from .services import HomeService
from .models import Asset, MaintenancePlan, MaintenanceEvent, ChorePlan, ChoreEvent, SafetyDevice

bp = Blueprint("home", __name__)


@bp.get("/")
def index():
    """Home & Property dashboard (HTML)."""
    db = get_session()
    svc = HomeService(db)
    data = svc.get_dashboard_data()
    return render_template("home/dashboard.html", data=data)


@bp.get("/dashboard")
def dashboard_data():
    """Home & Property dashboard data (JSON)."""
    db = get_session()
    svc = HomeService(db)
    return jsonify(svc.get_dashboard_data())


# --- Assets (placeholder CRUD) ---

@bp.get("/assets/view")
def assets_view():
    return render_template("home/assets.html")

@bp.get("/assets")
def list_assets():
    db = get_session()
    svc = HomeService(db)
    return jsonify(svc.list_assets())


@bp.post("/assets")
def create_asset():
    body = request.get_json() or {}
    name = body.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400
    db = get_session()
    svc = HomeService(db)
    asset = svc.create_asset(body)
    return jsonify(asset), 201


@bp.get("/assets/<int:asset_id>")
def get_asset(asset_id: int):
    db = get_session()
    svc = HomeService(db)
    asset = svc.get_asset(asset_id)
    if not asset:
        return jsonify({"error": "not found"}), 404
    return jsonify(asset)


@bp.put("/assets/<int:asset_id>")
def update_asset(asset_id: int):
    body = request.get_json() or {}
    db = get_session()
    svc = HomeService(db)
    asset = svc.update_asset(asset_id, body)
    if not asset:
        return jsonify({"error": "not found"}), 404
    return jsonify(asset)


@bp.delete("/assets/<int:asset_id>")
def delete_asset(asset_id: int):
    db = get_session()
    svc = HomeService(db)
    ok = svc.delete_asset(asset_id)
    if not ok:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "deleted"})


# --- Locations ---
@bp.get("/locations")
def list_locations():
    db = get_session()
    svc = HomeService(db)
    return jsonify(svc.list_locations())


# Manuals & Warranties (SLICE 5: Full CRUD)
@bp.get("/manuals")
def list_manuals():
    """List all manuals, optionally filtered by asset_id."""
    asset_id = request.args.get("asset_id", type=int)
    db = get_session()
    svc = HomeService(db)
    return jsonify(svc.list_manuals(asset_id))

@bp.post("/manuals")
def create_manual():
    """Create a new manual."""
    body = request.get_json() or {}
    asset_id = body.get("asset_id")
    if not asset_id:
        return jsonify({"error": "asset_id is required"}), 400
    db = get_session()
    svc = HomeService(db)
    manual = svc.create_manual(body)
    return jsonify(manual), 201

@bp.get("/manuals/<int:manual_id>")
def get_manual(manual_id: int):
    """Get a single manual by ID."""
    db = get_session()
    svc = HomeService(db)
    manual = svc.get_manual(manual_id)
    if not manual:
        return jsonify({"error": "not found"}), 404
    return jsonify(manual)

@bp.put("/manuals/<int:manual_id>")
def update_manual(manual_id: int):
    """Update an existing manual."""
    body = request.get_json() or {}
    db = get_session()
    svc = HomeService(db)
    manual = svc.update_manual(manual_id, body)
    if not manual:
        return jsonify({"error": "not found"}), 404
    return jsonify(manual)

@bp.delete("/manuals/<int:manual_id>")
def delete_manual(manual_id: int):
    """Delete a manual by ID."""
    db = get_session()
    svc = HomeService(db)
    ok = svc.delete_manual(manual_id)
    if not ok:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "deleted"})

@bp.get("/warranties")
def list_warranties():
    """List all warranties, optionally filtered by asset_id."""
    asset_id = request.args.get("asset_id", type=int)
    db = get_session()
    svc = HomeService(db)
    return jsonify(svc.list_warranties(asset_id))

@bp.post("/warranties")
def create_warranty():
    """Create a new warranty."""
    body = request.get_json() or {}
    asset_id = body.get("asset_id")
    if not asset_id:
        return jsonify({"error": "asset_id is required"}), 400
    db = get_session()
    svc = HomeService(db)
    warranty = svc.create_warranty(body)
    return jsonify(warranty), 201

@bp.get("/warranties/<int:warranty_id>")
def get_warranty(warranty_id: int):
    """Get a single warranty by ID."""
    db = get_session()
    svc = HomeService(db)
    warranty = svc.get_warranty(warranty_id)
    if not warranty:
        return jsonify({"error": "not found"}), 404
    return jsonify(warranty)

@bp.put("/warranties/<int:warranty_id>")
def update_warranty(warranty_id: int):
    """Update an existing warranty."""
    body = request.get_json() or {}
    db = get_session()
    svc = HomeService(db)
    warranty = svc.update_warranty(warranty_id, body)
    if not warranty:
        return jsonify({"error": "not found"}), 404
    return jsonify(warranty)

@bp.delete("/warranties/<int:warranty_id>")
def delete_warranty(warranty_id: int):
    """Delete a warranty by ID."""
    db = get_session()
    svc = HomeService(db)
    ok = svc.delete_warranty(warranty_id)
    if not ok:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "deleted"})

@bp.get("/warranties/expiring")
def get_expiring_warranties():
    """Get warranties expiring within the specified number of days."""
    days_ahead = request.args.get("days", 30, type=int)
    db = get_session()
    svc = HomeService(db)
    return jsonify(svc.get_expiring_warranties(days_ahead))


# --- Maintenance Plans ---
@bp.get("/maintenance/view")
def maintenance_view():
    return render_template("home/maintenance.html")

@bp.get("/maintenance/plans")
def list_maintenance_plans():
    db = get_session()
    svc = HomeService(db)
    return jsonify(svc.list_maintenance_plans())


@bp.post("/maintenance/plans")
def create_maintenance_plan():
    body = request.get_json() or {}
    title = body.get("title")
    if not title:
        return jsonify({"error": "title is required"}), 400
    db = get_session()
    svc = HomeService(db)
    plan = svc.create_maintenance_plan(body)
    return jsonify(plan), 201


@bp.get("/maintenance/plans/<int:plan_id>")
def get_maintenance_plan(plan_id: int):
    db = get_session()
    svc = HomeService(db)
    plan = svc.get_maintenance_plan(plan_id)
    if not plan:
        return jsonify({"error": "not found"}), 404
    return jsonify(plan)


@bp.put("/maintenance/plans/<int:plan_id>")
def update_maintenance_plan(plan_id: int):
    body = request.get_json() or {}
    db = get_session()
    svc = HomeService(db)
    plan = svc.update_maintenance_plan(plan_id, body)
    if not plan:
        return jsonify({"error": "not found"}), 404
    return jsonify(plan)


@bp.delete("/maintenance/plans/<int:plan_id>")
def delete_maintenance_plan(plan_id: int):
    db = get_session()
    svc = HomeService(db)
    ok = svc.delete_maintenance_plan(plan_id)
    if not ok:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "deleted"})


@bp.post("/maintenance/plans/<int:plan_id>/events")
def log_maintenance_event(plan_id: int):
    body = request.get_json() or {}
    db = get_session()
    svc = HomeService(db)
    event = svc.log_maintenance_event(plan_id, body)
    if not event:
        return jsonify({"error": "plan not found"}), 404
    return jsonify(event), 201


# --- Chores ---
@bp.get("/chores/view")
def chores_view():
    return render_template("home/chores.html")

@bp.get("/chores/plans")
def list_chore_plans():
    db = get_session()
    svc = HomeService(db)
    return jsonify(svc.list_chore_plans())


@bp.post("/chores/plans")
def create_chore_plan():
    body = request.get_json() or {}
    title = body.get("title")
    if not title:
        return jsonify({"error": "title is required"}), 400
    db = get_session()
    svc = HomeService(db)
    plan = svc.create_chore_plan(body)
    return jsonify(plan), 201


@bp.get("/chores/plans/<int:plan_id>")
def get_chore_plan(plan_id: int):
    db = get_session()
    svc = HomeService(db)
    plan = svc.get_chore_plan(plan_id)
    if not plan:
        return jsonify({"error": "not found"}), 404
    return jsonify(plan)


@bp.put("/chores/plans/<int:plan_id>")
def update_chore_plan(plan_id: int):
    body = request.get_json() or {}
    db = get_session()
    svc = HomeService(db)
    plan = svc.update_chore_plan(plan_id, body)
    if not plan:
        return jsonify({"error": "not found"}), 404
    return jsonify(plan)


@bp.delete("/chores/plans/<int:plan_id>")
def delete_chore_plan(plan_id: int):
    db = get_session()
    svc = HomeService(db)
    ok = svc.delete_chore_plan(plan_id)
    if not ok:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "deleted"})


@bp.post("/chores/plans/<int:plan_id>/events")
def log_chore_event(plan_id: int):
    body = request.get_json() or {}
    db = get_session()
    svc = HomeService(db)
    event = svc.log_chore_event(plan_id, body)
    if not event:
        return jsonify({"error": "plan not found"}), 404
    return jsonify(event), 201


# --- Safety (placeholder CRUD) ---

@bp.get("/safety/view")
def safety_view():
    return render_template("home/safety.html")

# --- Safety Devices ---
@bp.get("/safety/devices")
def list_safety_devices():
    db = get_session()
    svc = HomeService(db)
    return jsonify(svc.list_safety_devices())


@bp.post("/safety/devices")
def create_safety_device():
    body = request.get_json() or {}
    device_type = body.get("type")
    if not device_type:
        return jsonify({"error": "type is required"}), 400
    db = get_session()
    svc = HomeService(db)
    device = svc.create_safety_device(body)
    return jsonify(device), 201


@bp.get("/safety/devices/<int:device_id>")
def get_safety_device(device_id: int):
    db = get_session()
    svc = HomeService(db)
    device = svc.get_safety_device(device_id)
    if not device:
        return jsonify({"error": "not found"}), 404
    return jsonify(device)


@bp.put("/safety/devices/<int:device_id>")
def update_safety_device(device_id: int):
    body = request.get_json() or {}
    db = get_session()
    svc = HomeService(db)
    device = svc.update_safety_device(device_id, body)
    if not device:
        return jsonify({"error": "not found"}), 404
    return jsonify(device)


@bp.delete("/safety/devices/<int:device_id>")
def delete_safety_device(device_id: int):
    db = get_session()
    svc = HomeService(db)
    ok = svc.delete_safety_device(device_id)
    if not ok:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "deleted"})


@bp.post("/safety/devices/<int:device_id>/test")
def record_safety_test(device_id: int):
    body = request.get_json() or {}
    db = get_session()
    svc = HomeService(db)
    device = svc.record_safety_test(device_id, body)
    if not device:
        return jsonify({"error": "device not found"}), 404
    return jsonify(device)


# --- Phase 2: Utilities (SLICE 1) ---
@bp.get("/utilities/view")
def utilities_view():
    return render_template("home/utilities.html")


@bp.get("/utilities/accounts")
def list_utility_accounts():
    """List all utility accounts."""
    db = get_session()
    svc = HomeService(db)
    return jsonify(svc.list_utility_accounts())


@bp.post("/utilities/accounts")
def create_utility_account():
    """Create a new utility account."""
    body = request.get_json() or {}
    provider = body.get("provider")
    service_type = body.get("service_type")
    if not provider or not service_type:
        return jsonify({"error": "provider and service_type are required"}), 400
    
    db = get_session()
    svc = HomeService(db)
    account = svc.create_utility_account(body)
    return jsonify(account), 201


@bp.get("/utilities/accounts/<int:account_id>")
def get_utility_account(account_id: int):
    """Get a single utility account by ID."""
    db = get_session()
    svc = HomeService(db)
    account = svc.get_utility_account(account_id)
    if not account:
        return jsonify({"error": "not found"}), 404
    return jsonify(account)


@bp.put("/utilities/accounts/<int:account_id>")
def update_utility_account(account_id: int):
    """Update an existing utility account."""
    body = request.get_json() or {}
    db = get_session()
    svc = HomeService(db)
    account = svc.update_utility_account(account_id, body)
    if not account:
        return jsonify({"error": "not found"}), 404
    return jsonify(account)


@bp.delete("/utilities/accounts/<int:account_id>")
def delete_utility_account(account_id: int):
    """Delete a utility account by ID."""
    db = get_session()
    svc = HomeService(db)
    ok = svc.delete_utility_account(account_id)
    if not ok:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "deleted"})


@bp.post("/utilities/accounts/<int:account_id>/rates")
def add_rate_snapshot(account_id: int):
    """Add a new rate snapshot for a utility account."""
    body = request.get_json() or {}
    effective_date = body.get("effective_date")
    if not effective_date:
        return jsonify({"error": "effective_date is required"}), 400
    
    db = get_session()
    svc = HomeService(db)
    snapshot = svc.add_rate_snapshot(account_id, body)
    return jsonify(snapshot), 201


@bp.get("/utilities/accounts/<int:account_id>/rates")
def list_rate_snapshots(account_id: int):
    """List rate snapshots for a utility account."""
    db = get_session()
    svc = HomeService(db)
    return jsonify(svc.list_rate_snapshots(account_id))


@bp.post("/utilities/accounts/<int:account_id>/outages")
def log_outage(account_id: int):
    """Log a new outage report."""
    body = request.get_json() or {}
    start_ts = body.get("start_ts")
    if not start_ts:
        return jsonify({"error": "start_ts is required"}), 400
    
    db = get_session()
    svc = HomeService(db)
    outage = svc.log_outage(account_id, body)
    return jsonify(outage), 201


@bp.get("/utilities/accounts/<int:account_id>/outages")
def list_outages(account_id: int):
    """List outage reports for a utility account."""
    db = get_session()
    svc = HomeService(db)
    return jsonify(svc.list_outages(account_id))


# --- Phase 2: Inventory (SLICE 2) ---
@bp.get("/inventory/view")
def inventory_view():
    return render_template("home/inventory.html")


@bp.get("/inventory/items")
def list_inventory_items():
    """List all inventory items, optionally filtered by location or category."""
    location_id = request.args.get("location_id", type=int)
    category = request.args.get("category")
    db = get_session()
    svc = HomeService(db)
    return jsonify(svc.list_inventory_items(location_id, category))


@bp.post("/inventory/items")
def create_inventory_item():
    """Create a new inventory item."""
    body = request.get_json() or {}
    name = body.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400
    
    db = get_session()
    svc = HomeService(db)
    item = svc.create_inventory_item(body)
    return jsonify(item), 201


@bp.get("/inventory/items/<int:item_id>")
def get_inventory_item(item_id: int):
    """Get a single inventory item by ID."""
    db = get_session()
    svc = HomeService(db)
    item = svc.get_inventory_item(item_id)
    if not item:
        return jsonify({"error": "not found"}), 404
    return jsonify(item)


@bp.put("/inventory/items/<int:item_id>")
def update_inventory_item(item_id: int):
    """Update an existing inventory item."""
    body = request.get_json() or {}
    db = get_session()
    svc = HomeService(db)
    item = svc.update_inventory_item(item_id, body)
    if not item:
        return jsonify({"error": "not found"}), 404
    return jsonify(item)


@bp.delete("/inventory/items/<int:item_id>")
def delete_inventory_item(item_id: int):
    """Delete an inventory item by ID."""
    db = get_session()
    svc = HomeService(db)
    ok = svc.delete_inventory_item(item_id)
    if not ok:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "deleted"})


@bp.get("/inventory/low-stock")
def get_low_stock_items():
    """Get inventory items that are below their par level."""
    db = get_session()
    svc = HomeService(db)
    return jsonify(svc.get_low_stock_items())


@bp.get("/inventory/expiring")
def get_expiring_items():
    """Get inventory items expiring within the specified number of days."""
    days_ahead = request.args.get("days", 30, type=int)
    db = get_session()
    svc = HomeService(db)
    return jsonify(svc.get_expiring_items(days_ahead))


# --- Phase 2: Safety Enhancements (SLICE 3) ---
@bp.get("/safety/drills/view")
def safety_drills_view():
    return render_template("home/safety_drills.html")


@bp.get("/safety/drills")
def list_safety_drills():
    """List all safety drills."""
    db = get_session()
    svc = HomeService(db)
    return jsonify(svc.list_safety_drills())


@bp.post("/safety/drills")
def create_safety_drill():
    """Create a new safety drill."""
    body = request.get_json() or {}
    title = body.get("title")
    if not title:
        return jsonify({"error": "title is required"}), 400
    
    db = get_session()
    svc = HomeService(db)
    drill = svc.create_safety_drill(body)
    return jsonify(drill), 201


@bp.get("/safety/drills/<int:drill_id>")
def get_safety_drill(drill_id: int):
    """Get a single safety drill by ID."""
    db = get_session()
    svc = HomeService(db)
    drill = svc.get_safety_drill(drill_id)
    if not drill:
        return jsonify({"error": "not found"}), 404
    return jsonify(drill)


@bp.put("/safety/drills/<int:drill_id>")
def update_safety_drill(drill_id: int):
    """Update an existing safety drill."""
    body = request.get_json() or {}
    db = get_session()
    svc = HomeService(db)
    drill = svc.update_safety_drill(drill_id, body)
    if not drill:
        return jsonify({"error": "not found"}), 404
    return jsonify(drill)


@bp.delete("/safety/drills/<int:drill_id>")
def delete_safety_drill(drill_id: int):
    """Delete a safety drill by ID."""
    db = get_session()
    svc = HomeService(db)
    ok = svc.delete_safety_drill(drill_id)
    if not ok:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "deleted"})


@bp.post("/safety/drills/<int:drill_id>/complete")
def complete_safety_drill(drill_id: int):
    """Mark a safety drill as completed."""
    body = request.get_json() or {}
    db = get_session()
    svc = HomeService(db)
    drill = svc.complete_safety_drill(drill_id, body)
    if not drill:
        return jsonify({"error": "not found"}), 404
    return jsonify(drill)


@bp.get("/safety/kits/view")
def emergency_kits_view():
    return render_template("home/emergency_kits.html")


@bp.get("/safety/kits")
def list_emergency_kits():
    """List all emergency kits."""
    db = get_session()
    svc = HomeService(db)
    return jsonify(svc.list_emergency_kits())


@bp.post("/safety/kits")
def create_emergency_kit():
    """Create a new emergency kit."""
    body = request.get_json() or {}
    location_id = body.get("location_id")
    if not location_id:
        return jsonify({"error": "location_id is required"}), 400
    
    db = get_session()
    svc = HomeService(db)
    kit = svc.create_emergency_kit(body)
    return jsonify(kit), 201


@bp.get("/safety/kits/<int:kit_id>")
def get_emergency_kit(kit_id: int):
    """Get a single emergency kit by ID."""
    db = get_session()
    svc = HomeService(db)
    kit = svc.get_emergency_kit(kit_id)
    if not kit:
        return jsonify({"error": "not found"}), 404
    return jsonify(kit)


@bp.put("/safety/kits/<int:kit_id>")
def update_emergency_kit(kit_id: int):
    """Update an existing emergency kit."""
    body = request.get_json() or {}
    db = get_session()
    svc = HomeService(db)
    kit = svc.update_emergency_kit(kit_id, body)
    if not kit:
        return jsonify({"error": "not found"}), 404
    return jsonify(kit)


@bp.delete("/safety/kits/<int:kit_id>")
def delete_emergency_kit(kit_id: int):
    """Delete an emergency kit by ID."""
    db = get_session()
    svc = HomeService(db)
    ok = svc.delete_emergency_kit(kit_id)
    if not ok:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "deleted"})


@bp.post("/safety/kits/<int:kit_id>/audit")
def audit_emergency_kit(kit_id: int):
    """Complete an emergency kit audit."""
    db = get_session()
    svc = HomeService(db)
    data = request.get_json() or {}
    result = svc.audit_emergency_kit(kit_id, data)
    if result:
        return jsonify(result)
    return jsonify({"error": "Kit not found"}), 404

# --- Phase 2: Exports (SLICE 4) ---

@bp.get("/export/assets")
def export_assets_csv():
    """Export assets to CSV."""
    db = get_session()
    svc = HomeService(db)
    csv_data = svc.export_assets_csv()
    
    response = make_response(csv_data)
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = "attachment; filename=home_assets.csv"
    return response

@bp.get("/export/maintenance")
def export_maintenance_csv():
    """Export maintenance events to CSV."""
    db = get_session()
    svc = HomeService(db)
    csv_data = svc.export_maintenance_events_csv()
    
    response = make_response(csv_data)
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = "attachment; filename=home_maintenance.csv"
    return response

@bp.get("/export/inventory")
def export_inventory_csv():
    """Export inventory items to CSV."""
    db = get_session()
    svc = HomeService(db)
    csv_data = svc.export_inventory_csv()
    
    response = make_response(csv_data)
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = "attachment; filename=home_inventory.csv"
    return response

@bp.get("/export/combined")
def export_combined_csv():
    """Export combined home data to CSV."""
    db = get_session()
    svc = HomeService(db)
    csv_data = svc.export_combined_csv()
    
    response = make_response(csv_data)
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = "attachment; filename=home_combined.csv"
    return response


