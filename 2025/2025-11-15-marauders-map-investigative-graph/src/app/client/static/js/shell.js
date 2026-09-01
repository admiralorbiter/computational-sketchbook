import { getHealth, searchEntities } from "./api.js";
import { loadEntities, renderEntities } from "./entities.js";

let searchTimer = null;

async function refreshHealth() {
  const el = document.getElementById("health-status");
  if (!el) return;
  try {
    const data = await getHealth();
    el.textContent = `status=${data.status}, db=${data.database}`;
    el.classList.remove("text-red-400");
    el.classList.add("text-emerald-400");
  } catch (err) {
    el.textContent = "health check failed";
    el.classList.remove("text-emerald-400");
    el.classList.add("text-red-400");
  }
}

function setupRefreshButton() {
  const btn = document.getElementById("refresh-btn");
  if (!btn) return;
  btn.addEventListener("click", loadEntities);
}

function setupSearchBox() {
  const input = document.getElementById("entity-search");
  if (!input) return;

  input.addEventListener("input", () => {
    if (searchTimer) {
      window.clearTimeout(searchTimer);
    }
    searchTimer = window.setTimeout(async () => {
      const query = input.value || "";
      try {
        const results = await searchEntities(query);
        renderEntities(results);
      } catch (err) {
        console.error(err);
      }
    }, 200);
  });
}

export async function setupShell() {
  setupRefreshButton();
  setupSearchBox();
  await refreshHealth();
  await loadEntities();
}


