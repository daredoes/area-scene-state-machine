"""Custom types for area_scene_state_machine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import AreaSceneStateMachineApiClient
    from .coordinator import BlueprintDataUpdateCoordinator


type AreaSceneStateMachineConfigEntry = ConfigEntry[AreaSceneStateMachineData]


@dataclass
class AreaSceneStateMachineData:
    """Data for the Blueprint integration."""

    client: AreaSceneStateMachineApiClient
    coordinator: BlueprintDataUpdateCoordinator
    integration: Integration
