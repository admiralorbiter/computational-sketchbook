from flask import Blueprint, request, jsonify, render_template
import os
from datetime import datetime
from ...core.db import get_session
from .services import ResearchService

bp = Blueprint("research", __name__)

@bp.get("/")
def index():
    db = get_session()
    svc = ResearchService(db)
    counts = svc.get_dashboard_counts()
    return render_template("research/dashboard.html", data=counts)

@bp.get("/dashboard")
def dashboard_counts():
    db = get_session()
    svc = ResearchService(db)
    return jsonify(svc.get_dashboard_counts())

# Events
@bp.get("/events/view")
def events_view():
    return render_template("research/events.html")

@bp.get("/events")
def list_events():
    db = get_session()
    svc = ResearchService(db)
    filters = {
        'q': request.args.get('q'),
        'outlet': request.args.get('outlet'),
        'from': request.args.get('from'),
        'to': request.args.get('to'),
        'tag': request.args.get('tag'),
        'page': request.args.get('page', type=int),
        'page_size': request.args.get('page_size', type=int)
    }
    return jsonify(svc.list_events(filters))

@bp.post("/events")
def create_event():
    data = request.get_json() or {}
    if 'headline' not in data:
        return jsonify({'error': 'headline is required'}), 400
    db = get_session()
    svc = ResearchService(db)
    ev = svc.create_event(data)
    return jsonify(ev), 201

@bp.get("/events/<int:event_id>")
def get_event(event_id):
    db = get_session()
    svc = ResearchService(db)
    ev = svc.get_event(event_id)
    if not ev:
        return jsonify({'error': 'not found'}), 404
    return jsonify(ev)

@bp.put("/events/<int:event_id>")
def update_event(event_id):
    data = request.get_json() or {}
    db = get_session()
    svc = ResearchService(db)
    ev = svc.update_event(event_id, data)
    if not ev:
        return jsonify({'error': 'not found'}), 404
    return jsonify(ev)

@bp.delete("/events/<int:event_id>")
def delete_event(event_id):
    db = get_session()
    svc = ResearchService(db)
    ok = svc.delete_event(event_id)
    if not ok:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'message': 'deleted'})

# Sources
@bp.get("/sources/view")
def sources_view():
    return render_template("research/sources.html")

@bp.get("/sources/detail")
def source_detail_view():
    return render_template("research/source_detail.html")

@bp.get("/sources")
def list_sources():
    db = get_session()
    svc = ResearchService(db)
    filters = {
        'q': request.args.get('q'),
        'kind': request.args.get('kind'),
        'year': request.args.get('year'),
        'tag': request.args.get('tag'),
        'page': request.args.get('page', type=int),
        'page_size': request.args.get('page_size', type=int)
    }
    return jsonify(svc.list_sources(filters))

@bp.post("/sources")
def create_source():
    data = request.get_json() or {}
    if 'title' not in data:
        return jsonify({'error': 'title is required'}), 400
    db = get_session()
    svc = ResearchService(db)
    src = svc.create_source(data)
    return jsonify(src), 201

@bp.get("/sources/<int:source_id>")
def get_source(source_id):
    db = get_session()
    svc = ResearchService(db)
    src = svc.get_source(source_id)
    if not src:
        return jsonify({'error': 'not found'}), 404
    return jsonify(src)

@bp.put("/sources/<int:source_id>")
def update_source(source_id):
    data = request.get_json() or {}
    db = get_session()
    svc = ResearchService(db)
    src = svc.update_source(source_id, data)
    if not src:
        return jsonify({'error': 'not found'}), 404
    return jsonify(src)

@bp.delete("/sources/<int:source_id>")
def delete_source(source_id):
    db = get_session()
    svc = ResearchService(db)
    ok = svc.delete_source(source_id)
    if not ok:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'message': 'deleted'})

@bp.get("/sources/<int:source_id>/evidence")
def list_evidence_by_source(source_id):
    db = get_session()
    svc = ResearchService(db)
    return jsonify(svc.list_evidence_by_source(source_id))

# External links (generic; supports Google Docs/Sheets links)
@bp.get("/links/<entity_type>/<int:entity_id>")
def list_links(entity_type, entity_id):
    db = get_session()
    svc = ResearchService(db)
    return jsonify(svc.list_external_links(entity_type, entity_id))

@bp.post("/links/<entity_type>/<int:entity_id>")
def add_link(entity_type, entity_id):
    data = request.get_json() or {}
    if not data.get('url') and not data.get('external_id'):
        return jsonify({'error': 'url or external_id required'}), 400
    db = get_session()
    svc = ResearchService(db)
    link = svc.add_external_link(entity_type, entity_id, data)
    return jsonify(link), 201

@bp.delete("/links/<int:link_id>")
def delete_link(link_id):
    db = get_session()
    svc = ResearchService(db)
    ok = svc.delete_external_link(link_id)
    if not ok:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'message': 'deleted'})

# Tags
@bp.get("/tags")
def list_tags():
    db = get_session()
    svc = ResearchService(db)
    return jsonify(svc.list_tags())

@bp.get("/tags/<entity_type>/<int:entity_id>")
def list_entity_tags(entity_type, entity_id):
    db = get_session()
    svc = ResearchService(db)
    return jsonify(svc.list_entity_tags(entity_type, entity_id))

@bp.post("/tags/<entity_type>/<int:entity_id>")
def add_tag(entity_type, entity_id):
    body = request.get_json() or {}
    name = body.get('name')
    if not name:
        return jsonify({'error': 'name is required'}), 400
    db = get_session()
    svc = ResearchService(db)
    return jsonify(svc.add_tag(entity_type, entity_id, name)), 201

@bp.delete("/tags/<entity_type>/<int:entity_id>/<int:tag_id>")
def delete_tag(entity_type, entity_id, tag_id):
    db = get_session()
    svc = ResearchService(db)
    ok = svc.remove_tag(entity_type, entity_id, tag_id)
    if not ok:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'message': 'deleted'})

# Notes
@bp.get("/notes")
def list_notes():
    db = get_session()
    svc = ResearchService(db)
    filters = {
        'source_id': request.args.get('source_id', type=int),
        'question_id': request.args.get('question_id', type=int),
        'q': request.args.get('q'),
        'page': request.args.get('page', type=int),
        'page_size': request.args.get('page_size', type=int)
    }
    return jsonify(svc.list_notes(filters))

@bp.post("/notes")
def create_note():
    data = request.get_json() or {}
    if 'body' not in data:
        return jsonify({'error': 'body is required'}), 400
    db = get_session()
    svc = ResearchService(db)
    note = svc.create_note(data)
    return jsonify(note), 201

@bp.put("/notes/<int:note_id>")
def update_note(note_id):
    data = request.get_json() or {}
    db = get_session()
    svc = ResearchService(db)
    note = svc.update_note(note_id, data)
    if not note:
        return jsonify({'error': 'not found'}), 404
    return jsonify(note)

@bp.delete("/notes/<int:note_id>")
def delete_note(note_id):
    db = get_session()
    svc = ResearchService(db)
    ok = svc.delete_note(note_id)
    if not ok:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'message': 'deleted'})

# Highlights
@bp.get("/highlights")
def list_highlights():
    db = get_session()
    svc = ResearchService(db)
    filters = {
        'source_id': request.args.get('source_id', type=int),
        'q': request.args.get('q'),
        'page': request.args.get('page', type=int),
        'page_size': request.args.get('page_size', type=int)
    }
    return jsonify(svc.list_highlights(filters))

@bp.post("/highlights")
def create_highlight():
    data = request.get_json() or {}
    if 'source_id' not in data or 'text' not in data:
        return jsonify({'error': 'source_id and text are required'}), 400
    db = get_session()
    svc = ResearchService(db)
    h = svc.create_highlight(data)
    return jsonify(h), 201

@bp.put("/highlights/<int:hid>")
def update_highlight(hid):
    data = request.get_json() or {}
    db = get_session()
    svc = ResearchService(db)
    h = svc.update_highlight(hid, data)
    if not h:
        return jsonify({'error': 'not found'}), 404
    return jsonify(h)

@bp.delete("/highlights/<int:hid>")
def delete_highlight(hid):
    db = get_session()
    svc = ResearchService(db)
    ok = svc.delete_highlight(hid)
    if not ok:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'message': 'deleted'})

# Questions & Evidence
@bp.get("/questions")
def list_questions():
    db = get_session()
    svc = ResearchService(db)
    filters = {'status': request.args.get('status')}
    return jsonify(svc.list_questions(filters))

@bp.post("/questions")
def create_question():
    data = request.get_json() or {}
    if 'text' not in data:
        return jsonify({'error': 'text is required'}), 400
    db = get_session()
    svc = ResearchService(db)
    q = svc.create_question(data)
    return jsonify(q), 201

@bp.get("/questions/<int:qid>")
def get_question(qid):
    db = get_session()
    svc = ResearchService(db)
    q = svc.get_question(qid)
    if not q:
        return jsonify({'error': 'not found'}), 404
    return jsonify(q)

@bp.put("/questions/<int:qid>")
def update_question(qid):
    data = request.get_json() or {}
    db = get_session()
    svc = ResearchService(db)
    q = svc.update_question(qid, data)
    if not q:
        return jsonify({'error': 'not found'}), 404
    return jsonify(q)

@bp.delete("/questions/<int:qid>")
def delete_question(qid):
    db = get_session()
    svc = ResearchService(db)
    ok = svc.delete_question(qid)
    if not ok:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'message': 'deleted'})

@bp.get("/questions/<int:qid>/evidence")
def list_evidence(qid):
    db = get_session()
    svc = ResearchService(db)
    return jsonify(svc.list_evidence(qid))

@bp.post("/questions/<int:qid>/evidence")
def add_evidence(qid):
    data = request.get_json() or {}
    if 'source_id' not in data:
        return jsonify({'error': 'source_id is required'}), 400
    db = get_session()
    svc = ResearchService(db)
    ev = svc.add_evidence(qid, data)
    return jsonify(ev), 201

@bp.delete("/evidence/<int:eid>")
def delete_evidence(eid):
    db = get_session()
    svc = ResearchService(db)
    ok = svc.delete_evidence(eid)
    if not ok:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'message': 'deleted'})

# CSV Imports
@bp.post("/events/import/csv")
def import_events_csv():
    db = get_session()
    svc = ResearchService(db)
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        file = request.files.get('file')
        list_tag = (request.form.get('list_tag') or '').strip() or None
        if not file:
            return jsonify({'error': 'file is required'}), 400
        tmp_dir = os.path.join('var', 'uploads')
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_path = os.path.join(tmp_dir, f"events_{int(datetime.now().timestamp())}.csv")
        file.save(tmp_path)
        try:
            result = svc.import_events_from_csv(tmp_path, dry_run=False, extra_tags=[list_tag] if list_tag else None)
            return jsonify({'success': True, 'stats': result})
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
    else:
        body = request.get_json(silent=True) or {}
        list_tag = body.get('list_tag')
        try:
            result = svc.import_events_from_csv(body.get('path'), dry_run=bool(body.get('dry_run')), extra_tags=[list_tag] if list_tag else None)
            return jsonify({'success': True, 'stats': result})
        except FileNotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@bp.post("/sources/import/csv")
def import_sources_csv():
    # Supports JSON body (path) and optional list_tag, or multipart file upload
    db = get_session()
    svc = ResearchService(db)
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        file = request.files.get('file')
        list_tag = (request.form.get('list_tag') or '').strip() or None
        if not file:
            return jsonify({'error': 'file is required'}), 400
        tmp_dir = os.path.join('var', 'uploads')
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_path = os.path.join(tmp_dir, f"sources_{int(datetime.now().timestamp())}.csv")
        file.save(tmp_path)
        try:
            result = svc.import_sources_from_csv(tmp_path, dry_run=False, extra_tags=[list_tag] if list_tag else None)
            return jsonify({'success': True, 'stats': result})
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
    else:
        body = request.get_json(silent=True) or {}
        list_tag = body.get('list_tag')
        try:
            result = svc.import_sources_from_csv(body.get('path'), dry_run=bool(body.get('dry_run')), extra_tags=[list_tag] if list_tag else None)
            return jsonify({'success': True, 'stats': result})
        except FileNotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
