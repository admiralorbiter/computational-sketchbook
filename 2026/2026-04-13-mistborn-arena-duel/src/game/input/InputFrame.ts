import { InputAction } from './InputAction';

export interface InputFrame {
  actions: Set<InputAction>;
  timestamp: number;
}
