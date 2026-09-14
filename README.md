# Marstek BLE Integration for Home Assistant

Home Assistant integration for supported Marstek energy-storage systems over Bluetooth Low Energy (BLE).

This repository is preparing its first multi-product release. Venus E support includes monitoring and the existing write/control features. Jupiter-C Plus support is currently read-only while command semantics are still being validated.

## Supported devices

| Product | BLE prefix | Status | Monitoring | Controls |
| ------- | ---------- | ------ | ---------- | -------- |
| Marstek Venus E hardware v2 | `MST_ACCP_*` | Tested | Yes | Yes |
| Marstek Venus E hardware v3 | `MST_VNSE3_*` | Untested | Yes | Yes |
| Marstek Jupiter-C Plus | `MST_JPLS_*` | Tested | Yes | No, read-only |

Jupiter-C Plus expansion batteries are represented as child devices using their physical pack position as the stable identifier. Only populated battery positions are exposed.

## Features

- Multiple Marstek systems can be added as independent Home Assistant devices.
- Local BLE operation without a Marstek cloud dependency.
- ESPHome Bluetooth Proxy support.
- Configurable fast and medium polling intervals.
- Product-specific packet parsing and polling schedules.
- Battery, inverter/grid, PV, energy, temperature, firmware, and diagnostic telemetry where supported by the selected product.
- Home Assistant child devices for Jupiter-C Plus base/expansion battery packs.
- Existing Venus E output, mode, and configuration controls.

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

Venus E retains the integration's existing monitoring and write/control functionality. Depending on the device/firmware this includes battery telemetry, energy counters, output control, EPS-related controls, power limits, manual/self-consumption modes, and adaptive/AI-related controls.

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

Some Jupiter diagnostic entities intentionally include words such as **Unverified**. These represent useful reverse-engineering observations, not vendor-confirmed semantics.

## Polling

The integration has two configurable polling tiers:

- **Fast**: default 1 second, configurable from 1–60 seconds.
- **Medium**: default 60 seconds, configurable from 5–300 seconds and never faster than the fast interval.

Actual commands are product-specific. For Jupiter-C Plus the current read-only schedule is:

- fast: `0x03`, `0x14`;
- medium: `0x0D`, `0x08`, `0x04`, `0x13`.

Jupiter commands `0x1A`, `0x1C`, `0x21`, `0x22`, and `0x24` are not polled because their semantics are absent or unresolved.

## BLE proxy setup

To extend Bluetooth range, configure an [ESPHome Bluetooth Proxy](https://esphome.io/components/bluetooth_proxy/). One proxy can serve multiple Marstek devices.

## Development and testing

The repository contains an isolated test suite that does not require a real Home Assistant instance, network access, Bluetooth hardware, an ESPHome proxy, or a physical Marstek device.

Typical local checks are:

```bash
just install-quality
just check
just coverage
```

The full issue-inventory suite also includes tests marked `known_issue` and may intentionally fail for unresolved defects:

```bash
just test-known-issues
```

A separate genuine Home Assistant test harness is available for integration lifecycle/config-flow testing. See [`tests/README.md`](tests/README.md) and the `justfile` for the available test commands.

## Reporting problems

Please include the Home Assistant version, integration version/commit, Marstek product, and relevant sanitized logs when opening an issue. Do not publish device identifiers, MAC addresses, Wi-Fi names, account/cloud identifiers, or complete private diagnostic captures.

## Attribution

Based on reverse-engineering work from:

- [marstek-venus-monitor](https://github.com/rweijnen/marstek-venus-monitor) by @rweijnen
- [esphome-b2500](https://github.com/tomquist/esphome-b2500) by @tomquist
- [hm2500pub](https://github.com/noone2k/hm2500pub) by @noone2k

## License

MIT

## Disclaimer

This is unofficial software developed through reverse engineering and is not affiliated with Marstek Energy. Use it at your own risk.
