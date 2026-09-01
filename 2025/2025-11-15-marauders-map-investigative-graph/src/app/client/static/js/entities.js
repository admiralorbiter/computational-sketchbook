import {
  listEntities,
  createEntity,
  updateEntity,
  deleteEntity,
  listRelationshipsForEntity,
  createRelationship,
  updateRelationship,
  deleteRelationship,
} from "./api.js";
import {
  setSelectedEntity,
  getSelection,
  subscribeSelection,
  enableLocationPick,
} from "./state/selection.js";
import { refreshMapData } from "./map/index.js";

let currentEntities = [];
let currentRelationshipsByEntity = new Map();
let relEditorState = null;

function getElements() {
  return {
    listEl: document.getElementById("entities-list"),
    emptyEl: document.getElementById("entities-empty"),
    form: document.getElementById("entity-form"),
    formStatus: document.getElementById("form-status"),
    relPanel: document.getElementById("entity-rel-panel"),
    relList: document.getElementById("entity-rel-list"),
    relEditor: document.getElementById("rel-editor"),
    relEditorTitle: document.getElementById("rel-editor-title"),
    relEditorForm: document.getElementById("rel-editor-form"),
    relEditorCancel: document.getElementById("rel-editor-cancel"),
    relEditorSave: document.getElementById("rel-editor-save"),
    relEditorError: document.getElementById("rel-editor-error"),
    setLocationBtn: document.getElementById("set-location-btn"),
  };
}

export function renderEntities(entities) {
  currentEntities = entities;
  const { listEl, emptyEl } = getElements();
  listEl.innerHTML = "";

  if (!entities.length) {
    emptyEl.classList.remove("hidden");
    return;
  }
  emptyEl.classList.add("hidden");

  const { selectedEntityId } = getSelection();

  for (const e of entities) {
    const li = document.createElement("li");
    const isSelected = selectedEntityId && String(selectedEntityId) === String(e.id);
    li.className =
      "rounded-md border px-3 py-2 text-sm flex justify-between gap-3 " +
      (isSelected
        ? "border-sky-500 bg-slate-900"
        : "border-slate-800 bg-slate-900/60");
    li.innerHTML = `
      <div>
        <div class="font-medium">
          <button data-action="select" data-id="${e.id}" class="hover:underline text-left">
            ${e.name}
          </button>
        </div>
        <div class="text-xs text-slate-400">${e.entity_type}</div>
      </div>
      <div class="flex items-center gap-2">
        <button data-action="edit" data-id="${e.id}" class="text-xs text-sky-400 hover:underline">
          Edit
        </button>
        <button data-action="delete" data-id="${e.id}" class="text-xs text-rose-400 hover:underline">
          Delete
        </button>
        <div class="text-xs text-slate-500 font-mono hidden md:block">${e.created_at}</div>
      </div>
    `;
    listEl.appendChild(li);
  }
}

export async function loadEntities() {
  const entities = await listEntities();
  renderEntities(entities);
}

export async function loadRelationshipsForSelected() {
  const { selectedEntityId } = getSelection();
  const { relPanel, relList } = getElements();
  if (!relPanel || !relList) return;

  if (!selectedEntityId) {
    relPanel.classList.add("hidden");
    relList.innerHTML = "";
    return;
  }

  try {
    const rels = await listRelationshipsForEntity(selectedEntityId);
    currentRelationshipsByEntity.set(selectedEntityId, rels);

    relPanel.classList.remove("hidden");
    relList.innerHTML = "";

    if (!rels.length) {
      const li = document.createElement("li");
      li.className = "text-xs text-slate-500";
      li.textContent = "No relationships yet.";
      relList.appendChild(li);
      return;
    }

    for (const r of rels) {
      const li = document.createElement("li");
      li.className =
        "flex items-center justify-between text-xs bg-slate-900/60 border border-slate-800 rounded px-2 py-1";
      const otherId =
        String(r.source_id) === String(selectedEntityId)
          ? r.target_id
          : r.source_id;
      const other =
        currentEntities.find((e) => String(e.id) === String(otherId)) || null;
      li.innerHTML = `
        <div class="flex flex-col">
          <span class="font-medium">${r.relationship_type}${
        r.role ? " — " + r.role : ""
      }</span>
          <span class="text-slate-400">${
            other ? other.name : `Entity ${otherId}`
          }</span>
        </div>
        <div class="text-slate-500 font-mono">
          ${r.start_date || ""}${r.end_date ? "–" + r.end_date : ""}
        </div>
        <div class="flex gap-2">
          <button
            data-action="rel-edit"
            data-rel-id="${r.id}"
            class="text-[10px] text-sky-400 hover:underline"
          >
            Edit
          </button>
          <button
            data-action="rel-delete"
            data-rel-id="${r.id}"
            class="text-[10px] text-rose-400 hover:underline"
          >
            Delete
          </button>
        </div>
      `;
      relList.appendChild(li);
    }
  } catch (err) {
    console.error(err);
  }
}

export function setupEntitiesForm() {
  const { form, formStatus } = getElements();
  if (!form) return;

  form.addEventListener("submit", async (evt) => {
    evt.preventDefault();
    formStatus.textContent = "Saving…";
    const formData = new FormData(form);
    const payload = {
      name: formData.get("name"),
      entity_type: formData.get("entity_type"),
    };
    try {
      await createEntity(payload);
      form.reset();
      formStatus.textContent = "Saved.";
      await loadEntities();
    } catch (err) {
      formStatus.textContent = "Error: " + err.message;
    }
  });
}

export function setupEntitiesListInteractions() {
  const { listEl } = getElements();
  if (!listEl) return;

  listEl.addEventListener("click", async (evt) => {
    const target = evt.target;
    if (!(target instanceof HTMLElement)) return;
    const action = target.dataset.action;
    const id = target.dataset.id;
    if (!action || !id) return;

    if (action === "select") {
      setSelectedEntity(Number(id));
      loadRelationshipsForSelected();
      renderEntities(currentEntities);
      return;
    }

    if (action === "delete") {
      const confirmed = window.confirm("Delete this entity? This cannot be undone.");
      if (!confirmed) return;
      try {
        await deleteEntity(id);
        await loadEntities();
      } catch (err) {
        window.alert("Delete failed: " + err.message);
      }
    }

    if (action === "edit") {
      const entity = currentEntities.find((e) => String(e.id) === String(id));
      if (!entity) return;
      const newName = window.prompt("Edit name", entity.name);
      if (!newName || newName.trim() === entity.name) return;
      try {
        await updateEntity(id, { name: newName.trim() });
        await loadEntities();
      } catch (err) {
        window.alert("Update failed: " + err.message);
      }
    }

    if (action === "rel-edit") {
      const relId = target.dataset.relId;
      if (!relId) return;
      openRelationshipEditorForExisting(Number(relId));
      return;
    }

    if (action === "rel-delete") {
      const relId = target.dataset.relId;
      if (!relId) return;
      deleteRelationshipFlow(Number(relId));
      return;
    }
  });

  // keep selection-driven highlight and relationship panel in sync
  subscribeSelection(() => {
    renderEntities(currentEntities);
    loadRelationshipsForSelected();
  });
}

function openRelationshipEditorForExisting(relId) {
  const { selectedEntityId } = getSelection();
  if (!selectedEntityId) return;
  const rels = currentRelationshipsByEntity.get(selectedEntityId) || [];
  const rel = rels.find((r) => String(r.id) === String(relId));
  if (!rel) return;
  relEditorState = {
    mode: "edit",
    relationshipId: rel.id,
    source_id: rel.source_id,
    target_id: rel.target_id,
  };
  const { relEditor, relEditorTitle, relEditorForm, relEditorError } =
    getElements();
  if (!relEditor || !relEditorForm || !relEditorTitle) return;
  relEditorTitle.textContent = "Edit relationship";
  relEditorError.textContent = "";
  relEditor.classList.remove("hidden");
  relEditorForm.elements["relationship_type"].value =
    rel.relationship_type || "";
  relEditorForm.elements["role"].value = rel.role || "";
  relEditorForm.elements["start_date"].value = rel.start_date || "";
  relEditorForm.elements["end_date"].value = rel.end_date || "";
  relEditorForm.elements["strength"].value = rel.strength || "";
  relEditorForm.elements["confidence"].value = rel.confidence || "";
}

export function openRelationshipEditorForNew(sourceId, targetId) {
  relEditorState = {
    mode: "create",
    source_id: sourceId,
    target_id: targetId,
  };
  const { relEditor, relEditorTitle, relEditorForm, relEditorError } =
    getElements();
  if (!relEditor || !relEditorForm || !relEditorTitle) return;
  relEditorTitle.textContent = "New relationship";
  relEditorError.textContent = "";
  relEditor.classList.remove("hidden");
  relEditorForm.reset();
}

async function deleteRelationshipFlow(relId) {
  if (!window.confirm("Delete this relationship?")) return;
  try {
    await deleteRelationship(relId);
    await loadRelationshipsForSelected();
    await refreshMapData();
  } catch (err) {
    window.alert("Failed to delete relationship: " + err.message);
  }
}

export function setupRelationshipEditor() {
  const { relEditor, relEditorForm, relEditorCancel, relEditorError, setLocationBtn } =
    getElements();
  if (!relEditor || !relEditorForm) return;

  if (relEditorCancel) {
    relEditorCancel.addEventListener("click", (evt) => {
      evt.preventDefault();
      relEditor.classList.add("hidden");
      relEditorError.textContent = "";
      relEditorState = null;
    });
  }

  relEditorForm.addEventListener("submit", async (evt) => {
    evt.preventDefault();
    if (!relEditorState) return;
    relEditorError.textContent = "";
    const data = new FormData(relEditorForm);
    const payload = {
      relationship_type: data.get("relationship_type") || "",
      role: data.get("role") || "",
      start_date: data.get("start_date") || "",
      end_date: data.get("end_date") || "",
      strength: data.get("strength")
        ? Number(data.get("strength"))
        : undefined,
      confidence: data.get("confidence")
        ? Number(data.get("confidence"))
        : undefined,
    };
    try {
      if (relEditorState.mode === "create") {
        await createRelationship({
          source_id: relEditorState.source_id,
          target_id: relEditorState.target_id,
          ...payload,
        });
      } else if (relEditorState.mode === "edit") {
        await updateRelationship(relEditorState.relationshipId, payload);
      }
      relEditor.classList.add("hidden");
      relEditorState = null;
      await loadRelationshipsForSelected();
      await refreshMapData();
    } catch (err) {
      relEditorError.textContent = err.message;
    }
  });

  if (setLocationBtn) {
    setLocationBtn.addEventListener("click", () => {
      const { selectedEntityId } = getSelection();
      if (!selectedEntityId) {
        window.alert("Select an entity first.");
        return;
      }
      enableLocationPick();
      window.alert("Location mode: click on the map to set location for the selected entity.");
    });
  }
}


