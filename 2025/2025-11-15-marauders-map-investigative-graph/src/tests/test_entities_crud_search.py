from app import create_app


def make_client():
  app = create_app()
  app.config.update({"TESTING": True})
  return app.test_client()


def test_create_search_delete_entity():
  client = make_client()

  # create
  resp = client.post("/api/entities", json={"name": "Acme Corp", "entity_type": "organization"})
  assert resp.status_code == 201
  created = resp.get_json()["data"]
  entity_id = created["id"]

  # search by name
  resp = client.get("/api/entities/search", query_string={"q": "Acme"})
  assert resp.status_code == 200
  results = resp.get_json()["data"]
  assert any(e["id"] == entity_id for e in results)

  # update name
  resp = client.patch(f"/api/entities/{entity_id}", json={"name": "Acme Corp Intl"})
  assert resp.status_code == 200

  # search again with new name
  resp = client.get("/api/entities/search", query_string={"q": "Intl"})
  assert resp.status_code == 200
  results = resp.get_json()["data"]
  assert any(e["id"] == entity_id for e in results)

  # delete
  resp = client.delete(f"/api/entities/{entity_id}")
  assert resp.status_code == 200

  # ensure deleted from list and search
  resp = client.get("/api/entities")
  assert entity_id not in [e["id"] for e in resp.get_json()["data"]]

  resp = client.get("/api/entities/search", query_string={"q": "Acme"})
  assert entity_id not in [e["id"] for e in resp.get_json()["data"]]


