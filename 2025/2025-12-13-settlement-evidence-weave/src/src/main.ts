import Phaser from "phaser";
import { createGameConfig } from "./config/gameConfig";
import { registerScenes } from "./scenes/registerScenes";

const config = createGameConfig();
registerScenes(config);

// Mount canvas into #app
const parent = document.getElementById("app") ?? undefined;
(config as Phaser.Types.Core.GameConfig).parent = parent;

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const game = new Phaser.Game(config);
