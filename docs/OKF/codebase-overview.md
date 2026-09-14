---
type: Codebase Overview
title: ha-marstek-ble codebase overview
description: Purpose, supported products, Home Assistant surfaces, product runtime structure, and repository layout.
tags: [home-assistant, bluetooth, integration, architecture, venus, jupiter, multi-product]
status: draft
source_revision: "44aee70ecc78d854dd8170fbe0f19b24455d15d1"
generated: { by: openai/gpt-5.6-sol, at: 2026-09-14T12:45:00Z }
sources:
  - id: init
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/__init__.py
    title: Integration setup and product capabilities
  - id: runtime
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/product_runtime.py
    title: Generic product runtime
  - id: entities
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/product_entity_platform.py
    title: Declarative live entity synchronization
  - id: products
    resource: https://github.com/The-M1k3y/ha-marstek-ble/tree/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/products
    title: Product definitions and runtimes
---

# Purpose

`ha-marstek-ble` is a Home Assistant custom integration for local Bluetooth Low Energy communication with Marstek energy-storage devices. The runtime currently implements Venus and Jupiter-C Plus as separate product families.

# Supported discovery surface

| Prefix       | Product        |
| ------------ | -------------- |
| `MST_ACCP_`  | Venus E        |
| `MST_VNSE3_` | Venus E        |
| `MST_JPLS_`  | Jupiter-C Plus |

New entries persist the selected `product_id`. Legacy entries without one retain a Venus fallback.

# Home Assistant platforms

Sensor and binary-sensor entities are generated from product profiles for both runtime products. This allows product-specific fields, names, units, diagnostics, repeated PV inputs, and child-device topology without hard-coded product conditionals in the platform lists.

Venus additionally loads its existing `button`, `switch`, and `select` platforms. Jupiter remains read-only because its write/control command meanings have not been validated.

# Validation boundary

Runtime support and hardware validation are separate concepts. Jupiter-C Plus has been exercised on real hardware with the current multi-product implementation. The migrated Venus path is covered by automated regression/unit tests intended to preserve the original integration behavior, but this fork has not yet revalidated the refactored Venus path on a physical Venus device.

# Runtime model

`ProductRuntime` combines a `ProductProfile` with product-owned polling and any irregular payload parsers. `ProductProtocol` validates common Marstek framing and dispatches only to the selected runtime. `ProductDataUpdateCoordinator` reuses the shared BLE lifecycle and scheduling while holding the product-specific cumulative data object.

`ProductEntityManager` converts the current profile plan into live Home Assistant sensor/binary-sensor entities. Repeated Jupiter battery positions are added as they become populated and retain stable positional identities.

# Repository structure

| Path | Role |
| ---- | ---- |
| `custom_components/marstek_ble/__init__.py` | Product selection, device registration, capability-aware platform forwarding |
| `custom_components/marstek_ble/config_flow.py` | Bluetooth discovery and persisted product selection |
| `custom_components/marstek_ble/product_runtime.py` | Generic runtime, polling command validation, frame parsing, update metadata |
| `custom_components/marstek_ble/product_coordinator.py` | Product-aware coordinator adapter |
| `custom_components/marstek_ble/schema.py` | Declarative binary field/repeated-section parsing |
| `custom_components/marstek_ble/entity.py` | Product profiles, entity/device bindings, repeated topology |
| `custom_components/marstek_ble/product_entity_platform.py` | Live entity-plan synchronization |
| `custom_components/marstek_ble/products/venus.py` | Venus canonical data/schema/entity model |
| `custom_components/marstek_ble/products/venus_runtime.py` | Venus polling and custom parsing |
| `custom_components/marstek_ble/products/jupiter.py` | Jupiter canonical data/schema/entity model |
| `custom_components/marstek_ble/products/jupiter_runtime.py` | Jupiter polling, text parsing, update tracking |
| `custom_components/marstek_ble/{sensor,binary_sensor}.py` | Live declarative read-only platforms |
| `custom_components/marstek_ble/{button,switch,select}.py` | Venus write/control platforms |
| `custom_components/marstek_ble/marstek_device.py` | Shared BLE transport and retained legacy parser/data model |

# Polling configuration

Fast polling is configurable from `1–60 s` and medium polling from `5–300 s`; medium polling is clamped to at least the fast interval. The actual command schedules are product-specific and constrained by each runtime's supported-command policy.
