from __future__ import annotations

from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, request

from .db import get_db


def _response(ok: bool, data: Any = None, error: str | None = None, status: int = 200):
    payload: Dict[str, Any] = {"ok": ok}
    if ok:
        payload["data"] = data
    else:
        payload["error"] = error or "Unknown error"
    return jsonify(payload), status


def register_routes(app: Flask) -> None:
    @app.get("/api/health")
    def health() -> Any:
        db = get_db()
        db.execute("SELECT 1;")
        return _response(
            True,
            {
                "status": "ok",
                "database": "ok",
            },
        )

    @app.get("/api/entities")
    def list_entities() -> Any:
        db = get_db()
        rows = db.execute(
            """
            SELECT id, name, entity_type, created_at, lat, lng, location_label
            FROM entities
            WHERE is_deleted = 0
            ORDER BY created_at DESC;
            """
        ).fetchall()
        entities: List[Dict[str, Any]] = [
            {
                "id": row["id"],
                "name": row["name"],
                "entity_type": row["entity_type"],
                "created_at": row["created_at"],
                "lat": row["lat"],
                "lng": row["lng"],
                "location_label": row["location_label"],
            }
            for row in rows
        ]
        return _response(True, entities)

    @app.post("/api/entities")
    def create_entity() -> Any:
        payload = request.get_json(silent=True) or {}
        name = (payload.get("name") or "").strip()
        entity_type = (payload.get("entity_type") or "").strip() or "person"

        if not name:
            return _response(False, error="name is required", status=400)

        db = get_db()
        cur = db.execute(
            """
            INSERT INTO entities (name, entity_type)
            VALUES (?, ?);
            """,
            (name, entity_type),
        )
        db.commit()

        new_id = cur.lastrowid
        row = db.execute(
            """
            SELECT id, name, entity_type, created_at
            FROM entities
            WHERE id = ?;
            """,
            (new_id,),
        ).fetchone()

        entity = (
            dict(row)
            if row is not None
            else {"id": new_id, "name": name, "entity_type": entity_type}
        )
        return _response(True, entity, status=201)

    @app.patch("/api/entities/<int:entity_id>")
    def update_entity(entity_id: int) -> Any:
        payload = request.get_json(silent=True) or {}
        name = payload.get("name")
        entity_type = payload.get("entity_type")

        if name is not None and not str(name).strip():
            return _response(False, error="name cannot be empty", status=400)

        fields = []
        values: List[Any] = []
        if name is not None:
            fields.append("name = ?")
            values.append(str(name).strip())
        if entity_type is not None:
            fields.append("entity_type = ?")
            values.append(str(entity_type).strip())
        if not fields:
            return _response(False, error="no fields to update", status=400)

        fields.append("updated_at = datetime('now')")

        db = get_db()
        values.append(entity_id)
        cur = db.execute(
            f"""
            UPDATE entities
            SET {", ".join(fields)}
            WHERE id = ? AND is_deleted = 0;
            """,
            tuple(values),
        )
        if cur.rowcount == 0:
            return _response(False, error="entity not found", status=404)

        db.commit()
        row = db.execute(
            """
            SELECT id, name, entity_type, created_at
            FROM entities
            WHERE id = ? AND is_deleted = 0;
            """,
            (entity_id,),
        ).fetchone()
        entity = dict(row) if row is not None else None
        return _response(True, entity)

    @app.delete("/api/entities/<int:entity_id>")
    def delete_entity(entity_id: int) -> Any:
        db = get_db()
        cur = db.execute(
            """
            UPDATE entities
            SET is_deleted = 1, updated_at = datetime('now')
            WHERE id = ? AND is_deleted = 0;
            """,
            (entity_id,),
        )
        if cur.rowcount == 0:
            return _response(False, error="entity not found", status=404)
        db.commit()
        return _response(True, {"id": entity_id})

    @app.patch("/api/entities/<int:entity_id>/location")
    def update_entity_location(entity_id: int) -> Any:
        payload = request.get_json(silent=True) or {}
        lat = payload.get("lat")
        lng = payload.get("lng")
        label = payload.get("location_label")

        fields: List[str] = []
        values: List[Any] = []

        if lat is not None and lng is not None:
            fields.append("lat = ?")
            fields.append("lng = ?")
            values.extend([float(lat), float(lng)])
        elif lat is not None or lng is not None:
            return _response(False, error="both lat and lng are required", status=400)

        if label is not None:
            fields.append("location_label = ?")
            values.append(str(label))

        if not fields:
            return _response(False, error="no location fields to update", status=400)

        fields.append("updated_at = datetime('now')")

        db = get_db()
        values.append(entity_id)
        cur = db.execute(
            f"""
            UPDATE entities
            SET {", ".join(fields)}
            WHERE id = ? AND is_deleted = 0;
            """,
            tuple(values),
        )
        if cur.rowcount == 0:
            return _response(False, error="entity not found", status=404)

        db.commit()
        row = db.execute(
            """
            SELECT id, name, entity_type, created_at, lat, lng, location_label
            FROM entities
            WHERE id = ? AND is_deleted = 0;
            """,
            (entity_id,),
        ).fetchone()
        entity = dict(row) if row is not None else None
        return _response(True, entity)

    @app.get("/api/entities/search")
    def search_entities_route() -> Any:
        q = (request.args.get("q") or "").strip()
        db = get_db()
        if not q:
            rows = db.execute(
                """
                SELECT id, name, entity_type, created_at, lat, lng, location_label
                FROM entities
                WHERE is_deleted = 0
                ORDER BY created_at DESC;
                """
            ).fetchall()
        else:
            rows = db.execute(
                """
                SELECT e.id, e.name, e.entity_type, e.created_at, e.lat, e.lng, e.location_label
                FROM entities e
                JOIN entities_fts f ON f.rowid = e.id
                WHERE e.is_deleted = 0
                  AND f.entities_fts MATCH ?;
                """,
                (q,),
            ).fetchall()

        entities = [
            {
                "id": row["id"],
                "name": row["name"],
                "entity_type": row["entity_type"],
                "created_at": row["created_at"],
                "lat": row["lat"],
                "lng": row["lng"],
                "location_label": row["location_label"],
            }
            for row in rows
        ]
        return _response(True, entities)

    # Relationships

    def _serialize_relationship(row: Any) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "source_id": row["source_id"],
            "target_id": row["target_id"],
            "relationship_type": row["relationship_type"],
            "role": row["role"],
            "start_date": row["start_date"],
            "end_date": row["end_date"],
            "is_current": bool(row["is_current"]),
            "strength": row["strength"],
            "confidence": row["confidence"],
            "provenance_json": row["provenance_json"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    @app.get("/api/relationships")
    def list_relationships() -> Any:
        entity_id = request.args.get("entity_id", type=int)
        db = get_db()
        if entity_id is not None:
            rows = db.execute(
                """
                SELECT *
                FROM relationships
                WHERE is_deleted = 0
                  AND (source_id = ? OR target_id = ?)
                ORDER BY created_at DESC;
                """,
                (entity_id, entity_id),
            ).fetchall()
        else:
            rows = db.execute(
                """
                SELECT *
                FROM relationships
                WHERE is_deleted = 0
                ORDER BY created_at DESC;
                """
            ).fetchall()

        rels = [_serialize_relationship(r) for r in rows]
        return _response(True, rels)

    def _validate_relationship_payload(payload: Dict[str, Any]) -> Optional[str]:
        if not payload.get("source_id") or not payload.get("target_id"):
            return "source_id and target_id are required"
        if payload["source_id"] == payload["target_id"]:
            return "source_id and target_id must differ"
        rel_type = (payload.get("relationship_type") or "").strip()
        if not rel_type:
            return "relationship_type is required"
        return None

    @app.post("/api/relationships")
    def create_relationship() -> Any:
        payload = request.get_json(silent=True) or {}
        error = _validate_relationship_payload(payload)
        if error:
            return _response(False, error=error, status=400)

        db = get_db()
        # Basic existence check for entities
        src = db.execute(
            "SELECT id FROM entities WHERE id = ? AND is_deleted = 0;",
            (payload["source_id"],),
        ).fetchone()
        tgt = db.execute(
            "SELECT id FROM entities WHERE id = ? AND is_deleted = 0;",
            (payload["target_id"],),
        ).fetchone()
        if src is None or tgt is None:
            return _response(False, error="source or target entity not found", status=400)

        cur = db.execute(
            """
            INSERT INTO relationships (
                source_id, target_id, relationship_type, role,
                start_date, end_date, is_current, strength,
                confidence, provenance_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                payload["source_id"],
                payload["target_id"],
                (payload.get("relationship_type") or "").strip(),
                payload.get("role"),
                payload.get("start_date"),
                payload.get("end_date"),
                int(payload.get("is_current", 1)),
                payload.get("strength"),
                payload.get("confidence"),
                payload.get("provenance_json"),
            ),
        )
        db.commit()

        rel_id = cur.lastrowid
        row = db.execute(
            "SELECT * FROM relationships WHERE id = ?;",
            (rel_id,),
        ).fetchone()
        rel = _serialize_relationship(row) if row is not None else None
        return _response(True, rel, status=201)

    @app.patch("/api/relationships/<int:rel_id>")
    def update_relationship(rel_id: int) -> Any:
        payload = request.get_json(silent=True) or {}
        fields: List[str] = []
        values: List[Any] = []

        for key in [
            "relationship_type",
            "role",
            "start_date",
            "end_date",
            "strength",
            "confidence",
            "provenance_json",
        ]:
            if key in payload:
                fields.append(f"{key} = ?")
                values.append(payload[key])

        if "is_current" in payload:
            fields.append("is_current = ?")
            values.append(int(bool(payload["is_current"])))

        if not fields:
            return _response(False, error="no fields to update", status=400)

        fields.append("updated_at = datetime('now')")

        db = get_db()
        values.append(rel_id)
        cur = db.execute(
            f"""
            UPDATE relationships
            SET {", ".join(fields)}
            WHERE id = ? AND is_deleted = 0;
            """,
            tuple(values),
        )
        if cur.rowcount == 0:
            return _response(False, error="relationship not found", status=404)

        db.commit()
        row = db.execute(
            "SELECT * FROM relationships WHERE id = ?;",
            (rel_id,),
        ).fetchone()
        rel = _serialize_relationship(row) if row is not None else None
        return _response(True, rel)

    @app.delete("/api/relationships/<int:rel_id>")
    def delete_relationship(rel_id: int) -> Any:
        db = get_db()
        cur = db.execute(
            """
            UPDATE relationships
            SET is_deleted = 1, updated_at = datetime('now')
            WHERE id = ? AND is_deleted = 0;
            """,
            (rel_id,),
        )
        if cur.rowcount == 0:
            return _response(False, error="relationship not found", status=404)
        db.commit()
        return _response(True, {"id": rel_id})


