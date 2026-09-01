from app import create_app


def make_client():
    app = create_app()
    app.config.update({"TESTING": True})
    return app.test_client()


def test_relationships_crud_and_location():
    client = make_client()

    # Create two entities
    e1 = client.post(
        "/api/entities", json={"name": "Alice", "entity_type": "person"}
    ).get_json()["data"]
    e2 = client.post(
        "/api/entities", json={"name": "KC Org", "entity_type": "organization"}
    ).get_json()["data"]

    # Set location on second entity
    resp = client.patch(
        f"/api/entities/{e2['id']}/location",
        json={"lat": 39.0997, "lng": -94.5786, "location_label": "Kansas City"},
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["lat"] == 39.0997
    assert data["lng"] == -94.5786

    # Create relationship
    resp = client.post(
        "/api/relationships",
        json={
            "source_id": e1["id"],
            "target_id": e2["id"],
            "relationship_type": "member_of",
            "role": "Board Member",
            "strength": 4,
            "confidence": 3,
        },
    )
    assert resp.status_code == 201
    rel = resp.get_json()["data"]
    rel_id = rel["id"]

    # List relationships for each entity
    resp = client.get("/api/relationships", query_string={"entity_id": e1["id"]})
    assert any(r["id"] == rel_id for r in resp.get_json()["data"])

    resp = client.get("/api/relationships", query_string={"entity_id": e2["id"]})
    assert any(r["id"] == rel_id for r in resp.get_json()["data"])

    # Update relationship
    resp = client.patch(
        f"/api/relationships/{rel_id}",
        json={"role": "Chair", "is_current": False},
    )
    assert resp.status_code == 200
    updated = resp.get_json()["data"]
    assert updated["role"] == "Chair"
    assert updated["is_current"] is False

    # Delete relationship
    resp = client.delete(f"/api/relationships/{rel_id}")
    assert resp.status_code == 200

    resp = client.get("/api/relationships", query_string={"entity_id": e1["id"]})
    assert rel_id not in [r["id"] for r in resp.get_json()["data"]]


