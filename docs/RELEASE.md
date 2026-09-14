# Release process

This repository currently targets `0.5.0-rc1` as the first multi-product release candidate.

The release candidate includes:

- the migrated Venus E monitoring and existing write/control implementation, covered by regression/unit tests but not revalidated on physical Venus hardware after the multi-product refactor;
- Jupiter-C Plus read-only monitoring, exercised against real hardware;
- Jupiter base/expansion battery child devices;
- product-specific polling and parsing; and
- explicit Jupiter supported-command restrictions that exclude unresolved commands from polling.

## 1. Local release gate

Run these checks from the exact commit intended for release:

```bash
git status --short
git rev-parse HEAD
just install-quality
just compile
just test
just coverage
tox
```

When Python 3.14 and the genuine Home Assistant test dependencies are available, also run:

```bash
just install-ha
just test-ha
```

Run the unresolved-defect inventory separately:

```bash
just test-known-issues
```

Tests marked `known_issue` are tracked defects rather than part of the passing baseline. An empty known-issue inventory is valid; the `just` recipe treats pytest's no-tests-selected result as success. At the time of this release preparation there are no tests carrying the marker.

## 2. Physical-device release gate

### Jupiter-C Plus

Verify at minimum:

- device discovery and configuration succeed;
- no Jupiter `button`, `switch`, or `select` entities are created;
- battery SOC, voltage/current/power, AC output, PV inputs, grid values, temperatures, and energy counters remain plausible;
- base/expansion battery child-device identities remain stable after an integration reload and Home Assistant restart;
- no duplicate entities/devices are created;
- the integration reconnects after temporary BLE/device unavailability;
- Home Assistant logs contain no parser, unsupported-command, or repeated reconnect errors; and
- the Marstek surplus-feed-in setting remains unchanged while Home Assistant polls the device, tested once from both OFF and ON where practical.

The `Surplus Feed-In Active Unverified` entity is diagnostic only and must not be treated as a confirmed representation of the user-facing setting.

### Venus E

No physical Venus device is available for the current release preparation. The first RC therefore relies on automated compatibility/regression tests for the migrated Venus runtime and clearly documents that Venus has not been hardware-revalidated after the multi-product refactor.

Lack of local Venus hardware does not by itself block `0.5.0-rc1` if the complete automated release gate passes. During the RC period, Venus reports should receive priority. If physical Venus hardware becomes available, verify at minimum:

- discovery/config-entry loading;
- core battery telemetry;
- sensor/binary-sensor availability;
- the existing button/switch/select controls;
- integration reload; and
- Home Assistant restart.

Any confirmed Venus regression blocks promotion of the affected code to the stable release until it is understood and fixed.

## 3. Release preparation

Before merging the candidate to the default branch:

1. Confirm the local release gate and available physical-device checks above.
2. Confirm `README.md`, `hacs.json`, and `manifest.json` refer to this repository where appropriate.
3. Confirm the README clearly distinguishes hardware-tested Jupiter support from unit-test-only Venus compatibility.
4. Confirm the manifest still contains a valid semantic version. The release workflow will replace it with the requested release version.
5. Confirm Jupiter remains documented as read-only.
6. Confirm unresolved Jupiter commands remain absent from its poll schedule.
7. Review the final diff against `main` for private diagnostic material or identifiers.

## 4. Merge and version

Merge the validated candidate to `main` without changing the tested behavior.

The existing manual release workflow operates on the repository default branch. For the first release candidate, supply:

```text
0.5.0-rc1
```

The workflow updates `custom_components/marstek_ble/manifest.json`, creates commit `chore: release v0.5.0-rc1`, tags `v0.5.0-rc1`, pushes the default branch/tag, and creates a draft GitHub pre-release.

Do not run that workflow until the validated candidate has been merged to `main`.

## 5. RC validation and stable release

Install `0.5.0-rc1` through the same mechanism users will use, preferably HACS, and repeat the Jupiter smoke tests. Collect Venus feedback and perform a Venus hardware smoke test if suitable hardware becomes available.

A real Venus validation before the stable release is strongly preferred. If no Venus hardware becomes available, the stable release must continue to state clearly that Venus compatibility after the multi-product refactor is supported by automated regression tests rather than physical-device validation.

If no release-blocking regressions appear during the RC period, prepare `0.5.0` from the same code line plus explicitly reviewed RC fixes. Re-run the complete release gate before tagging the stable version.
