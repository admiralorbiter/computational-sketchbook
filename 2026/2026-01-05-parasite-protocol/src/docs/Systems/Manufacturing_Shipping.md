# System — Manufacturing & Shipping

## Summary
Modules are created through a 3-step pipeline:
Ribosomes (build time) → ER/Golgi (assembly) → Vesicles (delivery).

## Objects
- RibosomeSlot: holds 0..1 job
- Job: module_id, remaining_time, priority
- Assembler: processes finished parts into deployable module payloads
- Vesicle: carries payload from origin to target placement point

## State machine (job)
Queued → Producing → Assembling → Shipping → Delivered → Installed
Failure states: Stalled (infection), Destroyed (if you allow enemy interception), Cancelled

## Rules
- A module is non-functional until Installed.
- Cancelling:
  - If Queued/Producing: refund full blocks, partial ATP (design choice).
  - If Assembling: refund partial.
  - If Shipping: refund none or partial (design choice).

## UI requirements
- Queue list: reorder, cancel, prioritize
- Each job shows ETA and current stage
- Shipping line preview from ER/Golgi to placement point

## Tuning levers
- Ribosome slot count
- Build time multipliers
- Assembly time multipliers
- Vesicle count / speed
- Infection penalties to each stage

## Definition of Done
- [ ] You can queue at least 3 modules and reorder them.
- [ ] Delivered modules install and become active.
- [ ] Cancels behave consistently with clear messaging.
- [ ] Vesicles visually represent payload and route.
- [ ] Infection can stall shipping and tooltip explains why.
