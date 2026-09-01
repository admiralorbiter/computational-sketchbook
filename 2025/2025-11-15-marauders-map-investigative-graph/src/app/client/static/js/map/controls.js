const KC_CENTER = [39.0997, -94.5786];
const KC_ZOOM = 11;

export function centerOnKC(map) {
  map.setView(KC_CENTER, KC_ZOOM);
}

export function initControls(map) {
  const btn = document.getElementById("kc-center-btn");
  if (!btn) return;
  btn.addEventListener("click", () => centerOnKC(map));
}


