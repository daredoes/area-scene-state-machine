# Area Scene State Machine for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)

A Home Assistant integration that creates a `select` entity for each area containing scenes. This entity acts as a state machine, representing the currently active scene for that area.

## Features

- **Automatic Discovery:** Automatically discovers scenes within your Home Assistant areas and creates a corresponding `select` entity for each area.
- **State Tracking:** The `select` entity tracks which scene was last activated, whether from the UI or an automation.
- **Seamless Control:** Activating a scene from the `select` entity is the same as activating it directly, allowing for easy integration with your existing dashboards and automations.
- **UI Configuration:** Customize the name, icon, and other options for each area's `select` entity directly from the Home Assistant UI.
- **Reset Mode:** An optional "Reset Mode" allows the `select` entity to revert to a "None" state after a scene is activated, useful for triggering automations.

## Installation

### HACS (Home Assistant Community Store) - Recommended

1.  Ensure you have [HACS](https://hacs.xyz/) installed.
2.  Go to HACS > Integrations > and click the three dots in the top right.
3.  Select "Custom Repositories" and add this repository's URL (`https://github.com/daredoes/area_scene_state_machine`) with the category "Integration".
4.  Search for "Area Scene State Machine" and install it.
5.  Restart Home Assistant.

### Manual Installation

1.  Copy the `custom_components/area_scene_state_machine` directory into your Home Assistant `custom_components` directory.
2.  Restart Home Assistant.

## Configuration

1.  Go to **Settings > Devices & Services**.
2.  Click **Add Integration** and search for **Area Scene State Machine**.
3.  Follow the on-screen instructions. The integration will be set up, and you don't need to configure anything in this initial step.

## Customization

You can customize each area's `select` entity:

1.  Go to **Settings > Devices & Services**.
2.  Find the **Area Scene State Machine** integration and click **Configure**.
3.  Select the area you wish to customize from the dropdown.
4.  You can set a custom **Name** and **Icon**. You can also enable **Reset Mode**.

## How It Works

The integration listens for scene activations in your Home Assistant instance. When a scene is activated, it updates the state of the corresponding area's `select` entity to reflect the change. This provides a simple way to know the "state" of an area based on its scenes.

You can use this `select` entity in your automations or scripts. For example, you can build a lighting control automation that checks the state of an area's scene `select` before making changes.
