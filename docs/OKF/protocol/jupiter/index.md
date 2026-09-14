---
type: Protocol Index
title: Jupiter-C Plus BLE protocol
description: Progressive entry point for sanitized Jupiter packet schemas, runtime behavior, live entities, and battery-expansion topology.
tags: [jupiter, ble, protocol, index]
status: draft
source_revision: "03cd0abb9d3a3ac6421037a2f439a6aa9927cdb8"
generated: { by: openai/gpt-5.6-sol, at: 2026-09-14T16:30:00Z }
sources:
  - id: sanitized-map
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/03cd0abb9d3a3ac6421037a2f439a6aa9927cdb8/docs/sources/jupiter-c-plus-ble-field-map.md
    title: Sanitized Jupiter-C Plus BLE field map
  - id: model
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/8bd07088c023f3dc263982170cd573df77ebaee0/custom_components/marstek_ble/products/jupiter.py
    title: Jupiter product model
  - id: runtime
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/8bd07088c023f3dc263982170cd573df77ebaee0/custom_components/marstek_ble/products/jupiter_runtime.py
    title: Jupiter runtime
---

# Jupiter-C Plus BLE protocol

- [Message schemas](messages/) - Command-level packet documentation.
- [Battery expansions](battery-expansions.md) - Repeated records, stable child-device identity, live addition, and runtime presence.
- [Sanitized source map](../../../sources/jupiter-c-plus-ble-field-map.md) - Structural field map without private capture material.

Jupiter-C Plus is runtime-enabled for read-only telemetry and discovered through `MST_JPLS_*`. Its runtime owns its packet schemas and polling schedule; shared command numbers do not imply Venus layouts or control semantics.

The current read-only runtime polls:

| Cadence | Commands                         |
| ------- | -------------------------------- |
| Fast    | `0x03`, `0x14`                   |
| Medium  | `0x0D`, `0x08`, `0x04`, `0x13` |

Jupiter does **not** poll `0x1A`, `0x1C`, `0x21`, `0x22`, or `0x24`. The first two have no retained Jupiter response structure; the latter three produced unresolved one-byte replies during earlier investigation and are excluded from the supported polling command set because their Jupiter semantics are not established. The model-identification request `0x04` remains the sole polling exception to the per-product supported-command set.

The declarative sensor and binary-sensor entity plan is live. This includes the four PV inputs, compact event-history diagnostics, and child devices for populated battery-pack positions. Newly reported battery positions are added without renumbering existing children; disappearing positions become unavailable. Venus write/control platforms remain disabled for Jupiter.

Battery voltage and signed battery current also feed three derived power entities: signed `Battery Power`, non-negative charging `Battery Power In`, and non-negative discharging `Battery Power Out`. Positive signed power represents charging. The directional sensors do not add a new packet interpretation; they split the already modeled signed battery power into charge/discharge directions for Home Assistant consumers such as the Energy Dashboard or Integral helpers.

The Jupiter energy counters previously labeled as discharge energy are exposed as `Daily Output Energy`, `Monthly Output Energy`, and `Local Total Output Energy`. They measure energy delivered through the device output path and are not battery-discharge counters, because output may be supplied directly from PV as well as from the battery. Battery-side cumulative energy should therefore be derived from the directional battery-power sensors when required.

Runtime-enabled describes implementation status, not vendor confirmation of every interpreted field. Tentative and unverified Jupiter observations remain explicitly labeled in the detailed message concepts.
