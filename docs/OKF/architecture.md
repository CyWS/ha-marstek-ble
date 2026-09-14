---
type: Software Architecture
title: Marstek BLE runtime architecture
description: Product selection, polling, BLE lifecycle, product-specific parsing, declarative entities, and capability boundaries.
tags: [architecture, coordinator, polling, bluetooth, multi-product]
status: draft
source_revision: "44aee70ecc78d854dd8170fbe0f19b24455d15d1"
generated: { by: openai/gpt-5.6-sol, at: 2026-09-14T12:45:00Z }
sources:
  - id: init
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/__init__.py
    title: Integration setup and platform capabilities
  - id: coordinator
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/product_coordinator.py
    title: Product-aware coordinator
  - id: runtime
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/product_runtime.py
    title: Product runtime and protocol dispatcher
  - id: entities
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/product_entity_platform.py
    title: Live declarative entity synchronization
  - id: jupiter-runtime
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/products/jupiter_runtime.py
    title: Jupiter runtime
---

# Runtime data flow

```text
Bluetooth discovery
  -> config entry + product_id
  -> ProductRuntime registry
  -> ProductDataUpdateCoordinator
       -> MarstekBLEDevice transport
       -> ProductProtocol frame validation
       -> product-specific parser/poll schedule
  -> product-specific cumulative data
  -> ProductProfile entity plan
  -> sensor / binary_sensor entities
```

Venus and Jupiter-C Plus are explicitly registered runtime products. New entries persist a product ID; legacy entries without one retain the Venus fallback. Unknown persisted product IDs are rejected.

# Polling

Each product owns its polling schedule. Runtime construction rejects scheduled commands outside the product's explicit supported-command set, except for the model-identification command `0x04`.

| Cadence | Jupiter commands                 |
| ------- | -------------------------------- |
| Fast    | `0x03`, `0x14`                   |
| Medium  | `0x0D`, `0x08`, `0x04`, `0x13` |

Jupiter does not poll `0x1A`, `0x1C`, `0x21`, `0x22`, or `0x24`, because their Jupiter semantics are absent or unresolved. In particular, the existence of earlier one-byte replies for `0x21`, `0x22`, and `0x24` is not treated as evidence that those requests are safe read-only telemetry.

Venus keeps its own product-specific schedule, including the commands required by the original monitoring/configuration implementation.

# Parsing and state

`ProductProtocol` validates the common frame structure, including the declared frame length and checksum, then dispatches the payload only to the selected runtime. Fixed binary packets use declarative field metadata. Irregular text packets remain product-local custom parsers.

Venus stores nested `VenusData`; Jupiter stores `RuntimeJupiterData`. Jupiter additionally parses comma-separated `0x04` identity/version data and variable-length `0x08` Wi-Fi SSID data. Compatibility aliases remain available for regression/transition code, but live sensor creation now reads canonical `ProductProfile` bindings.

# Entity and device creation

`sensor.py` and `binary_sensor.py` consume `ProductProfile.build_entity_plan()`. Fixed entities are created immediately. Repeated Jupiter battery-pack entities are created when the reported pack count makes the corresponding slot present.

A `ProductEntityManager` listens for later coordinator updates. If the pack count increases, only the newly available child bindings are added. Existing child bindings are never renumbered. If the count decreases, their presence condition makes the removed slot unavailable without shifting identities.

Jupiter battery child identifiers are positional and stable:

```text
<main BLE identifier>:battery_pack:0
<main BLE identifier>:battery_pack:1
<main BLE identifier>:battery_pack:2
<main BLE identifier>:battery_pack:3
```

This exposes the modeled per-PV entities and populated base/expansion battery entities through Home Assistant.

# Capability boundary

Venus loads sensor, binary-sensor, button, switch, and select platforms. Jupiter loads only sensor and binary-sensor platforms. Venus write/control command semantics are not assumed to apply to Jupiter.

Runtime-enabled does not imply equal hardware validation. Jupiter-C Plus has been exercised against real hardware on the current branch. The migrated Venus runtime is covered by automated regression/unit tests but has not been revalidated against physical Venus hardware after the multi-product refactor.

Future work may add Jupiter controls only after their command semantics are explicitly validated. Optional repair/notification UX for topology changes may also be added later; neither is required for the current read-only Jupiter release scope.
