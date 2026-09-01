import * as Phaser from 'phaser';
import { PlayerState } from '../state/PlayerStateEnum';
import { StateMachine } from '../state/StateMachine';
import { CharacterDefinition, placeholderCharacter } from '../../data/characters/CharacterDefinition';
import { MoveDefinition } from '../../data/moves/MoveDefinition';

export class PlayerEntity extends Phaser.GameObjects.Rectangle {
  public declare body: Phaser.Physics.Arcade.Body;
  public stateMachine: StateMachine<PlayerState>;
  
  public health: number;
  public resource: number;
  public facingRight: boolean = true;
  
  public definition: CharacterDefinition;
  public dashCooldownTimerMs: number = 0;

  // Combat fields
  public activeMove: MoveDefinition | null = null;
  public movePhase: 'startup' | 'active' | 'recovery' | null = null;
  public movePhaseTimerMs: number = 0;
  public hitstunTimerMs: number = 0;
  public hitstopTimerMs: number = 0;

  constructor(scene: Phaser.Scene, x: number, y: number, color: number) {
    super(scene, x, y, 40, 80, color);
    
    scene.add.existing(this);
    scene.physics.add.existing(this);

    this.body.setCollideWorldBounds(true);
    
    this.definition = placeholderCharacter;
    this.health = this.definition.maxHealth;
    this.resource = this.definition.maxResource;

    this.stateMachine = new StateMachine<PlayerState>(PlayerState.Fall);
  }
}
