# Health Features Usage Guide

**Status:** v0 Implementation Complete
**Last Updated:** 2024-12-19

This guide explains how to use the health features in BonziBuddy v0.

---

## Quick Start

1. **Navigate to Health Dashboard**: Click "Health" in the main navigation
2. **Add Your First Medication**: Use the "Add Medication" button
3. **Log Daily Activities**: Use the quick action buttons to log symptoms, vitals, and appointments
4. **Monitor Progress**: View adherence percentages and health trends on the dashboard

---

## Dashboard Overview

The health dashboard provides a comprehensive view of your health data with six main cards:

### 1. Medications Card
- **Shows**: Total medications, recent adherence percentages
- **Actions**: View all medications, add new ones
- **Features**: Adherence tracking (last 14 days)

### 2. Appointments Card
- **Shows**: Upcoming appointments count, next appointment details
- **Actions**: View all appointments, add new ones
- **Features**: 30-day outlook

### 3. Recent Symptoms Card
- **Shows**: Symptoms logged in last 7 days, average severity
- **Actions**: View all symptoms, log new ones
- **Features**: Severity tracking (1-5 scale)

### 4. Recent Vitals Card
- **Shows**: Vital signs logged in last 7 days, grouped by type
- **Actions**: View all vitals, log new ones
- **Features**: Multiple vital types (BP, HR, Weight, etc.)

### 5. Recent Activity Card
- **Shows**: Latest health activities across all domains
- **Actions**: View detailed activity history

### 6. Health Summary Card
- **Shows**: Key metrics and counts
- **Actions**: Refresh dashboard data

---

## Quick Actions

### Add Medication
1. Click "Add Medication" button
2. Fill in:
   - **Name** (required): Medication name
   - **Dosage Instructions**: How to take it
   - **Notes**: Additional information
3. Click "Add Medication"

### Log Symptom
1. Click "Log Symptom" button
2. Fill in:
   - **Symptom** (required): What you're experiencing
   - **Severity** (required): 1-5 scale
   - **Trigger**: What caused it
   - **Notes**: Additional details
3. Click "Log Symptom"

### Log Vital Sign
1. Click "Log Vital" button
2. Fill in:
   - **Vital Type** (required): BP, HR, Weight, etc.
   - **Value** (required): Numeric measurement
   - **Unit**: mmHg, bpm, lbs, °F, etc.
   - **Notes**: Additional context
3. Click "Log Vital"

### Add Appointment
1. Click "Add Appointment" button
2. Fill in:
   - **Date & Time** (required): When it's scheduled
   - **Provider** (required): Doctor/clinic name
   - **Location**: Where it's happening
   - **Purpose**: Why you're going
   - **Notes**: Additional details
3. Click "Add Appointment"

---

## API Endpoints

The health features provide RESTful API endpoints for programmatic access:

### Medications
- `GET /health/meds` - List all medications
- `POST /health/meds` - Create new medication
- `GET /health/meds/{id}` - Get medication details
- `PUT /health/meds/{id}` - Update medication
- `DELETE /health/meds/{id}` - Delete medication
- `POST /health/meds/{id}/log` - Log medication event
- `GET /health/meds/{id}/events` - Get medication events

### Symptoms
- `GET /health/symptoms` - List symptoms (with optional `days` parameter)
- `POST /health/symptoms` - Log new symptom

### Vital Signs
- `GET /health/vitals` - List vitals (with optional `kind` and `days` parameters)
- `POST /health/vitals` - Log new vital sign

### Appointments
- `GET /health/appointments` - List appointments (with optional `days_ahead` and `include_past` parameters)
- `POST /health/appointments` - Create new appointment
- `GET /health/appointments/{id}` - Get appointment details
- `PUT /health/appointments/{id}` - Update appointment
- `DELETE /health/appointments/{id}` - Delete appointment

### Dashboard Data
- `GET /health/dashboard` - Get dashboard data as JSON
- `GET /health/` - View dashboard HTML

---

## Data Models

### Medication
```json
{
  "id": 1,
  "name": "Aspirin",
  "dose_text": "1 tablet daily",
  "notes": "Take with food",
  "created_at": "2024-01-15T10:00:00",
  "adherence_pct": 85.7
}
```

### Symptom Log
```json
{
  "id": 1,
  "ts": "2024-01-15T10:00:00",
  "label": "Headache",
  "severity": 3,
  "trigger": "Stress",
  "note": "Moderate pain"
}
```

### Vital Sign
```json
{
  "id": 1,
  "ts": "2024-01-15T10:00:00",
  "kind": "BP",
  "value_num": 120.0,
  "unit": "mmHg",
  "note": "Systolic pressure"
}
```

### Appointment
```json
{
  "id": 1,
  "ts": "2024-01-20T14:00:00",
  "provider": "Dr. Smith",
  "location": "Medical Center",
  "purpose": "Annual check-up",
  "note": "Bring lab results"
}
```

---

## Usage Examples

### Adding a Daily Medication
1. Add medication: "Vitamin D" with dosage "1000 IU daily"
2. Each day, use "Log Medication Event" to record taking it
3. Monitor adherence percentage on dashboard

### Tracking Blood Pressure
1. Log BP readings regularly (e.g., morning and evening)
2. Use "BP" as vital type with systolic value
3. Add notes for context (e.g., "Morning reading, before coffee")

### Managing Appointments
1. Add upcoming appointments with full details
2. Use notes field for prep instructions
3. Review upcoming appointments on dashboard

### Symptom Tracking
1. Log symptoms as they occur
2. Use consistent labels (e.g., "Headache", "Fatigue")
3. Track severity changes over time
4. Note triggers to identify patterns

---

## Best Practices

### Medication Management
- **Be Consistent**: Log every dose taken
- **Use Clear Names**: Full medication names, not abbreviations
- **Include Context**: Note any side effects or changes

### Symptom Tracking
- **Standardize Labels**: Use consistent symptom names
- **Track Severity**: Use the 1-5 scale consistently
- **Note Triggers**: Help identify patterns and causes

### Vital Signs
- **Regular Monitoring**: Log at consistent times
- **Include Units**: Always specify measurement units
- **Context Matters**: Note conditions (e.g., "After exercise")

### Appointments
- **Complete Information**: Fill in all relevant fields
- **Prep Notes**: Use notes for preparation instructions
- **Follow-up Tracking**: Note when follow-ups are needed

---

## Troubleshooting

### Common Issues

**"Medication not found" error**
- Ensure the medication ID is correct
- Check that the medication exists in the system

**"Invalid timestamp format" error**
- Use ISO format: YYYY-MM-DDTHH:MM:SS
- Example: 2024-01-15T14:30:00

**Dashboard not loading data**
- Check browser console for JavaScript errors
- Verify database connection
- Refresh the page

**Form validation errors**
- Ensure required fields are filled
- Check data types (numbers for severity, values)
- Verify date formats

### Getting Help

1. Check the browser console for error messages
2. Review the API response for validation errors
3. Verify data format matches expected schema
4. Check database connectivity

---

## Future Features (v1+)

- **Preventive Care Rules**: Automated screening reminders
- **Provider Directory**: Care team contact management
- **Mental Health Tracking**: Mood logs and therapy plans
- **Fitness Tracking**: Workout logs and progress
- **Sleep Monitoring**: Sleep quality and patterns
- **Data Export**: CSV/JSON export functionality
- **Import Tools**: Oura Ring, CGM data integration

---

## Security & Privacy

- **Local Storage**: All data is stored locally on your device
- **No Cloud Sync**: Data never leaves your computer
- **Audit Logging**: All changes are tracked for accountability
- **Data Export**: Backup your data regularly

**Recommendation**: Enable full-disk encryption on your device for sensitive health data.
