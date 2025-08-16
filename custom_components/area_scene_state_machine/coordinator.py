"""Data update coordinator for the Area Scenes integration."""

import logging
from typing import Dict, List

from homeassistant.core import HomeAssistant, callback, Event
from homeassistant.helpers.area_registry import EVENT_AREA_REGISTRY_UPDATED
from homeassistant.helpers.entity_registry import EVENT_ENTITY_REGISTRY_UPDATED
from homeassistant.helpers import entity_registry as er, area_registry as ar
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.components.scene import DOMAIN as SCENE_DOMAIN

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class AreaScenesCoordinator(DataUpdateCoordinator):
    """Coordinator to manage area and scene data."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
        )
        self.area_registry = ar.async_get(hass)
        self.entity_registry = er.async_get(hass)
        self.areas: Dict[str, ar.AreaEntry] = {}
        self.scenes: Dict[str, List[er.RegistryEntry]] = {}

        self._setup_listeners()

    @callback
    def _setup_listeners(self):
        """Set up listeners for area and entity registry changes."""
        self.hass.bus.async_listen(
            EVENT_AREA_REGISTRY_UPDATED, self._handle_area_registry_update
        )
        self.hass.bus.async_listen(
            EVENT_ENTITY_REGISTRY_UPDATED, self._handle_entity_registry_update
        )

    async def _async_update_data(self):
        """Fetch and process area and scene data."""
        _LOGGER.debug("Updating area and scene data")
        self.areas = {area.id: area for area in self.area_registry.async_list_areas()}
        
        all_scenes = [
            entity
            for entity in self.entity_registry.entities.values()
            if entity.domain == SCENE_DOMAIN and entity.area_id
        ]

        self.scenes.clear()
        for scene in all_scenes:
            if scene.area_id not in self.scenes:
                self.scenes[scene.area_id] = []
            self.scenes[scene.area_id].append(scene)

        return {"areas": self.areas, "scenes": self.scenes}

    @callback
    def _handle_area_registry_update(self, event: Event):
        """Handle area registry updates."""
        _LOGGER.debug(f"Area registry updated: {event.data}")
        self.hass.async_create_task(self.async_request_refresh())

    @callback
    def _handle_entity_registry_update(self, event: Event):
        """Handle entity registry updates."""
        # We don't have the domain, so we need to check the entity registry
        entity_id = event.data.get("entity_id")
        if not entity_id:
            return

        entity = self.entity_registry.async_get(entity_id)
        if entity and entity.domain == SCENE_DOMAIN:
            _LOGGER.debug(f"Scene entity registry updated: {entity_id}")
            self.hass.async_create_task(self.async_request_refresh())
