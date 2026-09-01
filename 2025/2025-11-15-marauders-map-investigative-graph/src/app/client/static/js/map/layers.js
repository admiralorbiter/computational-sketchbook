import { getSelection, setSelectedRelationship } from "../state/selection.js";

const markersById = new Map();
const linesById = new Map();

export function renderMarkers(map, entities) {
  const seen = new Set();

  for (const e of entities) {
    if (e.lat == null || e.lng == null) continue;
    const id = String(e.id);
    seen.add(id);

    let marker = markersById.get(id);
    if (!marker) {
      marker = window.L.marker([e.lat, e.lng]);
      marker.addTo(map);
      markersById.set(id, marker);
    } else {
      marker.setLatLng([e.lat, e.lng]);
    }

    const label = e.location_label || e.name;
    marker.bindTooltip(label, { permanent: false });
    marker.entityId = e.id;
  }

  // remove stale markers
  for (const [id, marker] of markersById.entries()) {
    if (!seen.has(id)) {
      map.removeLayer(marker);
      markersById.delete(id);
    }
  }
}

export function renderRelationships(map, entities, relationships) {
  const entityById = new Map(entities.map((e) => [String(e.id), e]));
  const seen = new Set();

  for (const r of relationships) {
    const id = String(r.id);
    const a = entityById.get(String(r.source_id));
    const b = entityById.get(String(r.target_id));
    if (!a || !b || a.lat == null || a.lng == null || b.lat == null || b.lng == null) {
      continue;
    }
    seen.add(id);

    let line = linesById.get(id);
    const latlngs = [
      [a.lat, a.lng],
      [b.lat, b.lng],
    ];

    const isCurrent = r.is_current;
    const color = "#38bdf8"; // sky-400
    const weight = r.strength ? 2 + r.strength * 0.3 : 2;
    const dashArray = isCurrent ? null : "4 6";

    if (!line) {
      line = window.L.polyline(latlngs, {
        color,
        weight,
        dashArray,
      });
      line.addTo(map);
      linesById.set(id, line);
    } else {
      line.setLatLngs(latlngs);
      line.setStyle({ color, weight, dashArray });
    }

    const dateRange =
      (r.start_date || "") + (r.end_date ? "–" + r.end_date : "");
    const tooltip = `${r.relationship_type}${
      r.role ? " — " + r.role : ""
    }\n${dateRange}\nS:${r.strength ?? "-"} C:${r.confidence ?? "-"}`;

    line.off("click");
    line.on("click", () => {
      setSelectedRelationship(r.id);
    });
    line.bindTooltip(tooltip);

    line.relationshipId = r.id;
  }

  // remove stale lines
  for (const [id, line] of linesById.entries()) {
    if (!seen.has(id)) {
      map.removeLayer(line);
      linesById.delete(id);
    }
  }

  // update selection styling
  const { selectedRelationshipId } = getSelection();
  for (const [id, line] of linesById.entries()) {
    const isSelected =
      selectedRelationshipId && String(selectedRelationshipId) === String(id);
    line.setStyle({
      weight: isSelected ? 5 : line.options.weight,
    });
  }
}

export function attachMarkerHandlers(map, onMarkerClick) {
  for (const marker of markersById.values()) {
    marker.off("click");
    marker.on("click", () => {
      onMarkerClick(marker.entityId);
    });
  }
}


