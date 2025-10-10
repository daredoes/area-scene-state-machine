# Area Scene State Machine

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)

A Home Assistant integration that creates a `select` entity for each area containing scenes. This entity acts as a state machine, allowing you to see which scene is currently active and to activate other scenes.

## Goal

The primary goal of this integration is to simplify scene management in Home Assistant, especially for tablet dashboards. Instead of adding individual scenes to a dashboard, you can add a single `select` entity that represents all scenes in a specific area. This provides a clean and intuitive way to manage scene states.

## How It Works

The integration automatically discovers all areas in your Home Assistant configuration that have scenes associated with them. For each of these areas, it creates a `select` entity.

- **State Tracking**: The `select` entity tracks which scene was last activated in that area. If you activate a scene through any means (e.g., an automation, a script, or the Home Assistant UI), the `select` entity will update to reflect that change.
- **Scene Activation**: You can use the `select` entity to activate any of the scenes in that area. Simply choose a scene from the dropdown list, and the integration will call the `scene.turn_on` service for that scene.

## Installation

### HACS (Recommended)

1.  Add this repository as a custom repository in HACS.
2.  Search for "Area Scene State Machine" and install it.
3.  Restart Home Assistant.

### Manual

1.  Copy the `custom_components/area_scene_state_machine` directory to your `custom_components` directory.
2.  Restart Home Assistant.

## Configuration

Configuration is done through the Home Assistant UI.

1.  Go to **Settings > Devices & Services**.
2.  Click **Add Integration** and search for **Area Scene State Machine**.
3.  The integration will be added. There is no initial configuration required.
4.  To customize the `select` entities, click **Configure** on the integration card. You can then select an area to customize the following options:
    - **Name**: A custom name for the `select` entity.
    - **Icon**: A custom icon for the `select` entitiy.
    - **Color**: A custom color for the `select` entity.
    - **Reset Mode**: If enabled, the `select` entity will reset to "None" after a scene is activated. This is useful for momentary-style scene activations.

## Use Cases

### Lovelace Dashboards

Add the `select` entity to your Lovelace dashboard to get a simple dropdown for controlling scenes in an area.

```yaml
type: entities
entities:
  - entity: select.living_room_scenes
```

### Automations

You can use the state of the `select` entity as a trigger or condition in your automations.

```yaml
trigger:
  - platform: state
    entity_id: select.living_room_scenes
    to: "Movie Time"
action:
  - service: light.turn_on
    target:
      entity_id: light.ambilight
```

## Future Vision

- **Advanced State Tracking**: Explore options for more advanced state tracking, such as tracking individual device states within a scene.
- **Support for Other Entities**: Potentially expand the integration to support other entity types, like scripts or automations.
- **Dynamic Scene Creation**: Allow users to create and edit scenes directly from the integration.