"""Sensor platform for Household Chores."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN
from .coordinator import HouseholdChoresCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Household Chores sensors from a config entry."""
    coordinator: HouseholdChoresCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NextChoreSensor(entry, coordinator)])


class NextChoreSensor(CoordinatorEntity[HouseholdChoresCoordinator], SensorEntity):
    """Sensor showing the next scheduled chore assignment."""

    _attr_has_entity_name = True
    _attr_name = "Next chore"
    _attr_icon = "mdi:broom"
    _attr_translation_key = "next_chore"

    def __init__(self, entry: ConfigEntry, coordinator: HouseholdChoresCoordinator) -> None:
        super().__init__(coordinator)
        configured_name = entry.options.get(CONF_NAME, entry.data.get(CONF_NAME, DEFAULT_NAME))
        self._attr_unique_id = f"{entry.entry_id}_next_chore"
        self._attr_extra_state_attributes = {"household": configured_name}

    @property
    def native_value(self) -> str | None:
        """Return summary for the next upcoming chore."""
        now = datetime.now().astimezone()
        for event in self.coordinator.data:
            if event.end >= now:
                return event.summary
        return None

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return details for the next upcoming chore."""
        now = datetime.now().astimezone()
        for event in self.coordinator.data:
            if event.end >= now:
                return {
                    "chore": event.chore,
                    "member": event.member,
                    "start": event.start.isoformat(),
                    "end": event.end.isoformat(),
                }
        return None
