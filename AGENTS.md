This document provides guidance for AI agents working with the `area_scene_state_machine` repository.

## About the Project

This is a Home Assistant custom component that creates a `select` entity for each area that contains scenes. This entity acts as a state machine for the scenes in that area, allowing users to see which scene is currently active and to change the active scene.

## Development Environment

The project is set up to be used with the Visual Studio Code Dev Container feature. This provides a consistent, pre-configured environment with all necessary dependencies.

To get started:
1.  Open this repository in a VS Code Dev Container.
2.  Run `scripts/develop` to start a Home Assistant instance with the integration loaded.

## Code Structure

-   `custom_components/area_scene_state_machine/`: The core integration code.
    -   `__init__.py`: Sets up the integration and config entry listeners.
    -   `config_flow.py`: Handles the UI configuration flow for the integration.
    -   `const.py`: Defines constants used throughout the integration.
    -   `coordinator.py`: The `DataUpdateCoordinator` that fetches and manages area and scene data.
    -   `select.py`: Defines the `AreaSceneSelect` entity, which is the core of this integration.
-   `tests/`: Contains unit and integration tests.

## Key Concepts

-   **Coordinator:** The `AreaScenesCoordinator` is responsible for fetching all areas and scenes from Home Assistant and notifying the `select` entities when there are changes.
-   **Select Entity:** The `AreaSceneSelect` class in `select.py` represents the `select` entity for an area. It gets its data from the coordinator and handles scene activation and state tracking.
-   **Config Flow:** The configuration flow in `config_flow.py` allows users to install the integration and customize the `select` entities for each area.

## Linting and Formatting

This project uses `ruff` for linting and formatting. Please ensure your changes are compliant by running `ruff check . --fix` and `ruff format .` before submitting.

## Testing

This project currently lacks a testing framework. Future contributors are encouraged to add one to improve the stability and reliability of the codebase.
