import { setupShell } from "./shell.js";
import {
  setupEntitiesForm,
  setupEntitiesListInteractions,
  setupRelationshipEditor,
} from "./entities.js";
import { setupMap, refreshMapData } from "./map/index.js";
import { setupGraph } from "./graph.js";

window.addEventListener("DOMContentLoaded", async () => {
  await setupMap();
  setupGraph();
  setupEntitiesForm();
  setupEntitiesListInteractions();
  setupRelationshipEditor();
  await setupShell();
  await refreshMapData();
});


