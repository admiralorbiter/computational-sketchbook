from typing import Any, Dict, List, Optional
from datetime import datetime, date, timedelta
from .models import (
    Location, Asset, Manual, Warranty, MaintenancePlan, MaintenanceEvent,
    ChorePlan, ChoreEvent, SafetyDevice, UtilityAccount, RateSnapshot, OutageReport,
    InventoryItem, EmergencyKit, SafetyDrill
)


# Temporary in-memory store for scaffold phase only (fallback on DB error)
_STORE: Dict[str, Any] = {
    "assets": [],
    "plans": [],
    "events": [],
    "chore_plans": [],
    "chore_events": [],
    "safety_devices": [],
    "manuals": [],
    "warranties": [],
    "counters": {"asset": 0, "plan": 0, "event": 0, "manual": 0, "warranty": 0},
}


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except Exception:
        return None


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None


class HomeService:
    """Home & Property service with database-backed operations.

    SLICE 1: Assets CRUD fully implemented with database operations.
    Other operations still use in-memory fallback until implemented.
    """

    def __init__(self, db_session):
        self.db = db_session

    # --- Dashboard ---
    def get_dashboard_data(self) -> Dict[str, Any]:
        try:
            assets_total = self.db.query(Asset).count()
            plans_total = self.db.query(MaintenancePlan).count()
            events_total = self.db.query(MaintenanceEvent).count()
            chore_plans_total = self.db.query(ChorePlan).count()
            safety_devices_due = self.db.query(SafetyDevice).filter(
                SafetyDevice.next_test_due < date.today()
            ).count()
            expiring_warranties = len(self.get_expiring_warranties(30))
            utilities_data = self.get_utility_dashboard_data()
            inventory_data = self.get_inventory_dashboard_data()
            safety_data = self.get_safety_dashboard_data()
        except Exception:
            assets_total = len(_STORE["assets"])
            plans_total = len(_STORE["plans"])
            events_total = len(_STORE["events"])
            chore_plans_total = len(_STORE["chore_plans"])
            safety_devices_due = 0
            expiring_warranties = 0
            utilities_data = {"accounts_total": 0, "renewals_soon": 0, "recent_outages": 0}
            inventory_data = {"items_total": 0, "low_stock_count": 0, "expiring_soon": 0}
            safety_data = {"drills_total": 0, "drills_overdue": 0, "kits_total": 0, "kits_due_audit": 0}
        return {
            "assets": {"total": assets_total},
            "maintenance": {"plans": plans_total, "recent_events": events_total},
            "chores": {"plans": chore_plans_total},
            "safety": {"devices_due": safety_devices_due},
            "warranties": {"expiring_soon": expiring_warranties},
            "utilities": utilities_data,
            "inventory": inventory_data,
            "safety_enhanced": safety_data,
        }

    # --- SLICE 1: Assets CRUD (Database-backed) ---
    def list_assets(self) -> List[Dict[str, Any]]:
        """List all assets ordered by name."""
        try:
            assets = self.db.query(Asset).order_by(Asset.name.asc()).all()
            return [a.to_dict() for a in assets]
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in list_assets: {e}")
            return list(_STORE["assets"])

    def list_locations(self) -> List[Dict[str, Any]]:
        """List all locations ordered by name."""
        try:
            from .models import Location
            locations = self.db.query(Location).order_by(Location.name.asc()).all()
            return [l.to_dict() for l in locations]
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in list_locations: {e}")
            return [
                {"id": 1, "name": "Kitchen", "parent_id": None},
                {"id": 2, "name": "Living Room", "parent_id": None},
                {"id": 3, "name": "Bedroom", "parent_id": None},
                {"id": 4, "name": "Garage", "parent_id": None},
                {"id": 5, "name": "Basement", "parent_id": None},
            ]

    def create_asset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new asset with database persistence."""
        try:
            asset = Asset(
                name=data.get("name"),
                type=data.get("type"),
                brand=data.get("brand"),
                model=data.get("model"),
                serial=data.get("serial"),
                purchase_date=_parse_date(data.get("purchase_date")),
                purchase_price=(float(data.get("purchase_price")) if data.get("purchase_price") is not None else None),
                location_id=data.get("location_id"),
                notes=data.get("notes"),
            )
            self.db.add(asset)
            self.db.commit()
            self.db.refresh(asset)
            return asset.to_dict()
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in create_asset: {e}")
            _STORE["counters"]["asset"] += 1
            asset_obj = {
                "id": _STORE["counters"]["asset"],
                "name": data.get("name"),
                "type": data.get("type"),
                "brand": data.get("brand"),
                "model": data.get("model"),
                "serial": data.get("serial"),
                "purchase_date": data.get("purchase_date"),
                "purchase_price": data.get("purchase_price"),
                "location_id": data.get("location_id"),
                "notes": data.get("notes"),
            }
            _STORE["assets"].append(asset_obj)
            return asset_obj

    def get_asset(self, asset_id: int) -> Optional[Dict[str, Any]]:
        """Get a single asset by ID."""
        try:
            asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
            return asset.to_dict() if asset else None
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in get_asset: {e}")
            for a in _STORE["assets"]:
                if a.get("id") == asset_id:
                    return a
            return None

    def update_asset(self, asset_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing asset."""
        try:
            asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset:
                return None
            
            # Update fields if provided
            if "name" in data:
                asset.name = data["name"]
            if "type" in data:
                asset.type = data["type"]
            if "brand" in data:
                asset.brand = data["brand"]
            if "model" in data:
                asset.model = data["model"]
            if "serial" in data:
                asset.serial = data["serial"]
            if "purchase_date" in data:
                asset.purchase_date = _parse_date(data["purchase_date"])
            if "purchase_price" in data:
                asset.purchase_price = float(data["purchase_price"]) if data["purchase_price"] is not None else None
            if "location_id" in data:
                asset.location_id = data["location_id"]
            if "notes" in data:
                asset.notes = data["notes"]
            
            # updated_at will be set automatically by SQLAlchemy
            self.db.commit()
            self.db.refresh(asset)
            return asset.to_dict()
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in update_asset: {e}")
            asset = self.get_asset(asset_id)
            if not asset:
                return None
            asset.update({k: v for k, v in data.items() if k in {"name", "type", "brand", "model", "serial", "location_id", "notes"}})
            return asset

    def delete_asset(self, asset_id: int) -> bool:
        """Delete an asset by ID."""
        try:
            asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset:
                return False
            self.db.delete(asset)
            self.db.commit()
            return True
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in delete_asset: {e}")
            for i, a in enumerate(_STORE["assets"]):
                if a.get("id") == asset_id:
                    _STORE["assets"].pop(i)
                    return True
            return False

    # --- SLICE 2: Maintenance Plans CRUD (Database-backed) ---
    def list_maintenance_plans(self) -> List[Dict[str, Any]]:
        """List all maintenance plans ordered by next due date."""
        try:
            plans = self.db.query(MaintenancePlan).order_by(
                MaintenancePlan.next_due.is_(None), 
                MaintenancePlan.next_due.asc()
            ).all()
            return [p.to_dict() for p in plans]
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in list_maintenance_plans: {e}")
            return list(_STORE["plans"])

    def create_maintenance_plan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new maintenance plan with database persistence."""
        try:
            plan = MaintenancePlan(
                title=data.get("title"),
                asset_id=data.get("asset_id"),
                cadence=data.get("cadence") or "RRULE:FREQ=MONTHLY",
                next_due=_parse_date(data.get("next_due")),
                last_done=_parse_date(data.get("last_done")),
                checklist_json=data.get("checklist_json") or data.get("checklist"),
            )
            self.db.add(plan)
            self.db.commit()
            self.db.refresh(plan)
            return plan.to_dict()
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in create_maintenance_plan: {e}")
            _STORE["counters"]["plan"] += 1
            plan = {
                "id": _STORE["counters"]["plan"],
                "title": data.get("title"),
                "asset_id": data.get("asset_id"),
                "cadence": data.get("cadence"),
                "next_due": data.get("next_due"),
                "last_done": data.get("last_done"),
                "checklist": data.get("checklist"),
            }
            _STORE["plans"].append(plan)
            return plan

    def get_maintenance_plan(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """Get a single maintenance plan by ID."""
        try:
            plan = self.db.query(MaintenancePlan).filter(MaintenancePlan.id == plan_id).first()
            return plan.to_dict() if plan else None
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in get_maintenance_plan: {e}")
            for p in _STORE["plans"]:
                if p.get("id") == plan_id:
                    return p
            return None

    def update_maintenance_plan(self, plan_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing maintenance plan."""
        try:
            plan = self.db.query(MaintenancePlan).filter(MaintenancePlan.id == plan_id).first()
            if not plan:
                return None
            
            # Update fields if provided
            if "title" in data:
                plan.title = data["title"]
            if "asset_id" in data:
                plan.asset_id = data["asset_id"]
            if "cadence" in data:
                plan.cadence = data["cadence"]
            if "next_due" in data:
                plan.next_due = _parse_date(data["next_due"])
            if "last_done" in data:
                plan.last_done = _parse_date(data["last_done"])
            if "checklist_json" in data:
                plan.checklist_json = data["checklist_json"]
            
            # updated_at will be set automatically by SQLAlchemy
            self.db.commit()
            self.db.refresh(plan)
            return plan.to_dict()
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in update_maintenance_plan: {e}")
            for p in _STORE["plans"]:
                if p["id"] == plan_id:
                    p.update({k: v for k, v in data.items() if k in {"title", "asset_id", "cadence", "next_due", "last_done", "checklist"}})
                    return p
            return None

    def delete_maintenance_plan(self, plan_id: int) -> bool:
        """Delete a maintenance plan by ID."""
        try:
            plan = self.db.query(MaintenancePlan).filter(MaintenancePlan.id == plan_id).first()
            if not plan:
                return False
            self.db.delete(plan)
            self.db.commit()
            return True
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in delete_maintenance_plan: {e}")
            for i, p in enumerate(_STORE.get("plans", [])):
                if p.get("id") == plan_id:
                    _STORE["plans"].pop(i)
                    return True
            return False

    def log_maintenance_event(self, plan_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Log a maintenance event for a plan."""
        try:
            plan = self.db.query(MaintenancePlan).filter(MaintenancePlan.id == plan_id).first()
            if not plan:
                return None
            
            event = MaintenanceEvent(
                plan_id=plan_id,
                ts=_parse_datetime(data.get("ts")) or datetime.utcnow(),
                notes=data.get("notes"),
                cost=(float(data.get("cost")) if data.get("cost") is not None else None),
            )
            self.db.add(event)
            
            # Update the plan's last_done date
            plan.last_done = event.ts.date() if event.ts else plan.last_done
            
            self.db.commit()
            self.db.refresh(event)
            return event.to_dict()
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in log_maintenance_event: {e}")
            if not any(p.get("id") == plan_id for p in _STORE.get("plans", [])):
                return None
            _STORE["counters"]["event"] += 1
            event = {
                "id": _STORE["counters"]["event"],
                "plan_id": plan_id,
                "ts": data.get("ts"),
                "notes": data.get("notes"),
                "cost": data.get("cost"),
            }
            _STORE["events"].append(event)
            return event

    # --- SLICE 3: Chores CRUD (Database-backed) ---
    def list_chore_plans(self) -> List[Dict[str, Any]]:
        """List all chore plans ordered by next due date."""
        try:
            plans = self.db.query(ChorePlan).order_by(
                ChorePlan.next_due.is_(None), 
                ChorePlan.next_due.asc()
            ).all()
            return [p.to_dict() for p in plans]
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in list_chore_plans: {e}")
            return list(_STORE["chore_plans"])

    def create_chore_plan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new chore plan with database persistence."""
        try:
            plan = ChorePlan(
                title=data.get("title"),
                cadence=data.get("cadence") or "RRULE:FREQ=WEEKLY",
                location_id=data.get("location_id"),
                next_due=_parse_date(data.get("next_due")),
                last_done=_parse_date(data.get("last_done")),
                checklist_json=data.get("checklist_json") or data.get("checklist"),
            )
            self.db.add(plan)
            self.db.commit()
            self.db.refresh(plan)
            return plan.to_dict()
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in create_chore_plan: {e}")
            _STORE["counters"]["plan"] += 1
            plan = {
                "id": _STORE["counters"]["plan"],
                "title": data.get("title"),
                "cadence": data.get("cadence"),
                "location_id": data.get("location_id"),
                "next_due": data.get("next_due"),
                "last_done": data.get("last_done"),
                "checklist": data.get("checklist"),
            }
            _STORE["chore_plans"].append(plan)
            return plan

    def get_chore_plan(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """Get a single chore plan by ID."""
        try:
            plan = self.db.query(ChorePlan).filter(ChorePlan.id == plan_id).first()
            return plan.to_dict() if plan else None
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in get_chore_plan: {e}")
            for p in _STORE["chore_plans"]:
                if p.get("id") == plan_id:
                    return p
            return None

    def update_chore_plan(self, plan_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing chore plan."""
        try:
            plan = self.db.query(ChorePlan).filter(ChorePlan.id == plan_id).first()
            if not plan:
                return None
            
            # Update fields if provided
            if "title" in data:
                plan.title = data["title"]
            if "cadence" in data:
                plan.cadence = data["cadence"]
            if "location_id" in data:
                plan.location_id = data["location_id"]
            if "next_due" in data:
                plan.next_due = _parse_date(data["next_due"])
            if "last_done" in data:
                plan.last_done = _parse_date(data["last_done"])
            if "checklist_json" in data:
                plan.checklist_json = data["checklist_json"]
            
            # updated_at will be set automatically by SQLAlchemy
            self.db.commit()
            self.db.refresh(plan)
            return plan.to_dict()
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in update_chore_plan: {e}")
            for p in _STORE["chore_plans"]:
                if p["id"] == plan_id:
                    p.update({k: v for k, v in data.items() if k in {"title", "cadence", "location_id", "next_due", "last_done", "checklist"}})
                    return p
            return None

    def delete_chore_plan(self, plan_id: int) -> bool:
        """Delete a chore plan by ID."""
        try:
            plan = self.db.query(ChorePlan).filter(ChorePlan.id == plan_id).first()
            if not plan:
                return False
            self.db.delete(plan)
            self.db.commit()
            return True
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in delete_chore_plan: {e}")
            for i, p in enumerate(_STORE.get("chore_plans", [])):
                if p.get("id") == plan_id:
                    _STORE["chore_plans"].pop(i)
                    return True
            return False

    def log_chore_event(self, plan_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Log a chore completion event for a plan."""
        try:
            plan = self.db.query(ChorePlan).filter(ChorePlan.id == plan_id).first()
            if not plan:
                return None
            
            event = ChoreEvent(
                plan_id=plan_id,
                ts=_parse_datetime(data.get("ts")) or datetime.utcnow(),
                who=data.get("who") or "Unknown",
                notes=data.get("notes"),
            )
            self.db.add(event)
            
            # Update the plan's last_done date
            plan.last_done = event.ts.date() if event.ts else plan.last_done
            
            self.db.commit()
            self.db.refresh(event)
            return event.to_dict()
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in log_chore_event: {e}")
            if not any(p.get("id") == plan_id for p in _STORE.get("chore_plans", [])):
                return None
            _STORE["counters"]["event"] += 1
            event = {
                "id": _STORE["counters"]["event"],
                "plan_id": plan_id,
                "ts": data.get("ts"),
                "who": data.get("who") or "Unknown",
                "notes": data.get("notes"),
            }
            _STORE["chore_events"].append(event)
            return event

    # --- SLICE 4: Safety Devices CRUD (Database-backed) ---
    def list_safety_devices(self) -> List[Dict[str, Any]]:
        """List all safety devices ordered by next test due date."""
        try:
            devices = self.db.query(SafetyDevice).order_by(
                SafetyDevice.next_test_due.is_(None), 
                SafetyDevice.next_test_due.asc()
            ).all()
            return [d.to_dict() for d in devices]
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in list_safety_devices: {e}")
            return list(_STORE["safety_devices"])

    def create_safety_device(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new safety device with database persistence."""
        try:
            device = SafetyDevice(
                type=data.get("type"),
                location_id=data.get("location_id"),
                model=data.get("model"),
                purchase_date=_parse_date(data.get("purchase_date")),
                expiry_date=_parse_date(data.get("expiry_date")),
                test_cadence=data.get("test_cadence") or "RRULE:FREQ=MONTHLY",
                next_test_due=_parse_date(data.get("next_test_due")),
                last_test=_parse_date(data.get("last_test")),
            )
            self.db.add(device)
            self.db.commit()
            self.db.refresh(device)
            return device.to_dict()
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in create_safety_device: {e}")
            _STORE["counters"]["device"] = _STORE["counters"].get("device", 0) + 1
            device = {
                "id": _STORE["counters"]["device"],
                "type": data.get("type"),
                "location_id": data.get("location_id"),
                "model": data.get("model"),
                "purchase_date": data.get("purchase_date"),
                "expiry_date": data.get("expiry_date"),
                "test_cadence": data.get("test_cadence"),
                "next_test_due": data.get("next_test_due"),
                "last_test": data.get("last_test"),
            }
            _STORE["safety_devices"].append(device)
            return device

    def get_safety_device(self, device_id: int) -> Optional[Dict[str, Any]]:
        """Get a single safety device by ID."""
        try:
            device = self.db.query(SafetyDevice).filter(SafetyDevice.id == device_id).first()
            return device.to_dict() if device else None
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in get_safety_device: {e}")
            for d in _STORE["safety_devices"]:
                if d.get("id") == device_id:
                    return d
            return None

    def update_safety_device(self, device_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing safety device."""
        try:
            device = self.db.query(SafetyDevice).filter(SafetyDevice.id == device_id).first()
            if not device:
                return None
            
            # Update fields if provided
            if "type" in data:
                device.type = data["type"]
            if "location_id" in data:
                device.location_id = data["location_id"]
            if "model" in data:
                device.model = data["model"]
            if "purchase_date" in data:
                device.purchase_date = _parse_date(data["purchase_date"])
            if "expiry_date" in data:
                device.expiry_date = _parse_date(data["expiry_date"])
            if "test_cadence" in data:
                device.test_cadence = data["test_cadence"]
            if "next_test_due" in data:
                device.next_test_due = _parse_date(data["next_test_due"])
            if "last_test" in data:
                device.last_test = _parse_date(data["last_test"])
            
            # updated_at will be set automatically by SQLAlchemy
            self.db.commit()
            self.db.refresh(device)
            return device.to_dict()
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in update_safety_device: {e}")
            for d in _STORE["safety_devices"]:
                if d["id"] == device_id:
                    d.update({k: v for k, v in data.items() if k in {"type", "location_id", "model", "purchase_date", "expiry_date", "test_cadence", "next_test_due", "last_test"}})
                    return d
            return None

    def delete_safety_device(self, device_id: int) -> bool:
        """Delete a safety device by ID."""
        try:
            device = self.db.query(SafetyDevice).filter(SafetyDevice.id == device_id).first()
            if not device:
                return False
            self.db.delete(device)
            self.db.commit()
            return True
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in delete_safety_device: {e}")
            for i, d in enumerate(_STORE.get("safety_devices", [])):
                if d.get("id") == device_id:
                    _STORE["safety_devices"].pop(i)
                    return True
            return False

    def record_safety_test(self, device_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Record a safety test for a device."""
        try:
            device = self.db.query(SafetyDevice).filter(SafetyDevice.id == device_id).first()
            if not device:
                return None
            
            # Update the device's test information
            device.last_test = _parse_date(data.get("test_date")) or date.today()
            
            # Calculate next test due based on cadence (simple implementation)
            if device.test_cadence and device.last_test:
                if "MONTHLY" in device.test_cadence:
                    if "INTERVAL=3" in device.test_cadence:
                        months = 3
                    elif "INTERVAL=6" in device.test_cadence:
                        months = 6
                    else:
                        months = 1
                    # Simple month addition (could use dateutil.relativedelta for more accuracy)
                    next_test = device.last_test.replace(month=device.last_test.month + months)
                    if next_test.month > 12:
                        next_test = next_test.replace(year=next_test.year + 1, month=next_test.month - 12)
                    device.next_test_due = next_test
                elif "YEARLY" in device.test_cadence:
                    device.next_test_due = device.last_test.replace(year=device.last_test.year + 1)
                elif "WEEKLY" in device.test_cadence:
                    if "INTERVAL=2" in device.test_cadence:
                        device.next_test_due = device.last_test + timedelta(weeks=2)
                    else:
                        device.next_test_due = device.last_test + timedelta(weeks=1)
            
            self.db.commit()
            self.db.refresh(device)
            return device.to_dict()
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in record_safety_test: {e}")
            for d in _STORE["safety_devices"]:
                if d["id"] == device_id:
                    d["last_test"] = data.get("test_date") or date.today().isoformat()
                    # Simple next test calculation for fallback
                    if "MONTHLY" in d.get("test_cadence", ""):
                        d["next_test_due"] = (date.today() + timedelta(days=30)).isoformat()
                    elif "YEARLY" in d.get("test_cadence", ""):
                        d["next_test_due"] = (date.today() + timedelta(days=365)).isoformat()
                    elif "WEEKLY" in d.get("test_cadence", ""):
                        d["next_test_due"] = (date.today() + timedelta(days=7)).isoformat()
                    return d
            return None

    # --- SLICE 5: Manuals & Warranties CRUD (Database-backed) ---
    def list_manuals(self, asset_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """List all manuals, optionally filtered by asset_id."""
        try:
            query = self.db.query(Manual)
            if asset_id:
                query = query.filter(Manual.asset_id == asset_id)
            manuals = query.order_by(Manual.created_at.desc()).all()
            return [m.to_dict() for m in manuals]
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in list_manuals: {e}")
            if asset_id:
                return [m for m in _STORE["manuals"] if m.get("asset_id") == asset_id]
            return list(_STORE["manuals"])

    def create_manual(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new manual with database persistence."""
        try:
            manual = Manual(
                asset_id=data.get("asset_id"),
                file_id=data.get("file_id"),
                url=data.get("url"),
                note=data.get("note"),
            )
            self.db.add(manual)
            self.db.commit()
            self.db.refresh(manual)
            return manual.to_dict()
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in create_manual: {e}")
            _STORE["counters"]["manual"] += 1
            manual = {
                "id": _STORE["counters"]["manual"],
                "asset_id": data.get("asset_id"),
                "file_id": data.get("file_id"),
                "url": data.get("url"),
                "note": data.get("note"),
            }
            _STORE["manuals"].append(manual)
            return manual

    def get_manual(self, manual_id: int) -> Optional[Dict[str, Any]]:
        """Get a single manual by ID."""
        try:
            manual = self.db.query(Manual).filter(Manual.id == manual_id).first()
            return manual.to_dict() if manual else None
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in get_manual: {e}")
            for m in _STORE["manuals"]:
                if m.get("id") == manual_id:
                    return m
            return None

    def update_manual(self, manual_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing manual."""
        try:
            manual = self.db.query(Manual).filter(Manual.id == manual_id).first()
            if not manual:
                return None
            
            # Update fields if provided
            if "asset_id" in data:
                manual.asset_id = data["asset_id"]
            if "file_id" in data:
                manual.file_id = data["file_id"]
            if "url" in data:
                manual.url = data["url"]
            if "note" in data:
                manual.note = data["note"]
            
            # updated_at will be set automatically by SQLAlchemy
            self.db.commit()
            self.db.refresh(manual)
            return manual.to_dict()
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in update_manual: {e}")
            for m in _STORE["manuals"]:
                if m["id"] == manual_id:
                    m.update({k: v for k, v in data.items() if k in {"asset_id", "file_id", "url", "note"}})
                    return m
            return None

    def delete_manual(self, manual_id: int) -> bool:
        """Delete a manual by ID."""
        try:
            manual = self.db.query(Manual).filter(Manual.id == manual_id).first()
            if not manual:
                return False
            self.db.delete(manual)
            self.db.commit()
            return True
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in delete_manual: {e}")
            for i, m in enumerate(_STORE.get("manuals", [])):
                if m.get("id") == manual_id:
                    _STORE["manuals"].pop(i)
                    return True
            return False

    def list_warranties(self, asset_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """List all warranties, optionally filtered by asset_id."""
        try:
            query = self.db.query(Warranty)
            if asset_id:
                query = query.filter(Warranty.asset_id == asset_id)
            warranties = query.order_by(Warranty.end_date.asc()).all()
            return [w.to_dict() for w in warranties]
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in list_warranties: {e}")
            if asset_id:
                return [w for w in _STORE["warranties"] if w.get("asset_id") == asset_id]
            return list(_STORE["warranties"])

    def create_warranty(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new warranty with database persistence."""
        try:
            warranty = Warranty(
                asset_id=data.get("asset_id"),
                provider=data.get("provider"),
                policy_no=data.get("policy_no"),
                start_date=_parse_date(data.get("start_date")),
                end_date=_parse_date(data.get("end_date")),
                coverage_note=data.get("coverage_note"),
                claim_steps=data.get("claim_steps"),
            )
            self.db.add(warranty)
            self.db.commit()
            self.db.refresh(warranty)
            return warranty.to_dict()
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in create_warranty: {e}")
            _STORE["counters"]["warranty"] += 1
            warranty = {
                "id": _STORE["counters"]["warranty"],
                "asset_id": data.get("asset_id"),
                "provider": data.get("provider"),
                "policy_no": data.get("policy_no"),
                "start_date": data.get("start_date"),
                "end_date": data.get("end_date"),
                "coverage_note": data.get("coverage_note"),
                "claim_steps": data.get("claim_steps"),
            }
            _STORE["warranties"].append(warranty)
            return warranty

    def get_warranty(self, warranty_id: int) -> Optional[Dict[str, Any]]:
        """Get a single warranty by ID."""
        try:
            warranty = self.db.query(Warranty).filter(Warranty.id == warranty_id).first()
            return warranty.to_dict() if warranty else None
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in get_warranty: {e}")
            for w in _STORE["warranties"]:
                if w.get("id") == warranty_id:
                    return w
            return None

    def update_warranty(self, warranty_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing warranty."""
        try:
            warranty = self.db.query(Warranty).filter(Warranty.id == warranty_id).first()
            if not warranty:
                return None
            
            # Update fields if provided
            if "asset_id" in data:
                warranty.asset_id = data["asset_id"]
            if "provider" in data:
                warranty.provider = data["provider"]
            if "policy_no" in data:
                warranty.policy_no = data["policy_no"]
            if "start_date" in data:
                warranty.start_date = _parse_date(data["start_date"])
            if "end_date" in data:
                warranty.end_date = _parse_date(data["end_date"])
            if "coverage_note" in data:
                warranty.coverage_note = data["coverage_note"]
            if "claim_steps" in data:
                warranty.claim_steps = data["claim_steps"]
            
            # updated_at will be set automatically by SQLAlchemy
            self.db.commit()
            self.db.refresh(warranty)
            return warranty.to_dict()
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in update_warranty: {e}")
            for w in _STORE["warranties"]:
                if w["id"] == warranty_id:
                    w.update({k: v for k, v in data.items() if k in {"asset_id", "provider", "policy_no", "start_date", "end_date", "coverage_note", "claim_steps"}})
                    return w
            return None

    def delete_warranty(self, warranty_id: int) -> bool:
        """Delete a warranty by ID."""
        try:
            warranty = self.db.query(Warranty).filter(Warranty.id == warranty_id).first()
            if not warranty:
                return False
            self.db.delete(warranty)
            self.db.commit()
            return True
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in delete_warranty: {e}")
            for i, w in enumerate(_STORE.get("warranties", [])):
                if w.get("id") == warranty_id:
                    _STORE["warranties"].pop(i)
                    return True
            return False

    def get_expiring_warranties(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get warranties expiring within the specified number of days."""
        try:
            from datetime import timedelta
            cutoff_date = date.today() + timedelta(days=days_ahead)
            warranties = self.db.query(Warranty).filter(
                Warranty.end_date <= cutoff_date,
                Warranty.end_date >= date.today()
            ).order_by(Warranty.end_date.asc()).all()
            return [w.to_dict() for w in warranties]
        except Exception as e:
            # Fallback to in-memory for now
            print(f"Database error in get_expiring_warranties: {e}")
            cutoff_date = date.today() + timedelta(days=days_ahead)
            expiring = []
            for w in _STORE["warranties"]:
                if w.get("end_date"):
                    try:
                        end_date = date.fromisoformat(w["end_date"])
                        if end_date <= cutoff_date and end_date >= date.today():
                            expiring.append(w)
                    except:
                        continue
            return sorted(expiring, key=lambda x: x.get("end_date", ""))

    # --- Phase 2: Utilities CRUD (SLICE 1) ---
    def list_utility_accounts(self) -> List[Dict[str, Any]]:
        """List all utility accounts."""
        try:
            accounts = self.db.query(UtilityAccount).order_by(UtilityAccount.provider.asc()).all()
            return [a.to_dict() for a in accounts]
        except Exception as e:
            print(f"Database error in list_utility_accounts: {e}")
            return []

    def create_utility_account(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new utility account."""
        try:
            account = UtilityAccount(
                provider=data.get("provider"),
                service_type=data.get("service_type"),
                account_no=data.get("account_no"),
                start_date=_parse_date(data.get("start_date")),
                renewal_date=_parse_date(data.get("renewal_date")),
                website=data.get("website"),
                support_phone=data.get("support_phone"),
                address=data.get("address"),
            )
            self.db.add(account)
            self.db.commit()
            self.db.refresh(account)
            return account.to_dict()
        except Exception as e:
            print(f"Database error in create_utility_account: {e}")
            return {}

    def get_utility_account(self, account_id: int) -> Optional[Dict[str, Any]]:
        """Get a single utility account by ID."""
        try:
            account = self.db.query(UtilityAccount).filter(UtilityAccount.id == account_id).first()
            return account.to_dict() if account else None
        except Exception as e:
            print(f"Database error in get_utility_account: {e}")
            return None

    def update_utility_account(self, account_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing utility account."""
        try:
            account = self.db.query(UtilityAccount).filter(UtilityAccount.id == account_id).first()
            if not account:
                return None
            
            if "provider" in data:
                account.provider = data["provider"]
            if "service_type" in data:
                account.service_type = data["service_type"]
            if "account_no" in data:
                account.account_no = data["account_no"]
            if "start_date" in data:
                account.start_date = _parse_date(data["start_date"])
            if "renewal_date" in data:
                account.renewal_date = _parse_date(data["renewal_date"])
            if "website" in data:
                account.website = data["website"]
            if "support_phone" in data:
                account.support_phone = data["support_phone"]
            if "address" in data:
                account.address = data["address"]
            
            account.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(account)
            return account.to_dict()
        except Exception as e:
            print(f"Database error in update_utility_account: {e}")
            return None

    def delete_utility_account(self, account_id: int) -> bool:
        """Delete a utility account by ID."""
        try:
            account = self.db.query(UtilityAccount).filter(UtilityAccount.id == account_id).first()
            if not account:
                return False
            
            self.db.delete(account)
            self.db.commit()
            return True
        except Exception as e:
            print(f"Database error in delete_utility_account: {e}")
            return False

    def add_rate_snapshot(self, account_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new rate snapshot for a utility account."""
        try:
            snapshot = RateSnapshot(
                utility_account_id=account_id,
                effective_date=_parse_date(data.get("effective_date")),
                unit_price=data.get("unit_price"),
                unit_name=data.get("unit_name"),
                base_fee=data.get("base_fee"),
            )
            self.db.add(snapshot)
            self.db.commit()
            self.db.refresh(snapshot)
            return snapshot.to_dict()
        except Exception as e:
            print(f"Database error in add_rate_snapshot: {e}")
            return {}

    def list_rate_snapshots(self, account_id: int) -> List[Dict[str, Any]]:
        """List rate snapshots for a utility account."""
        try:
            snapshots = self.db.query(RateSnapshot).filter(
                RateSnapshot.utility_account_id == account_id
            ).order_by(RateSnapshot.effective_date.desc()).all()
            return [s.to_dict() for s in snapshots]
        except Exception as e:
            print(f"Database error in list_rate_snapshots: {e}")
            return []

    def log_outage(self, account_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Log a new outage report."""
        try:
            outage = OutageReport(
                utility_account_id=account_id,
                start_ts=_parse_datetime(data.get("start_ts")),
                end_ts=_parse_datetime(data.get("end_ts")),
                ticket_no=data.get("ticket_no"),
                notes=data.get("notes"),
            )
            self.db.add(outage)
            self.db.commit()
            self.db.refresh(outage)
            return outage.to_dict()
        except Exception as e:
            print(f"Database error in log_outage: {e}")
            return {}

    def list_outages(self, account_id: int) -> List[Dict[str, Any]]:
        """List outage reports for a utility account."""
        try:
            outages = self.db.query(OutageReport).filter(
                OutageReport.utility_account_id == account_id
            ).order_by(OutageReport.start_ts.desc()).all()
            return [o.to_dict() for o in outages]
        except Exception as e:
            print(f"Database error in list_outages: {e}")
            return []

    def get_utility_dashboard_data(self) -> Dict[str, Any]:
        """Get utility-specific dashboard data."""
        try:
            accounts_total = self.db.query(UtilityAccount).count()
            renewals_soon = self.db.query(UtilityAccount).filter(
                UtilityAccount.renewal_date <= date.today() + timedelta(days=30)
            ).count()
            recent_outages = self.db.query(OutageReport).filter(
                OutageReport.start_ts >= datetime.now() - timedelta(days=30)
            ).count()
            
            return {
                "accounts_total": accounts_total,
                "renewals_soon": renewals_soon,
                "recent_outages": recent_outages,
            }
        except Exception as e:
            print(f"Database error in get_utility_dashboard_data: {e}")
            return {
                "accounts_total": 0,
                "renewals_soon": 0,
                "recent_outages": 0,
            }

    # --- Phase 2: Inventory CRUD (SLICE 2) ---
    def list_inventory_items(self, location_id: Optional[int] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all inventory items, optionally filtered by location or category."""
        try:
            query = self.db.query(InventoryItem)
            if location_id:
                query = query.filter(InventoryItem.location_id == location_id)
            if category:
                query = query.filter(InventoryItem.category == category)
            items = query.order_by(InventoryItem.name.asc()).all()
            return [i.to_dict() for i in items]
        except Exception as e:
            print(f"Database error in list_inventory_items: {e}")
            return []

    def create_inventory_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new inventory item."""
        try:
            item = InventoryItem(
                name=data.get("name"),
                category=data.get("category"),
                location_id=data.get("location_id"),
                qty=float(data.get("qty", 1.0)),
                unit=data.get("unit"),
                par_level=float(data.get("par_level")) if data.get("par_level") else None,
                expiry_date=_parse_date(data.get("expiry_date")),
                photo_path=data.get("photo_path"),
                notes=data.get("notes"),
            )
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item.to_dict()
        except Exception as e:
            print(f"Database error in create_inventory_item: {e}")
            return {}

    def get_inventory_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Get a single inventory item by ID."""
        try:
            item = self.db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
            return item.to_dict() if item else None
        except Exception as e:
            print(f"Database error in get_inventory_item: {e}")
            return None

    def update_inventory_item(self, item_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing inventory item."""
        try:
            item = self.db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
            if not item:
                return None
            
            if "name" in data:
                item.name = data["name"]
            if "category" in data:
                item.category = data["category"]
            if "location_id" in data:
                item.location_id = data["location_id"]
            if "qty" in data:
                item.qty = float(data["qty"])
            if "unit" in data:
                item.unit = data["unit"]
            if "par_level" in data:
                item.par_level = float(data["par_level"]) if data["par_level"] else None
            if "expiry_date" in data:
                item.expiry_date = _parse_date(data["expiry_date"])
            if "photo_path" in data:
                item.photo_path = data["photo_path"]
            if "notes" in data:
                item.notes = data["notes"]
            
            item.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(item)
            return item.to_dict()
        except Exception as e:
            print(f"Database error in update_inventory_item: {e}")
            return None

    def delete_inventory_item(self, item_id: int) -> bool:
        """Delete an inventory item by ID."""
        try:
            item = self.db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
            if not item:
                return False
            
            self.db.delete(item)
            self.db.commit()
            return True
        except Exception as e:
            print(f"Database error in delete_inventory_item: {e}")
            return False

    def get_low_stock_items(self) -> List[Dict[str, Any]]:
        """Get inventory items that are below their par level."""
        try:
            items = self.db.query(InventoryItem).filter(
                InventoryItem.par_level.isnot(None),
                InventoryItem.qty < InventoryItem.par_level
            ).order_by(InventoryItem.qty.asc()).all()
            return [i.to_dict() for i in items]
        except Exception as e:
            print(f"Database error in get_low_stock_items: {e}")
            return []

    def get_expiring_items(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get inventory items expiring within the specified number of days."""
        try:
            cutoff_date = date.today() + timedelta(days=days_ahead)
            items = self.db.query(InventoryItem).filter(
                InventoryItem.expiry_date.isnot(None),
                InventoryItem.expiry_date <= cutoff_date
            ).order_by(InventoryItem.expiry_date.asc()).all()
            return [i.to_dict() for i in items]
        except Exception as e:
            print(f"Database error in get_expiring_items: {e}")
            return []

    def get_inventory_dashboard_data(self) -> Dict[str, Any]:
        """Get inventory-specific dashboard data."""
        try:
            items_total = self.db.query(InventoryItem).count()
            low_stock_count = len(self.get_low_stock_items())
            expiring_soon = len(self.get_expiring_items(30))
            
            return {
                "items_total": items_total,
                "low_stock_count": low_stock_count,
                "expiring_soon": expiring_soon,
            }
        except Exception as e:
            print(f"Database error in get_inventory_dashboard_data: {e}")
            return {
                "items_total": 0,
                "low_stock_count": 0,
                "expiring_soon": 0,
            }

    # --- Phase 2: Safety Enhancements (SLICE 3) ---
    def list_safety_drills(self) -> List[Dict[str, Any]]:
        """List all safety drills."""
        try:
            drills = self.db.query(SafetyDrill).order_by(SafetyDrill.next_due.asc()).all()
            return [d.to_dict() for d in drills]
        except Exception as e:
            print(f"Database error in list_safety_drills: {e}")
            return []

    def create_safety_drill(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new safety drill."""
        try:
            drill = SafetyDrill(
                title=data.get("title"),
                cadence=data.get("cadence"),
                next_due=_parse_datetime(data.get("next_due")),
                last_done=_parse_datetime(data.get("last_done")),
                notes=data.get("notes"),
            )
            self.db.add(drill)
            self.db.commit()
            self.db.refresh(drill)
            return drill.to_dict()
        except Exception as e:
            print(f"Database error in create_safety_drill: {e}")
            return {}

    def get_safety_drill(self, drill_id: int) -> Optional[Dict[str, Any]]:
        """Get a single safety drill by ID."""
        try:
            drill = self.db.query(SafetyDrill).filter(SafetyDrill.id == drill_id).first()
            return drill.to_dict() if drill else None
        except Exception as e:
            print(f"Database error in get_safety_drill: {e}")
            return None

    def update_safety_drill(self, drill_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing safety drill."""
        try:
            drill = self.db.query(SafetyDrill).filter(SafetyDrill.id == drill_id).first()
            if not drill:
                return None
            
            # Update fields if provided
            if "title" in data:
                drill.title = data["title"]
            if "cadence" in data:
                drill.cadence = data["cadence"]
            if "next_due" in data:
                drill.next_due = _parse_datetime(data["next_due"])
            if "last_done" in data:
                drill.last_done = _parse_datetime(data["last_done"])
            if "notes" in data:
                drill.notes = data["notes"]
            
            # updated_at will be set automatically by SQLAlchemy
            self.db.commit()
            self.db.refresh(drill)
            return drill.to_dict()
        except Exception as e:
            print(f"Database error in update_safety_drill: {e}")
            return None

    def delete_safety_drill(self, drill_id: int) -> bool:
        """Delete a safety drill by ID."""
        try:
            drill = self.db.query(SafetyDrill).filter(SafetyDrill.id == drill_id).first()
            if not drill:
                return False
            self.db.delete(drill)
            self.db.commit()
            return True
        except Exception as e:
            print(f"Database error in delete_safety_drill: {e}")
            return False

    def complete_safety_drill(self, drill_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Mark a safety drill as completed and calculate next due date."""
        try:
            drill = self.db.query(SafetyDrill).filter(SafetyDrill.id == drill_id).first()
            if not drill:
                return None
            
            # Update last_done
            drill.last_done = _parse_datetime(data.get("ts")) or datetime.utcnow()
            
            # Calculate next_due based on cadence
            if drill.cadence:
                next_due = self._calculate_next_due(drill.last_done, drill.cadence)
                drill.next_due = next_due
            
            # updated_at will be set automatically by SQLAlchemy
            self.db.commit()
            self.db.refresh(drill)
            return drill.to_dict()
        except Exception as e:
            print(f"Database error in complete_safety_drill: {e}")
            return None

    def list_emergency_kits(self) -> List[Dict[str, Any]]:
        """List all emergency kits."""
        try:
            kits = self.db.query(EmergencyKit).order_by(EmergencyKit.next_audit_due.asc()).all()
            return [k.to_dict() for k in kits]
        except Exception as e:
            print(f"Database error in list_emergency_kits: {e}")
            return []

    def create_emergency_kit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new emergency kit."""
        try:
            kit = EmergencyKit(
                location_id=data.get("location_id"),
                contents_json=data.get("contents_json", "[]"),
                last_audited=_parse_datetime(data.get("last_audited")),
                next_audit_due=_parse_datetime(data.get("next_audit_due")),
            )
            self.db.add(kit)
            self.db.commit()
            self.db.refresh(kit)
            return kit.to_dict()
        except Exception as e:
            print(f"Database error in create_emergency_kit: {e}")
            return {}

    def get_emergency_kit(self, kit_id: int) -> Optional[Dict[str, Any]]:
        """Get a single emergency kit by ID."""
        try:
            kit = self.db.query(EmergencyKit).filter(EmergencyKit.id == kit_id).first()
            return kit.to_dict() if kit else None
        except Exception as e:
            print(f"Database error in get_emergency_kit: {e}")
            return None

    def update_emergency_kit(self, kit_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing emergency kit."""
        try:
            kit = self.db.query(EmergencyKit).filter(EmergencyKit.id == kit_id).first()
            if not kit:
                return None
            
            # Update fields if provided
            if "location_id" in data:
                kit.location_id = data["location_id"]
            if "contents_json" in data:
                kit.contents_json = data["contents_json"]
            if "last_audited" in data:
                kit.last_audited = _parse_datetime(data["last_audited"])
            if "next_audit_due" in data:
                kit.next_audit_due = _parse_datetime(data["next_audit_due"])
            
            # updated_at will be set automatically by SQLAlchemy
            self.db.commit()
            self.db.refresh(kit)
            return kit.to_dict()
        except Exception as e:
            print(f"Database error in update_emergency_kit: {e}")
            return None

    def delete_emergency_kit(self, kit_id: int) -> bool:
        """Delete an emergency kit by ID."""
        try:
            kit = self.db.query(EmergencyKit).filter(EmergencyKit.id == kit_id).first()
            if not kit:
                return False
            self.db.delete(kit)
            self.db.commit()
            return True
        except Exception as e:
            print(f"Database error in delete_emergency_kit: {e}")
            return False

    def audit_emergency_kit(self, kit_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Complete an emergency kit audit and calculate next audit due."""
        try:
            kit = self.db.query(EmergencyKit).filter(EmergencyKit.id == kit_id).first()
            if not kit:
                return None
            
            # Update last_audited
            kit.last_audited = _parse_datetime(data.get("ts")) or datetime.utcnow()
            
            # Calculate next_audit_due (default to 6 months from now)
            audit_cadence = data.get("audit_cadence", "6 months")
            next_audit = self._calculate_next_due(kit.last_audited, audit_cadence)
            kit.next_audit_due = next_audit
            
            # updated_at will be set automatically by SQLAlchemy
            self.db.commit()
            self.db.refresh(kit)
            return kit.to_dict()
        except Exception as e:
            print(f"Database error in audit_emergency_kit: {e}")
            return None

    def get_safety_dashboard_data(self) -> Dict[str, Any]:
        """Get safety-specific dashboard metrics."""
        try:
            drills = self.db.query(SafetyDrill).all()
            kits = self.db.query(EmergencyKit).all()
            
            drills_total = len(drills)
            drills_overdue = len([d for d in drills if d.next_due and d.next_due < datetime.utcnow()])
            kits_total = len(kits)
            kits_due_audit = len([k for k in kits if k.next_audit_due and k.next_audit_due < datetime.utcnow()])
            
            return {
                "drills_total": drills_total,
                "drills_overdue": drills_overdue,
                "kits_total": kits_total,
                "kits_due_audit": kits_due_audit
            }
        except Exception as e:
            print(f"Database error in get_safety_dashboard_data: {e}")
            return {"drills_total": 0, "drills_overdue": 0, "kits_total": 0, "kits_due_audit": 0}

    # --- Phase 2: Exports (SLICE 4) ---
    
    def export_assets_csv(self) -> str:
        """Export assets to CSV format."""
        try:
            assets = self.db.query(Asset).order_by(Asset.name.asc()).all()
            
            # CSV header
            csv_lines = [
                "ID,Name,Location,Category,Brand,Model,Serial Number,Purchase Date,Purchase Price,Status,Notes,Created,Updated"
            ]
            
            for asset in assets:
                location_name = asset.location.name if asset.location else "Unknown"
                csv_lines.append(
                    f"{asset.id},{asset.name},{location_name},{asset.category},{asset.brand or ''},"
                    f"{asset.model or ''},{asset.serial_number or ''},{asset.purchase_date or ''},"
                    f"{asset.purchase_price or ''},{asset.status},{asset.notes or ''},"
                    f"{asset.created_at},{asset.updated_at}"
                )
            
            return "\n".join(csv_lines)
        except Exception as e:
            print(f"Database error in export_assets_csv: {e}")
            return "ID,Name,Location,Category,Brand,Model,Serial Number,Purchase Date,Purchase Price,Status,Notes,Created,Updated"
    
    def export_maintenance_events_csv(self) -> str:
        """Export maintenance events to CSV format."""
        try:
            events = self.db.query(MaintenanceEvent).order_by(MaintenanceEvent.completed_at.desc()).all()
            
            # CSV header
            csv_lines = [
                "ID,Asset,Plan,Completed Date,Cost,Technician,Notes,Status,Created,Updated"
            ]
            
            for event in events:
                asset_name = event.asset.name if event.asset else "Unknown"
                plan_name = event.plan.name if event.plan else "Ad-hoc"
                csv_lines.append(
                    f"{event.id},{asset_name},{plan_name},{event.completed_at or ''},"
                    f"{event.cost or ''},{event.technician or ''},{event.notes or ''},"
                    f"{event.status},{event.created_at},{event.updated_at}"
                )
            
            return "\n".join(csv_lines)
        except Exception as e:
            print(f"Database error in export_maintenance_events_csv: {e}")
            return "ID,Asset,Plan,Completed Date,Cost,Technician,Notes,Status,Created,Updated"
    
    def export_inventory_csv(self) -> str:
        """Export inventory items to CSV format."""
        try:
            items = self.db.query(InventoryItem).order_by(InventoryItem.location_id.asc(), InventoryItem.name.asc()).all()
            
            # CSV header
            csv_lines = [
                "ID,Name,Location,Category,Quantity,Unit,Low Stock Threshold,Expiry Date,Notes,Created,Updated"
            ]
            
            for item in items:
                location_name = item.location.name if item.location else "Unknown"
                csv_lines.append(
                    f"{item.id},{item.name},{location_name},{item.category},{item.quantity},"
                    f"{item.unit},{item.low_stock_threshold or ''},{item.expiry_date or ''},"
                    f"{item.notes or ''},{item.created_at},{item.updated_at}"
                )
            
            return "\n".join(csv_lines)
        except Exception as e:
            print(f"Database error in export_inventory_csv: {e}")
            return "ID,Name,Location,Category,Quantity,Unit,Low Stock Threshold,Expiry Date,Notes,Created,Updated"
    
    def export_combined_csv(self) -> str:
        """Export combined data (assets, maintenance, inventory) to CSV format."""
        try:
            # Get all data
            assets = self.db.query(Asset).order_by(Asset.name.asc()).all()
            events = self.db.query(MaintenanceEvent).order_by(MaintenanceEvent.completed_at.desc()).all()
            inventory = self.db.query(InventoryItem).order_by(InventoryItem.location_id.asc(), InventoryItem.name.asc()).all()
            
            csv_lines = []
            
            # Assets section
            csv_lines.append("=== ASSETS ===")
            csv_lines.append("ID,Name,Location,Category,Brand,Model,Serial Number,Purchase Date,Purchase Price,Status,Notes")
            for asset in assets:
                location_name = asset.location.name if asset.location else "Unknown"
                csv_lines.append(
                    f"{asset.id},{asset.name},{location_name},{asset.category},{asset.brand or ''},"
                    f"{asset.model or ''},{asset.serial_number or ''},{asset.purchase_date or ''},"
                    f"{asset.purchase_price or ''},{asset.status},{asset.notes or ''}"
                )
            
            csv_lines.append("")  # Empty line between sections
            
            # Maintenance Events section
            csv_lines.append("=== MAINTENANCE EVENTS ===")
            csv_lines.append("ID,Asset,Plan,Completed Date,Cost,Technician,Notes,Status")
            for event in events:
                asset_name = event.asset.name if event.asset else "Unknown"
                plan_name = event.plan.name if event.plan else "Ad-hoc"
                csv_lines.append(
                    f"{event.id},{asset_name},{plan_name},{event.completed_at or ''},"
                    f"{event.cost or ''},{event.technician or ''},{event.notes or ''},{event.status}"
                )
            
            csv_lines.append("")  # Empty line between sections
            
            # Inventory section
            csv_lines.append("=== INVENTORY ===")
            csv_lines.append("ID,Name,Location,Category,Quantity,Unit,Low Stock Threshold,Expiry Date,Notes")
            for item in inventory:
                location_name = item.location.name if item.location else "Unknown"
                csv_lines.append(
                    f"{item.id},{item.name},{location_name},{item.category},{item.quantity},"
                    f"{item.unit},{item.low_stock_threshold or ''},{item.expiry_date or ''},{item.notes or ''}"
                )
            
            return "\n".join(csv_lines)
        except Exception as e:
            print(f"Database error in export_combined_csv: {e}")
            return "Error exporting data"

    def _calculate_next_due(self, from_date: datetime, cadence: str) -> datetime:
        """Calculate next due date based on cadence string."""
        try:
            # Parse cadence like "3 months", "2 weeks", "1 year"
            import re
            match = re.match(r'(\d+)\s+(day|week|month|year)s?', cadence.lower())
            if not match:
                return from_date + timedelta(days=30)  # Default to 30 days
            
            amount = int(match.group(1))
            unit = match.group(2)
            
            if unit == "day":
                return from_date + timedelta(days=amount)
            elif unit == "week":
                return from_date + timedelta(weeks=amount)
            elif unit == "month":
                # Approximate month as 30 days
                return from_date + timedelta(days=amount * 30)
            elif unit == "year":
                # Approximate year as 365 days
                return from_date + timedelta(days=amount * 365)
            else:
                return from_date + timedelta(days=30)
        except Exception:
            return from_date + timedelta(days=30)


