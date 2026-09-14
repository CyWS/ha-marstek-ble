# Marstek BLE Integration for Home Assistant

Home Assistant integration for Marstek energy-storage systems over Bluetooth Low Energy (BLE).

> [!IMPORTANT]
> **AI-assisted development**
>
> Significant parts of the multi-product work in this fork were developed with assistance from large language models. AI tools were used to analyze the existing codebase and sanitized diagnostics, help reverse-engineer protocol behavior, propose and write implementation changes, create tests, review failures, and draft documentation. The human maintainer defined the goals, supplied hardware observations, reviewed the changes, and ran the local and real-device tests that were available.
>
> AI-generated analysis and code are not independent verification. Protocol interpretations may be wrong, and passing automated tests do not prove compatibility with hardware that has not been tested. Assistant-authored commits are identified in their commit messages where applicable.

## Origin and project scope

This project is a fork and continuation of [jaapp/ha-marstek-ble](https://github.com/jaapp/ha-marstek-ble). jaapp's work provided the original Home Assistant integration, BLE transport and discovery, Venus E telemetry and controls, configurable polling, HACS packaging, and ESPHome Bluetooth Proxy support. That work was essential to this project and remains the foundation on which this fork is built.

This fork extends and restructures the original integration with:

- a product-specific runtime, parser, schema, polling, and entity architecture intended to support multiple Marstek product families without reusing unverified protocol semantics between them;
- read-only Jupiter-C Plus support based on reverse engineering and real-device testing;
- explicit per-product command allowlists and safer Jupiter polling that avoids unresolved command meanings;
- a model for Jupiter base/expansion battery child devices;
- substantially expanded isolated regression, malformed-input, lifecycle, topology, and failure-path tests, plus a separate Home Assistant test harness; and
- structured protocol and architecture documentation under [`docs/OKF/`](docs/OKF/).

The Venus implementation was migrated onto the new multi-product runtime and is covered by automated compatibility/regression tests. No physical Venus device has been available to verify the refactored code path, so Venus support should currently be treated as **expected compatible rather than hardware-verified**.

## Supported devices

| Product | BLE prefix | Validation status | Monitoring | Controls |
| ------- | ---------- | ----------------- | ---------- | -------- |
| Marstek Venus E hardware v2 | `MST_ACCP_*` | Expected compatible; regression/unit tested after the refactor, not hardware-retested | Yes | Yes, expected compatible |
| Marstek Venus E hardware v3 | `MST_VNSE3_*` | Expected compatible; regression/unit tested, not hardware-validated in this fork | Yes | Yes, expected compatible |
| Marstek Jupiter-C Plus | `MST_JPLS_*` | Base unit tested on real hardware | Yes | No, read-only |

### Jupiter expansion batteries

The integration contains a model for the Jupiter-C Plus base battery and up to three expansion-battery positions. These are represented as Home Assistant child devices using the physical pack position as the stable identifier.

**Expansion-battery behavior has not been tested against hardware with actual expansion packs installed.** The current implementation is based on the observed packet structure and synthetic/regression tests. Pack detection, field interpretation, child-device behavior, or additional expansion-specific data may therefore be incomplete or wrong.

If you use a Jupiter-C Plus with one or more expansion batteries, please see [Diagnostics and hardware reports](#diagnostics-and-hardware-reports). Diagnostics from these installations are especially valuable even when the integration appears to work correctly.

## Features

- Multiple Marstek systems can be added as independent Home Assistant devices.
- Local BLE operation without a Marstek cloud dependency.
- ESPHome Bluetooth Proxy support.
- Configurable fast and medium polling intervals.
- Product-specific packet parsing and polling schedules.
- Battery, inverter/grid, PV, energy, temperature, firmware, and diagnostic telemetry where supported by the selected product.
- Experimental Jupiter-C Plus base/expansion battery child-device support.
- The original Venus monitoring and control surfaces retained by the implementation and covered by automated compatibility tests.

## Installation

### HACS

1. Open **HACS → Integrations → Custom repositories**.
2. Add `https://github.com/The-M1k3y/ha-marstek-ble` as an **Integration** repository.
3. Install **Marstek BLE**.
4. Restart Home Assistant.

You can also open the repository directly in HACS:

[![Open this repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=The-M1k3y&repository=ha-marstek-ble&category=integration)

### Manual installation

1. Copy `custom_components/marstek_ble` into the Home Assistant `custom_components` directory.
2. Restart Home Assistant.

## Setup

1. Go to **Settings → Devices & services**.
2. Select **Add Integration**.
3. Search for **Marstek BLE**.
4. Select the discovered device.
5. Complete the configuration flow.
6. Optionally adjust the fast and medium polling intervals in the integration options.

Repeat this process for each Marstek device you want to add.

## Product behavior

### Venus E

The implementation is intended to preserve the original integration's Venus monitoring and write/control behavior. Automated compatibility and regression tests cover the migrated Venus runtime, parsing, entity generation, polling schedule, and legacy control platforms, but the refactored implementation has not yet been validated on physical Venus hardware.

Implemented Venus controls currently include:

- `Output 1 Control`, `EPS Mode`, `AC Input`, `Generator`, and `Buzzer` switches;
- an `Operating Mode` select for **Self-Consumption** and **Manual**;
- `Charge Mode` and `CT Polling Rate` selects; and
- reboot plus fixed power-mode/power-limit buttons.

The current code does **not** expose AI Optimization as a BLE control. Venus behavior that depends on device or firmware details should therefore be considered expected compatibility until confirmed on real hardware.

### Jupiter-C Plus

Jupiter support is intentionally **read-only**. The base unit has been exercised against real hardware. The integration exposes modeled telemetry including:

- battery state of charge, voltage, current, power, stored energy, temperatures, limits, and diagnostic state;
- AC/grid output power, grid qualification, grid voltage/frequency, inverter state/errors, and temperatures;
- four PV input channels with connection/activity state and available voltage/current/power telemetry;
- PV-generation and discharge-energy counters;
- MPPT state and diagnostics;
- modeled base/expansion battery child devices; and
- diagnostic event-history records and other explicitly marked tentative/unverified observations.

No Jupiter `button`, `switch`, or `select` entities are created. Commands whose Jupiter semantics are unresolved are not polled.

Some Jupiter diagnostic entities intentionally include words such as **Unverified**. These represent useful reverse-engineering observations, not vendor-confirmed semantics. In particular, `Surplus Feed-In Active Unverified` must not be interpreted as a confirmed representation of the user-facing surplus-feed-in setting.

## Polling

The integration has two configurable polling tiers:

- **Fast**: default 1 second, configurable from 1–60 seconds.
- **Medium**: default 60 seconds, configurable from 5–300 seconds and never faster than the fast interval.

Actual commands are product-specific. For Jupiter-C Plus the current read-only schedule is:

- fast: `0x03`, `0x14`;
- medium: `0x0D`, `0x08`, `0x04`, `0x13`.

Jupiter commands `0x1A`, `0x1C`, `0x21`, `0x22`, and `0x24` are not polled because their semantics are absent or unresolved.

Venus keeps its own product-specific polling schedule. Automated tests verify the intended behavior of the refactored schedule, but it has not yet been revalidated against Venus hardware in this fork.

## BLE proxy setup

To extend Bluetooth range, configure an [ESPHome Bluetooth Proxy](https://esphome.io/components/bluetooth_proxy/). One proxy can serve multiple Marstek devices.

## Diagnostics and hardware reports

Real-device diagnostics are important because Marstek protocol details can vary by product, hardware revision, firmware, and installed battery configuration. Reports are useful even when no obvious bug is present.

We are particularly interested in diagnostics from:

- **Venus E v2 and v3 devices**, to verify that the refactored multi-product implementation behaves like the original integration on real hardware;
- **Jupiter-C Plus systems with expansion batteries**, because expansion handling has not yet been hardware-tested and the packets may contain additional information or behavior that is not represented by the current model; and
- **other Marstek products**. If a device is not currently supported, open an issue with its model, BLE advertising name/prefix, and a Home Assistant diagnostics download. We are willing to investigate additional products where the BLE protocol is accessible.

When reporting a problem or providing a compatibility report, please include:

- Home Assistant version;
- integration version or commit;
- Marstek model and, where known, hardware/firmware revision;
- whether a direct Bluetooth adapter or ESPHome Bluetooth Proxy is used;
- for Jupiter, the number of installed expansion batteries; and
- the Home Assistant diagnostics download for the Marstek BLE config entry.

The diagnostics exporter redacts known parsed identifiers such as MAC addresses, serial numbers, device IDs, Wi-Fi names, and network addresses. It currently also includes recent raw BLE frame/payload hex for protocol troubleshooting; those raw payloads can encode values that are not independently redacted. Review a diagnostics file before posting it publicly if that is a concern.

## Development and testing

The repository contains an isolated test suite that does not require a real Home Assistant instance, network access, Bluetooth hardware, an ESPHome proxy, or a physical Marstek device.

Typical local checks are:

```bash
just install-quality
just check
just coverage
tox
```

A separate genuine Home Assistant test harness is available for config-flow and integration-lifecycle testing while still mocking Bluetooth/device hardware.

Tests marked `known_issue` are used as an unresolved-defect inventory. The inventory is currently empty; `just test-known-issues` treats an empty selection as success.

See [`tests/README.md`](tests/README.md), [`docs/RELEASE.md`](docs/RELEASE.md), and the `justfile` for the available test and release commands.

## Attribution

This project builds directly on prior open-source work:

- [jaapp/ha-marstek-ble](https://github.com/jaapp/ha-marstek-ble) by @jaapp — the original Home Assistant integration from which this fork was developed;
- [marstek-venus-monitor](https://github.com/rweijnen/marstek-venus-monitor) by @rweijnen;
- [esphome-b2500](https://github.com/tomquist/esphome-b2500) by @tomquist; and
- [hm2500pub](https://github.com/noone2k/hm2500pub) by @noone2k.

## License

MIT

## Disclaimer

This is unofficial software developed through reverse engineering and is not affiliated with Marstek Energy. Use it at your own risk.
