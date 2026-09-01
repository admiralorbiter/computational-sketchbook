import { fetchJSON, updateEntityLocation } from "../api.js";
import {
  setSelectedEntity,
  startLinkFromEntity,
  clearLink,
  setLinkMode,
  disableLocationPick,
  getSelection,
  subscribeSelection,
} from "../state/selection.js";
import { renderMarkers, renderRelationships, attachMarkerHandlers } from "./layers.js";
import { initControls } from "./controls.js";
import { openRelationshipEditorForNew } from "../entities.js";

let map;
let currentEntities = [];
let currentRelationships = [];

async function loadData() {
  currentEntities = await fetchJSON("/api/entities");
  currentRelationships = await fetchJSON("/api/relationships");
}

function render() {
  if (!map) return;
  renderMarkers(map, currentEntities);
  renderRelationships(map, currentEntities, currentRelationships);
  attachMarkerHandlers(map, handleMarkerClick);
}

function handleMarkerClick(entityId) {
  const sel = getSelection();
  if (sel.linkMode) {
    if (!sel.linkSourceId) {
      startLinkFromEntity(entityId);
      setSelectedEntity(entityId);
    } else if (sel.linkSourceId && sel.linkSourceId !== entityId) {
      // Have source and target; open editor
      openRelationshipEditorForNew(sel.linkSourceId, entityId);
      clearLink();
      setLinkMode(false);
    }
  } else {
    setSelectedEntity(entityId);
  }
}

export async function setupMap() {
  const container = document.getElementById("map-canvas");
  if (!container || !window.L) {
    return;
  }

  map = window.L.map(container, {
    center: [39.0997, -94.5786],
    zoom: 11,
    zoomControl: true,
  });

  window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  initControls(map);

  await loadData();
  render();

  // Re-render when selection changes (for highlighting)
  subscribeSelection(() => {
    render();
  });

  // Location pick handler
  map.on("click", async (evt) => {
    const sel = getSelection();
    if (!sel.locationPickMode || !sel.selectedEntityId) {
      return;
    }
    try {
      await updateEntityLocation(sel.selectedEntityId, {
        lat: evt.latlng.lat,
        lng: evt.latlng.lng,
      });
      disableLocationPick();
      await loadData();
      render();
    } catch (err) {
      console.error(err);
      disableLocationPick();
    }
  });

  const relButton = document.getElementById("new-rel-btn");
  if (relButton) {
    relButton.addEventListener("click", () => {
      const sel = getSelection();
      const next = !sel.linkMode;
      setLinkMode(next);
      if (!next) {
        clearLink();
      }
      relButton.classList.toggle("bg-sky-600", next);
      relButton.classList.toggle("border-sky-500", next);
    });
  }
}

export async function refreshMapData() {
  if (!map) return;
  await loadData();
  render();
}


