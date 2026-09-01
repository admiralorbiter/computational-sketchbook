export type ClauseType =
  | "IF"
  | "THEN"
  | "AND"
  | "OR"
  | "DEADLINE"
  | "EVIDENCE"
  | "AMBIGUOUS"
  | "AUDIT";

export const CLAUSE_COLORS: Record<ClauseType, number> = {
  IF: 0x6aa6ff,
  THEN: 0x7dffb2,
  AND: 0xffd36a,
  OR: 0xff8aa1,
  DEADLINE: 0xd07dff,
  EVIDENCE: 0x9ad0ff,
  AMBIGUOUS: 0xa3a9b8,
  AUDIT: 0xff6a6a
};
