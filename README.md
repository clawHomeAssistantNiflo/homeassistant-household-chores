# homeassistant-household-chores

Household Chores is a HACS-installable custom integration that creates a weekly household chore calendar and assigns chores to people in the home.

## Features

- Config flow setup in Home Assistant UI
- Weekly chore assignments with member rotation
- Calendar entity with generated chore events
- Sensor for the next upcoming chore
- Options flow to edit members/chores later

## Install (HACS)

1. Push this repository to GitHub.
2. In Home Assistant, open HACS -> Integrations -> three dots -> Custom repositories.
3. Add your repository URL and select category `Integration`.
4. Search for `Household Chores` in HACS and install.
5. Restart Home Assistant.
6. Go to Settings -> Devices & Services -> Add Integration -> `Household Chores`.

## Configuration

During setup you can define:
- Household name
- Comma-separated list of people (members)
- Comma-separated list of chores

The integration will generate weekly chore events and rotate assignments across members.

## Notes

This scaffold is intentionally local-first (no external API). You can extend it later with:
- per-chore preferred weekday/time
- completion tracking with persistent storage
- notifications/reminders
- dashboard card
