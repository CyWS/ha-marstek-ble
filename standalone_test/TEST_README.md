# Marstek BLE Proxy Verification Script

This directory contains the ESPHome-proxy based verification script in `marstek_basic_info.py`. Unlike the previous macOS/Bleak harness, this tool talks to the same ESPHome Bluetooth proxy that Home Assistant uses so you can quickly confirm whether Home Assistant can receive connectable advertisements and basic telemetry.

## Requirements

- Python 3.11+ (3.10 also works, but matching your Home Assistant environment is preferable)
- Access to the ESPHome Bluetooth proxy that is forwarding your Marstek devices
- The proxy's API noise key (the same base64 value configured in ESPHome)

Install the dependency from this directory:

```bash
cd standalone_test
python3 -m pip install -r requirements.txt
```

> Tip: export `PIP_REQUIRE_VIRTUALENV=true` and create a venv if you do not want global installs: `python3 -m venv .venv && source .venv/bin/activate`.

## Basic usage

```bash
python3 marstek_basic_info.py \
  --host 192.0.2.10 \
  --noise-psk "base64-noise-key" \
  --target MST_EXAMPLE
```

`192.0.2.10` and `MST_EXAMPLE` are documentation-only placeholders. Replace them with your own proxy address and advertised device name.

The script will:

1. Connect to the proxy via `aioesphomeapi`.
2. Request active BLE scanning (or passive if you set `--scan-mode passive`).
3. Locate targets either by exact advertisement name (`--target`) or by `--name-prefix`.
4. Establish BLE tunnels through the proxy and send the Marstek/HM `0x04` Device Info command.
5. Print a per-device summary plus a table that mirrors the basic information Home Assistant should receive.

## Discovering devices

- Provide `--target` multiple times to query specific names or MAC addresses.
- If you omit `--target`, the script uses `--name-prefix` (default `MST_`) and reads up to `--max-devices` advertisements before attempting connections.
- Set `--case-sensitive-prefix` if exact advertisement-name casing matters.

You can also inspect the proxy's advertisements for troubleshooting:

```bash
python3 marstek_basic_info.py --log-advertisements 5 --log-level DEBUG
```

## Timeouts and retries

- `--scan-timeout` controls how long the script waits to resolve the requested devices.
- `--connect-timeout` is applied to each BLE tunnel establishment.
- `--command-timeout` bounds the wait for the `0x04` reply once connected.

Raising the connect timeout can help investigate Home Assistant messages such as `Failed to establish an encrypted connection to the Bluetooth proxy`.

## Proxy configuration notes

- The noise PSK can be pulled from ESPHome logs or `secrets.yaml`; alternatively set the `MARSTEK_PROXY_NOISE_PSK` environment variable and omit `--noise-psk`.
- Use `--port` if your proxy does not listen on the default 6053.
- `--scan-mode passive` mirrors Home Assistant's default behavior when you want to reproduce it more closely.

Never commit a real proxy host, noise key, device identifier, MAC address, Wi-Fi name, or complete private diagnostic capture to this repository.

## Output interpretation

At the end of a run you will see:

- a device-by-device block containing the decoded key/value pairs returned by command `0x04`;
- a consolidated battery/device summary table containing fields such as name, MAC, RSSI, state, and firmware; and
- failures reported inline with status information such as timeouts, API connection problems, or BLE tunnels that never formed.

If the script itself fails to locate or connect to a device, that is useful evidence when diagnosing why Home Assistant cannot communicate through the same proxy. It is a troubleshooting tool, not a substitute for the integration's automated test suite or product-specific hardware validation.

## Advanced debugging flags

- `--log-scanner-state` prints scanner state changes from the proxy so you can confirm whether active scans were accepted.
- `--raw-advertisements` subscribes to raw BLE advertisements instead of ESPHome's decoded view; combine with `--log-advertisements -1` to capture everything the proxy sees.
- `--log-level DEBUG` enables verbose logging from `aioesphomeapi` plus this script's tracing of connection attempts and frame parsing.
