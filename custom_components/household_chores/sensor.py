"""Sensor platform for Household Chores."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN, SIGNAL_BOARD_UPDATED
from .coordinator import HouseholdChoresCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Household Chores sensors from a config entry."""
    coordinator: HouseholdChoresCoordinator = hass.data[DOMAIN][entry.entry_id]
    board_store = hass.data[DOMAIN]["boards"][entry.entry_id]
    async_add_entities(
        [
            NextChoreSensor(entry, coordinator),
            BoardStateSensor(entry, board_store),
        ]
    )


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


class BoardStateSensor(SensorEntity):
    """Sensor exposing board data for fallback UI loading."""

    _attr_has_entity_name = True
    _attr_name = "Board state"
    _attr_icon = "mdi:view-kanban"

    def __init__(self, entry: ConfigEntry, board_store: Any) -> None:
        self._entry = entry
        self._board_store = board_store
        self._attr_unique_id = f"{entry.entry_id}_board_state"
        self._unsub_dispatcher = None

    async def async_added_to_hass(self) -> None:
        """Subscribe to board update events."""
        self._unsub_dispatcher = async_dispatcher_connect(
            self.hass,
            f"{SIGNAL_BOARD_UPDATED}_{self._entry.entry_id}",
            self._handle_board_updated,
        )

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe from events."""
        if self._unsub_dispatcher:
            self._unsub_dispatcher()
            self._unsub_dispatcher = None

    def _handle_board_updated(self) -> None:
        """Handle board updates from store."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> str | None:
        """Return last update timestamp."""
        board = getattr(self._board_store, "_data", None)
        if isinstance(board, dict):
            return str(board.get("updated_at") or "")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return complete board payload attributes."""
        board = getattr(self._board_store, "_data", None) or {}
        return {
            "entry_id": self._entry.entry_id,
            "board": {
                "people": board.get("people", []),
                "tasks": board.get("tasks", []),
                "templates": board.get("templates", []),
                "updated_at": board.get("updated_at", ""),
            },
        }
