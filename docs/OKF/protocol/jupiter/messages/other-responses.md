---
type: BLE Message Collection
title: Other Jupiter-C Plus responses
description: Identity, SSID, unresolved status responses, and commands without an observed response schema.
tags: [jupiter, ble, identity, unresolved]
status: draft
source_revision: "44aee70ecc78d854dd8170fbe0f19b24455d15d1"
generated: { by: openai/gpt-5.6-sol, at: 2026-09-14T12:45:00Z }
sources:
  - id: sanitized-map
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/docs/sources/jupiter-c-plus-ble-field-map.md
    title: Sanitized Jupiter field map
  - id: runtime
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/products/jupiter_runtime.py
    title: Jupiter polling and parsing runtime
  - id: model
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/products/jupiter.py
    title: Jupiter packet schemas and supported commands
---

# `0x04` device information

The response is comma-separated ASCII `key=value` data. Recognized keys are:

| Key      | Meaning                   |
| -------- | ------------------------- |
| `type`   | Device type / model ID    |
| `id`     | Cloud/device identifier   |
| `mac`    | Bluetooth MAC address     |
| `ems_v`  | EMS firmware version      |
| `inv_v`  | Inverter firmware version |
| `mppt_v` | MPPT firmware version     |
| `bms_v`  | BMS firmware version      |

Unknown keys must not fail the complete packet. Values are not included in this repository source.

`0x04` is used for model/identity information and remains available as the explicit identification-command exception to the normal product supported-command restriction.

# `0x08` Wi-Fi SSID

The complete payload is an ASCII SSID with configuration-dependent length. No network name is committed to the repository.

# `0x0D` unresolved status

Payload length: 12 bytes. The Venus interpretation has not been validated for Jupiter, so no field mapping is defined. The current Jupiter runtime still polls this command but does not expose a field interpretation.

# `0x21`, `0x22`, and `0x24`

Earlier investigation observed one-byte replies for each of these command numbers. Their Jupiter semantics remain unresolved; a one-byte reply is not sufficient evidence that the request is read-only telemetry or that the Venus meaning applies.

The declarative model retains separate raw packet schemas for reverse-engineering compatibility, but the current Jupiter runtime does **not** send or poll `0x21`, `0x22`, or `0x24`, and they are excluded from the Jupiter supported-command set.

# `0x1A` and `0x1C`

No Jupiter response structure is retained for these command numbers. The current Jupiter runtime does not send or poll either command.
