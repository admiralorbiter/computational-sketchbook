import * as Phaser from 'phaser';
import { PlayerEntity } from '../entities/PlayerEntity';
import { InputManager } from '../input/InputManager';
import { MovementController } from '../controllers/MovementController';
import { DebugOverlay } from '../ui/DebugOverlay';
import { debugConfig } from '../../config/debugConfig';
import { EventBus } from '../utils/events';
import { MoveExecutor } from '../combat/MoveExecutor';
import { BlockSystem } from '../combat/BlockSystem';
import { HitboxSystem } from '../combat/HitboxSystem';
import { HurtboxSystem } from '../combat/HurtboxSystem';
import { DamageSystem } from '../combat/DamageSystem';
import { KnockbackSystem } from '../combat/KnockbackSystem';
import { characterA } from '../../data/characters/characterA';
import { characterB } from '../../data/characters/characterB';

export class CombatScene extends Phaser.Scene {
  private p1!: PlayerEntity;
  private p2!: PlayerEntity;
  
  private inputManager!: InputManager;
  private movementController!: MovementController;
  private debugOverlay!: DebugOverlay;

  private eventBus!: EventBus;
  private moveExecutor!: MoveExecutor;
  private blockSystem!: BlockSystem;
  private hitboxSystem!: HitboxSystem;
  private hurtboxSystem!: HurtboxSystem;
  private damageSystem!: DamageSystem;

  constructor() {
    super('CombatScene');
  }

  create() {
    // 1. Create a stage floor
    const floor = this.add.rectangle(640, 680, 1000, 40, 0x555555);
    this.physics.add.existing(floor, true); // static body

    // 2. Spawn players (placeholder colors)
    this.p1 = new PlayerEntity(this, 400, 500, 0xff0000); // Red
    this.p1.definition = characterA; // Assign Character A

    this.p2 = new PlayerEntity(this, 880, 500, 0x0000ff); // Blue
    this.p2.definition = characterB; // Assign Character B
    this.p2.facingRight = false; // P2 faces left initially

    // 3. Add collisions
    this.physics.add.collider(this.p1, floor);
    this.physics.add.collider(this.p2, floor);
    // Note: MVP design typically avoids player-to-player physics collisions 
    // to prevent jitter, but we can add it if desired later.

    // 4. Initialize Controllers & Combat Systems
    this.inputManager = new InputManager(this);
    this.movementController = new MovementController();
    
    this.eventBus = new EventBus();
    this.moveExecutor = new MoveExecutor(this.eventBus);
    this.blockSystem = new BlockSystem();
    this.hitboxSystem = new HitboxSystem();
    this.hurtboxSystem = new HurtboxSystem(this.eventBus);
    this.damageSystem = new DamageSystem(this.eventBus);
    new KnockbackSystem(this.eventBus); // Subscribes internally
    
    // 5. Initialize UI
    this.debugOverlay = new DebugOverlay(this);
    this.debugOverlay.isVisible = debugConfig.showStateOverlay;
  }

  update(time: number, delta: number) {
    const p1Input = this.inputManager.getFrame(0);
    const p2Input = this.inputManager.getFrame(1);
    const p1Prev = this.inputManager.getPreviousFrame(0);
    const p2Prev = this.inputManager.getPreviousFrame(1);

    // 1. Poll inputs
    this.inputManager.update(time);

    // 2. Resolve block intents
    this.blockSystem.update(this.p1, p1Input);
    this.blockSystem.update(this.p2, p2Input);

    // 3. Resolve movement logic
    this.movementController.update(this.p1, p1Input, p1Prev, delta);
    this.movementController.update(this.p2, p2Input, p2Prev, delta);

    // 4. Execute move logic (timers & attacks)
    this.moveExecutor.update(this.p1, p1Input, delta);
    this.moveExecutor.update(this.p2, p2Input, delta);

    // 5. Spawn hitboxes
    this.hitboxSystem.update([this.p1, this.p2]);

    // 6. Resolve hit detection & trigger events
    this.hurtboxSystem.update([this.p1, this.p2], this.hitboxSystem);

    // 7. Update Damage states (hitstop and hitstun timers)
    this.damageSystem.update([this.p1, this.p2], delta);

    // 8. Update debug UI
    this.debugOverlay.update(this.p1, this.p2, this.hitboxSystem);
  }
}
