"""Tests for Jupiter output-energy counter semantics."""

from __future__ import annotations

import struct

import pytest

from custom_components.marstek_ble.entity import EntityPlatform
from custom_components.marstek_ble.products import JUPITER_RUNTIME
from custom_components.marstek_ble.products.jupiter import (
    JUPITER_PROFILE,
    JupiterData,
    JupiterPackets,
)
from custom_components.marstek_ble.schema import parse_into


def test_jupiter_output_energy_entities_use_output_keys_and_names() -> None:
    data = JupiterData()
    plan = JUPITER_PROFILE.build_entity_plan(data)
    sensors = {
        entity.unique_key: entity
        for entity in plan.entities
        if entity.platform is EntityPlatform.SENSOR
    }

    expected = {
        "daily_output_energy": (
            "Daily Output Energy",
            ("energy", "daily_output_energy"),
        ),
        "monthly_output_energy": (
            "Monthly Output Energy",
            ("energy", "monthly_output_energy"),
        ),
        "local_total_output_energy": (
            "Local Total Output Energy",
            ("energy", "local_total_output_energy"),
        ),
    }

    for unique_key, (name, path) in expected.items():
        entity = sensors[unique_key]
        assert entity.description.name == name
        assert entity.path == path

    assert "daily_discharge_energy" not in sensors
    assert "monthly_discharge_energy" not in sensors
    assert "local_total_discharge_energy" not in sensors


def test_jupiter_output_energy_counters_parse_from_runtime_and_detail_packets() -> None:
    data = JupiterData()

    runtime = bytearray(74)
    runtime[0x27:0x2B] = struct.pack("<I", 1234)
    runtime[0x2B:0x2F] = struct.pack("<I", 5678)
    parse_into(runtime, JupiterPackets.RUNTIME_INFORMATION, data)

    assert data.energy.daily_output_energy == pytest.approx(12.34)
    assert data.energy.monthly_output_energy == pytest.approx(56.78)

    detail = bytearray(165)
    detail[0x14:0x18] = struct.pack("<I", 2345)
    detail[0x18:0x1C] = struct.pack("<I", 6789)
    detail[0x1C:0x20] = struct.pack("<I", 3456)
    parse_into(detail, JupiterPackets.DETAILED_TELEMETRY, data)

    assert data.energy.daily_output_energy == pytest.approx(23.45)
    assert data.energy.local_total_output_energy == pytest.approx(67.89)
    assert data.energy.monthly_output_energy == pytest.approx(34.56)


def test_jupiter_legacy_discharge_accessors_follow_output_energy_fields() -> None:
    data = JUPITER_RUNTIME.create_data()
    detail = bytearray(165)
    detail[0x14:0x18] = struct.pack("<I", 111)
    detail[0x18:0x1C] = struct.pack("<I", 222)
    detail[0x1C:0x20] = struct.pack("<I", 333)

    assert JUPITER_RUNTIME.parse_payload(0x14, bytes(detail), data)

    assert data.energy.daily_discharge_energy == pytest.approx(1.11)
    assert data.energy.local_total_discharge_energy == pytest.approx(2.22)
    assert data.energy.monthly_discharge_energy == pytest.approx(3.33)
    assert data.daily_energy_discharged == pytest.approx(1.11)
    assert data.total_energy_discharged == pytest.approx(2.22)
    assert data.monthly_energy_discharged == pytest.approx(3.33)
