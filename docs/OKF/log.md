# Marstek BLE OKF update log

## 2026-09-19

- **Jupiter stored battery energy source**: `stored_battery_energy` was fed by both `0x03` offset `0x13` (10 Wh units) and `0x14` offset `0x77` (whole watt-hours). Both commands sit in the one-second fast poll and the field model has no source precedence, so the canonical value alternated between the two resolutions on every poll. Only the higher-resolution `0x14` source writes it now; the `0x03` mapping remains documented as decoded-but-redundant.

## 2026-09-18

- **Jupiter `0x14` payload length and BMS firmware version width**: Corrected the declared payload length for `0x14` `jupiter_detailed_telemetry` from an unconditional 166 bytes to 165 bytes, confirmed on a JPLS-8H, firmware V133, no expansion batteries, across two independent captures plus a 20-request repeatability burst. Root cause: `0x64` BMS firmware version was declared as a 2-byte `u16` but is a constant single byte on this device; the strict exact-length packet schema discarded every `0x14` packet outright, leaving every Jupiter entity `unknown`. Every field from the old `0x65` onward, including the repeated battery-pack records and `stored_battery_energy`, shifts by −1 and now decodes to independently plausible values (matching an external field map, the device's own cloud-reported values, a base-only pack count of 1, and previously unexamined per-cell voltages). Whether other Jupiter-C Plus hardware/firmware combinations genuinely use a distinct 166-byte layout with a real 2-byte firmware version remains open.
- **Jupiter `0x03` payload length**: A second confirmed Jupiter-C Plus unit consistently sends 67-byte `0x03` responses instead of the previously assumed fixed 74 bytes. Every field mapped through offset `0x3C` (inclusive) is unchanged; only the unresolved trailing bytes are shorter (6 instead of 13). The response-length check was relaxed to accept 61–74 bytes so the shorter, otherwise fully decodable frame is no longer rejected outright.

## 2026-09-14

- **Jupiter output-energy semantics**: Renamed the Jupiter counters previously exposed as daily/monthly/local discharge energy to `Daily Output Energy`, `Monthly Output Energy`, and `Local Total Output Energy`. Observed behavior indicates these counters track energy delivered through the device output path regardless of whether PV or battery supplied it. Battery-side cumulative charge/discharge energy remains intentionally delegated to Home Assistant using the directional battery-power sensors.
- **Jupiter directional battery power**: Added `Battery Power In` and `Battery Power Out` as non-negative derived sensors from the existing signed battery voltage/current power calculation. Positive signed power is charging; negative signed power is discharging. The directional sensors add no new protocol interpretation and are intended for Home Assistant Energy Dashboard or Integral-helper use.
- **Release preparation**: Reconciled the physically tested Jupiter diagnostic branch with the supported-command branch without reintroducing unresolved Jupiter polling commands.
- **Jupiter diagnostics**: Restored the tested diagnostic-only MPPT/PV state observations, tentative base/PE voltages, diagnostic classifications, and compact event-history entities while retaining the newer grid-validity, inverter-error, and 16-bit event-code interpretations.
- **Polling safety**: Confirmed Jupiter remains read-only and limited to the explicit supported-command set plus the model-identification exception. Commands `0x1A`, `0x1C`, `0x21`, `0x22`, and `0x24` remain unpolled.
- **Operational status caution**: Retained the bit-1 diagnostic observation at runtime offset `0x3C` but explicitly documented that it is not a confirmed representation of the user-facing surplus-feed-in setting.
- **Release documentation**: Updated repository metadata, HACS installation instructions, supported-device documentation, and isolated-test documentation for the first multi-product release candidate.
- **Hardware-validation boundary**: Clarified that Jupiter-C Plus has real-device validation on the current multi-product path, while Venus compatibility after the refactor is currently supported by regression/unit tests rather than physical Venus hardware validation.
- **Venus controls**: Corrected release-facing documentation to match the current implementation: Self-Consumption/Manual are options of the `Operating Mode` select, and AI Optimization is not exposed as a BLE control.
- **Protocol documentation audit**: Corrected the Jupiter protocol index to remove `0x21`, `0x22`, and `0x24` from the live polling schedule, documented the distinction between retained unresolved schemas and commands that are actually sent, and updated the Venus framing reference for current declared-length validation and product-runtime dispatch.
- **Testing documentation audit**: Removed stale references to Jupiter as not runtime-enabled and documented that the current `known_issue` inventory is empty while preserving the marker policy for future defects.
- **AI disclosure**: Added a prominent README disclosure describing how LLM assistance was used for code analysis, reverse-engineering support, implementation, tests, failure review, and documentation, while distinguishing AI assistance from human review and hardware validation.

## 2026-08-13

- **Supported polling commands**: Added explicit per-product supported-command sets and runtime validation. The product-identification request `0x04` remains available outside those sets. Jupiter no longer polls unresolved commands `0x21`, `0x22`, or `0x24`; its existing exclusions for `0x1A` and `0x1C` remain.

## 2026-08-10

- **MPPT state flags**: Refined Jupiter `0x14` offset `0x20` from a mostly opaque raw word into a partially understood bitfield. Bit 2 (`0x0004`) is strongly supported as MPPT controller initialized/ready; bits 4–7 (`0x0010`–`0x0080`) remain confirmed as PV inputs 1–4 active. Bit 0 (`0x0001`) is tentatively associated with an opposing MPPT stopped/parked/disabled state after appearing alone during the full-battery PV shutdown sequence. Captures also showed `0x0014` during restart with only PV1 active and `0x0004` with the controller ready but no active PV input. Bit 0 and bit 2 were not observed set simultaneously. Bits 1, 3, and 8–15 remain unresolved, while the integration continues to preserve the complete raw 16-bit word.
- **Operational status**: Refined the tentative interpretation of Jupiter `0x03` offset `0x3C`. Bit 1 (`0x02`) correlates with full-battery/excess-energy handling but is not a generic surplus-feed-in, grid-export, inverter-active, or battery-discharge flag. A scheduled-export counterexample showed the bit clear while the inverter was exporting substantially from the battery. Its exact trigger and semantics remain unresolved; `excess-energy/full-battery mode` is only a working description. Bit 0 remains unresolved.
- **Grid validity**: Reclassified Jupiter `0x03` offset `0x0E` from `AC Output Active` to `Grid Connection Valid`. Controlled zero-output, grid-loss, and grid-return behavior shows that it represents a qualified grid connection rather than output power or raw voltage presence.
- **Inverter errors**: Identified Jupiter `0x03` offsets `0x23–0x24` as the same little-endian inverter error code exposed at `0x14` offset `0x02`. A controlled grid disconnect produced transient `0x040A` followed by persistent `0x0426`; the numeric mapping is confirmed while the tentative semantic labels remain `overfrequency` and `island / anti-islanding detection` respectively.
- **Event history**: Reclassified the final two bytes of each Jupiter `0x13` record from separate event-value/state bytes to one `u16 LE` event/error identifier. The persistent grid-loss inverter error was written unchanged into a new event record, providing a controlled correlation.
- **Inverter state**: Refined `0x14` inverter state flags as grid/inverter qualification state. They can remain clear after voltage and frequency measurements return, so they are not direct output-power or voltage-presence flags.
- **Entities**: Replaced the misleading `AC Output Active` binary entity with `Grid Connection Valid`; compatibility access to the previous field name remains internal for transition callers.
- **Tests**: Added regression coverage for grid validity, the runtime-summary inverter-error mirror, the 16-bit event-code interpretation, and the new binary-sensor contract. Test execution was explicitly delegated to the repository owner for this change set.
- **Battery state**: Reclassified Jupiter `0x03` offset `0x12` from a boolean charging flag to a three-state field: `0` idle, `1` charging, and `2` discharging. Unknown raw values remain unresolved.
- **Entities**: Replaced the misleading `Battery Charging Active` binary entity with a `Battery State` sensor and removed the redundant battery-power-derived charging binary sensor. The signed `Battery Power` sensor remains available.
- **Grid telemetry**: Withdrew the `Grid Current` entity because controlled Jupiter behavior contradicted the previous interpretation of `0x14` offset `0x08`; the field remains available internally for further protocol investigation.
- **Display metadata**: Set grid frequency to two suggested decimal places and renamed the identity sensor to `Bluetooth MAC Address`.
- **Tests**: Added regression coverage for all verified battery-state values, unknown-state handling, removed charging binaries, grid-current suppression, frequency precision, and Bluetooth MAC naming.

## 2026-08-09

- **Jupiter runtime**: Enabled Jupiter-C Plus as the `jupiter_c_plus` runtime product and added `MST_JPLS_*` Bluetooth discovery.
- **Polling**: Added Jupiter-owned fast polling for `0x03`/`0x14` and medium polling for the observed `0x0D`, `0x08`, `0x22`, `0x21`, `0x24`, `0x04`, and `0x13` responses. Jupiter `0x1A` and `0x1C` remain unpolled because no response structure is retained in the sanitized source.
- **Parsing**: Connected the declarative Jupiter binary schemas to the live protocol and added product-local parsers for `0x04` device information and `0x08` Wi-Fi SSID.
- **Entities**: Connected sensor and binary-sensor platforms to `ProductProfile` plans. Jupiter now exposes its modeled PV, inverter, energy, BMS, and derived read-only entities without inheriting Venus field definitions.
- **Battery topology**: Populated base/expansion battery records create stable positional child devices. New positions are added on later count increases; positions that disappear become unavailable without renumbering existing children.
- **Controls**: Jupiter remains read-only. Venus button, switch, and select command semantics are not exposed for Jupiter.
- **Compatibility**: Retained tracked Jupiter compatibility aliases and legacy entity constructors for transition/regression callers; canonical product bindings are now the live sensor path.
- **Tests**: Added Jupiter runtime, dynamic entity-manager, and live declarative entity tests. Updated the existing runtime-registry test to verify that every declared discovery prefix resolves to an enabled runtime, including Jupiter-C Plus.

## 2026-08-08

- **Venus runtime migration**: Connected the Venus declarative packet/dataclass model to the live integration through a generic product runtime and product-aware coordinator adapter.
- **Product selection**: Added explicit runtime registration and persisted `product_id` selection for new config entries; legacy entries without a product ID retain the Venus fallback, while unknown persisted products are rejected.
- **Polling**: Moved the Venus fast and medium command schedules out of the generic coordinator and into `VENUS_RUNTIME`.
- **Parsing**: Fixed-layout Venus responses now use declarative field sources; Venus-specific text responses remain product-local custom parsers.
- **State model**: The live Venus coordinator now stores nested `VenusData`. Temporary flat read/metadata aliases preserve compatibility during platform migration.
- **Tests**: Added isolated tests for runtime registration, parsing, field metadata, poll dispatch, product selection, compatibility behavior, and failure/boundary cases.
- **Declarative coverage tests**: Added direct tests for schema validation and failure paths, entity-plan topology and presence logic, and the declarative Jupiter runtime-summary, detailed-telemetry, event-history, repeated battery-pack, expansion, and derived-entity behavior.
- **Coverage**: Coverage includes every Python source file under `custom_components/marstek_ble` and `standalone_test` with no file-level exceptions.
- **Testing policy**: Added a dedicated testing-and-coverage OKF concept and updated `Agents.md` to prohibit coverage omissions and use uncovered statements and branches as test-design input rather than exclusion criteria.

## 2026-08-05

- **Architecture**: Added branch-only declarative packet, dataclass, entity-description, product-profile, repeated-record, and child-device scaffolding.
- **Products**: Added declarative Venus and Jupiter-C Plus definitions without connecting them to the integration runtime.
- **Expansions**: Added fixed-limit Jupiter battery-pack records, setup-time child-device planning, slot-based identifiers, runtime presence checks, and expansion-increase records.
- **Jupiter protocol**: Added a sanitized structural field map and progressive OKF hierarchy for runtime, event history, detailed telemetry, unresolved responses, and battery expansions.
- **Privacy**: Prohibited committing raw captures, frames, payload hex, capture timestamps, identifiers, Wi-Fi names, observed values, counters, or event records.

## 2026-08-04

- **Update**: Added a progressive `protocol/venus/messages/` hierarchy with one focused concept for every BLE message sent or parsed by the integration.
- **Update**: Documented request and response fields by byte offset, including length, type, unit, and a name; added descriptions where names were insufficient and explicitly listed unknown/unused ranges.
- **Update**: Refactored the command reference into a compact inventory linking to the detailed message concepts.
- **Update**: Required aligned Markdown tables and byte-offset ordering in `Agents.md`.
- **Initialization**: Created the OKF v0.2 knowledge bundle from repository revision `59ea1c3f0e6f239cecbae7f9024e0dc48c328d89`.
- **Creation**: Added codebase, architecture, Venus BLE transport, and Venus command/payload references.
- **Scope**: Explicitly excluded Jupiter-C reverse-engineering material and any information not present in repository sources.
