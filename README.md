# Area Scene State Machine

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)
[![hacs][hacs-shield]][hacs-url]

_Integration to manage scenes for each area in Home Assistant._

**This integration creates a `select` entity for each area that contains scenes.** This entity acts as a state machine for the scenes in that area, allowing you to easily switch between them.

## Installation

### HACS (Home Assistant Community Store)

1.  Go to HACS.
2.  Go to integrations.
3.  Click the three dots in the top right corner.
4.  Select "Custom Repositories".
5.  Add the URL to this repository in the "Repository" field.
6.  Select the "Integration" category.
7.  Click the "ADD" button.
8.  Search for "Area Scene State Machine" and install it.
9.  Restart Home Assistant.

### Manual Installation

1.  Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2.  If you do not have a `custom_components` directory (folder) there, you need to create it.
3.  In the `custom_components` directory (folder) create a new folder called `area_scene_state_machine`.
4.  Download all the files from the `custom_components/area_scene_state_machine/` directory (folder) in this repository.
5.  Place the files you downloaded in the new directory (folder) you created.
6.  Restart Home Assistant.

## Configuration

The Area Scene State Machine is configured through the Home Assistant UI.

1.  Go to **Settings** -> **Devices & Services**.
2.  Click the **+ Add Integration** button.
3.  Search for "Area Scene State Machine" and select it.
4.  Follow the on-screen instructions to complete the setup.

The integration will automatically discover all areas that contain scenes and create a `select` entity for each one. You can then customize the name, icon, and other options for each entity.

[releases]: https://github.com/daredoes/area_scene_state_machine/releases
[releases-shield]: https://img.shields.io/github/release/daredoes/area_scene_state_machine.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/daredoes/area_scene_state_machine.svg?style=for-the-badge
[hacs-shield]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[hacs-url]: https://hacs.xyz