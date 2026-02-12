"""Frontend asset registration for Household Chores card."""

from __future__ import annotations

import json
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

CARD_STATIC_URL = "/household_chores_files/household-chores-card.js"


def _manifest_version() -> str:
    """Read integration version from manifest for cache-busting."""
    manifest_path = Path(__file__).parent / "manifest.json"
    try:
        with manifest_path.open(encoding="utf-8") as manifest_file:
            manifest = json.load(manifest_file)
        version = str(manifest.get("version", "0"))
        return version
    except (OSError, ValueError, TypeError):
        return "0"


async def async_register_card(hass: HomeAssistant) -> None:
    """Register the custom card static path and JS resource."""
    card_path = Path(__file__).parent / "frontend" / "household-chores-card.js"
    versioned_url = f"{CARD_STATIC_URL}?v={_manifest_version()}"
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                CARD_STATIC_URL,
                str(card_path),
                cache_headers=False,
            )
        ]
    )
    add_extra_js_url(hass, versioned_url)
