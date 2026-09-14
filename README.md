# Marstek BLE Integration for Home Assistant

Home Assistant integration for supported Marstek energy-storage systems over Bluetooth Low Energy (BLE).

> [!IMPORTANT]
> **AI-assisted development**
>
> Significant parts of the multi-product work in this fork were developed with assistance from large language models. AI tools were used to analyze the existing codebase and sanitized diagnostics, help reverse-engineer protocol behavior, propose and write implementation changes, create tests, review failures, and draft documentation. The human maintainer defined the goals, supplied hardware observations, reviewed the changes, and ran the local and real-device tests that were available.
>
> AI-generated analysis and code are not independent verification. Protocol interpretations may be wrong, and passing automated tests do not prove compatibility with hardware that has not been tested. Assistant-authored commits are identified in their commit messages where applicable.

This repository is preparing its first multi-product release. Jupiter-C Plus has been exercised against real hardware and is intentionally read-only. The current multi-product Venus code path has **not** been tested against a physical Venus device; Venus compatibility is based on regression/unit tests that indicate the refactor should preserve the behavior of the original integration.

## Supported devices

| Product | BLE prefix | Current validation status | Monitoring | Controls |
| ------- | ---------- | ------------------------- | ---------- | -------- |
| Marstek Venus E hardware v2 | `MST_ACCP_*` | Expected compatible; regression/unit tested, not hardware-retested after the refactor | Yes | Yes, expected compatible |
| Marstek Venus E hardware v3 | `MST_VNSE3_*` | Expected compatible; regression/unit tested, not hardware-validated in this fork | Yes | Yes, expected compatible |
| Marstek Jupiter-C Plus | `MST_JPLS_*` | Tested on real hardware | Yes | No, read-only |

For Venus, **supported** means that the implementation and automated compatibility tests are present. It does not currently mean that this fork has been verified on a physical Venus system. Reports from Venus users are especially useful during the release-candidate phase.

Jupiter-C Plus expansion batteries are represented as child devices using their physical pack position as the stable identifier. Only populated battery positions are exposed.

## Features

- Multiple Marstek systems can be added as independent Home Assistant devices.
- Local BLE operation without a Marstek cloud dependency.
- ESPHome Bluetooth Proxy support.
- Configurable fast and medium polling intervals.
- Product-specific packet parsing and polling schedules.
- Battery, inverter/grid, PV, energy, temperature, firmware, and diagnostic telemetry where supported by the selected product.
- Home Assistant child devices for Jupiter-C Plus base/expansion battery packs.
- The original Venus monitoring and control surfaces are retained by the implementation and covered by compatibility tests, but have not yet been revalidated on physical Venus hardware after the multi-product refactor.

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

The current implementation is intended to preserve the original integration's Venus monitoring and write/control behavior. Automated compatibility and regression tests cover the migrated Venus runtime, parsing, entity generation, polling schedule, and legacy control platforms, but no physical Venus device was available for validation of this release candidate.

Implemented Venus controls currently include:

- `Output 1 Control`, `EPS Mode`, `AC Input`, `Generator`, and `Buzzer` switches;
- an `Operating Mode` select for **Self-Consumption** and **Manual**;
- `Charge Mode` and `CT Polling Rate` selects; and
- reboot plus fixed power-mode/power-limit buttons.

The current code does **not** expose AI Optimization as a BLE control. Any Venus behavior that depends on device or firmware details should therefore be considered expected compatibility until it has been confirmed on real hardware.

### Jupiter-C Plus

Jupiter support is intentionally **read-only** in the first multi-product release. The integration exposes modeled telemetry including:

- battery state of charge, voltage, current, power, stored energy, temperatures, limits, and diagnostic state;
- AC/grid output power, grid qualification, grid voltage/frequency, inverter state/errors, and temperatures;
- four PV input channels with connection/activity state and available voltage/current/power telemetry;
- PV-generation and discharge-energy counters;
- MPPT state and diagnostics;
- base battery and installed expansion-battery child devices; and
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

Venus keeps its own product-specific polling schedule. Automated tests verify that the refactored schedule matches the intended Venus behavior, but that schedule has not yet been revalidated against Venus hardware in this fork.

## BLE proxy setup

To extend Bluetooth range, configure an [ESPHome Bluetooth Proxy](https://esphome.io/components/bluetooth_proxy/). One proxy can serve multiple Marstek devices.

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

Tests marked `known_issue` are used as an unresolved-defect inventory. At the time of this release preparation the inventory is empty; `just test-known-issues` also treats an empty selection as success.

See [`tests/README.md`](tests/README.md), [`docs/RELEASE.md`](docs/RELEASE.md), and the `justfile` for the available test and release commands.

## Reporting problems

Please include the Home Assistant version, integration version/commit, Marstek product, and relevant sanitized logs when opening an issue. For Venus reports, also include the hardware revision/prefix and firmware version where possible because the current multi-product branch has not been physically validated on Venus hardware.

Do not publish device identifiers, MAC addresses, Wi-Fi names, account/cloud identifiers, or complete private diagnostic captures.

## Attribution

Based on reverse-engineering work from:

- [marstek-venus-monitor](https://github.com/rweijnen/marstek-venus-monitor) by @rweijnen
- [esphome-b2500](https://github.com/tomquist/esphome-b2500) by @tomquist
- [hm2500pub](https://github.com/noone2k/hm2500pub) by @noone2k

## License

MIT

## Disclaimer

This is unofficial software developed through reverse engineering and is not affiliated with Marstek Energy. Use it at your own risk.
