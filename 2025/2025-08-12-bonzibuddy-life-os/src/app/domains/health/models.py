from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Med(Base):
    """Medication entity"""
    __tablename__ = 'med'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    dose_text = Column(Text)
    # Prescription support fields
    dosage = Column(Text)  # strength, e.g., "50 mg"
    qty = Column(Integer)  # quantity dispensed
    refills_left = Column(Integer)
    last_refilled = Column(DateTime)
    qty_per_day = Column(Float)  # doses per day
    condition = Column(String(255))
    pharmacy = Column(String(255))
    notes = Column(Text)
    # OTC fields
    is_otc = Column(Boolean, default=False)
    on_hand_qty = Column(Float, default=0.0)
    unit = Column(String(50))
    low_threshold = Column(Float, default=0.0)
    is_low = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    events = relationship("MedEvent", back_populates="med", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'dose_text': self.dose_text,
            'dosage': self.dosage,
            'qty': self.qty,
            'refills_left': self.refills_left,
            'last_refilled': self.last_refilled.isoformat() if self.last_refilled else None,
            'qty_per_day': self.qty_per_day,
            'condition': self.condition,
            'pharmacy': self.pharmacy,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'adherence_pct': getattr(self, 'adherence_pct', None),
            'supply': getattr(self, 'supply', None),
            'is_otc': self.is_otc,
            'on_hand_qty': self.on_hand_qty,
            'unit': self.unit,
            'low_threshold': self.low_threshold
            , 'is_low': self.is_low
        }

class MedEvent(Base):
    """Medication event/adherence log"""
    __tablename__ = 'med_event'
    
    id = Column(Integer, primary_key=True)
    med_id = Column(Integer, ForeignKey('med.id'), nullable=False, index=True)
    ts = Column(DateTime, nullable=False, default=func.now(), index=True)
    amount = Column(Float)
    note = Column(Text)
    
    # Relationships
    med = relationship("Med", back_populates="events")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'med_id': self.med_id,
            'ts': self.ts.isoformat() if self.ts else None,
            'amount': self.amount,
            'note': self.note
        }

class SymptomLog(Base):
    """Symptom logging"""
    __tablename__ = 'symptom_log'
    
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, nullable=False, default=func.now(), index=True)
    label = Column(String(255), nullable=False, index=True)
    severity = Column(Integer, nullable=False)  # 1-5 scale
    trigger = Column(Text)
    note = Column(Text)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'ts': self.ts.isoformat() if self.ts else None,
            'label': self.label,
            'severity': self.severity,
            'trigger': self.trigger,
            'note': self.note
        }

class Vital(Base):
    """Vital signs and measurements"""
    __tablename__ = 'vital'
    
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, nullable=False, default=func.now(), index=True)
    kind = Column(String(100), nullable=False, index=True)  # BP, HR, weight, temp, etc.
    value_num = Column(Float, nullable=False)
    unit = Column(String(50))
    note = Column(Text)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'ts': self.ts.isoformat() if self.ts else None,
            'kind': self.kind,
            'value_num': self.value_num,
            'unit': self.unit,
            'note': self.note
        }

class Appointment(Base):
    """Medical appointments"""
    __tablename__ = 'appointment'
    
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, nullable=False, index=True)
    provider = Column(String(255), nullable=False)
    location = Column(String(255))
    purpose = Column(Text)
    note = Column(Text)
    specialty = Column(String(255))
    is_virtual = Column(Boolean, default=False)
    status = Column(String(50), default='planned')
    reminder_days = Column(Integer)
    follow_up_ts = Column(DateTime)
    lab_due_ts = Column(DateTime)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'ts': self.ts.isoformat() if self.ts else None,
            'provider': self.provider,
            'location': self.location,
            'purpose': self.purpose,
            'note': self.note,
            'specialty': self.specialty,
            'is_virtual': self.is_virtual,
            'status': self.status,
            'reminder_days': self.reminder_days,
            'follow_up_ts': self.follow_up_ts.isoformat() if self.follow_up_ts else None,
            'lab_due_ts': self.lab_due_ts.isoformat() if self.lab_due_ts else None
        }

class AppointmentTask(Base):
    """Checklist tasks for appointments"""
    __tablename__ = 'appointment_task'
    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey('appointment.id'), nullable=False, index=True)
    label = Column(Text, nullable=False)
    due_ts = Column(DateTime)
    done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'label': self.label,
            'due_ts': self.due_ts.isoformat() if self.due_ts else None,
            'done': self.done,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class LabOrder(Base):
    """Standalone lab orders that can optionally link to an appointment"""
    __tablename__ = 'lab_order'
    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey('appointment.id'))
    label = Column(String(255), nullable=False)
    kind = Column(String(100))  # bloodwork, imaging, urine, etc.
    provider = Column(String(255))
    location = Column(String(255))
    instructions = Column(Text)
    status = Column(String(50), default='ordered')
    ordered_ts = Column(DateTime, default=func.now())
    scheduled_ts = Column(DateTime)
    due_ts = Column(DateTime)
    completed_ts = Column(DateTime)
    reminder_days = Column(Integer)
    result_note = Column(Text)
    created_at = Column(DateTime, default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'label': self.label,
            'kind': self.kind,
            'provider': self.provider,
            'location': self.location,
            'instructions': self.instructions,
            'status': self.status,
            'ordered_ts': self.ordered_ts.isoformat() if self.ordered_ts else None,
            'scheduled_ts': self.scheduled_ts.isoformat() if self.scheduled_ts else None,
            'due_ts': self.due_ts.isoformat() if self.due_ts else None,
            'completed_ts': self.completed_ts.isoformat() if self.completed_ts else None,
            'reminder_days': self.reminder_days,
            'result_note': self.result_note,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Sensors/CGM
class SensorType(Base):
    __tablename__ = 'sensor_type'
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    label = Column(String(255), nullable=False)
    wear_days = Column(Integer, nullable=False, default=15)
    pack_size = Column(Integer, nullable=False, default=2)
    default_lead_time_days = Column(Integer, nullable=False, default=7)
    default_reminder_days = Column(Integer, nullable=False, default=3)
    safety_stock = Column(Integer, nullable=False, default=1)

    def to_dict(self):
        return {
            'key': self.key,
            'label': self.label,
            'wear_days': self.wear_days,
            'pack_size': self.pack_size,
            'default_lead_time_days': self.default_lead_time_days,
            'default_reminder_days': self.default_reminder_days,
            'safety_stock': self.safety_stock,
        }

class SensorUse(Base):
    __tablename__ = 'sensor_use'
    id = Column(Integer, primary_key=True)
    type_key = Column(String(100), nullable=False, index=True)
    start_ts = Column(DateTime, nullable=False, index=True)
    end_ts_expected = Column(DateTime)
    end_ts_actual = Column(DateTime)
    note = Column(Text)
    created_at = Column(DateTime, default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'type_key': self.type_key,
            'start_ts': self.start_ts.isoformat() if self.start_ts else None,
            'end_ts_expected': self.end_ts_expected.isoformat() if self.end_ts_expected else None,
            'end_ts_actual': self.end_ts_actual.isoformat() if self.end_ts_actual else None,
            'note': self.note,
        }

class SensorInventory(Base):
    __tablename__ = 'sensor_inventory'
    id = Column(Integer, primary_key=True)
    type_key = Column(String(100), nullable=False, index=True)
    ts = Column(DateTime, default=func.now(), index=True)
    delta_sensors = Column(Integer, nullable=False)
    source = Column(String(50), nullable=False)  # purchase|adjust|waste|correction
    note = Column(Text)

    def to_dict(self):
        return {
            'id': self.id,
            'type_key': self.type_key,
            'ts': self.ts.isoformat() if self.ts else None,
            'delta_sensors': self.delta_sensors,
            'source': self.source,
            'note': self.note
        }

# Oura OAuth Models
class OuraUser(Base):
    """Oura user account"""
    __tablename__ = 'oura_user'
    
    user_id = Column(String(255), primary_key=True)  # Oura user ID
    email = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    last_sync = Column(DateTime)
    
    # Relationships
    tokens = relationship("OuraToken", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None
        }

class OuraToken(Base):
    """Oura OAuth tokens"""
    __tablename__ = 'oura_token'
    
    user_id = Column(String(255), ForeignKey('oura_user.user_id'), primary_key=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    expires_at = Column(Integer, nullable=False)  # Unix timestamp
    scope = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("OuraUser", back_populates="tokens")
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_at': self.expires_at,
            'scope': self.scope,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def is_expired(self):
        """Check if token is expired"""
        from datetime import datetime
        return datetime.now().timestamp() > self.expires_at

# Core tables (already exist in migration 0001)
class Profile(Base):
    """User profile"""
    __tablename__ = 'profile'
    
    id = Column(Integer, primary_key=True)
    display_name = Column(String(255))
    timezone = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'display_name': self.display_name,
            'timezone': self.timezone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Tag(Base):
    """Tags for categorizing health data"""
    __tablename__ = 'tag'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name
        }

class Attachment(Base):
    """File attachments for health records"""
    __tablename__ = 'attachment'
    
    id = Column(Integer, primary_key=True)
    path = Column(String(500), nullable=False)
    mime = Column(String(100))
    bytes = Column(Integer)
    note = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'path': self.path,
            'mime': self.mime,
            'bytes': self.bytes,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Audit(Base):
    """Audit log for health data changes"""
    __tablename__ = 'audit'
    
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=func.now(), index=True)
    actor = Column(String(100))
    action = Column(String(100), nullable=False)
    entity = Column(String(100), nullable=False)
    entity_id = Column(Integer)
    note = Column(Text)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'ts': self.ts.isoformat() if self.ts else None,
            'actor': self.actor,
            'action': self.action,
            'entity': self.entity,
            'entity_id': self.entity_id,
            'note': self.note
        }
