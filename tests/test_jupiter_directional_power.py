"""Tests for Jupiter directional battery-power entities."""

from __future__ import annotations

import pytest

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfPower

from custom_components.marstek_ble.entity import EntityPlatform
from custom_components.marstek_ble.products.jupiter import JUPITER_PROFILE, JupiterData


def _power_entities(data: JupiterData):
    plan = JUPITER_PROFILE.build_entity_plan(data)
    return {
        entity.description.key: entity
        for entity in plan.entities
        if entity.platform is EntityPlatform.SENSOR
        and entity.description.key in {
            "battery_power",
            "battery_power_in",
            "battery_power_out",
        }
    }


def test_jupiter_directional_power_entity_contract() -> None:
    data = JupiterData()
    entities = _power_entities(data)

    assert set(entities) == {
        "battery_power",
        "battery_power_in",
        "battery_power_out",
    }
    assert entities["battery_power_in"].description.name == "Battery Power In"
    assert entities["battery_power_out"].description.name == "Battery Power Out"

    for entity in entities.values():
        assert entity.description.native_unit_of_measurement == UnitOfPower.WATT
        assert entity.description.device_class is SensorDeviceClass.POWER
        assert entity.description.state_class is SensorStateClass.MEASUREMENT
        assert entity.stale_paths == (
            ("battery", "voltage"),
            ("battery", "current"),
        )


def test_jupiter_directional_power_clamps_charge_and_discharge() -> None:
    data = JupiterData()
    entities = _power_entities(data)

    assert entities["battery_power"].value_from(data) is None
    assert entities["battery_power_in"].value_from(data) is None
    assert entities["battery_power_out"].value_from(data) is None

    data.battery.voltage = 50.0
    assert entities["battery_power_in"].value_from(data) is None
    assert entities["battery_power_out"].value_from(data) is None

    data.battery.current = 4.0
    assert entities["battery_power"].value_from(data) == pytest.approx(200.0)
    assert entities["battery_power_in"].value_from(data) == pytest.approx(200.0)
    assert entities["battery_power_out"].value_from(data) == 0

    data.battery.current = -3.0
    assert entities["battery_power"].value_from(data) == pytest.approx(-150.0)
    assert entities["battery_power_in"].value_from(data) == 0
    assert entities["battery_power_out"].value_from(data) == pytest.approx(150.0)

    data.battery.current = 0.0
    assert entities["battery_power"].value_from(data) == 0
    assert entities["battery_power_in"].value_from(data) == 0
    assert entities["battery_power_out"].value_from(data) == 0
