from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, text
from datetime import datetime
from dateutil import parser as date_parser
import csv
import os

from ...core.db import get_session


class ResearchService:
    """Service layer for research domain business logic."""

    def __init__(self, db_session: Session):
        self.db = db_session

    # Dashboard counts
    def get_dashboard_counts(self) -> Dict[str, int]:
        counts = {
            'events': self._count('news_event'),
            'sources': self._count('source'),
            'notes': self._count('note'),
            'highlights': self._count('highlight'),
            'questions': self._count('question'),
        }
        return counts

    def _count(self, table_name: str) -> int:
        return int(self.db.execute(text(f"SELECT COUNT(1) FROM {table_name}"))
                   .scalar() or 0)

    # Events
    def list_events(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        where = []
        params = {}
        if filters.get('q'):
            where.append("(headline LIKE :q OR summary LIKE :q OR outlet LIKE :q)")
            params['q'] = f"%{filters['q']}%"
        if filters.get('outlet'):
            where.append("outlet = :outlet")
            params['outlet'] = filters['outlet']
        if filters.get('from'):
            where.append("date_ts >= :from_dt")
            params['from_dt'] = filters['from']
        if filters.get('to'):
            where.append("date_ts <= :to_dt")
            params['to_dt'] = filters['to']
        if filters.get('tag'):
            where.append("EXISTS (SELECT 1 FROM tag_map tm JOIN tag t ON t.id = tm.tag_id WHERE tm.entity_type = 'news_event' AND tm.entity_id = news_event.id AND t.name = :tag)")
            params['tag'] = filters['tag']
        sql = "SELECT id, date_ts, headline, outlet, summary, url, added_ts FROM news_event"
        if where:
            sql += " WHERE " + " AND ".join(where)
        # SQLite lacks NULLS LAST; emulate with (date_ts IS NULL) ASC
        sql += " ORDER BY (date_ts IS NULL) ASC, date_ts DESC, id DESC"
        # Pagination
        page_size = int(filters.get('page_size') or 25)
        if page_size > 100:
            page_size = 100
        if page_size <= 0:
            page_size = 25
        page = int(filters.get('page') or 1)
        if page < 1:
            page = 1
        params['limit'] = page_size
        params['offset'] = (page - 1) * page_size
        sql += " LIMIT :limit OFFSET :offset"
        rows = self.db.execute(text(sql), params).mappings().all()
        return [dict(r) for r in rows]

    def create_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        date_ts = data.get('date_ts')
        self.db.execute(
            text("""
            INSERT INTO news_event(date_ts, headline, outlet, summary, url)
            VALUES (:date_ts, :headline, :outlet, :summary, :url)
            """),
            {
                'date_ts': date_ts,
                'headline': data['headline'],
                'outlet': data.get('outlet'),
                'summary': data.get('summary'),
                'url': data.get('url')
            }
        )
        self.db.commit()
        new_id = int(self.db.execute(text("SELECT last_insert_rowid()"))
                     .scalar())
        return self.get_event(new_id) or {'id': new_id}

    def get_event(self, event_id: int) -> Optional[Dict[str, Any]]:
        row = self.db.execute(
            text("SELECT id, date_ts, headline, outlet, summary, url, added_ts FROM news_event WHERE id = :id"),
            {'id': event_id}
        ).mappings().first()
        return dict(row) if row else None

    def update_event(self, event_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        current = self.get_event(event_id)
        if not current:
            return None
        fields = ['date_ts', 'headline', 'outlet', 'summary', 'url']
        sets = []
        params = {'id': event_id}
        for f in fields:
            if f in data:
                sets.append(f"{f} = :{f}")
                params[f] = data[f]
        if not sets:
            return current
        sql = f"UPDATE news_event SET {', '.join(sets)} WHERE id = :id"
        self.db.execute(text(sql), params)
        self.db.commit()
        return self.get_event(event_id)

    def delete_event(self, event_id: int) -> bool:
        res = self.db.execute(text("DELETE FROM news_event WHERE id = :id"), {'id': event_id})
        self.db.commit()
        return res.rowcount > 0

    # Notes
    def list_notes(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        where = []
        params: Dict[str, Any] = {}
        if filters.get('source_id'):
            where.append("source_id = :source_id")
            params['source_id'] = filters['source_id']
        if filters.get('question_id'):
            where.append("question_id = :question_id")
            params['question_id'] = filters['question_id']
        if filters.get('q'):
            where.append("(body LIKE :q)")
            params['q'] = f"%{filters['q']}%"
        sql = "SELECT id, source_id, question_id, ts, body, kind, pinned FROM note"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY ts DESC, id DESC"
        # Pagination (defaults are small when used on dashboard; callers can override)
        page_size = int(filters.get('page_size') or 25)
        if page_size > 100:
            page_size = 100
        if page_size <= 0:
            page_size = 25
        page = int(filters.get('page') or 1)
        if page < 1:
            page = 1
        params['limit'] = page_size
        params['offset'] = (page - 1) * page_size
        sql += " LIMIT :limit OFFSET :offset"
        rows = self.db.execute(text(sql), params).mappings().all()
        return [dict(r) for r in rows]

    def create_note(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.db.execute(
            text("""
            INSERT INTO note(source_id, question_id, body, kind)
            VALUES (:source_id, :question_id, :body, :kind)
            """),
            {
                'source_id': data.get('source_id'),
                'question_id': data.get('question_id'),
                'body': data['body'],
                'kind': data.get('kind')
            }
        )
        self.db.commit()
        new_id = int(self.db.execute(text("SELECT last_insert_rowid()")).scalar())
        return self.get_note(new_id) or {'id': new_id}

    def get_note(self, note_id: int) -> Optional[Dict[str, Any]]:
        row = self.db.execute(
            text("SELECT id, source_id, question_id, ts, body, kind, pinned FROM note WHERE id = :id"),
            {'id': note_id}
        ).mappings().first()
        return dict(row) if row else None

    def update_note(self, note_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        current = self.get_note(note_id)
        if not current:
            return None
        fields = ['source_id','question_id','body','kind','pinned']
        sets, params = [], {'id': note_id}
        for f in fields:
            if f in data:
                sets.append(f"{f} = :{f}")
                params[f] = data[f]
        if not sets:
            return current
        self.db.execute(text(f"UPDATE note SET {', '.join(sets)} WHERE id = :id"), params)
        self.db.commit()
        return self.get_note(note_id)

    def delete_note(self, note_id: int) -> bool:
        res = self.db.execute(text("DELETE FROM note WHERE id = :id"), {'id': note_id})
        self.db.commit()
        return res.rowcount > 0

    # Highlights
    def list_highlights(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        where: List[str] = []
        params: Dict[str, Any] = {}
        if filters.get('source_id'):
            where.append("source_id = :source_id")
            params['source_id'] = filters['source_id']
        if filters.get('q'):
            where.append("(text LIKE :q OR location LIKE :q)")
            params['q'] = f"%{filters['q']}%"
        sql = "SELECT id, source_id, location, text, comment FROM highlight"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY id DESC"
        # Pagination
        page_size = int(filters.get('page_size') or 25)
        if page_size > 100:
            page_size = 100
        if page_size <= 0:
            page_size = 25
        page = int(filters.get('page') or 1)
        if page < 1:
            page = 1
        params['limit'] = page_size
        params['offset'] = (page - 1) * page_size
        sql += " LIMIT :limit OFFSET :offset"
        rows = self.db.execute(text(sql), params).mappings().all()
        return [dict(r) for r in rows]

    def create_highlight(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.db.execute(
            text("""
            INSERT INTO highlight(source_id, location, text, comment)
            VALUES (:source_id, :location, :text, :comment)
            """),
            {
                'source_id': data['source_id'],
                'location': data.get('location'),
                'text': data['text'],
                'comment': data.get('comment')
            }
        )
        self.db.commit()
        new_id = int(self.db.execute(text("SELECT last_insert_rowid()")).scalar())
        return self.get_highlight(new_id) or {'id': new_id}

    def get_highlight(self, highlight_id: int) -> Optional[Dict[str, Any]]:
        row = self.db.execute(
            text("SELECT id, source_id, location, text, comment FROM highlight WHERE id = :id"),
            {'id': highlight_id}
        ).mappings().first()
        return dict(row) if row else None

    def update_highlight(self, highlight_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        current = self.get_highlight(highlight_id)
        if not current:
            return None
        fields = ['source_id','location','text','comment']
        sets, params = [], {'id': highlight_id}
        for f in fields:
            if f in data:
                sets.append(f"{f} = :{f}")
                params[f] = data[f]
        if not sets:
            return current
        self.db.execute(text(f"UPDATE highlight SET {', '.join(sets)} WHERE id = :id"), params)
        self.db.commit()
        return self.get_highlight(highlight_id)

    def delete_highlight(self, highlight_id: int) -> bool:
        res = self.db.execute(text("DELETE FROM highlight WHERE id = :id"), {'id': highlight_id})
        self.db.commit()
        return res.rowcount > 0

    # Questions & Evidence
    def list_questions(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        where, params = [], {}
        if filters.get('status'):
            where.append("status = :status")
            params['status'] = filters['status']
        sql = "SELECT id, text, area, status, created_at FROM question"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY created_at DESC, id DESC"
        rows = self.db.execute(text(sql), params).mappings().all()
        return [dict(r) for r in rows]

    def create_question(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.db.execute(
            text("INSERT INTO question(text, area, status) VALUES (:text, :area, :status)"),
            {'text': data['text'], 'area': data.get('area'), 'status': data.get('status')}
        )
        self.db.commit()
        new_id = int(self.db.execute(text("SELECT last_insert_rowid()")).scalar())
        return self.get_question(new_id) or {'id': new_id}

    def get_question(self, qid: int) -> Optional[Dict[str, Any]]:
        row = self.db.execute(text("SELECT id, text, area, status, created_at FROM question WHERE id = :id"), {'id': qid}).mappings().first()
        return dict(row) if row else None

    def update_question(self, qid: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        current = self.get_question(qid)
        if not current:
            return None
        fields = ['text','area','status']
        sets, params = [], {'id': qid}
        for f in fields:
            if f in data:
                sets.append(f"{f} = :{f}")
                params[f] = data[f]
        if not sets:
            return current
        self.db.execute(text(f"UPDATE question SET {', '.join(sets)} WHERE id = :id"), params)
        self.db.commit()
        return self.get_question(qid)

    def delete_question(self, qid: int) -> bool:
        res = self.db.execute(text("DELETE FROM question WHERE id = :id"), {'id': qid})
        self.db.commit()
        return res.rowcount > 0

    def list_evidence(self, qid: int) -> List[Dict[str, Any]]:
        rows = self.db.execute(text(
            """
            SELECT e.id, e.question_id, e.source_id, e.stance, e.note,
                   s.title AS source_title, s.kind AS source_kind, s.year AS source_year
            FROM evidence_link e JOIN source s ON s.id = e.source_id
            WHERE e.question_id = :id
            ORDER BY e.id DESC
            """
        ), {'id': qid}).mappings().all()
        return [dict(r) for r in rows]

    def add_evidence(self, qid: int, data: Dict[str, Any]) -> Dict[str, Any]:
        self.db.execute(text(
            "INSERT INTO evidence_link(question_id, source_id, stance, note) VALUES (:qid, :sid, :stance, :note)"
        ), {'qid': qid, 'sid': data['source_id'], 'stance': data.get('stance', 'neutral'), 'note': data.get('note')})
        self.db.commit()
        new_id = int(self.db.execute(text("SELECT last_insert_rowid()")).scalar())
        row = self.db.execute(text("SELECT id, question_id, source_id, stance, note FROM evidence_link WHERE id = :id"), {'id': new_id}).mappings().first()
        return dict(row) if row else {'id': new_id}

    def delete_evidence(self, evidence_id: int) -> bool:
        res = self.db.execute(text("DELETE FROM evidence_link WHERE id = :id"), {'id': evidence_id})
        self.db.commit()
        return res.rowcount > 0
    
    def list_evidence_by_source(self, source_id: int) -> List[Dict[str, Any]]:
        rows = self.db.execute(text(
            """
            SELECT e.id, e.question_id, e.source_id, e.stance, e.note,
                   q.text AS question_text, q.status AS question_status, q.area AS question_area
            FROM evidence_link e JOIN question q ON q.id = e.question_id
            WHERE e.source_id = :sid
            ORDER BY e.id DESC
            """
        ), {'sid': source_id}).mappings().all()
        return [dict(r) for r in rows]
    # Sources (minimal v0, using direct SQL to match manual migrations)
    def list_sources(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        where = []
        params = {}
        if filters.get('q'):
            where.append("(title LIKE :q OR author LIKE :q OR venue LIKE :q OR abstract LIKE :q)")
            params['q'] = f"%{filters['q']}%"
        if filters.get('kind'):
            where.append("kind = :kind")
            params['kind'] = filters['kind']
        if filters.get('year'):
            where.append("year = :year")
            params['year'] = filters['year']
        if filters.get('tag'):
            where.append("EXISTS (SELECT 1 FROM tag_map tm JOIN tag t ON t.id = tm.tag_id WHERE tm.entity_type = 'source' AND tm.entity_id = source.id AND t.name = :tag)")
            params['tag'] = filters['tag']
        sql = "SELECT id, kind, title, author, year, url, doi, arxiv_id, venue, publisher, abstract, citation, added_ts FROM source"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY added_ts DESC, id DESC"
        # Pagination
        page_size = int(filters.get('page_size') or 25)
        if page_size > 100:
            page_size = 100
        if page_size <= 0:
            page_size = 25
        page = int(filters.get('page') or 1)
        if page < 1:
            page = 1
        params['limit'] = page_size
        params['offset'] = (page - 1) * page_size
        sql += " LIMIT :limit OFFSET :offset"
        rows = self.db.execute(text(sql), params).mappings().all()
        return [dict(r) for r in rows]

    def create_source(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Dedup by doi → arxiv_id → url
        for key in ('doi', 'arxiv_id', 'url'):
            val = (data.get(key) or '').strip()
            if val:
                row = self.db.execute(text(f"SELECT id FROM source WHERE {key} = :v"), {'v': val}).first()
                if row:
                    # Update existing minimal fields
                    return self.update_source(int(row[0]), data) or {'id': int(row[0])}
        self.db.execute(
            text("""
            INSERT INTO source(kind, title, author, year, url, doi, arxiv_id, venue, publisher, abstract, citation)
            VALUES (:kind, :title, :author, :year, :url, :doi, :arxiv_id, :venue, :publisher, :abstract, :citation)
            """),
            {
                'kind': data.get('kind'),
                'title': data['title'],
                'author': data.get('author'),
                'year': data.get('year'),
                'url': data.get('url'),
                'doi': data.get('doi'),
                'arxiv_id': data.get('arxiv_id'),
                'venue': data.get('venue'),
                'publisher': data.get('publisher'),
                'abstract': data.get('abstract'),
                'citation': data.get('citation')
            }
        )
        self.db.commit()
        new_id = int(self.db.execute(text("SELECT last_insert_rowid()"))
                     .scalar())
        return self.get_source(new_id) or {'id': new_id}

    def get_source(self, source_id: int) -> Optional[Dict[str, Any]]:
        row = self.db.execute(
            text("SELECT id, kind, title, author, year, url, doi, arxiv_id, venue, publisher, abstract, citation, added_ts FROM source WHERE id = :id"),
            {'id': source_id}
        ).mappings().first()
        return dict(row) if row else None

    def update_source(self, source_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        current = self.get_source(source_id)
        if not current:
            return None
        fields = ['kind','title','author','year','url','doi','arxiv_id','venue','publisher','abstract','citation']
        sets = []
        params = {'id': source_id}
        for f in fields:
            if f in data and data[f] is not None:
                sets.append(f"{f} = :{f}")
                params[f] = data[f]
        if not sets:
            return current
        sql = f"UPDATE source SET {', '.join(sets)} WHERE id = :id"
        self.db.execute(text(sql), params)
        self.db.commit()
        return self.get_source(source_id)

    def delete_source(self, source_id: int) -> bool:
        res = self.db.execute(text("DELETE FROM source WHERE id = :id"), {'id': source_id})
        self.db.commit()
        return res.rowcount > 0

    # CSV Imports
    def import_events_from_csv(self, file_path: Optional[str] = None, dry_run: bool = False, extra_tags: Optional[List[str]] = None) -> Dict[str, Any]:
        default_path = os.path.join('data', 'research - events.csv')
        path = file_path or default_path
        if not os.path.exists(path):
            raise FileNotFoundError(f"CSV not found: {path}")

        created = 0
        updated = 0
        total = 0
        try:
            with open(path, newline='', encoding='utf-8-sig') as csvfile:
                head = csvfile.read(4096)
                csvfile.seek(0)
                delimiter = '\t' if head.count('\t') > head.count(',') else ','
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                for row in reader:
                    total += 1
                    norm = {self._norm(k): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
                    tags = self._split_tags(norm.get('tags'))
                    if extra_tags:
                        tags.extend([t for t in extra_tags if t])
                    # Skip empty rows
                    if not (norm.get('headline') or norm.get('title') or norm.get('url')):
                        continue
                    # Upsert key preference: url → (date, headline)
                    existing = None
                    if norm.get('url'):
                        existing = self.db.execute(text("SELECT id FROM news_event WHERE url = :url"), {'url': norm['url']}).first()
                    if not existing and norm.get('date') and norm.get('headline'):
                        existing = self.db.execute(text("SELECT id FROM news_event WHERE date_ts = :d AND headline = :h"), {'d': norm['date'], 'h': norm['headline']}).first()

                    if not existing:
                        self.db.execute(text(
                            """
                            INSERT INTO news_event(date_ts, headline, outlet, summary, url)
                            VALUES (:date_ts, :headline, :outlet, :summary, :url)
                            """
                        ), {
                            'date_ts': self._parse_date_to_iso(norm.get('date') or norm.get('date_ts')) or (norm.get('date') or norm.get('date_ts')),
                            'headline': norm.get('headline') or norm.get('title'),
                            'outlet': norm.get('outlet') or norm.get('source'),
                            'summary': norm.get('summary') or norm.get('notes'),
                            'url': norm.get('url')
                        })
                        ev_id = int(self.db.execute(text("SELECT last_insert_rowid()" )).scalar())
                        if tags:
                            self._apply_tags('news_event', ev_id, tags)
                        created += 1
                    else:
                        ev_id = int(existing[0])
                        # Minimal update: summary/outlet/date
                        upd = []
                        params = {'id': ev_id}
                        for f_map in [('date_ts','date'), ('headline','headline'), ('outlet','outlet'), ('summary','summary'), ('url','url')]:
                            col, src = f_map
                            val = norm.get(src) or norm.get(col)
                            if col == 'date_ts' and val:
                                val = self._parse_date_to_iso(val) or val
                            if val:
                                upd.append(f"{col} = :{col}")
                                params[col] = val
                        if upd:
                            self.db.execute(text(f"UPDATE news_event SET {', '.join(upd)} WHERE id = :id"), params)
                        if tags:
                            self._apply_tags('news_event', ev_id, tags)
                        updated += 1
        finally:
            if dry_run:
                self.db.rollback()
            else:
                self.db.commit()
        return {'created': created, 'updated': updated, 'total': total, 'dry_run': bool(dry_run)}

    def import_sources_from_csv(self, file_path: Optional[str] = None, dry_run: bool = False, extra_tags: Optional[List[str]] = None) -> Dict[str, Any]:
        default_path = os.path.join('data', 'research - sources.csv')
        path = file_path or default_path
        if not os.path.exists(path):
            raise FileNotFoundError(f"CSV not found: {path}")

        created = 0
        updated = 0
        total = 0
        try:
            with open(path, newline='', encoding='utf-8-sig') as csvfile:
                head = csvfile.read(4096)
                csvfile.seek(0)
                delimiter = '\t' if head.count('\t') > head.count(',') else ','
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                for row in reader:
                    total += 1
                    n = {self._norm(k): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
                    # Friendly header mapping
                    if 'kind' not in n and 'type' in n:
                        n['kind'] = n.get('type')
                    if 'year' not in n and 'date' in n:
                        n['year'] = self._parse_year(n.get('date'))
                    if 'abstract' not in n and 'notes' in n:
                        n['abstract'] = n.get('notes')
                    if 'url' not in n and 'link' in n:
                        n['url'] = n.get('link')
                    if 'citation' not in n and 'biblo' in n:
                        n['citation'] = n.get('biblo')
                    tags = self._split_tags(n.get('tags'))
                    if extra_tags:
                        tags.extend([t for t in extra_tags if t])
                    # Skip empty rows that lack identifiers and title
                    if not (n.get('title') or n.get('url') or n.get('doi') or n.get('arxiv_id')):
                        continue
                    # Dedup: doi → arxiv_id → url
                    existing = None
                    for key in ('doi','arxiv_id','url'):
                        val = n.get(key)
                        if val:
                            existing = self.db.execute(text(f"SELECT id FROM source WHERE {key} = :v"), {'v': val}).first()
                            if existing:
                                break
                    if not existing:
                        self.db.execute(text(
                            """
                            INSERT INTO source(kind, title, author, year, url, doi, arxiv_id, venue, publisher, abstract, citation)
                            VALUES (:kind, :title, :author, :year, :url, :doi, :arxiv_id, :venue, :publisher, :abstract, :citation)
                            """
                        ), {
                            'kind': n.get('kind'), 'title': n.get('title'), 'author': n.get('author'),
                            'year': n.get('year'), 'url': n.get('url'), 'doi': n.get('doi'), 'arxiv_id': n.get('arxiv_id'),
                            'venue': n.get('venue'), 'publisher': n.get('publisher'), 'abstract': n.get('abstract'), 'citation': n.get('citation')
                        })
                        sid = int(self.db.execute(text("SELECT last_insert_rowid()" )).scalar())
                        if tags:
                            self._apply_tags('source', sid, tags)
                        created += 1
                    else:
                        sid = int(existing[0])
                        upd = []
                        params = {'id': sid}
                        for col in ('kind','title','author','year','url','doi','arxiv_id','venue','publisher','abstract','citation'):
                            val = n.get(col)
                            if val:
                                upd.append(f"{col} = :{col}")
                                params[col] = val
                        if upd:
                            self.db.execute(text(f"UPDATE source SET {', '.join(upd)} WHERE id = :id"), params)
                        if tags:
                            self._apply_tags('source', sid, tags)
                        updated += 1
        finally:
            if dry_run:
                self.db.rollback()
            else:
                self.db.commit()
        return {'created': created, 'updated': updated, 'total': total, 'dry_run': bool(dry_run)}

    # External links
    def list_external_links(self, entity_type: str, entity_id: int) -> List[Dict[str, Any]]:
        rows = self.db.execute(text(
            "SELECT id, provider, kind, title, url, external_id, note, added_ts FROM external_link WHERE entity_type = :et AND entity_id = :eid ORDER BY id DESC"
        ), {'et': entity_type, 'eid': entity_id}).mappings().all()
        return [dict(r) for r in rows]

    def add_external_link(self, entity_type: str, entity_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        self.db.execute(text(
            """
            INSERT INTO external_link(entity_type, entity_id, provider, kind, title, url, external_id, note)
            VALUES (:et, :eid, :provider, :kind, :title, :url, :external_id, :note)
            """
        ), {
            'et': entity_type,
            'eid': entity_id,
            'provider': data.get('provider') or 'web',
            'kind': data.get('kind'),
            'title': data.get('title'),
            'url': data.get('url'),
            'external_id': data.get('external_id'),
            'note': data.get('note')
        })
        self.db.commit()
        new_id = int(self.db.execute(text("SELECT last_insert_rowid()" )).scalar())
        row = self.db.execute(text("SELECT id, provider, kind, title, url, external_id, note, added_ts FROM external_link WHERE id = :id"), {'id': new_id}).mappings().first()
        return dict(row) if row else {'id': new_id}

    def delete_external_link(self, link_id: int) -> bool:
        res = self.db.execute(text("DELETE FROM external_link WHERE id = :id"), {'id': link_id})
        self.db.commit()
        return res.rowcount > 0

    # Helpers (CSV/Tags)
    @staticmethod
    def _norm(s: Optional[str]) -> str:
        if s is None:
            return ''
        return s.strip().lower().replace(' ', '_')

    @staticmethod
    def _split_tags(s: Optional[str]) -> List[str]:
        if not s:
            return []
        raw = str(s).replace(';', ',')
        tags = [t.strip() for t in raw.split(',') if t and t.strip()]
        # Deduplicate while preserving order
        seen = set()
        out = []
        for t in tags:
            if t.lower() not in seen:
                seen.add(t.lower())
                out.append(t)
        return out

    @staticmethod
    def _parse_year(value: Optional[str]) -> Optional[int]:
        if not value:
            return None
        s = str(value).strip()
        # Try direct year
        try:
            y = int(s)
            if 1000 <= y <= 3000:
                return y
        except Exception:
            pass
        # Extract first 4-digit year-like token
        for tok in s.replace('-', ' ').replace('/', ' ').replace('.', ' ').split():
            try:
                y = int(tok)
                if 1000 <= y <= 3000:
                    return y
            except Exception:
                continue
        return None

    @staticmethod
    def _parse_date_to_iso(value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        s = str(value).strip()
        try:
            dt = date_parser.parse(s, dayfirst=False, yearfirst=False)
            # Normalize to ISO date only if time not provided
            return dt.strftime('%Y-%m-%d')
        except Exception:
            return None

    def _apply_tags(self, entity_type: str, entity_id: int, tag_names: List[str]) -> None:
        for name in tag_names:
            tag_id = self._ensure_tag(name)
            try:
                self.db.execute(text(
                    "INSERT OR IGNORE INTO tag_map(entity_type, entity_id, tag_id) VALUES (:et, :eid, :tid)"
                ), {'et': entity_type, 'eid': entity_id, 'tid': tag_id})
            except Exception:
                pass

    def _ensure_tag(self, name: str) -> int:
        # Lookup
        row = self.db.execute(text("SELECT id FROM tag WHERE name = :n"), {'n': name}).first()
        if row:
            return int(row[0])
        # Create
        self.db.execute(text("INSERT INTO tag(name) VALUES (:n)"), {'n': name})
        return int(self.db.execute(text("SELECT last_insert_rowid()" )).scalar())

    # Tagging APIs
    def list_tags(self) -> List[Dict[str, Any]]:
        rows = self.db.execute(text(
            """
            SELECT DISTINCT t.id, t.name
            FROM tag t
            WHERE EXISTS (
              SELECT 1 FROM tag_map tm
              WHERE tm.tag_id = t.id AND tm.entity_type IN ('source','news_event')
            )
            ORDER BY t.name COLLATE NOCASE
            """
        )).mappings().all()
        return [dict(r) for r in rows]

    def list_entity_tags(self, entity_type: str, entity_id: int) -> List[Dict[str, Any]]:
        rows = self.db.execute(text(
            "SELECT tm.tag_id AS id, t.name FROM tag_map tm JOIN tag t ON t.id = tm.tag_id WHERE tm.entity_type = :et AND tm.entity_id = :eid ORDER BY t.name COLLATE NOCASE"
        ), {'et': entity_type, 'eid': entity_id}).mappings().all()
        return [dict(r) for r in rows]

    def add_tag(self, entity_type: str, entity_id: int, tag_name: str) -> Dict[str, Any]:
        tag_id = self._ensure_tag(tag_name)
        self.db.execute(text(
            "INSERT OR IGNORE INTO tag_map(entity_type, entity_id, tag_id) VALUES (:et, :eid, :tid)"
        ), {'et': entity_type, 'eid': entity_id, 'tid': tag_id})
        self.db.commit()
        return {'id': tag_id, 'name': tag_name}

    def remove_tag(self, entity_type: str, entity_id: int, tag_id: int) -> bool:
        res = self.db.execute(text(
            "DELETE FROM tag_map WHERE entity_type = :et AND entity_id = :eid AND tag_id = :tid"
        ), {'et': entity_type, 'eid': entity_id, 'tid': tag_id})
        self.db.commit()
        return res.rowcount > 0


