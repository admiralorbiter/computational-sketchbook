let selectedEntityId = null;
let hoverEntityId = null;
let selectedRelationshipId = null;
let linkSourceId = null;
let linkMode = false;
let locationPickMode = false;

const listeners = new Set();

function notify() {
  const snapshot = getSelection();
  listeners.forEach((fn) => {
    try {
      fn(snapshot);
    } catch (err) {
      console.error("selection listener error", err);
    }
  });
}

export function getSelection() {
  return {
    selectedEntityId,
    hoverEntityId,
    selectedRelationshipId,
    linkSourceId,
    linkMode,
    locationPickMode,
  };
}

export function setSelectedEntity(id) {
  selectedEntityId = id;
  notify();
}

export function setHoverEntity(id) {
  hoverEntityId = id;
  notify();
}

export function setSelectedRelationship(id) {
  selectedRelationshipId = id;
  notify();
}

export function startLinkFromEntity(id) {
  linkSourceId = id;
  notify();
}

export function clearLink() {
  linkSourceId = null;
  notify();
}

export function setLinkMode(active) {
  linkMode = !!active;
  if (!linkMode) {
    linkSourceId = null;
  }
  notify();
}

export function enableLocationPick() {
  locationPickMode = true;
  notify();
}

export function disableLocationPick() {
  locationPickMode = false;
  notify();
}

export function subscribeSelection(listener) {
  listeners.add(listener);
  listener(getSelection());
  return () => listeners.delete(listener);
}


