# Area Scene State Machine AI Agent Guide

This document provides guidance for AI agents working with the `area_scene_state_machine` codebase.

## Project Overview

The `area_scene_state_machine` is a Home Assistant integration that creates a `select` entity for each area that contains scenes. This entity acts as a state machine for the scenes in that area, allowing users to easily switch between them.

The integration is configured through the Home Assistant UI, where users can customize the name, icon, and other options for each area's `select` entity.

## Development

The core logic for the integration is located in `custom_components/area_scene_state_machine/`.

-   `__init__.py`: The main entry point for the integration.
-   `config_flow.py`: Handles the UI configuration flow.
-   `const.py`: Defines constants used throughout the integration.
-   `coordinator.py`: Manages the data and state for the integration.
-   `select.py`: Implements the `select` entity.

## Testing

This project uses `pytest` for testing. To run the tests, use the following command:

```bash
pytest
```

When adding new features, please include corresponding tests to ensure the code is working as expected.

## Known Issues

-   **Testing Environment:** The test environment is not correctly configured, and the tests fail with a `ModuleNotFoundError: No module named 'homeassistant'`. This issue persists even after adding `homeassistant` to `requirements.txt` and attempting to configure the Python path with `pytest.ini`. Further investigation is needed to resolve this issue.
