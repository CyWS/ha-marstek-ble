---
type: Software Architecture
title: Declarative product, parsing, and entity model
description: Product-specific packet schemas, cumulative dataclasses, runtime parsing, live Home Assistant entity metadata, repeated records, and expansion topology.
tags: [architecture, dataclass, parsing, entities, products, expansions]
status: draft
source_revision: "44aee70ecc78d854dd8170fbe0f19b24455d15d1"
generated: { by: openai/gpt-5.6-sol, at: 2026-09-14T12:45:00Z }
sources:
  - id: schema
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/schema.py
    title: Declarative packet parsing primitives
  - id: entities
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/entity.py
    title: Entity metadata and topology planning
  - id: entity-runtime
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/product_entity_platform.py
    title: Live entity synchronization
  - id: venus-runtime
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/products/venus_runtime.py
    title: Enabled Venus runtime adapter
  - id: jupiter-runtime
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/products/jupiter_runtime.py
    title: Enabled Jupiter runtime adapter
---

# Status

The declarative parsing and read-only entity model is live for both Venus and Jupiter-C Plus. Product dataclasses are the canonical state, packet schemas define binary parsing, runtimes own polling/custom parsing, and sensor/binary-sensor platforms consume generated `ProductProfile` entity bindings.

Venus write/control platforms remain legacy implementations. They are loaded only for Venus and are not exposed for Jupiter.

# Single source of truth

Each product model combines packet schemas, nested cumulative state, Home Assistant entity descriptions, and an explicit supported-command set. A `FieldSource` normalizes one packet representation into the canonical field unit. Direct entity metadata is attached to the corresponding dataclass field; derived entities stay in profile metadata.

Product runtime construction rejects scheduled commands outside the profile's supported-command set, except for the product-identification command `0x04`. The presence of a packet schema alone therefore does not authorize polling a command.

# Runtime parsing

`ProductProtocol` performs common Marstek frame validation, including declared-length and checksum validation, and dispatches only to the selected `ProductRuntime`. Declarative parsing validates packet length and decodes matching fields before applying changes, avoiding partial updates on decoding failure.

Repeated binary records retain indexed canonical paths such as:

```text
pv_inputs.3.power
battery.packs.1.highest_cell_voltage
```

Jupiter's runtime adds custom parsing for `0x04` key/value device information and the variable-length `0x08` SSID response. `RuntimeJupiterData` also retains compatibility aliases for older callers, but live declarative entities read canonical bindings.

# Live entity plans

`ProductProfile.build_entity_plan()` recursively produces:

- main and child-device bindings;
- sensor and binary-sensor bindings;
- direct or derived value accessors;
- canonical staleness paths;
- stable product-local entity keys; and
- repeated-record presence conditions.

The sensor and binary-sensor platforms consume this plan through `ProductEntityManager`. Fixed entities are added immediately. When a repeated record count later increases, a fresh plan contributes only entity keys that have not already been created.

# Jupiter topology

Jupiter exposes four fixed PV input records as entities on the main device. Its BMS section contains four fixed battery-pack slots controlled by the reported `pack_count`.

Populated battery slots become child devices with stable positional identifiers. Each exposes the modeled highest/lowest cell indices, highest/lowest cell voltages, and raw status. A decrease in `pack_count` does not rename or delete an existing binding; its presence condition makes it unavailable. A later increase adds only newly populated slots.

`detect_expansion_increases()` remains available as topology-analysis infrastructure, but live entity synchronization no longer requires a reload merely to add newly reported battery slots. A future repair flow may still be useful for explicit user notification or reconfiguration policy.

# Validation boundary

The declarative architecture and both product runtimes are exercised by isolated tests. Those tests validate implementation contracts but do not replace hardware testing. Jupiter-C Plus has separate real-device validation on the current branch; the migrated Venus runtime has not yet been revalidated on physical Venus hardware after the multi-product refactor.
