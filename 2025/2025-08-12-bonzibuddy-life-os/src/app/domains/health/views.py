from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, current_app
from .services import HealthService, init_oura_oauth, get_oura_user_info, store_oura_user, get_oura_sleep_data, get_oura_activity_data, get_oura_readiness_data
from ...core.db import get_session
from datetime import datetime
import json

bp = Blueprint("health", __name__)

# Oura OAuth client will be initialized when first needed
_oura_oauth = None

def get_oura_oauth():
    """Get or initialize Oura OAuth client"""
    global _oura_oauth
    if _oura_oauth is None:
        _oura_oauth = init_oura_oauth(current_app)
    return _oura_oauth

# Oura OAuth Routes
@bp.get("/oura/connect")
def oura_connect():
    """Start Oura OAuth flow"""
    try:
        oauth = get_oura_oauth()
        return oauth.oura.authorize_redirect(current_app.config['OURA_REDIRECT_URI'])
    except Exception as e:
        current_app.logger.error(f"Oura connection error: {e}")
        return jsonify({'error': f'Oura connection error: {str(e)}'}), 500

@bp.get("/oura/callback")
def oura_callback():
    """Handle Oura OAuth callback"""
    try:
        oauth = get_oura_oauth()
        token = oauth.oura.authorize_access_token()
        
        # Get user info from Oura
        user_info = get_oura_user_info(token['access_token'])
        
        # Store or update user and tokens
        user = store_oura_user(user_info, token)
        
        # Redirect to dashboard with success message
        return redirect(url_for('health.index', oura_connected='true'))
    except Exception as e:
        current_app.logger.error(f"Oura callback error: {e}")
        return redirect(url_for('health.index', oura_error='true'))

@bp.get("/oura/status")
def oura_status():
    """Get Oura connection status"""
    from .models import OuraUser
    from ...core.db import get_session
    
    db = get_session()
    users = db.query(OuraUser).all()
    
    return jsonify({
        'connected': len(users) > 0,
        'users': [user.to_dict() for user in users]
    })

@bp.get("/oura/sleep")
def oura_sleep():
    """Get Oura sleep data"""
    from .models import OuraUser
    from ...core.db import get_session
    
    db = get_session()
    user = db.query(OuraUser).first()  # For now, get first user
    
    if not user:
        return jsonify({'error': 'No Oura user connected'}), 400
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    sleep_data = get_oura_sleep_data(user.user_id, start_date, end_date)
    
    if sleep_data is None:
        return jsonify({'error': 'Failed to fetch sleep data'}), 500
    
    return jsonify(sleep_data)

@bp.get("/oura/sleep/view")
def oura_sleep_view():
    """Oura sleep data HTML view"""
    return render_template("health/oura-sleep.html")

@bp.get("/oura/activity/view")
def oura_activity_view():
    """Oura activity data HTML view"""
    return render_template("health/oura-activity.html")

@bp.get("/oura/readiness/view")
def oura_readiness_view():
    """Oura readiness data HTML view"""
    return render_template("health/oura-readiness.html")

@bp.get("/oura/activity")
def oura_activity():
    """Get Oura activity data"""
    from .models import OuraUser
    from ...core.db import get_session
    
    db = get_session()
    user = db.query(OuraUser).first()  # For now, get first user
    
    if not user:
        return jsonify({'error': 'No Oura user connected'}), 400
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    activity_data = get_oura_activity_data(user.user_id, start_date, end_date)
    
    if activity_data is None:
        return jsonify({'error': 'Failed to fetch activity data'}), 500
    
    return jsonify(activity_data)

@bp.get("/oura/readiness")
def oura_readiness():
    """Get Oura readiness data"""
    from .models import OuraUser
    from ...core.db import get_session
    
    db = get_session()
    user = db.query(OuraUser).first()  # For now, get first user
    
    if not user:
        return jsonify({'error': 'No Oura user connected'}), 400
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    readiness_data = get_oura_readiness_data(user.user_id, start_date, end_date)
    
    if readiness_data is None:
        return jsonify({'error': 'Failed to fetch readiness data'}), 500
    
    return jsonify(readiness_data)

@bp.get("/oura/disconnect")
def oura_disconnect():
    """Disconnect Oura account"""
    from .models import OuraUser, OuraToken
    from ...core.db import get_session
    
    db = get_session()
    
    # Remove all Oura users and tokens
    db.query(OuraToken).delete()
    db.query(OuraUser).delete()
    db.commit()
    
    return jsonify({'message': 'Oura account disconnected successfully'})

@bp.get("/oura/sync")
def oura_sync():
    """Sync Oura data (sleep, activity, readiness)"""
    from .models import OuraUser
    from ...core.db import get_session
    
    db = get_session()
    user = db.query(OuraUser).first()  # For now, get first user
    
    if not user:
        return jsonify({'error': 'No Oura user connected'}), 400
    
    try:
        # Sync sleep data
        sleep_data = get_oura_sleep_data(user.user_id)
        current_app.logger.info(f"Sleep data fetched: {sleep_data}")
        
        # Sync activity data
        activity_data = get_oura_activity_data(user.user_id)
        current_app.logger.info(f"Activity data fetched: {activity_data}")
        
        # Sync readiness data
        readiness_data = get_oura_readiness_data(user.user_id)
        current_app.logger.info(f"Readiness data fetched: {readiness_data}")
        
        # Update last sync timestamp
        user.last_sync = datetime.now()
        db.commit()
        
        # Log the update
        current_app.logger.info(f"Updated last_sync to: {user.last_sync}")
        
        return jsonify({
            'message': 'Oura data synced successfully',
            'sleep_records': len(sleep_data.get('data', [])) if sleep_data else 0,
            'activity_records': len(activity_data.get('data', [])) if activity_data else 0,
            'readiness_records': len(readiness_data.get('data', [])) if readiness_data else 0,
            'last_sync': user.last_sync.isoformat() if user.last_sync else None,
            'debug': {
                'sleep_data_keys': list(sleep_data.keys()) if sleep_data else None,
                'activity_data_keys': list(activity_data.keys()) if activity_data else None,
                'readiness_data_keys': list(readiness_data.keys()) if readiness_data else None,
                'user_id': user.user_id,
                'user_last_sync': user.last_sync.isoformat() if user.last_sync else None
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Oura sync error: {e}")
        return jsonify({'error': f'Failed to sync Oura data: {str(e)}'}), 500

@bp.get("/oura/recent_data")
def oura_recent_data():
    """Get recent Oura data scores for dashboard display"""
    from .models import OuraUser
    from ...core.db import get_session
    
    db = get_session()
    user = db.query(OuraUser).first()  # For now, get first user
    
    if not user:
        return jsonify({'error': 'No Oura user connected'}), 400
    
    days = request.args.get('days', 7, type=int)
    
    try:
        # Get recent data
        sleep_data = get_oura_sleep_data(user.user_id)
        activity_data = get_oura_activity_data(user.user_id)
        readiness_data = get_oura_readiness_data(user.user_id)
        
        # Extract latest scores
        latest_sleep = None
        latest_activity = None
        latest_readiness = None
        
        if sleep_data and sleep_data.get('data'):
            # Get the most recent sleep data
            sleep_records = sorted(sleep_data['data'], key=lambda x: x.get('day', ''), reverse=True)
            if sleep_records:
                latest_sleep = sleep_records[0].get('score', 0)
        
        if activity_data and activity_data.get('data'):
            # Get the most recent activity data
            activity_records = sorted(activity_data['data'], key=lambda x: x.get('day', ''), reverse=True)
            if activity_records:
                latest_activity = activity_records[0].get('score', 0)
        
        if readiness_data and readiness_data.get('data'):
            # Get the most recent readiness data
            readiness_records = sorted(readiness_data['data'], key=lambda x: x.get('day', ''), reverse=True)
            if readiness_records:
                latest_readiness = readiness_records[0].get('score', 0)
        
        return jsonify({
            'sleep_score': latest_sleep,
            'activity_score': latest_activity,
            'readiness_score': latest_readiness,
            'last_updated': user.last_sync.isoformat() if user.last_sync else None
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting recent Oura data: {e}")
        return jsonify({'error': f'Failed to get recent data: {str(e)}'}), 500

# Dashboard view
@bp.get("/")
def index():
    """Health dashboard"""
    db = get_session()
    service = HealthService(db)
    dashboard_data = service.get_dashboard_data()
    return render_template("health/dashboard.html", data=dashboard_data)
# Appointments page (HTML)
@bp.get("/appointments/view")
def appointments_view():
    return render_template("health/appointments.html")

# Labs page (HTML)
@bp.get("/labs/view")
def labs_view():
    return render_template("health/labs.html")

# Medication endpoints
@bp.get("/meds")
def list_meds():
    """List all medications"""
    db = get_session()
    service = HealthService(db)
    meds = service.get_meds()
    return jsonify([med.to_dict() for med in meds])

@bp.post("/meds")
def create_med():
    """Create a new medication"""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400
        
        db = get_session()
        service = HealthService(db)
        med = service.create_med(data)
        return jsonify(med.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.get("/meds/<int:med_id>")
def get_med(med_id):
    """Get medication by ID"""
    db = get_session()
    service = HealthService(db)
    med = service.get_med(med_id)
    
    if not med:
        return jsonify({'error': 'Medication not found'}), 404
    
    return jsonify(med.to_dict())

@bp.put("/meds/<int:med_id>")
def update_med(med_id):
    """Update medication"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        db = get_session()
        service = HealthService(db)
        med = service.update_med(med_id, data)
        
        if not med:
            return jsonify({'error': 'Medication not found'}), 404
        
        return jsonify(med.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.delete("/meds/<int:med_id>")
def delete_med(med_id):
    """Delete medication"""
    db = get_session()
    service = HealthService(db)
    success = service.delete_med(med_id)
    
    if not success:
        return jsonify({'error': 'Medication not found'}), 404
    
    return jsonify({'message': 'Medication deleted successfully'})

@bp.post("/meds/<int:med_id>/log")
def log_med_event(med_id):
    """Log a medication event"""
    try:
        data = request.get_json()
        if not data or 'amount' not in data:
            return jsonify({'error': 'Amount is required'}), 400
        
        db = get_session()
        service = HealthService(db)
        event = service.log_med_event(
            med_id=med_id,
            amount=data['amount'],
            note=data.get('note')
        )
        
        if not event:
            return jsonify({'error': 'Medication not found'}), 404
        
        return jsonify(event.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# OTC endpoints
@bp.get("/otc/summary")
def otc_summary():
    db = get_session()
    service = HealthService(db)
    return jsonify(service.get_otc_summary())

@bp.get("/otc")
def list_otc():
    db = get_session()
    service = HealthService(db)
    meds = [m.to_dict() for m in service.get_meds()]
    return jsonify([m for m in meds if m.get('is_otc')])

@bp.post("/meds/<int:med_id>/stock/adjust")
def adjust_otc_stock(med_id):
    try:
        data = request.get_json() or {}
        delta = float(data.get('delta', 0))
        db = get_session()
        service = HealthService(db)
        med = service.get_med(med_id)
        if not med or not med.is_otc:
            return jsonify({'error': 'OTC medication not found'}), 404
        med.on_hand_qty = max(0.0, (med.on_hand_qty or 0.0) + delta)
        service.db.commit()
        service._log_audit('update', 'med', med_id, f'OTC stock adjust {delta}')
        return jsonify(med.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.get("/meds/<int:med_id>/events")
def get_med_events(med_id):
    """Get medication events for a specific medication"""
    days = request.args.get('days', 30, type=int)
    
    db = get_session()
    service = HealthService(db)
    events = service.get_med_events(med_id, days)
    
    return jsonify([event.to_dict() for event in events])

# Symptom endpoints
@bp.get("/symptoms")
def list_symptoms():
    """List symptoms"""
    days = request.args.get('days', 30, type=int)
    
    db = get_session()
    service = HealthService(db)
    symptoms = service.get_symptoms(days)
    
    return jsonify([symptom.to_dict() for symptom in symptoms])

@bp.post("/symptoms")
def log_symptom():
    """Log a new symptom"""
    try:
        data = request.get_json()
        if not data or 'label' not in data or 'severity' not in data:
            return jsonify({'error': 'Label and severity are required'}), 400
        
        if not isinstance(data['severity'], int) or data['severity'] < 1 or data['severity'] > 5:
            return jsonify({'error': 'Severity must be an integer between 1 and 5'}), 400
        
        db = get_session()
        service = HealthService(db)
        symptom = service.log_symptom(data)
        
        return jsonify(symptom.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vital signs endpoints
@bp.get("/vitals")
def list_vitals():
    """List vital signs"""
    days = request.args.get('days', 30, type=int)
    kind = request.args.get('kind')
    
    db = get_session()
    service = HealthService(db)
    vitals = service.get_vitals(kind, days)
    
    return jsonify([vital.to_dict() for vital in vitals])

@bp.post("/vitals")
def log_vital():
    """Log a new vital sign"""
    try:
        data = request.get_json()
        if not data or 'kind' not in data or 'value_num' not in data:
            return jsonify({'error': 'Kind and value are required'}), 400
        
        if not isinstance(data['value_num'], (int, float)):
            return jsonify({'error': 'Value must be a number'}), 400
        
        db = get_session()
        service = HealthService(db)
        vital = service.log_vital(data)
        
        return jsonify(vital.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Appointment endpoints
@bp.get("/appointments")
def list_appointments():
    """List appointments"""
    days_ahead = request.args.get('days_ahead', 30, type=int)
    include_past = request.args.get('include_past', 'false').lower() == 'true'
    
    db = get_session()
    service = HealthService(db)
    appointments = service.get_appointments(days_ahead, include_past)
    
    return jsonify([appointment.to_dict() for appointment in appointments])

@bp.post("/appointments")
def create_appointment():
    """Create a new appointment"""
    try:
        data = request.get_json()
        if not data or 'ts' not in data or 'provider' not in data:
            return jsonify({'error': 'Timestamp and provider are required'}), 400
        
        # Validate timestamp format
        try:
            datetime.fromisoformat(data['ts'])
        except ValueError:
            return jsonify({'error': 'Invalid timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
        
        db = get_session()
        service = HealthService(db)
        appointment = service.create_appointment(data)
        
        return jsonify(appointment.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.get("/appointments/<int:appointment_id>")
def get_appointment(appointment_id):
    """Get appointment by ID"""
    db = get_session()
    service = HealthService(db)
    
    # Get all appointments and find the one we want
    appointments = service.get_appointments(365, include_past=True)
    appointment = next((a for a in appointments if a.id == appointment_id), None)
    
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    return jsonify(appointment.to_dict())

@bp.put("/appointments/<int:appointment_id>")
def update_appointment(appointment_id):
    """Update appointment"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate timestamp format if provided
        if 'ts' in data:
            try:
                datetime.fromisoformat(data['ts'])
            except ValueError:
                return jsonify({'error': 'Invalid timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
        
        db = get_session()
        service = HealthService(db)
        appointment = service.update_appointment(appointment_id, data)
        
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        return jsonify(appointment.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.delete("/appointments/<int:appointment_id>")
def delete_appointment(appointment_id):
    """Delete appointment"""
    db = get_session()
    service = HealthService(db)
    success = service.delete_appointment(appointment_id)
    
    if not success:
        return jsonify({'error': 'Appointment not found'}), 404
    
    return jsonify({'message': 'Appointment deleted successfully'})

# Appointment tasks endpoints
@bp.get("/appointments/<int:appointment_id>/tasks")
def list_appointment_tasks(appointment_id):
    db = get_session()
    service = HealthService(db)
    tasks = service.get_appointment_tasks(appointment_id)
    return jsonify([t.to_dict() for t in tasks])

@bp.post("/appointments/<int:appointment_id>/tasks")
def create_appointment_task(appointment_id):
    try:
        data = request.get_json() or {}
        if 'label' not in data:
            return jsonify({'error': 'label is required'}), 400
        db = get_session()
        service = HealthService(db)
        task = service.create_appointment_task(appointment_id, data)
        return jsonify(task.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.put("/appointments/tasks/<int:task_id>")
def update_appointment_task(task_id):
    try:
        data = request.get_json() or {}
        db = get_session()
        service = HealthService(db)
        task = service.update_appointment_task(task_id, data)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify(task.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Lab order endpoints
@bp.get("/labs")
def list_labs():
    appt_id = request.args.get('appointment_id', type=int)
    db = get_session()
    service = HealthService(db)
    labs = service.list_labs(appt_id)
    return jsonify([l.to_dict() for l in labs])

@bp.post("/labs")
def create_lab():
    try:
        data = request.get_json() or {}
        if 'label' not in data:
            return jsonify({'error': 'label is required'}), 400
        db = get_session()
        service = HealthService(db)
        lab = service.create_lab(data)
        return jsonify(lab.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.put("/labs/<int:lab_id>")
def update_lab(lab_id):
    try:
        data = request.get_json() or {}
        db = get_session()
        service = HealthService(db)
        lab = service.update_lab(lab_id, data)
        if not lab:
            return jsonify({'error': 'Lab not found'}), 404
        return jsonify(lab.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Sensors (CGM) endpoints
@bp.get("/sensors/summary")
def get_sensor_summary():
    type_key = request.args.get('type', 'stelo_cgm')
    db = get_session()
    service = HealthService(db)
    return jsonify(service.get_sensor_summary(type_key))

@bp.post("/sensors/uses/start")
def start_sensor_use():
    try:
        data = request.get_json() or {}
        type_key = data.get('type_key', 'stelo_cgm')
        db = get_session()
        service = HealthService(db)
        use = service.start_sensor(type_key=type_key, start_ts=data.get('start_ts'), note=data.get('note'))
        return jsonify(use.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.post("/sensors/uses/end")
def end_sensor_use():
    try:
        data = request.get_json() or {}
        if 'id' not in data:
            return jsonify({'error': 'id is required'}), 400
        db = get_session()
        service = HealthService(db)
        use = service.end_sensor(use_id=int(data['id']), end_ts=data.get('end_ts_actual'))
        if not use:
            return jsonify({'error': 'Sensor use not found'}), 404
        return jsonify(use.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.post("/sensors/inventory/add_pack")
def add_sensor_pack():
    try:
        data = request.get_json() or {}
        type_key = data.get('type_key', 'stelo_cgm')
        packs = int(data.get('packs', 1))
        db = get_session()
        service = HealthService(db)
        inv = service.add_sensor_packs(type_key, packs, data.get('ts'), data.get('note'))
        return jsonify(inv.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.post("/sensors/inventory/adjust")
def adjust_sensor_inv():
    try:
        data = request.get_json() or {}
        type_key = data.get('type_key', 'stelo_cgm')
        delta = int(data.get('delta_sensors', 0))
        db = get_session()
        service = HealthService(db)
        inv = service.adjust_sensor_inventory(type_key, delta, data.get('note'))
        return jsonify(inv.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.get("/sensors/uses")
def list_sensor_uses():
    type_key = request.args.get('type', 'stelo_cgm')
    db = get_session()
    service = HealthService(db)
    uses = service.list_sensor_uses(type_key)
    return jsonify([u.to_dict() for u in uses])

@bp.get("/sensors/inventory")
def list_sensor_inventory():
    type_key = request.args.get('type', 'stelo_cgm')
    db = get_session()
    service = HealthService(db)
    inv = service.list_sensor_inventory(type_key)
    return jsonify([i.to_dict() for i in inv])

# Dashboard data endpoint
@bp.get("/dashboard")
def get_dashboard_data():
    """Get dashboard data as JSON"""
    db = get_session()
    service = HealthService(db)
    dashboard_data = service.get_dashboard_data()
    return jsonify(dashboard_data)

# Import prescriptions from CSV
@bp.post("/meds/import")
def import_meds():
    """Import medications from CSV file in data directory or provided path."""
    try:
        body = request.get_json(silent=True) or {}
        path = body.get('path')
        db = get_session()
        service = HealthService(db)
        result = service.import_meds_from_csv(path)
        return jsonify({
            'success': True,
            'message': f"Imported prescriptions: created={result['created']}, updated={result['updated']} (total rows={result['total']})",
            'stats': result
        })
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Medications full view (HTML)
@bp.get("/meds/view")
def meds_view():
    db = get_session()
    service = HealthService(db)
    meds = [m.to_dict() for m in service.get_meds()]
    return render_template("health/meds.html", meds=meds)