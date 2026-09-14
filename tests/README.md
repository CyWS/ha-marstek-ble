# Isolated tests

The default test suite covers the runtime integration under `custom_components/marstek_ble/`, including the original Venus code and the integrated declarative multi-product model in `schema.py`, `entity.py`, `product_runtime.py`, `product_entity_platform.py`, and `products/`. It also covers the ESPHome proxy utility under `standalone_test/`.

The default environment supplies lightweight stubs for Home Assistant, BLE, and ESPHome API libraries. It requires no Home Assistant installation or instance, Bluetooth adapter, ESPHome proxy, network access, or Marstek device. All packet replay data is generated and contains no captured identifiers or telemetry.

These tests can provide strong regression coverage, but they are not a substitute for physical-device validation. In particular, the migrated Venus path is covered by automated compatibility tests but has not been revalidated on real Venus hardware for the current multi-product release candidate.

## Default suite

Install and run:

```bash
python -m pip install -r requirements-test.txt
pytest -m "not known_issue"
pytest -m "not known_issue" --cov --cov-report=term-missing
```

The default suite includes:

- example-based unit tests;
- deterministic property and malformed-input fuzz tests;
- asynchronous connection, command, cancellation, and response-order tests;
- product-profile, polling, parsing, entity-plan, and child-device tests;
- synthetic packet replay fixtures; and
- manifest, HACS, platform, translation-string, import-boundary, and packaging contracts.

Tests marked `known_issue` are ordinary failing tests, not skips or expected failures. The known-issue run therefore acts as an unresolved-defect inventory. The filtered baseline must pass and confirms that no unrelated regression was introduced.

At the time of the first multi-product release preparation, no tests carry the `known_issue` marker. An empty selection is valid; `just test-known-issues` treats pytest exit code 5 (`no tests collected/selected`) as success while preserving real test failures.

The `justfile` provides the preferred wrappers:

```bash
just check
just coverage
just test-known-issues
```

## Genuine Home Assistant harness

The separate `tests_ha/` suite runs against the real Home Assistant testing framework while still mocking Bluetooth and using an in-memory Home Assistant instance. It is kept outside `tests/` so the lightweight default suite never imports the real framework.

Use the configured Python version and run:

```bash
python -m pip install -r requirements-test-ha.txt
pytest -c pytest-ha.ini
```

The corresponding `just test-ha`/tox targets check the real flow manager, option flow, config-entry lifecycle, custom-integration loading behavior, and other integration-level contracts.

## Python compatibility

Run the passing isolated baseline on the configured Python matrix:

```bash
python -m pip install -r requirements-test-quality.txt
tox
```

Run the genuine Home Assistant suite through tox using the interpreter configured by `tox.ini`/`justfile`.

## Mutation testing

Mutation testing is intentionally separate because it is substantially slower than normal tests. Its configured source scope and exclusions are defined by the repository's mutation configuration; it uses the passing baseline rather than treating the known-defect inventory as a release gate.

```bash
python -m pip install -r requirements-test.txt -r requirements-test-quality.txt
pytest -m "not known_issue" --cov
mutmut run
mutmut browse
```

Run mutmut on a platform with process-fork support. Its results are a test-quality report, not a release gate with a predefined mutation-score requirement.
