export class StateMachine<T extends string> {
  public current: T;
  public timerMs: number = 0;

  public onEnter?: (state: T) => void;
  public onExit?: (state: T) => void;
  public onUpdate?: (state: T, delta: number) => void;

  constructor(initialState: T) {
    this.current = initialState;
  }

  public transition(next: T): boolean {
    if (this.current === next) {
      return false;
    }

    if (this.onExit) {
      this.onExit(this.current);
    }

    this.current = next;
    this.timerMs = 0;

    if (this.onEnter) {
      this.onEnter(this.current);
    }

    return true;
  }

  public update(delta: number): void {
    this.timerMs += delta;

    if (this.onUpdate) {
      this.onUpdate(this.current, delta);
    }
  }
}
