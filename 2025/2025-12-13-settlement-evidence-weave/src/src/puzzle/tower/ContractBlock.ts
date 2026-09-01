import Phaser from "phaser";
import { ClauseType, CLAUSE_COLORS } from "./ClauseTypes";

export type ContractBlockSpec = {
  clause: ClauseType;
  label: string;
  isHazard?: boolean;
  isFragile?: boolean; // e.g., ambiguous clauses can "collapse"
};

export class ContractBlock {
  public body: MatterJS.BodyType;
  public labelText: Phaser.GameObjects.Text;

  constructor(
    private scene: Phaser.Scene,
    x: number,
    y: number,
    width: number,
    height: number,
    public spec: ContractBlockSpec
  ) {
    // Phaser's Matter factory returns a GameObject with a body.
    const rect = scene.matter.add.rectangle(x, y, width, height, {
      restitution: 0.0,
      friction: 0.8,
      frictionStatic: 1.0,
      chamfer: { radius: 6 }
    });

    // Color via a graphics overlay (fast placeholder).
    const gfx = scene.add.graphics();
    gfx.fillStyle(CLAUSE_COLORS[spec.clause], 1);
    gfx.fillRoundedRect(x - width / 2, y - height / 2, width, height, 6);

    // Attach graphics to the body by updating in scene's update loop (managed externally).
    // We'll store the body and provide a simple sync helper.
    this.body = rect;

    this.labelText = scene.add.text(x, y, spec.label, {
      fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
      fontSize: "14px",
      color: "#0b0d12"
    }).setOrigin(0.5);

    // Store references for syncing
    (this.body as any).__settlementGfx = gfx;
    (this.body as any).__settlementText = this.labelText;
    (this.body as any).__settlementSpec = spec;
  }

  static syncVisuals(body: MatterJS.BodyType) {
    const gfx: Phaser.GameObjects.Graphics | undefined = (body as any).__settlementGfx;
    const txt: Phaser.GameObjects.Text | undefined = (body as any).__settlementText;
    if (!gfx || !txt) return;

    const pos = body.position;
    const angle = body.angle;

    // Graphics: easiest is to clear and redraw at current pose
    const width = (body as any).bounds.max.x - (body as any).bounds.min.x;
    const height = (body as any).bounds.max.y - (body as any).bounds.min.y;
    const spec = (body as any).__settlementSpec as ContractBlockSpec;

    gfx.clear();
    gfx.fillStyle(CLAUSE_COLORS[spec.clause], 1);

    // Phaser Graphics doesn't support transform methods, so we draw at position
    // For rotation, we'll use the graphics object's transform or calculate manually
    // For now, draw unrotated (rotation will be handled by the text rotation)
    gfx.fillRoundedRect(pos.x - width / 2, pos.y - height / 2, width, height, 6);

    txt.setPosition(pos.x, pos.y);
    txt.setRotation(angle);
  }
}
