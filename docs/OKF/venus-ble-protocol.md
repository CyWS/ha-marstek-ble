---
type: Protocol Reference
title: Venus BLE transport and framing
description: GATT transport, frame encoding, validation, command correlation, and current Venus runtime dispatch.
tags: [venus, ble, gatt, protocol, framing]
status: draft
source_revision: "44aee70ecc78d854dd8170fbe0f19b24455d15d1"
generated: { by: openai/gpt-5.6-sol, at: 2026-09-14T12:45:00Z }
sources:
  - id: constants
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/const.py
    title: BLE UUID and frame constants
  - id: device
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/marstek_device.py
    title: Shared BLE connection and command transport
  - id: protocol
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/product_runtime.py
    title: Shared product-aware frame validator and dispatcher
  - id: runtime
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/products/venus_runtime.py
    title: Venus polling and irregular payload parsers
  - id: coordinator
    resource: https://github.com/The-M1k3y/ha-marstek-ble/blob/44aee70ecc78d854dd8170fbe0f19b24455d15d1/custom_components/marstek_ble/product_coordinator.py
    title: Product-aware coordinator notification path
---

# Scope

This document describes the BLE framing and transport used by the current Venus runtime. It is an implementation reference, not a vendor protocol specification. The common frame mechanism is shared infrastructure, but the command set, payload schemas, polling schedule, and controls documented here are Venus-specific. See [the knowledge scope](scope.md) before applying any interpretation to another product.

# Discovery and GATT characteristics

The integration discovers Venus devices using the `MST_ACCP_*` and `MST_VNSE3_*` advertising-name prefixes.

| Role                 | UUID                                   |
| -------------------- | -------------------------------------- |
| Service              | `0000ff00-0000-1000-8000-00805f9b34fb` |
| Command write        | `0000ff01-0000-1000-8000-00805f9b34fb` |
| Notification receive | `0000ff02-0000-1000-8000-00805f9b34fb` |

Commands are written to `FF01`. Responses and other device frames arrive as notifications on `FF02`.

# Frame schema

Outgoing commands and accepted notifications use this byte layout:

| Offset | Size     | Meaning                                  |
| -----: | -------: | ---------------------------------------- |
| `0`    | 1        | Start byte `0x73`                        |
| `1`    | 1        | Total frame length, including checksum   |
| `2`    | 1        | Frame type `0x23`                        |
| `3`    | 1        | Command identifier                       |
| `4`    | variable | Command or response payload              |
| final  | 1        | XOR checksum                             |

In symbolic form:

```text
73 LL 23 CC [payload ...] XX
```

The builder initially creates `[0x73, 0x00, 0x23, command]`, appends the payload, stores `len(frame) + 1` in `LL`, XORs every byte accumulated so far, and appends that XOR as `XX`. Therefore `LL` equals the final number of bytes in the frame.

## Checksum

```python
checksum = 0
for byte in frame_without_checksum:
    checksum ^= byte
```

The product-aware notification parser recomputes the XOR over all bytes except the final byte and rejects a mismatch.

# Notification validation

The current `ProductProtocol` accepts a notification for product-specific parsing only when:

- it contains at least five bytes;
- byte `0` is `0x73`;
- byte `2` is `0x23`;
- byte `1` exactly matches the actual received frame length; and
- the final byte equals the XOR checksum.

After frame validation, byte `3` selects the product-local packet/parser and bytes `4:-1` are passed as the payload. Fixed packet schemas additionally validate their allowed payload lengths before applying any field updates.

This differs from the earlier legacy parser, which did not independently enforce the declared frame length.

# Request and response behavior

The shared BLE transport supports one in-flight command per `MarstekBLEDevice`:

1. acquire the operation lock;
2. ensure a BLE connection and notification subscription;
3. set the pending command byte and a new response event;
4. write the frame to `FF01`;
5. wait for the response within the configured timeout; and
6. treat a notification with the same command byte at offset `3` as the command response.

There is no transaction identifier. Correlation is based on the command byte, which is safe within the implementation because command operations are serialized.

A matching notification can complete the command transport even when no product payload parser maps that response into Home Assistant state. Parsing success controls data updates; response matching controls command completion.

# Connection lifecycle

The BLE client is established through `bleak_retry_connector` using the service cache. Notifications are started once per connection. A fresh Home Assistant `BLEDevice` reference may be obtained before reconnecting, supporting direct adapters and BLE proxies.

After transmitted commands, the integration resets its inactivity disconnect timer. A later command reconnects as needed after an intentional idle disconnect.

# Current Venus parser dispatch

The live Venus runtime uses declarative packet schemas for fixed binary responses and product-local custom parsers for irregular text responses.

| Command | Current handling                                      |
| ------: | ----------------------------------------------------- |
| `0x03`  | Declarative runtime information                       |
| `0x04`  | Custom ASCII device-information parser                |
| `0x08`  | Custom ASCII Wi-Fi SSID parser                        |
| `0x0D`  | Declarative system data                               |
| `0x13`  | Declarative timer information                         |
| `0x14`  | Declarative BMS data                                  |
| `0x1A`  | Declarative configuration data                        |
| `0x21`  | Custom meter-IP parser                                |
| `0x22`  | Declarative CT polling-rate readback                  |
| `0x24`  | Custom network-information parser                     |
| `0x28`  | Custom local-API status parser                        |
| `0x1C`  | Polled for Venus compatibility; no state parser mapped |

Notifications for commands with no Venus schema/parser are recorded by the BLE diagnostics path but do not update the canonical `VenusData` state.

# Polling

The Venus runtime currently polls:

| Cadence | Commands |
| ------- | -------- |
| Fast | `0x03`, `0x14` |
| Medium | `0x0D`, `0x08`, `0x1A`, `0x22`, `0x21` with request payload `0x0B`, `0x24`, `0x04`, `0x13`, `0x28`, `0x1C` |

These are Venus command semantics. The same command numbers must not be assumed to be safe or equivalent for Jupiter or other products.

# Byte order

All binary multi-byte Venus fields parsed by the repository use little-endian `struct` formats such as `<H`, `<h`, and `<I`. ASCII-based responses are decoded separately. Exact field layouts and scaling are listed in the [Venus command and payload reference](venus-command-reference.md).

# Validation boundary

The current Venus runtime and polling behavior are covered by automated compatibility/regression tests. The multi-product branch has not yet been revalidated against physical Venus hardware, so this document describes implemented behavior rather than confirmed end-to-end hardware compatibility of the refactored release.
