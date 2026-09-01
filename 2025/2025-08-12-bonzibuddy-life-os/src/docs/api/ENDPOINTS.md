# API Endpoints Documentation

This document describes all available REST API endpoints in the BonziBuddy application.

## 🏠 **Main Routes**

| Method | Endpoint | Description | Status |
|--------|----------|-------------|---------|
| `GET` | `/` | Home dashboard with domain cards | ✅ **Implemented** |
| `GET` | `/health/` | Health dashboard with data summaries | ✅ **Implemented** |
| `GET` | `/research/` | Research dashboard with data summaries | ✅ **Implemented (basic)** |
| `GET` | `/home/` | Home & Property dashboard with summaries | ✅ **Implemented (scaffold)** |
| `GET` | `/home/dashboard` | Home & Property dashboard JSON | ✅ **Implemented (scaffold)** |
| `GET` | `/home/assets/view` | Assets HTML UI | ✅ **Implemented (basic)** |
| `GET` | `/home/maintenance/view` | Maintenance HTML UI | ✅ **Implemented (basic)** |
| `GET` | `/home/chores/view` | Chores HTML UI | ✅ **Implemented (basic)** |
| `GET` | `/home/safety/view` | Safety HTML UI | ✅ **Implemented (basic)** |
| `GET` | `/home/maintenance/plans` | List maintenance plans | ✅ **Implemented (scaffold)** |
| `POST` | `/home/maintenance/plans` | Create maintenance plan | ✅ **Implemented (scaffold)** |
| `POST` | `/home/maintenance/plans/{id}/events` | Log maintenance event | ✅ **Implemented (scaffold)** |
| `GET` | `/home/assets` | List assets | ✅ **Implemented (scaffold)** |
| `POST` | `/home/assets` | Create asset | ✅ **Implemented (scaffold)** |
| `GET` | `/research/dashboard` | Research dashboard JSON counts | ✅ **Implemented** |

## 🏥 **Health Domain** ✅ **FULLY IMPLEMENTED**

### **Dashboard & Overview**
| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `GET` | `/health/` | Health dashboard HTML page | HTML Dashboard |
| `GET` | `/health/dashboard` | Dashboard data as JSON | JSON Data |

### **Medications Management**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/health/meds` | List all medications | - | JSON Array |
| `POST` | `/health/meds` | Create new medication | `{name, dose_text?, dosage?, qty?, refills_left?, last_refilled?, qty_per_day?, condition?, pharmacy?, notes?}` | JSON Object |
| `GET` | `/health/meds/<id>` | Get medication details | - | JSON Object |
| `PUT` | `/health/meds/<id>` | Update medication | `{name?, dose_text?, dosage?, qty?, refills_left?, last_refilled?, qty_per_day?, condition?, pharmacy?, notes?}` | JSON Object |
| `DELETE` | `/health/meds/<id>` | Delete medication | - | Success Message |
| `POST` | `/health/meds/<id>/log` | Log medication event | `{amount, note}` | JSON Object |
| `GET` | `/health/meds/<id>/events` | Get medication events | - | JSON Array |
| `POST` | `/health/meds/import` | Import prescriptions from CSV | `{path?}` (optional custom path; defaults to `data/health - prescriptions.csv`) | Stats `{created, updated, total}` |

Response objects for medications now include a `supply` field when calculable:

```json
"supply": {
  "days_total": 90.0,
  "days_elapsed": 30.0,
  "days_remaining": 60.0,
  "percent_left": 66.7,
  "refill_date": "2025-11-10T00:00:00",
  "due_soon": false,
  "overdue": false
}
```

### **Symptom Tracking**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/health/symptoms` | List recent symptoms | - | JSON Array |
| `POST` | `/health/symptoms` | Log new symptom | `{label, severity, trigger, note}` | JSON Object |

### **Vital Signs**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/health/vitals` | List recent vitals | - | JSON Array |
| `POST` | `/health/vitals` | Log new vital | `{kind, value_num, unit, note}` | JSON Object |

### **Appointments**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/health/appointments` | List appointments | Query: `include_past?`, `days_ahead?` | JSON Array |
| `POST` | `/health/appointments` | Create appointment | `{ts, provider, location, purpose, note?, specialty?, is_virtual?, status?, reminder_days?, follow_up_ts?, lab_due_ts?}` | JSON Object |
| `GET` | `/health/appointments/<id>` | Get appointment details | - | JSON Object |
| `PUT` | `/health/appointments/<id>` | Update appointment | Same as create (all optional) | JSON Object |
| `DELETE` | `/health/appointments/<id>` | Delete appointment | - | Success Message |
| `GET` | `/health/appointments/<id>/tasks` | List tasks | - | JSON Array |
| `POST` | `/health/appointments/<id>/tasks` | Create task | `{label, due_ts?}` | JSON Object |
| `PUT` | `/health/appointments/tasks/<task_id>` | Update task | `{label?, due_ts?, done?}` | JSON Object |

### **Labs**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/health/labs` | List lab orders | Query: `appointment_id?` | JSON Array |
| `POST` | `/health/labs` | Create lab order | `{label, appointment_id?, kind?, provider?, location?, instructions?, status?, scheduled_ts?, due_ts?, completed_ts?, reminder_days?, result_note?}` | JSON Object |
| `PUT` | `/health/labs/<id>` | Update lab order | Same fields (all optional) | JSON Object |

### **Sensors (Planned)**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/health/sensors/summary` | Summary for CGM/sensors | - | JSON Object |
| `POST` | `/health/sensors/uses/start` | Start a wear session | `{type_key, start_ts?, note?}` | JSON Object |
| `POST` | `/health/sensors/uses/end` | End a wear session | `{id, end_ts_actual?}` | JSON Object |
| `GET` | `/health/sensors/uses` | List wear sessions | Query: `type` | JSON Array |
| `POST` | `/health/sensors/inventory/add_pack` | Add inventory packs | `{type_key, packs, ts?}` | JSON Object |
| `POST` | `/health/sensors/inventory/adjust` | Manual adjust inventory | `{type_key, delta_sensors, note?}` | JSON Object |

### **OTC Medications (Planned)**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/health/otc/summary` | OTC dashboard summary | - | JSON Object |
| `GET` | `/health/otc` | List OTC items | - | JSON Array |
| `POST` | `/health/meds` | Create med (supports `is_otc,on_hand_qty,unit,low_threshold`) | `{...}` | JSON Object |
| `PUT` | `/health/meds/<id>` | Update med (same fields) | `{...}` | JSON Object |
| `POST` | `/health/meds/<id>/stock/adjust` | Adjust OTC stock | `{delta, reason?}` | JSON Object |

## 🎨 **Hobbies Domain** 🚧 **BASIC STRUCTURE**

| Method | Endpoint | Description | Status |
|--------|----------|-------------|---------|
| `GET` | `/hobbies/` | Hobbies dashboard | 🚧 **Placeholder** |
| `GET` | `/hobbies/projects` | List projects | 🚧 **Placeholder** |
| `POST` | `/hobbies/projects` | Create project | 🚧 **Placeholder** |
| `GET` | `/hobbies/sessions` | List sessions | 🚧 **Placeholder** |
| `POST` | `/hobbies/sessions` | Create session | 🚧 **Placeholder** |

## 🏠 **Home & Property Domain** ✅ **SCAFFOLD READY (v0)**

### **Dashboard & Overview**
| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `GET` | `/home/` | Home & Property dashboard HTML page | HTML Dashboard |
| `GET` | `/home/dashboard` | Dashboard data as JSON | JSON Data |
| `GET` | `/home/assets/view` | Assets HTML UI | HTML |
| `GET` | `/home/maintenance/view` | Maintenance HTML UI | HTML |
| `GET` | `/home/chores/view` | Chores HTML UI | HTML |
| `GET` | `/home/safety/view` | Safety HTML UI | HTML |

### **Assets (placeholder)**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/home/assets` | List assets | - | JSON Array |
| `POST` | `/home/assets` | Create asset | `{name, type?, brand?, model?, serial?, location?, notes?}` | JSON Object |
| `GET` | `/home/assets/<id>` | Get asset | - | JSON Object |
| `PUT` | `/home/assets/<id>` | Update asset | Fields optional | JSON Object |
| `DELETE` | `/home/assets/<id>` | Delete asset | - | Success Message |
| `GET` | `/home/assets/<id>/manuals` | List manuals | - | JSON Array |
| `POST` | `/home/assets/<id>/manuals` | Add manual | `{url?, file_path?, note?}` | JSON Object |
| `GET` | `/home/assets/<id>/warranties` | List warranties | - | JSON Array |
| `POST` | `/home/assets/<id>/warranties` | Add warranty | `{provider?, policy_no?, start_date?, end_date?, coverage_note?, claim_steps?}` | JSON Object |

### **Maintenance (placeholder)**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/home/maintenance/plans` | List maintenance plans | - | JSON Array |
| `POST` | `/home/maintenance/plans` | Create plan | `{title, asset_id?, cadence?, next_due?, last_done?, checklist?}` | JSON Object |
| `PUT` | `/home/maintenance/plans/<id>` | Update plan | Fields optional | JSON Object |
| `DELETE` | `/home/maintenance/plans/<id>` | Delete plan | - | Success Message |
| `POST` | `/home/maintenance/plans/<id>/events` | Log completion event | `{ts?, notes?, cost?}` | JSON Object |

### **Chores (placeholder)**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/home/chores/plans` | List chore plans | - | JSON Array |
| `POST` | `/home/chores/plans` | Create chore plan | `{title, cadence?, location_id?, next_due?, last_done?, checklist?}` | JSON Object |
| `POST` | `/home/chores/plans/<id>/events` | Log chore event | `{ts?, who?, notes?}` | JSON Object |

### **Safety (placeholder)**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/home/safety/devices` | List safety devices | - | JSON Array |
| `POST` | `/home/safety/devices` | Create safety device | `{type, model?, location_id?, next_test_due?, last_test?, test_cadence?}` | JSON Object |
| `POST` | `/home/safety/devices/<id>/test` | Record a test | `{last_test?, next_test_due?}` | JSON Object |

Notes: These are temporary in-memory endpoints to unblock UI; will be replaced by SQLAlchemy-backed models as outlined in `planning/HomePropImplementationPlan.md`.

## 🔬 **Research Domain** 🚧 **SPEC DRAFTED (v0 PLANNED)**

### **Dashboard & Overview**
| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `GET` | `/research/` | Research dashboard HTML page | HTML Dashboard |
| `GET` | `/research/dashboard` | Dashboard counts (events, sources, notes, highlights, questions) | JSON Data |

### **Current Events**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/research/events` | List current events | Query: `q?, tag?, from?, to?, outlet?, page?, page_size?` | JSON Array |
| `POST` | `/research/events` | Create event | `{date_ts, headline, outlet?, summary?, url?, tags?}` | JSON Object |
| `GET` | `/research/events/<id>` | Get event details | - | JSON Object |
| `PUT` | `/research/events/<id>` | Update event | Fields optional | JSON Object |
| `DELETE` | `/research/events/<id>` | Delete event | - | Success Message |
| `POST` | `/research/events/import/csv` | Import events from CSV | JSON: `{path?, dry_run?, list_tag?}` or Multipart: `file`, `list_tag?` | Stats `{created, updated, total, dry_run}` |
| `GET` | `/research/events/view` | Events HTML UI | - | HTML |

### **Sources**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/research/sources` | List sources | Query: `q?, kind?, year?, tag?, page?, page_size?` | JSON Array |
| `POST` | `/research/sources` | Create source | `{kind, title, author?, year?, url?, doi?, arxiv_id?, venue?, publisher?, abstract?, tags?}` | JSON Object |
| `GET` | `/research/sources/<id>` | Get source details | - | JSON Object |
| `PUT` | `/research/sources/<id>` | Update source | Fields optional | JSON Object |
| `DELETE` | `/research/sources/<id>` | Delete source | - | Success Message |
| `POST` | `/research/sources/<id>/attachments` | Attach local file | `{path, note?}` | JSON Object |
| `GET` | `/research/sources/<id>/evidence` | List evidence for a source | - | JSON Array |
| `POST` | `/research/sources/import/csv` | Import sources from CSV | JSON: `{path?, dry_run?, list_tag?}` or Multipart: `file`, `list_tag?` | Stats `{created, updated, total, dry_run}` |
| `GET` | `/research/sources/view` | Sources HTML UI | - | HTML |
| `GET` | `/research/sources/detail?id={id}` | Source detail HTML UI | - | HTML |

### **Notes & Highlights**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/research/notes` | List notes | Query: `source_id?, question_id?, q?` | JSON Array |
| `POST` | `/research/notes` | Create note | `{source_id?, question_id?, body, kind?}` | JSON Object |
| `PUT` | `/research/notes/<id>` | Update note | `{body?, kind?, pinned?}` | JSON Object |
| `DELETE` | `/research/notes/<id>` | Delete note | - | Success Message |
| `GET` | `/research/highlights` | List highlights | Query: `source_id?, q?` | JSON Array |
| `POST` | `/research/highlights` | Create highlight | `{source_id, text, location?, comment?, tags?}` | JSON Object |
| `PUT` | `/research/highlights/<id>` | Update highlight | Fields optional | JSON Object |
| `DELETE` | `/research/highlights/<id>` | Delete highlight | - | Success Message |

### **Questions & Evidence**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/research/questions` | List questions | Query: `status?, tag?` | JSON Array |
| `POST` | `/research/questions` | Create question | `{text, area?, status?}` | JSON Object |
| `GET` | `/research/questions/<id>` | Get question | - | JSON Object |
| `PUT` | `/research/questions/<id>` | Update question | Fields optional | JSON Object |
| `DELETE` | `/research/questions/<id>` | Delete question | - | Success Message |
| `GET` | `/research/questions/<id>/evidence` | List evidence links | - | JSON Array |
| `POST` | `/research/questions/<id>/evidence` | Link a source with stance | `{source_id, stance?, note?}` | JSON Object |
| `DELETE` | `/research/evidence/<id>` | Remove evidence link | - | Success Message |

### **External Links**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/research/links/<entity_type>/<id>` | List external links for entity | - | JSON Array |
| `POST` | `/research/links/<entity_type>/<id>` | Add external link (Google Docs/Sheets/Web) | `{provider, kind?, title?, url?, external_id?, note?}` | JSON Object |
| `DELETE` | `/research/links/<id>` | Delete external link | - | Success Message |

### **Tags**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/research/tags` | List all tags used by research entities | - | JSON Array |
| `GET` | `/research/tags/<entity_type>/<id>` | List tags for an entity (`source` or `news_event`) | - | JSON Array |
| `POST` | `/research/tags/<entity_type>/<id>` | Add a tag to an entity | `{name}` | JSON Object |
| `DELETE` | `/research/tags/<entity_type>/<id>/<tag_id>` | Remove tag from entity | - | Success Message |

### **Search (v1)**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/research/search` | Unified FTS search across entities | Query: `q` | Grouped JSON Results |

## 📊 **Response Formats**

### **Success Response**
```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully"
}
```

### **Error Response**
```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

### **Health Dashboard Data**
```json
{
  "meds": {
    "total": 5,
    "recent_events": [...]
  },
  "symptoms": {
    "total": 12,
    "by_severity": {...},
    "by_label": {...},
    "avg_severity": 2.5
  },
  "vitals": {
    "total": 8,
    "by_kind": {...},
    "recent": [...]
  },
  "appointments": {
    "upcoming": 2,
    "next": {...}
  }
}
```

## 🔐 **Authentication & Security**

- **Current**: No authentication (single-user local app)
- **Future**: JWT-based authentication for multi-user support
- **Data**: All health data stored locally in SQLite database
- **Audit**: All changes logged to audit table

---

*Last Updated: August 2025 - Health API Complete; Research API Spec Drafted; Home & Property Scaffold Ready*
