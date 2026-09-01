export async function fetchJSON(url, options) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!data.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data.data;
}

export async function getHealth() {
  return fetchJSON("/api/health");
}

export async function listEntities() {
  return fetchJSON("/api/entities");
}

export async function createEntity(payload) {
  return fetchJSON("/api/entities", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateEntity(id, payload) {
  return fetchJSON(`/api/entities/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteEntity(id) {
  return fetchJSON(`/api/entities/${id}`, {
    method: "DELETE",
  });
}

export async function updateEntityLocation(id, payload) {
  return fetchJSON(`/api/entities/${id}/location`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function searchEntities(query) {
  const q = query.trim();
  const url = q ? `/api/entities/search?q=${encodeURIComponent(q)}` : "/api/entities";
  return fetchJSON(url);
}

export async function listRelationshipsForEntity(entityId) {
  return fetchJSON(`/api/relationships?entity_id=${encodeURIComponent(entityId)}`);
}

export async function createRelationship(payload) {
  return fetchJSON("/api/relationships", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateRelationship(id, payload) {
  return fetchJSON(`/api/relationships/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteRelationship(id) {
  return fetchJSON(`/api/relationships/${id}`, {
    method: "DELETE",
  });
}



