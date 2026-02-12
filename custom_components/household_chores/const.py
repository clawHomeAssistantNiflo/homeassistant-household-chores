"""Constants for Household Chores."""

from datetime import time

from homeassistant.const import Platform

DOMAIN = "household_chores"
PLATFORMS: list[Platform] = [Platform.CALENDAR, Platform.SENSOR]

CONF_MEMBERS = "members"
CONF_CHORES = "chores"

DEFAULT_NAME = "Household Chores"
DEFAULT_MEMBERS = ["Alex", "Sam"]
DEFAULT_CHORES = [
    "Take out trash",
    "Vacuum living room",
    "Clean kitchen",
    "Laundry",
]

DEFAULT_CHORE_TIME = time(hour=18, minute=0)
