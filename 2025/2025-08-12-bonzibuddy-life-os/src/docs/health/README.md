# Health Features User Guide

**Status:** ✅ **FULLY IMPLEMENTED**  
**Last Updated:** August 2025  
**Version:** v0 Complete

## 🚀 **Quick Start**

1. **Access Health Dashboard**: Visit `http://localhost:5000/health/`
2. **View Current Data**: See summaries of medications, symptoms, vitals, and appointments
3. **Add New Data**: Use the quick action buttons to log new entries
4. **Manage Data**: Edit, delete, or view detailed information for each entry

## 🏥 **Health Dashboard Overview**

### **Appointments Enhancements (Roadmap)**

Planned robust features for managing appointments:

- **Core fields**: Date/Time, Doctor, Location, Reason, Notes, Specialty, Virtual vs In‑person
- **Status**: planned, completed, canceled, rescheduled
- **Reminders**: configurable days before, support multiple reminders per appointment
- **Tasks/Checklist**: pre‑visit and post‑visit tasks (e.g., labs, forms, referrals) with due dates and completion state
- **Follow‑ups**: track a follow‑up appointment date and link to parent appointment
- **Labs**: standalone lab orders with optional linking to appointments; statuses (ordered/scheduled/completed), reminders, due dates, and results
- **Attachments**: upload instructions, orders, visit summaries
- **Recurring/series**: optional repeats (future)
- **Integrations**: iCalendar export, desktop notifications (future)

Initial slice in v0.1 will add: Specialty, Virtual flag, Status, single reminder_days, optional follow_up date, basic tasks per appointment, and standalone Lab Orders.

#### Labs API Quick Start
```bash
# Create a lab order linked to an appointment
POST /health/labs
{
  "appointment_id": 123,
  "label": "CMP + Tacrolimus",
  "kind": "bloodwork",
  "provider": "KU Med",
  "due_ts": "2025-08-19T00:00:00",
  "reminder_days": 3
}

# List all labs or filter by appointment
GET /health/labs?appointment_id=123

# Update lab status and result note
PUT /health/labs/456
{
  "status": "completed",
  "completed_ts": "2025-08-18T09:00:00",
  "result_note": "All within target range"
}
```

The health dashboard provides a comprehensive view of your health data with quick access to all features:

### **Dashboard Cards**

#### **Medications Summary**
- **Total Medications**: Count of active medications
- **Recent Events**: Last 7 days of medication logs
- **Quick Actions**: Add new medication, log medication event

#### **Appointments Summary**
- **Upcoming**: Count of appointments in next 30 days
- **Next Appointment**: Details of your next scheduled visit
- **Quick Actions**: Schedule new appointment

#### **Symptoms Summary**
- **Total Logs**: Count of symptom entries in last 7 days
- **Average Severity**: Mean severity level (1-5 scale)
- **Quick Actions**: Log new symptom

#### **Vitals Summary**
- **Total Readings**: Count of vital sign entries in last 7 days
- **By Type**: Breakdown by vital sign type (BP, HR, weight, etc.)
- **Quick Actions**: Log new vital reading

## 📱 **Quick Actions**

### **Add Medication**
1. Click "Add Medication" button
2. Fill in:
   - **Name**: Medication name (required)
   - **Strength (Dosage)**: e.g., "50 mg" (optional)
   - **Dosage Instructions**: e.g., "1 tablet daily" (optional)
   - **Qty**: Total quantity dispensed (optional)
   - **Refills Left**: Remaining refills (optional)
   - **Doses/Day**: Used to calculate adherence (optional)
   - **Last Refilled**: Date (optional)
   - **Pharmacy**: e.g., Walgreens (optional)
   - **Condition**: e.g., diabetes (optional)
   - **Notes**: Additional information
3. Click "Save"

### **Log Medication Event**
1. Click "Log Event" on any medication card
2. Enter:
   - **Amount**: Dose taken
   - **Note**: Optional notes about the event
3. Click "Log Event"

### **Log Symptom**
1. Click "Log Symptom" button
2. Fill in:
   - **Label**: Symptom name (e.g., "Headache")
   - **Severity**: 1-5 scale (1=mild, 5=severe)
   - **Trigger**: What caused the symptom
   - **Note**: Additional details
3. Click "Log Symptom"

### **Log Vital Sign**
1. Click "Log Vital" button
2. Enter:
   - **Type**: Vital sign type (BP, HR, weight, temperature)
   - **Value**: Numerical reading
   - **Unit**: Measurement unit (mmHg, bpm, lbs, °F)
   - **Note**: Additional context
3. Click "Log Vital"

### **Schedule Appointment**
1. Click "Schedule Appointment" button
2. Fill in:
   - **Date & Time**: Appointment datetime
   - **Provider**: Doctor or healthcare provider
   - **Location**: Office or facility
   - **Purpose**: Reason for visit
   - **Notes**: Additional details
3. Click "Schedule"

## 🔧 **API Usage**

### **Authentication**
Currently no authentication required (single-user local app).

### **Base URL**
```
http://localhost:5000/health/
```

### **Common Endpoints**

#### **Medications**
```bash
# List all medications
GET /health/meds

# Create new medication
POST /health/meds
{
  "name": "Metformin",
  "dosage": "500 mg",
  "dose_text": "1 tablet twice daily",
  "qty": 180,
  "refills_left": 3,
  "last_refilled": "2025-07-14",
  "qty_per_day": 2,
  "condition": "diabetes",
  "pharmacy": "Walgreens",
  "notes": "Take with meals"
}

# Get medication details
GET /health/meds/{id}

# Update medication
PUT /health/meds/{id}
{
  "dose_text": "500 mg twice daily",
  "qty_per_day": 2,
  "refills_left": 2
}

# Delete medication
DELETE /health/meds/{id}

# Log medication event
POST /health/meds/{id}/log
{
  "amount": 1.0,
  "note": "Taken as prescribed"
}

# Import prescriptions from CSV (defaults to data/health - prescriptions.csv)
POST /health/meds/import
{}
```

### CSV Format

Your CSV can include columns (case-insensitive):

- name, dosage, qty, refill left, last refilled, qty per day, notes, condition, provider/pharmacy

Example (matches `data/health - prescriptions.csv`):

```
name,dosage,qty,refill left,last refilled,qty per day,notes,condition,Provider
Pioglitazone,15 mg,90,1,8/12/25,1,haven't been consistent,diabetes,Walgreens
```
```

#### **Symptoms**
```bash
# List recent symptoms
GET /health/symptoms

# Log new symptom
POST /health/symptoms
{
  "label": "Headache",
  "severity": 3,
  "trigger": "Stress",
  "note": "Moderate pain"
}
```

#### **Vitals**
```bash
# List recent vitals
GET /health/vitals

# Log new vital
POST /health/vitals
{
  "kind": "BP",
  "value_num": 120.0,
  "unit": "mmHg",
  "note": "Systolic pressure"
}
```

#### **Appointments**
```bash
# List appointments
GET /health/appointments

# Create appointment
POST /health/appointments
{
  "ts": "2025-08-12T10:00:00",
  "provider": "Dr. Gupta",
  "location": "KU Med (Virtual)",
  "purpose": "Kidney Transplant",
  "note": "Follow up with testing",
  "specialty": "Transplant",
  "is_virtual": true,
  "status": "planned",            # planned|completed|canceled|rescheduled
  "reminder_days": 7,              # days before to remind
  "follow_up_ts": "2025-09-05T09:00:00",
  "lab_due_ts": "2025-08-19T00:00:00"  
}
```

#### Appointment Tasks
```bash
# List tasks for an appointment
GET /health/appointments/{id}/tasks

# Create task
POST /health/appointments/{id}/tasks
{
  "label": "Do labs",
  "due_ts": "2025-08-19T00:00:00"
}

# Update/complete task
PUT /health/appointments/tasks/{task_id}
{
  "done": true
}
```

## 📊 **Data Export**

### **Dashboard Data**
Get all dashboard data as JSON:
```bash
GET /health/dashboard
```

Response includes:
- Medication summaries (now includes supply percent and refill-by when available)
- Symptom statistics
- Vital sign trends
- Appointment schedules

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **Page Not Loading**
- Ensure Flask app is running: `python app.py`
- Check database exists: `var/bonzibuddy.db`
- Verify migrations applied: `python scripts/db_apply.py`

#### **Data Not Saving**
- Check browser console for JavaScript errors
- Verify API endpoints are responding
- Ensure database has write permissions

#### **Missing Data**
- Check if database tables exist
- Verify migration 0005 was applied
- Check browser network tab for API errors

### **Getting Help**

1. **Check Logs**: Flask debug output in terminal
2. **Database**: Verify table structure with SQLite browser
3. **API Testing**: Use browser dev tools or Postman
4. **Documentation**: Review API endpoints and data model docs

## 🔮 **Future Features (v1+)**

### **Planned Enhancements**
- **Medication Scheduling**: Automated reminders and due dates
- **Condition Tracking**: Chronic condition management
- **Mental Health**: Mood and therapy session logging
- **Fitness Tracking**: Workout and exercise logging
- **Sleep Monitoring**: Sleep quality and patterns
- **Nutrition**: Meal tracking and hydration logging
- **Lab Results**: Medical test result management
- **Data Import/Export**: CSV, JSON, and external integrations

### Stelo CGM (Glucose Biosensor)

Planned v0.1 feature to manage a 15‑day Stelo CGM cycle and inventory:

- Log wear sessions (start, expected end, actual end, notes)
- Track inventory in packs of 2; show on‑hand and reorder point
- Countdown for active sensor and order reminders
- Quick actions: start/end sensor, add pack, adjust inventory
- Future: import from Stelo directly or via Oura; CSV import

Proposed endpoints:
- `GET /health/sensors/summary`
- `POST /health/sensors/uses/start`, `POST /health/sensors/uses/end`
- `GET /health/sensors/uses?type=stelo_cgm`
- `POST /health/sensors/inventory/add_pack`, `POST /health/sensors/inventory/adjust`

### Over-the-Counter (OTC) Medications

Goal: Track on‑hand quantity and low‑stock reminders for key OTC items (initial focus: Tums, Tylenol, Famotidine). Optionally log intake events (e.g., Tums) similar to prescription meds.

Planned features (v0.1):
- Maintain on‑hand quantity with units (e.g., tablets, mL)
- Low‑stock threshold and “Reorder soon” reminder on the dashboard
- Quick stock adjust (add/subtract) actions
- Optional intake logging (uses same event log as meds) and auto‑decrement on‑hand

Data model updates:
- Extend `Med` with fields:
  - `is_otc` (bool)
  - `on_hand_qty` (number)
  - `unit` (string, e.g., "tabs", "mL")
  - `low_threshold` (number)
- Behavior: when `is_otc` and a `MedEvent` is logged, decrease `on_hand_qty` by event `amount` (configurable per item)

New/updated endpoints (planned):
- `GET /health/otc/summary` → `{ total, low_count, items: [{id,name,on_hand_qty,unit,low}] }`
- `GET /health/otc` → list OTC items (subset of meds where `is_otc=true`)
- `POST /health/meds` / `PUT /health/meds/{id}` → accept OTC fields (`is_otc,on_hand_qty,unit,low_threshold`)
- `POST /health/meds/{id}/stock/adjust` → `{delta, reason?}`
- `POST /health/meds/{id}/log` → existing; when OTC, also decrements stock

UI (planned):
- Dashboard "OTC" card showing low items with quick “Add stock” and “Log Tums” actions
- Medications page gains columns for Unit, On‑hand, Low threshold, with filters for OTC only

### **Integration Possibilities**
- **Oura Ring**: Sleep and recovery data
- **Diabetes Devices**: CGM and glucose monitoring
- **Fitness Apps**: Workout and activity data
- **EHR Systems**: Electronic health record sync

## 📚 **Additional Resources**

- **[API Documentation](api/ENDPOINTS.md)** - Complete endpoint reference
- **[Data Model](data/DATA_MODEL.md)** - Database schema details
- **[Implementation Plan](planning/HealthImplementationPlan.md)** - Technical roadmap
- **[Health Features](features/health.md)** - Feature specifications

---

*This guide covers the v0 implementation. For advanced features and integrations, see the v1+ roadmap.*
