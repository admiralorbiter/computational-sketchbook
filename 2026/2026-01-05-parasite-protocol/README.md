# Parasite Protocol — Reactive Logistics & Cellular Systems Defense (January 2026)

> **Category:** `[SKETCHBOOK EXPERIMENT / SYSTEMS GAME & REACTIVE BIOLOGICAL CONTROL]`  
> **Date:** January 5–6, 2026  
> **Stack:** Rust, Bevy 0.12, ECS, WebAssembly  
> **Original Origin:** `admiralorbiter/parasite-protocol` (HEAD: `42f6ab3`)  

---

## 1. Project Vision & The Biological Control Architecture

*Parasite Protocol* explored transforming the internal machinery of a biological cell into a distributed reactive control game:

```text
               ┌────────────────────────────────────────────────────────┐
               │                 PARASITE PROTOCOL                      │
               │   "Manufacturing logistics, event-driven signaling,    │
               │    and adaptive selection pressure as tower defense"   │
               └──────────────────────────┬─────────────────────────────┘
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        ▼                                 ▼                                 ▼
INFORMATION FLOW                  MATERIAL LOGISTICS                SYSTEMIC PATHOLOGY
├── Receptor (senses state)       ├── Ribosome (manufacturing)      ├── Spreading infection field
├── Relay (gates/amplifies)       ├── ER/Golgi (assembly)           ├── Logistics disruption & noise
└── Effector (targeted reaction)  └── Vesicles (cytoskeleton route) └── Coevolutionary counter-traits
```

---

## 2. Core Conceptual Innovations

1. **Signaling Circuits as Defenses:** Defenses are not static automatic turrets; they are directed reactive graphs (`Receptor` $	o$ `Relay` $	o$ `Effector`) wired by the player to trigger responses only when specific biological conditions occur (e.g. membrane breach, low ATP).
2. **Physical Manufacturing & Shipping Lifecycles:** Defenses do not appear instantaneously upon purchase; they must be queued, assembled in the ER/Golgi, shipped via vesicles along cytoskeleton tracks, and installed before activation.
3. **Infection as Functional Degradation:** Rather than a simple health bar, spreading infection creates signal noise, slows vesicle transit, and raises cellular stress.
4. **Adversarial Selection Pressure:** Pathogen waves analyze player defensive tendencies and adaptively generate counter-traits (stealth, tunneling, biofilm).

---

## 3. Implementation Status: Built vs. Designed

- **BUILT:** Bevy 0.12 application foundation, camera pan/zoom controls, time scale manager, cell arena layout with membrane, nucleus, ER/Golgi, mitochondria, and procedural texture generators.
- **DESIGNED (NOT BUILT):** Combat execution, vesicle shipping state machines, reactive signaling graph builder, ATP/stress economy, infection diffusion fields, and pathogen coevolution engine.
