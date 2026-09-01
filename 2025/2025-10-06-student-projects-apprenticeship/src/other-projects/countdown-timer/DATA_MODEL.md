# Data Model & Validation

## Event
```ts
type Event = {
  id: string;
  name: string;         // 1-100 chars
  targetISO: string;    // ISO date/time (local display)
  category: string;     // Exam, Assignment, Holiday, Sports, Other
  color?: string;       // theme or hex
  createdAt: string;    // ISO
  active: boolean;      // true until ended or archived
};
```

## Storage keys
- `countdownTimer_events`: Event[]
- `countdownTimer_backup`: Event[]
- `countdownTimer_settings`: preferences

## Validation
- Future dates only for new/edited events
- Reasonable range (≤ 10 years ahead)
- Trim names; allow letters, numbers, punctuation
