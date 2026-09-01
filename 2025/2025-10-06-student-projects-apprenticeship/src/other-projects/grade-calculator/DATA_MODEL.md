# Data Model & Validation

## Assignment
```ts
type Assignment = {
  id: string;            // unique
  name: string;          // 1-50 chars
  earned: number;        // 0..possible
  possible: number;      // 1..1000
  weight?: number;       // 0..100 (percent)
  category?: string;     // optional
  createdAt: string;     // ISO
};
```

## Categories (optional)
```ts
type Category = {
  name: string;          // 'Tests', 'Quizzes', ...
  weight: number;        // must sum to 100 across categories
  assignments: string[]; // assignment ids
  average?: number;
};
```

## Storage keys
- `gradeCalc_assignments`: Assignment[]
- `gradeCalc_categories`: Category[]
- `gradeCalc_settings`: preferences

## Validation rules
- Name required (1–50 chars)
- earned ≤ possible; possible ≥ 1
- Weights 0–100; warn if totals ≠ 100%
