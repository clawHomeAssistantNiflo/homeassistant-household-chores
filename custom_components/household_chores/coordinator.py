"""Data coordinator for Household Chores."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import DEFAULT_CHORE_TIME, DOMAIN


@dataclass(slots=True)
class ChoreEvent:
    """Represents one chore event."""

    start: datetime
    end: datetime
    summary: str
    chore: str
    member: str


class HouseholdChoresCoordinator(DataUpdateCoordinator[list[ChoreEvent]]):
    """Coordinates household chore schedule data."""

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        entry_id: str,
        name: str,
        members: list[str],
        chores: list[str],
    ) -> None:
        self.entry_id = entry_id
        self.name = name
        self.members = members
        self.chores = chores

        super().__init__(
            hass,
            logger=hass.data[DOMAIN]["logger"],
            name=f"{DOMAIN}_{entry_id}",
            update_interval=timedelta(hours=1),
        )

    def _generate_events(self, weeks: int = 8) -> list[ChoreEvent]:
        """Generate rotating weekly chore assignments."""
        now_local = dt_util.as_local(dt_util.utcnow())
        this_monday = (now_local - timedelta(days=now_local.weekday())).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        if not self.members or not self.chores:
            return []

        events: list[ChoreEvent] = []

        for week_offset in range(weeks):
            week_start = this_monday + timedelta(days=week_offset * 7)
            for chore_index, chore in enumerate(self.chores):
                weekday_offset = chore_index % 7
                event_start = week_start + timedelta(days=weekday_offset)
                event_start = event_start.replace(
                    hour=DEFAULT_CHORE_TIME.hour,
                    minute=DEFAULT_CHORE_TIME.minute,
                )
                event_start = event_start.astimezone(dt_util.DEFAULT_TIME_ZONE)
                member_index = (week_offset + chore_index) % len(self.members)
                member = self.members[member_index]

                summary = f"{chore} - {member}"
                events.append(
                    ChoreEvent(
                        start=event_start,
                        end=event_start + timedelta(minutes=30),
                        summary=summary,
                        chore=chore,
                        member=member,
                    )
                )

        return sorted(events, key=lambda event: event.start)

    async def _async_update_data(self) -> list[ChoreEvent]:
        """Refresh coordinator data."""
        return self._generate_events()

    def update_config(self, *, members: list[str], chores: list[str], name: str) -> None:
        """Update coordinator with config entry options."""
        self.members = members
        self.chores = chores
        self.name = name
