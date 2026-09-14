"""Regression coverage for carried-forward Jupiter diagnostic observations."""

from __future__ import annotations

import struct

from homeassistant.helpers.entity import EntityCategory

from custom_components.marstek_ble.entity import EntityPlatform
from custom_components.marstek_ble.products.jupiter import JUPITER_PROFILE, JupiterData, JupiterPackets
from custom_components.marstek_ble.schema import parse_into


def test_interpreted_status_bits_are_binary_entities() -> None:
    data = JupiterData()
    runtime_payload = bytearray(74)
    runtime_payload[0x3C] = 0b00000010
    detail_payload = bytearray(166)
    detail_payload[0x20:0x22] = struct.pack("<H", 0b11110100)

    parse_into(runtime_payload, JupiterPackets.RUNTIME_INFORMATION, data)
    parse_into(detail_payload, JupiterPackets.DETAILED_TELEMETRY, data)

    assert data.runtime.surplus_feed_in_active is True
    assert data.mppt.controller_ready is True
    assert data.mppt.pv_input_1_active is True
    assert data.mppt.pv_input_2_active is True
    assert data.mppt.pv_input_3_active is True
    assert data.mppt.pv_input_4_active is True

    entities = {entity.unique_key: entity for entity in JUPITER_PROFILE.build_entity_plan(data).entities}
    expected = {
        "surplus_feed_in_active": "Surplus Feed-In Active Unverified",
        "mppt_controller_ready": "MPPT Controller Ready Unverified",
        "pv_input_1_active": "PV Input 1 Active",
        "pv_input_2_active": "PV Input 2 Active",
        "pv_input_3_active": "PV Input 3 Active",
        "pv_input_4_active": "PV Input 4 Active",
    }
    for key, name in expected.items():
        entity = entities[key]
        assert entity.platform is EntityPlatform.BINARY_SENSOR
        assert entity.description.name == name
        assert entity.value_from(data) is True


def test_interpreted_status_bits_clear_independently() -> None:
    data = JupiterData()
    runtime_payload = bytearray(74)
    detail_payload = bytearray(166)
    detail_payload[0x20:0x22] = struct.pack("<H", 0b01010000)

    parse_into(runtime_payload, JupiterPackets.RUNTIME_INFORMATION, data)
    parse_into(detail_payload, JupiterPackets.DETAILED_TELEMETRY, data)

    assert data.runtime.surplus_feed_in_active is False
    assert data.mppt.controller_ready is False
    assert data.mppt.pv_input_1_active is True
    assert data.mppt.pv_input_2_active is False
    assert data.mppt.pv_input_3_active is True
    assert data.mppt.pv_input_4_active is False


def test_event_history_exposes_compact_record_and_preserves_event_code() -> None:
    data = JupiterData()
    payload = bytearray(160)
    payload[0:8] = struct.pack("<HBBBBBB", 2026, 8, 10, 14, 5, 0x12, 0xA4)
    parse_into(payload, JupiterPackets.EVENT_HISTORY, data)

    entities = {entity.unique_key: entity for entity in JUPITER_PROFILE.build_entity_plan(data).entities}
    for index in range(20):
        summary = entities[f"events_{index}_summary"]
        assert summary.description.entity_category is EntityCategory.DIAGNOSTIC
        assert summary.description.name == f"Event {index + 1} Record"
        for key in ("year", "month", "day", "hour", "minute", "event_code", "event_value", "event_state"):
            assert f"events_{index}_{key}" not in entities

    assert entities["events_0_summary"].value_from(data) == "2026-08-10 14:05 | 0x12 0xA4"
    assert data.events[0].event_code == 0xA412
    assert data.events[0].event_value == 0x12
    assert data.events[0].event_state == 0xA4


def test_tentative_base_and_pe_voltages_are_diagnostic_entities() -> None:
    data = JupiterData()
    payload = bytearray(166)
    payload[0x54:0x56] = struct.pack("<H", 523)
    payload[0x56:0x58] = struct.pack("<H", 17)
    parse_into(payload, JupiterPackets.DETAILED_TELEMETRY, data)

    assert data.battery.base_voltage == 52.3
    assert data.battery.pe_voltage == 1.7
    entities = {entity.unique_key: entity for entity in JUPITER_PROFILE.build_entity_plan(data).entities}
    assert entities["base_voltage"].description.entity_category is EntityCategory.DIAGNOSTIC
    assert entities["pe_voltage"].description.entity_category is EntityCategory.DIAGNOSTIC


def test_carried_forward_values_remain_diagnostic() -> None:
    data = JupiterData()
    data.battery.pack_count = 1
    entities = {entity.unique_key: entity for entity in JUPITER_PROFILE.build_entity_plan(data).entities}
    for key in (
        "daily_pv_generation",
        "monthly_pv_generation",
        "grid_voltage",
        "inverter_temperature",
        "mppt_temperature",
        "battery_soh",
        "battery_temperature",
        "battery_pack_0_highest_cell_voltage",
        "battery_pack_0_lowest_cell_voltage",
    ):
        assert entities[key].description.entity_category is EntityCategory.DIAGNOSTIC


def test_unresolved_raw_status_fields_remain_unexposed() -> None:
    keys = {entity.description.key for entity in JUPITER_PROFILE.build_entity_plan(JupiterData()).entities}
    assert "grid_current" not in keys
    assert "status_21" not in keys
    assert "status_22" not in keys
    assert "status_24" not in keys
