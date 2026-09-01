# System — Circuits (Receptors → Relays → Effectors)

## Summary
Player builds a directed graph. Receptors emit signals when triggered; relays transform signals; effectors execute payloads.

## Core concepts
- Signal: magnitude, tags, source_id, timestamp
- Node: receptor|relay|effector
- Edge: from_node → to_node, with optional attenuation

## Trigger model
- Receptors subscribe to events (enemy enters radius, membrane damaged, etc.)
- When condition met: create Signal and propagate along outgoing edges.

## Relay transforms (MVP)
- Amplify: magnitude *= k; ATP cost += c
- Split: duplicate signals across N outputs with magnitude *= s
- Gate: min interval between activations; optionally charge and release bigger pulse
- Delay: buffer signal for t seconds

## Effector execution
- Convert final signal magnitude into effect payload (damage, slow, cleanse, etc.)
- Target selection: closest/strongest/tagged/within area

## UI requirements
- Circuit overlay shows nodes/edges, arrows, and highlights active paths.
- Selecting a node shows:
  - incoming/outgoing edges
  - computed final effect preview (estimated damage/slow) for a representative target

## Failure modes
- Node disabled by infection: edges shown as broken; downstream doesn’t trigger.
- Insufficient ATP: trigger fails gracefully with UI reason.

## Definition of Done
- [ ] Build a simple chain receptor→effector and it triggers correctly.
- [ ] Add relay amplify and see measurable output change.
- [ ] Gate prevents rapid retrigger spam.
- [ ] Disable a node and see downstream stop with clear UI.
- [ ] Circuit view clearly shows flow during activation.
