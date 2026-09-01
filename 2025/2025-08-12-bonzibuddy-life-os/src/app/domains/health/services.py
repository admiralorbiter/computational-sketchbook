from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import csv
import os
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from .models import Med, MedEvent, SymptomLog, Vital, Appointment, AppointmentTask, LabOrder, SensorType, SensorUse, SensorInventory, Audit

# Oura OAuth Service
from authlib.integrations.flask_client import OAuth
from datetime import datetime, timedelta
import requests
import json
from flask import current_app

def init_oura_oauth(app):
    """Initialize Oura OAuth client"""
    oauth = OAuth(app)
    
    oauth.register(
        name='oura',
        client_id=app.config['OURA_CLIENT_ID'],
        client_secret=app.config['OURA_CLIENT_SECRET'],
        access_token_url=app.config['OURA_TOKEN_URL'],
        access_token_params=None,
        authorize_url=app.config['OURA_AUTHORIZE_URL'],
        authorize_params=None,
        api_base_url=app.config['OURA_API_BASE_URL'],
        client_kwargs={
            'scope': app.config['OURA_SCOPE']
        }
    )
    
    return oauth

def get_oura_user_info(access_token):
    """Get user info from Oura API"""
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(
        f"{current_app.config['OURA_API_BASE_URL']}v2/usercollection/personal_info",
        headers=headers
    )
    response.raise_for_status()
    return response.json()

def store_oura_user(user_info, token):
    """Store or update Oura user and tokens in database"""
    from .models import OuraUser, OuraToken
    from app.core.db import get_session
    
    db = get_session()
    
    # Create or update user
    user = db.query(OuraUser).filter_by(user_id=user_info['id']).first()
    if not user:
        user = OuraUser(
            user_id=user_info['id'],
            email=user_info.get('email', ''),
            created_at=datetime.now()
        )
        db.add(user)
    else:
        user.email = user_info.get('email', user.email)
        user.last_sync = datetime.now()
    
    # Store or update tokens
    token_record = db.query(OuraToken).filter_by(user_id=user_info['id']).first()
    if not token_record:
        token_record = OuraToken(
            user_id=user_info['id'],
            access_token=token['access_token'],
            refresh_token=token.get('refresh_token', ''),
            expires_at=int(token.get('expires_at', 0)),
            scope=token.get('scope', '')
        )
        db.add(token_record)
    else:
        token_record.access_token = token['access_token']
        token_record.refresh_token = token.get('refresh_token', token_record.refresh_token)
        token_record.expires_at = int(token.get('expires_at', 0))
        token_record.scope = token.get('scope', token_record.scope)
    
    db.commit()
    return user

def get_valid_oura_token(user_id):
    """Get valid Oura access token for user, refresh if needed"""
    from .models import OuraToken
    from app.core.db import get_session
    
    db = get_session()
    token_record = db.query(OuraToken).filter_by(user_id=user_id).first()
    
    if not token_record:
        return None
    
    if token_record.is_expired():
        # Token expired, need to refresh
        new_token = refresh_oura_token(token_record.refresh_token)
        if new_token:
            token_record.access_token = new_token['access_token']
            token_record.expires_at = int(new_token.get('expires_at', 0))
            db.commit()
            return new_token['access_token']
        else:
            return None
    
    return token_record.access_token

def refresh_oura_token(refresh_token):
    """Refresh Oura access token"""
    try:
        response = requests.post(
            current_app.config['OURA_TOKEN_URL'],
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': current_app.config['OURA_CLIENT_ID'],
                'client_secret': current_app.config['OURA_CLIENT_SECRET']
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        current_app.logger.error(f"Oura token refresh error: {e}")
        return None

def get_oura_sleep_data(user_id, start_date=None, end_date=None):
    """Get sleep data from Oura API"""
    access_token = get_valid_oura_token(user_id)
    if not access_token:
        return None
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Default to last 7 days if no dates specified
    if not start_date:
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        response = requests.get(
            f"{current_app.config['OURA_API_BASE_URL']}v2/usercollection/daily_sleep",
            headers=headers,
            params={'start_date': start_date, 'end_date': end_date}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        current_app.logger.error(f"Oura sleep data error: {e}")
        return None

def get_oura_activity_data(user_id, start_date=None, end_date=None):
    """Get activity data from Oura API"""
    access_token = get_valid_oura_token(user_id)
    if not access_token:
        return None
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Default to last 7 days if no dates specified
    if not start_date:
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        response = requests.get(
            f"{current_app.config['OURA_API_BASE_URL']}v2/usercollection/daily_activity",
            headers=headers,
            params={'start_date': start_date, 'end_date': end_date}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        current_app.logger.error(f"Oura activity data error: {e}")
        return None

def get_oura_readiness_data(user_id, start_date=None, end_date=None):
    """Get readiness data from Oura API"""
    access_token = get_valid_oura_token(user_id)
    if not access_token:
        return None
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    if not start_date:
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        response = requests.get(
            f"{current_app.config['OURA_API_BASE_URL']}v2/usercollection/daily_readiness",
            headers=headers,
            params={'start_date': start_date, 'end_date': end_date}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        current_app.logger.error(f"Oura readiness data error: {e}")
        return None

class HealthService:
    """Service layer for health domain business logic"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    # Medication Management
    
    def get_meds(self) -> List[Med]:
        """Get all medications with adherence data"""
        meds = self.db.query(Med).all()
        for med in meds:
            # Preserve adherence for backward compatibility (unused by UI)
            med.adherence_pct = self._calculate_adherence(med.id)
            # Add supply status for UI
            med.supply = self._calculate_supply(med)
        return meds
    
    def get_med(self, med_id: int) -> Optional[Med]:
        """Get medication by ID"""
        med = self.db.query(Med).filter(Med.id == med_id).first()
        if med:
            med.adherence_pct = self._calculate_adherence(med.id)
            med.supply = self._calculate_supply(med)
        return med
    
    def create_med(self, data: Dict[str, Any]) -> Med:
        """Create a new medication"""
        last_refilled_dt = self._parse_last_refilled(data.get('last_refilled'))

        med = Med(
            name=data['name'],
            dose_text=data.get('dose_text'),
            dosage=data.get('dosage'),
            qty=self._coerce_int(data.get('qty')),
            refills_left=self._coerce_int(data.get('refills_left')),
            last_refilled=last_refilled_dt,
            qty_per_day=self._coerce_float(data.get('qty_per_day')),
            condition=data.get('condition'),
            pharmacy=data.get('pharmacy') or data.get('provider'),
            notes=data.get('notes'),
            is_otc=bool(data.get('is_otc', False)),
            on_hand_qty=self._coerce_float(data.get('on_hand_qty')) or 0.0,
            unit=data.get('unit'),
            low_threshold=self._coerce_float(data.get('low_threshold')) or 0.0,
            is_low=bool(data.get('is_low', False))
        )
        self.db.add(med)
        self.db.commit()
        self.db.refresh(med)
        
        # Log audit
        self._log_audit('create', 'med', med.id, f"Created medication: {med.name}")
        
        return med
    
    def update_med(self, med_id: int, data: Dict[str, Any]) -> Optional[Med]:
        """Update medication"""
        med = self.db.query(Med).filter(Med.id == med_id).first()
        if not med:
            return None
        
        # Track changes for audit
        changes = []
        for key, raw_value in data.items():
            if not hasattr(med, key):
                continue
            value = raw_value
            if key in ('qty', 'refills_left'):
                value = self._coerce_int(raw_value)
            elif key in ('qty_per_day','on_hand_qty','low_threshold'):
                value = self._coerce_float(raw_value)
            elif key == 'last_refilled':
                value = self._parse_last_refilled(raw_value)
            elif key in ('is_otc','is_low'):
                value = bool(raw_value)

            if getattr(med, key) != value:
                changes.append(f"{key}: {getattr(med, key)} → {value}")
                setattr(med, key, value)
        
        if changes:
            self.db.commit()
            self._log_audit('update', 'med', med_id, f"Updated: {', '.join(changes)}")
        
        return med
    
    def delete_med(self, med_id: int) -> bool:
        """Delete medication and all associated events"""
        med = self.db.query(Med).filter(Med.id == med_id).first()
        if not med:
            return False
        
        med_name = med.name
        self.db.delete(med)
        self.db.commit()
        
        self._log_audit('delete', 'med', med_id, f"Deleted medication: {med_name}")
        return True
    
    def log_med_event(self, med_id: int, amount: float, note: Optional[str] = None) -> Optional[MedEvent]:
        """Log a medication event"""
        # Verify medication exists
        med = self.db.query(Med).filter(Med.id == med_id).first()
        if not med:
            return None
        
        event = MedEvent(
            med_id=med_id,
            amount=amount,
            note=note
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        self._log_audit('create', 'med_event', event.id, f"Logged {amount} of {med.name}")
        # OTC auto-decrement stock (defensive for mocks/None values)
        try:
            if getattr(med, 'is_otc', False):
                current = getattr(med, 'on_hand_qty', 0.0) or 0.0
                current = float(current)
                amt = float(amount or 0.0)
                new_qty = max(0.0, current - amt)
                if new_qty != current:
                    med.on_hand_qty = new_qty
                    self.db.commit()
        except Exception:
            pass
        return event

    # OTC summary
    def get_otc_summary(self) -> Dict[str, Any]:
        items = self.db.query(Med).filter(Med.is_otc == True).all()  # noqa: E712
        result = []
        low_count = 0
        for m in items:
            # If using explicit is_low flag, prefer it; else fallback to thresholds if provided
            low = bool(getattr(m, 'is_low', False))
            if not low:
                if m.low_threshold not in (None, 0) and m.on_hand_qty is not None:
                    low = (m.on_hand_qty or 0.0) <= (m.low_threshold or 0.0)
            if low:
                low_count += 1
            result.append({
                'id': m.id,
                'name': m.name,
                'on_hand_qty': m.on_hand_qty or 0.0,
                'unit': m.unit,
                'low': low
            })
        return {'total': len(items), 'low_count': low_count, 'items': result}
    
    def get_med_events(self, med_id: int, days: int = 30) -> List[MedEvent]:
        """Get medication events for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return self.db.query(MedEvent).filter(
            and_(
                MedEvent.med_id == med_id,
                MedEvent.ts >= cutoff_date
            )
        ).order_by(MedEvent.ts.desc()).all()
    
    def _calculate_adherence(self, med_id: int, days: int = 14) -> Optional[float]:
        """Calculate medication adherence percentage for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        # Load med for schedule context
        med: Optional[Med] = self.db.query(Med).filter(Med.id == med_id).first()
        
        # Count events in the period
        event_count = self.db.query(func.count(MedEvent.id)).filter(
            and_(
                MedEvent.med_id == med_id,
                MedEvent.ts >= cutoff_date
            )
        ).scalar()
        
        # Use qty_per_day if available, else assume 1/day
        qty_per_day = med.qty_per_day if med and med.qty_per_day else 1
        target_count = days * qty_per_day
        if target_count == 0:
            return None
        
        adherence = (float(event_count) / float(target_count)) * 100
        return min(100.0, max(0.0, adherence))

    def _calculate_supply(self, med: Med, soon_threshold_days: int = 7) -> Optional[Dict[str, Any]]:
        """Calculate supply status for a medication using qty, qty_per_day, and last_refilled.

        Returns None if insufficient data.
        """
        if not med:
            return None
        if med.qty is None or med.qty_per_day in (None, 0) or med.last_refilled is None:
            return None
        try:
            total_days = float(med.qty) / float(med.qty_per_day)
            if total_days <= 0:
                return None
            now = datetime.now()
            days_elapsed = (now - med.last_refilled).total_seconds() / 86400.0
            days_remaining = total_days - days_elapsed
            percent_left = max(0.0, min(100.0, (max(0.0, days_remaining) / total_days) * 100.0))
            refill_date = (med.last_refilled + timedelta(days=total_days))
            pills_remaining = max(0, int(round(days_remaining * float(med.qty_per_day))))
            return {
                'days_total': round(total_days, 1),
                'days_elapsed': round(days_elapsed, 1),
                'days_remaining': round(days_remaining, 1),
                'percent_left': round(percent_left, 1),
                'refill_date': refill_date.isoformat(),
                'due_soon': days_remaining <= float(soon_threshold_days),
                'overdue': days_remaining < 0.0,
                'pills_remaining': pills_remaining,
                'pills_total': med.qty
            }
        except Exception:
            return None

    # Import prescriptions from CSV
    def import_meds_from_csv(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Import or upsert medications from a CSV file.

        Expected headers (case/space-insensitive):
        name, dosage, qty, refill left, last refilled, qty per day, notes, condition, provider|pharmacy
        """
        default_path = os.path.join('data', 'health - prescriptions.csv')
        path = file_path or default_path
        if not os.path.exists(path):
            raise FileNotFoundError(f"CSV not found: {path}")

        created = 0
        updated = 0
        total = 0

        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                total += 1
                normalized = {self._normalize_header(k): (v.strip() if isinstance(v, str) else v)
                              for k, v in row.items()}

                data = {
                    'name': normalized.get('name'),
                    'dosage': normalized.get('dosage'),
                    'dose_text': normalized.get('dose_text'),
                    'qty': self._coerce_int(normalized.get('qty')),
                    'refills_left': self._coerce_int(normalized.get('refill_left')),
                    'last_refilled': self._normalize_date_str(normalized.get('last_refilled')),
                    'qty_per_day': self._coerce_float(normalized.get('qty_per_day')),
                    'notes': normalized.get('notes'),
                    'condition': normalized.get('condition'),
                    'pharmacy': normalized.get('pharmacy') or normalized.get('provider')
                }

                if not data['name']:
                    continue

                # Upsert by (name, dosage)
                existing: Optional[Med] = self.db.query(Med).filter(
                    and_(Med.name == data['name'], Med.dosage == data.get('dosage'))
                ).first()

                if existing is None:
                    self.create_med(data)
                    created += 1
                else:
                    self.update_med(existing.id, data)
                    updated += 1

        return {'created': created, 'updated': updated, 'total': total}

    # Helpers
    @staticmethod
    def _normalize_header(header: str) -> str:
        if header is None:
            return ''
        return header.strip().lower().replace(' ', '_')

    @staticmethod
    def _coerce_int(value: Any) -> Optional[int]:
        if value is None or value == '':
            return None
        try:
            return int(float(value))
        except Exception:
            return None

    @staticmethod
    def _coerce_float(value: Any) -> Optional[float]:
        if value is None or value == '':
            return None
        try:
            return float(value)
        except Exception:
            return None

    @staticmethod
    def _normalize_date_str(date_str: Optional[str]) -> Optional[str]:
        if not date_str:
            return None
        # If it's already ISO-like, return as-is
        ds = date_str.strip()
        return ds

    @staticmethod
    def _parse_last_refilled(value: Any) -> Optional[datetime]:
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        s = str(value).strip()
        # Try ISO
        try:
            return datetime.fromisoformat(s)
        except Exception:
            pass
        # Try common US formats
        for fmt in ('%m/%d/%y', '%m/%d/%Y', '%Y-%m-%d'):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                continue
        return None
    
    # Symptom Management
    
    def get_symptoms(self, days: int = 30) -> List[SymptomLog]:
        """Get symptoms for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return self.db.query(SymptomLog).filter(
            SymptomLog.ts >= cutoff_date
        ).order_by(SymptomLog.ts.desc()).all()
    
    def log_symptom(self, data: Dict[str, Any]) -> SymptomLog:
        """Log a new symptom"""
        symptom = SymptomLog(
            label=data['label'],
            severity=data['severity'],
            trigger=data.get('trigger'),
            note=data.get('note')
        )
        self.db.add(symptom)
        self.db.commit()
        self.db.refresh(symptom)
        
        self._log_audit('create', 'symptom_log', symptom.id, f"Logged symptom: {symptom.label}")
        return symptom
    
    def get_symptom_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get symptom summary for dashboard"""
        cutoff_date = datetime.now() - timedelta(days=days)
        symptoms = self.db.query(SymptomLog).filter(
            SymptomLog.ts >= cutoff_date
        ).all()
        
        if not symptoms:
            return {
                'total': 0,
                'by_severity': {},
                'by_label': {},
                'avg_severity': 0
            }
        
        # Group by severity
        by_severity = {}
        by_label = {}
        total_severity = 0
        
        for symptom in symptoms:
            by_severity[symptom.severity] = by_severity.get(symptom.severity, 0) + 1
            by_label[symptom.label] = by_label.get(symptom.label, 0) + 1
            total_severity += symptom.severity
        
        return {
            'total': len(symptoms),
            'by_severity': by_severity,
            'by_label': by_label,
            'avg_severity': round(total_severity / len(symptoms), 1)
        }
    
    # Vital Signs Management
    
    def get_vitals(self, kind: Optional[str] = None, days: int = 30) -> List[Vital]:
        """Get vitals for the last N days, optionally filtered by kind"""
        cutoff_date = datetime.now() - timedelta(days=days)
        query = self.db.query(Vital).filter(Vital.ts >= cutoff_date)
        
        if kind:
            query = query.filter(Vital.kind == kind)
        
        return query.order_by(Vital.ts.desc()).all()
    
    def log_vital(self, data: Dict[str, Any]) -> Vital:
        """Log a new vital sign"""
        vital = Vital(
            kind=data['kind'],
            value_num=data['value_num'],
            unit=data.get('unit'),
            note=data.get('note')
        )
        self.db.add(vital)
        self.db.commit()
        self.db.refresh(vital)
        
        self._log_audit('create', 'vital', vital.id, f"Logged {vital.kind}: {vital.value_num} {vital.unit or ''}")
        return vital
    
    def get_vital_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get vital signs summary for dashboard"""
        cutoff_date = datetime.now() - timedelta(days=days)
        vitals = self.db.query(Vital).filter(
            Vital.ts >= cutoff_date
        ).all()
        
        if not vitals:
            return {
                'total': 0,
                'by_kind': {},
                'recent': []
            }
        
        # Group by kind
        by_kind = {}
        for vital in vitals:
            if vital.kind not in by_kind:
                by_kind[vital.kind] = []
            by_kind[vital.kind].append(vital)
        
        # Get most recent of each kind
        recent = []
        for kind, kind_vitals in by_kind.items():
            most_recent = max(kind_vitals, key=lambda v: v.ts)
            recent.append(most_recent)
        
        return {
            'total': len(vitals),
            'by_kind': {kind: len(vitals) for kind, vitals in by_kind.items()},
            'recent': [v.to_dict() for v in recent]
        }
    
    # Appointment Management
    
    def get_appointments(self, days_ahead: int = 30, include_past: bool = False) -> List[Appointment]:
        """Get appointments, optionally including past ones"""
        now = datetime.now()
        query = self.db.query(Appointment)
        
        if not include_past:
            query = query.filter(Appointment.ts >= now)
        
        cutoff_date = now + timedelta(days=days_ahead)
        query = query.filter(Appointment.ts <= cutoff_date)
        
        return query.order_by(Appointment.ts).all()
    
    def create_appointment(self, data: Dict[str, Any]) -> Appointment:
        """Create a new appointment"""
        appointment = Appointment(
            ts=datetime.fromisoformat(data['ts']),
            provider=data['provider'],
            location=data.get('location'),
            purpose=data.get('purpose'),
            note=data.get('note'),
            specialty=data.get('specialty'),
            is_virtual=bool(data.get('is_virtual', False)),
            status=data.get('status', 'planned'),
            reminder_days=self._coerce_int(data.get('reminder_days')),
            follow_up_ts=datetime.fromisoformat(data['follow_up_ts']) if data.get('follow_up_ts') else None,
            lab_due_ts=datetime.fromisoformat(data['lab_due_ts']) if data.get('lab_due_ts') else None
        )
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        
        self._log_audit('create', 'appointment', appointment.id, f"Created appointment with {appointment.provider}")
        return appointment
    
    def update_appointment(self, appointment_id: int, data: Dict[str, Any]) -> Optional[Appointment]:
        """Update appointment"""
        appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            return None
        
        # Track changes for audit
        changes = []
        for key, value in data.items():
            if hasattr(appointment, key):
                if key == 'ts':
                    new_ts = datetime.fromisoformat(value)
                    if appointment.ts != new_ts:
                        changes.append(f"{key}: {appointment.ts} → {new_ts}")
                        appointment.ts = new_ts
                elif key in ('follow_up_ts', 'lab_due_ts'):
                    new_dt = datetime.fromisoformat(value) if value else None
                    if getattr(appointment, key) != new_dt:
                        changes.append(f"{key}: {getattr(appointment, key)} → {new_dt}")
                        setattr(appointment, key, new_dt)
                elif getattr(appointment, key) != value:
                    changes.append(f"{key}: {getattr(appointment, key)} → {value}")
                    setattr(appointment, key, value)
        
        if changes:
            self.db.commit()
            self._log_audit('update', 'appointment', appointment_id, f"Updated: {', '.join(changes)}")
        
        return appointment
    
    def delete_appointment(self, appointment_id: int) -> bool:
        """Delete appointment"""
        appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            return False
        
        provider = appointment.provider
        self.db.delete(appointment)
        self.db.commit()
        
        self._log_audit('delete', 'appointment', appointment_id, f"Deleted appointment with {provider}")
        return True

    # Appointment Tasks
    def get_appointment_tasks(self, appointment_id: int) -> List[AppointmentTask]:
        return self.db.query(AppointmentTask).filter(AppointmentTask.appointment_id == appointment_id).order_by(AppointmentTask.due_ts.is_(None), AppointmentTask.due_ts).all()

    def create_appointment_task(self, appointment_id: int, data: Dict[str, Any]) -> AppointmentTask:
        task = AppointmentTask(
            appointment_id=appointment_id,
            label=data['label'],
            due_ts=datetime.fromisoformat(data['due_ts']) if data.get('due_ts') else None,
            done=bool(data.get('done', False))
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        self._log_audit('create', 'appointment_task', task.id, f"Task for appt {appointment_id}: {task.label}")
        return task

    # Labs
    def list_labs(self, appointment_id: Optional[int] = None) -> List[LabOrder]:
        q = self.db.query(LabOrder)
        if appointment_id is not None:
            q = q.filter(LabOrder.appointment_id == appointment_id)
        return q.order_by(LabOrder.due_ts.is_(None), LabOrder.due_ts).all()

    def create_lab(self, data: Dict[str, Any]) -> LabOrder:
        lab = LabOrder(
            appointment_id=data.get('appointment_id'),
            label=data['label'],
            kind=data.get('kind'),
            provider=data.get('provider'),
            location=data.get('location'),
            instructions=data.get('instructions'),
            status=data.get('status', 'ordered'),
            scheduled_ts=datetime.fromisoformat(data['scheduled_ts']) if data.get('scheduled_ts') else None,
            due_ts=datetime.fromisoformat(data['due_ts']) if data.get('due_ts') else None,
            completed_ts=datetime.fromisoformat(data['completed_ts']) if data.get('completed_ts') else None,
            reminder_days=self._coerce_int(data.get('reminder_days')),
            result_note=data.get('result_note')
        )
        self.db.add(lab)
        self.db.commit()
        self.db.refresh(lab)
        self._log_audit('create', 'lab_order', lab.id, f"Lab: {lab.label}")
        return lab

    def update_lab(self, lab_id: int, data: Dict[str, Any]) -> Optional[LabOrder]:
        lab = self.db.query(LabOrder).filter(LabOrder.id == lab_id).first()
        if not lab:
            return None
        changes = []
        mapping = {
            'appointment_id': 'appointment_id', 'label': 'label', 'kind': 'kind', 'provider': 'provider',
            'location': 'location', 'instructions': 'instructions', 'status': 'status', 'reminder_days': 'reminder_days', 'result_note': 'result_note'
        }
        for key, attr in mapping.items():
            if key in data and getattr(lab, attr) != data[key]:
                changes.append(f"{attr} updated")
                setattr(lab, attr, data[key])
        for key in ('scheduled_ts','due_ts','completed_ts'):
            if key in data:
                new_dt = datetime.fromisoformat(data[key]) if data[key] else None
                if getattr(lab, key) != new_dt:
                    changes.append(f"{key} updated")
                    setattr(lab, key, new_dt)
        if changes:
            self.db.commit()
            self._log_audit('update', 'lab_order', lab_id, f"Updated: {', '.join(changes)}")
        return lab

    def update_appointment_task(self, task_id: int, data: Dict[str, Any]) -> Optional[AppointmentTask]:
        task = self.db.query(AppointmentTask).filter(AppointmentTask.id == task_id).first()
        if not task:
            return None
        changes = []
        if 'label' in data and data['label'] != task.label:
            changes.append(f"label: {task.label} → {data['label']}")
            task.label = data['label']
        if 'due_ts' in data:
            new_dt = datetime.fromisoformat(data['due_ts']) if data['due_ts'] else None
            if task.due_ts != new_dt:
                changes.append("due_ts updated")
                task.due_ts = new_dt
        if 'done' in data and bool(data['done']) != bool(task.done):
            changes.append(f"done: {task.done} → {bool(data['done'])}")
            task.done = bool(data['done'])
        if changes:
            self.db.commit()
            self._log_audit('update', 'appointment_task', task_id, f"Updated: {', '.join(changes)}")
        return task
    
    # Dashboard Data
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get all data needed for health dashboard"""
        return {
            'meds': {
                'total': len(self.get_meds()),
                'recent_events': self._get_recent_med_events(7)
            },
            'symptoms': self.get_symptom_summary(7),
            'vitals': self.get_vital_summary(7),
            'appointments': {
                'upcoming': len(self.get_appointments(30, include_past=False)),
                'next': self._get_next_appointment()
            }
        }
    
    def _get_recent_med_events(self, days: int) -> List[Dict[str, Any]]:
        """Get recent medication events across all medications"""
        cutoff_date = datetime.now() - timedelta(days=days)
        events = self.db.query(MedEvent).join(Med).filter(
            MedEvent.ts >= cutoff_date
        ).order_by(MedEvent.ts.desc()).limit(10).all()
        
        return [{
            'med_name': event.med.name,
            'ts': event.ts.isoformat(),
            'amount': event.amount,
            'note': event.note
        } for event in events]
    
    def _get_next_appointment(self) -> Optional[Dict[str, Any]]:
        """Get the next upcoming appointment"""
        appointments = self.get_appointments(30, include_past=False)
        if not appointments:
            return None
        
        next_appt = min(appointments, key=lambda a: a.ts)
        # Task counts
        open_tasks = self.db.query(func.count(AppointmentTask.id)).filter(
            and_(AppointmentTask.appointment_id == next_appt.id, AppointmentTask.done == False)  # noqa: E712
        ).scalar()
        now = datetime.now()
        due_tasks = self.db.query(func.count(AppointmentTask.id)).filter(
            and_(
                AppointmentTask.appointment_id == next_appt.id,
                AppointmentTask.done == False,  # noqa: E712
                AppointmentTask.due_ts != None,  # noqa: E711
                AppointmentTask.due_ts <= now
            )
        ).scalar()

        # Labs summary for the next appointment
        labs_for_appt = self.db.query(LabOrder).filter(LabOrder.appointment_id == next_appt.id).all()
        total_labs = len(labs_for_appt)
        scheduled_labs = len([l for l in labs_for_appt if l.status == 'scheduled'])
        # compute next due ts among labs with due_ts
        due_dates = [l.due_ts for l in labs_for_appt if l.due_ts is not None]
        next_lab_due = min(due_dates) if due_dates else None
        overdue_labs = 0
        due_soon_labs = 0
        for l in labs_for_appt:
            if l.status == 'completed' or l.due_ts is None:
                continue
            if l.due_ts < now:
                overdue_labs += 1
            else:
                reminder_days = l.reminder_days or 0
                try:
                    if reminder_days > 0 and l.due_ts <= now + timedelta(days=reminder_days):
                        due_soon_labs += 1
                except Exception:
                    # In case of any bad data, skip
                    pass

        return {
            'id': next_appt.id,
            'ts': next_appt.ts.isoformat(),
            'provider': next_appt.provider,
            'purpose': next_appt.purpose,
            'location': next_appt.location,
            'status': next_appt.status,
            'is_virtual': next_appt.is_virtual,
            'open_tasks': int(open_tasks or 0),
            'due_tasks': int(due_tasks or 0),
            'labs': {
                'total': int(total_labs or 0),
                'scheduled': int(scheduled_labs or 0),
                'due_soon': int(due_soon_labs or 0),
                'overdue': int(overdue_labs or 0),
                'next_due_ts': (next_lab_due.isoformat() if next_lab_due else None)
            }
        }
    
    # Audit Logging
    
    def _log_audit(self, action: str, entity: str, entity_id: int, note: str):
        """Log an audit entry"""
        audit = Audit(
            action=action,
            entity=entity,
            entity_id=entity_id,
            note=note
        )
        self.db.add(audit)
        self.db.commit()

    # Sensors (CGM) management
    def get_sensor_summary(self, type_key: str = 'stelo_cgm') -> Dict[str, Any]:
        st: SensorType = self.db.query(SensorType).filter(SensorType.key == type_key).first()
        if not st:
            return {'type_key': type_key, 'active': False, 'on_hand': 0}
        # Active session
        active: Optional[SensorUse] = self.db.query(SensorUse).filter(
            and_(SensorUse.type_key == type_key, SensorUse.end_ts_actual == None)
        ).order_by(SensorUse.start_ts.desc()).first()
        # Inventory on hand (sensors)
        on_hand = self.db.query(func.coalesce(func.sum(SensorInventory.delta_sensors), 0)).filter(
            SensorInventory.type_key == type_key
        ).scalar() or 0
        # on_hand already accounts for consumption because a start event records -1
        on_hand_effective = int(on_hand)
        lead_time = st.default_lead_time_days
        reorder_point = int((lead_time + st.wear_days - 1) // st.wear_days) + st.safety_stock
        countdown_days = None
        next_end_ts = None
        if active and active.end_ts_expected:
            delta = active.end_ts_expected - datetime.now()
            countdown_days = max(0, int(delta.total_seconds() // 86400))
            next_end_ts = active.end_ts_expected.isoformat()
        # Only remind when truly out of sensors on hand
        need_reorder = on_hand_effective <= 0
        return {
            'type_key': type_key,
            'active': bool(active),
            'active_use_id': active.id if active else None,
            'countdown_days': countdown_days,
            'next_end_ts': next_end_ts,
            'on_hand': int(on_hand_effective),
            'reorder_point': reorder_point,
            'need_reorder': need_reorder
        }

    def start_sensor(self, type_key: str = 'stelo_cgm', start_ts: Optional[str] = None, note: Optional[str] = None) -> SensorUse:
        st: SensorType = self.db.query(SensorType).filter(SensorType.key == type_key).first()
        if not st:
            st = SensorType(key=type_key, label='Sensor', wear_days=15, pack_size=2)
            self.db.add(st)
            self.db.commit()
        start = datetime.fromisoformat(start_ts) if start_ts else datetime.now()
        # expected end
        end_expected = start + timedelta(days=st.wear_days)
        use = SensorUse(type_key=type_key, start_ts=start, end_ts_expected=end_expected, note=note)
        self.db.add(use)
        # consume one sensor from inventory
        inv = SensorInventory(type_key=type_key, delta_sensors=-1, source='use', note='Start sensor')
        self.db.add(inv)
        self.db.commit()
        self.db.refresh(use)
        self._log_audit('create', 'sensor_use', use.id, f'Started {type_key}')
        return use

    def end_sensor(self, use_id: int, end_ts: Optional[str] = None) -> Optional[SensorUse]:
        use: Optional[SensorUse] = self.db.query(SensorUse).filter(SensorUse.id == use_id).first()
        if not use:
            return None
        if use.end_ts_actual:
            return use
        end = datetime.fromisoformat(end_ts) if end_ts else datetime.now()
        use.end_ts_actual = end
        self.db.commit()
        self._log_audit('update', 'sensor_use', use.id, 'Ended sensor')
        return use

    def add_sensor_packs(self, type_key: str, packs: int, ts_iso: Optional[str] = None, note: Optional[str] = None) -> SensorInventory:
        st: SensorType = self.db.query(SensorType).filter(SensorType.key == type_key).first()
        pack_size = st.pack_size if st else 2
        sensors = int(packs) * pack_size
        ts = datetime.fromisoformat(ts_iso) if ts_iso else datetime.now()
        inv = SensorInventory(type_key=type_key, ts=ts, delta_sensors=sensors, source='purchase', note=note or 'Add packs')
        self.db.add(inv)
        self.db.commit()
        self._log_audit('create', 'sensor_inventory', inv.id, f'Added {sensors} sensors ({packs} packs)')
        return inv

    def adjust_sensor_inventory(self, type_key: str, delta_sensors: int, note: Optional[str] = None) -> SensorInventory:
        inv = SensorInventory(type_key=type_key, delta_sensors=int(delta_sensors), source='adjust', note=note)
        self.db.add(inv)
        self.db.commit()
        self._log_audit('create', 'sensor_inventory', inv.id, f'Adjust {delta_sensors}')
        return inv

    def list_sensor_uses(self, type_key: str = 'stelo_cgm') -> List[SensorUse]:
        return self.db.query(SensorUse).filter(SensorUse.type_key == type_key).order_by(SensorUse.start_ts.desc()).all()

    def list_sensor_inventory(self, type_key: str = 'stelo_cgm') -> List[SensorInventory]:
        return self.db.query(SensorInventory).filter(SensorInventory.type_key == type_key).order_by(SensorInventory.ts.desc()).all()
