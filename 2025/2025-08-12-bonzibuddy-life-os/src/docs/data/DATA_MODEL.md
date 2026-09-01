# Data Model (v0)

**Status:** ✅ **IMPLEMENTED**  
**Last Updated:** August 2025  
**Database:** SQLite with 17 tables

## 🏗️ **Core Tables** ✅ **IMPLEMENTED**

| Table | Columns | Description | Status |
|-------|---------|-------------|---------|
| **schema_version** | `version INT, applied_at DATETIME` | Migration tracking | ✅ **Active** |
| **profile** | `id PK, display_name, timezone, created_at` | User profile | ✅ **Active** |
| **tag** | `id PK, name UNIQUE` | Categorization tags | ✅ **Active** |
| **attachment** | `id PK, path, mime, bytes, note, created_at` | File attachments | ✅ **Active** |
| **audit** | `id PK, ts, actor, action, entity, entity_id, note` | Change logging | ✅ **Active** |

## 🏥 **Health Domain** ✅ **FULLY IMPLEMENTED**

| Table | Columns | Description | Relationships | Status |
|-------|---------|-------------|---------------|---------|
| **med** | `id PK, name, dose_text, notes, created_at` | Medications | → med_event | ✅ **Active** |
| **med_event** | `id PK, med_id FK, ts, amount, note, created_at` | Medication logs | ← med | ✅ **Active** |
| **symptom_log** | `id PK, ts, label, severity INT, trigger, note, created_at` | Symptom tracking | - | ✅ **Active** |
| **vital** | `id PK, ts, kind, value_num, unit, note, created_at` | Vital signs | - | ✅ **Active** |
| **appointment** | `id PK, ts, provider, location, purpose, note, created_at` | Medical appointments | - | ✅ **Active** |

### **Health Data Relationships**
```
med (1) ←→ (many) med_event
med_event.med_id → med.id (FK)
```

### **Health Data Examples**
```sql
-- Sample medication
INSERT INTO med (name, dose_text, notes) 
VALUES ('Aspirin', '81mg daily', 'Take with food');

-- Sample symptom log
INSERT INTO symptom_log (label, severity, trigger, note) 
VALUES ('Headache', 3, 'Stress', 'Moderate pain');

-- Sample vital sign
INSERT INTO vital (kind, value_num, unit, note) 
VALUES ('BP', 120.0, 'mmHg', 'Systolic pressure');
```

## Hobbies
- **project**(id PK, domain TEXT, title, status, started_at, note)
- **session**(id PK, project_id FK, ts_start, ts_end, focus, quality INT, note)
- **milestone**(id PK, project_id FK, title, due_date, done BOOL)

## Research
- **question**(id PK, text, area, status, created_at)
- **source**(id PK, kind, title, author, year, url, citation)
- **note**(id PK, source_id FK NULL, question_id FK NULL, ts, body)
- **highlight**(id PK, source_id FK, location, text)

## Timezones
- Store UTC in `ts*`; render per `profile.timezone`.
