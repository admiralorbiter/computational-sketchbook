from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Location(Base):
    __tablename__ = 'location'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    parent_id = Column(Integer, ForeignKey('location.id'))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Asset(Base):
    __tablename__ = 'asset'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    type = Column(String(80))
    brand = Column(String(120))
    model = Column(String(120))
    serial = Column(String(120))
    purchase_date = Column(Date)
    purchase_price = Column(Float)
    location_id = Column(Integer, ForeignKey('location.id'))
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'brand': self.brand,
            'model': self.model,
            'serial': self.serial,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'purchase_price': self.purchase_price,
            'location_id': self.location_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Manual(Base):
    __tablename__ = 'manual'
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('asset.id'), nullable=False)
    file_path = Column(String(500))
    url = Column(String(500))
    note = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'file_path': self.file_path,
            'url': self.url,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Warranty(Base):
    __tablename__ = 'warranty'
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('asset.id'), nullable=False)
    provider = Column(String(255))
    policy_no = Column(String(255))
    start_date = Column(Date)
    end_date = Column(Date)
    coverage_note = Column(Text)
    claim_steps = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'provider': self.provider,
            'policy_no': self.policy_no,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'coverage_note': self.coverage_note,
            'claim_steps': self.claim_steps,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class MaintenancePlan(Base):
    __tablename__ = 'maintenance_plan'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    asset_id = Column(Integer, ForeignKey('asset.id'))
    cadence = Column(String(120), nullable=False)
    next_due = Column(Date)
    last_done = Column(Date)
    checklist_json = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'asset_id': self.asset_id,
            'cadence': self.cadence,
            'next_due': self.next_due.isoformat() if self.next_due else None,
            'last_done': self.last_done.isoformat() if self.last_done else None,
            'checklist_json': self.checklist_json,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class MaintenanceEvent(Base):
    __tablename__ = 'maintenance_event'
    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('maintenance_plan.id'), nullable=False)
    ts = Column(DateTime, server_default=func.now())
    notes = Column(Text)
    cost = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'ts': self.ts.isoformat() if self.ts else None,
            'notes': self.notes,
            'cost': self.cost,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class ChorePlan(Base):
    __tablename__ = 'chore_plan'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    cadence = Column(String(120), nullable=False)
    location_id = Column(Integer, ForeignKey('location.id'))
    next_due = Column(Date)
    last_done = Column(Date)
    checklist_json = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'cadence': self.cadence,
            'location_id': self.location_id,
            'next_due': self.next_due.isoformat() if self.next_due else None,
            'last_done': self.last_done.isoformat() if self.last_done else None,
            'checklist_json': self.checklist_json,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class ChoreEvent(Base):
    __tablename__ = 'chore_event'
    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('chore_plan.id'), nullable=False)
    ts = Column(DateTime, server_default=func.now())
    who = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'ts': self.ts.isoformat() if self.ts else None,
            'who': self.who,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class SafetyDevice(Base):
    __tablename__ = 'safety_device'
    id = Column(Integer, primary_key=True)
    type = Column(String(80), nullable=False)
    location_id = Column(Integer, ForeignKey('location.id'))
    model = Column(String(120))
    purchase_date = Column(Date)
    expiry_date = Column(Date)
    test_cadence = Column(String(120))
    next_test_due = Column(Date)
    last_test = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'location_id': self.location_id,
            'model': self.model,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'test_cadence': self.test_cadence,
            'next_test_due': self.next_test_due.isoformat() if self.next_test_due else None,
            'last_test': self.last_test.isoformat() if self.last_test else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# --- Phase 2: Utilities Models ---
class UtilityAccount(Base):
    __tablename__ = 'utility_account'
    id = Column(Integer, primary_key=True)
    provider = Column(String(255), nullable=False)
    service_type = Column(String(80), nullable=False)
    account_no = Column(String(255))
    start_date = Column(Date)
    renewal_date = Column(Date)
    website = Column(String(500))
    support_phone = Column(String(80))
    address = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'provider': self.provider,
            'service_type': self.service_type,
            'account_no': self.account_no,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'renewal_date': self.renewal_date.isoformat() if self.renewal_date else None,
            'website': self.website,
            'support_phone': self.support_phone,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class RateSnapshot(Base):
    __tablename__ = 'rate_snapshot'
    id = Column(Integer, primary_key=True)
    utility_account_id = Column(Integer, ForeignKey('utility_account.id'), nullable=False)
    effective_date = Column(Date, nullable=False)
    unit_price = Column(Float)
    unit_name = Column(String(80))
    base_fee = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'utility_account_id': self.utility_account_id,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'unit_price': self.unit_price,
            'unit_name': self.unit_name,
            'base_fee': self.base_fee,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class OutageReport(Base):
    __tablename__ = 'outage_report'
    id = Column(Integer, primary_key=True)
    utility_account_id = Column(Integer, ForeignKey('utility_account.id'), nullable=False)
    start_ts = Column(DateTime, nullable=False)
    end_ts = Column(DateTime)
    ticket_no = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'utility_account_id': self.utility_account_id,
            'start_ts': self.start_ts.isoformat() if self.start_ts else None,
            'end_ts': self.end_ts.isoformat() if self.end_ts else None,
            'ticket_no': self.ticket_no,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# --- Phase 2: Inventory Models (SLICE 2) ---
class InventoryItem(Base):
    __tablename__ = 'inventory_item'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(80))
    location_id = Column(Integer, ForeignKey('location.id'))
    qty = Column(Float, default=1.0)
    unit = Column(String(80))
    par_level = Column(Float)
    expiry_date = Column(Date)
    photo_path = Column(String(500))
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'location_id': self.location_id,
            'qty': self.qty,
            'unit': self.unit,
            'par_level': self.par_level,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'photo_path': self.photo_path,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class EmergencyKit(Base):
    __tablename__ = 'emergency_kit'
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('location.id'))
    contents_json = Column(Text)
    last_audited = Column(DateTime)
    next_audit_due = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'location_id': self.location_id,
            'contents_json': self.contents_json,
            'last_audited': self.last_audited.isoformat() if self.last_audited else None,
            'next_audit_due': self.next_audit_due.isoformat() if self.next_audit_due else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class SafetyDrill(Base):
    __tablename__ = 'safety_drill'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    cadence = Column(String(120))
    next_due = Column(DateTime)
    last_done = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'cadence': self.cadence,
            'next_due': self.next_due.isoformat() if self.next_due else None,
            'last_done': self.last_done.isoformat() if self.last_done else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


