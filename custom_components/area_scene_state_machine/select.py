"""Platform for select entities that control scenes in an area."""

import logging
from asyncio import sleep

from homeassistant.components.select import SelectEntity
from homeassistant.components.scene import DOMAIN as SCENE_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er, area_registry as ar
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AreaScenesCoordinator

_LOGGER = logging.getLogger(__name__)

RESET_OPTION = "None"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the area scenes select entities from a config entry."""
    coordinator: AreaScenesCoordinator = hass.data[DOMAIN][entry.entry_id]
    area_config = entry.options.get("customize", {})

    @callback
    def _async_add_entities_for_area(area_id: str):
        """Add select entities for a specific area."""
        if area_id in coordinator.data["areas"]:
            area = coordinator.data["areas"][area_id]
            scenes = coordinator.data["scenes"].get(area_id, [])
            if scenes:
                customization = area_config.get(area.id, {})
                async_add_entities(
                    [
                        AreaSceneSelect(
                            coordinator,
                            entry.entry_id,
                            area,
                            scenes,
                            customization,
                        )
                    ]
                )

    # Add initial entities
    for area_id in coordinator.data["areas"]:
        _async_add_entities_for_area(area_id)

    # Listen for coordinator updates to add new entities
    entry.async_on_unload(
        coordinator.async_add_listener(
            lambda: _handle_coordinator_update(coordinator, async_add_entities, area_config, entry.entry_id)
        )
    )

@callback
def _handle_coordinator_update(
    coordinator: AreaScenesCoordinator,
    async_add_entities: AddEntitiesCallback,
    area_config: dict,
    entry_id: str,
):
    """Handle coordinator updates and add new select entities if areas are added."""
    existing_entities = {e.unique_id for e in coordinator.hass.data["entity_registry"].entities.values() if e.platform == DOMAIN}
    
    new_selects = []
    for area_id, area in coordinator.data["areas"].items():
        uid = f"{DOMAIN}_{area_id}_scenes"
        if uid not in existing_entities and coordinator.data["scenes"].get(area_id):
            _LOGGER.debug(f"Found new area with scenes: {area.name}. Creating select entity.")
            customization = area_config.get(area.id, {})
            new_selects.append(
                AreaSceneSelect(
                    coordinator,
                    entry_id,
                    area,
                    coordinator.data["scenes"][area_id],
                    customization,
                )
            )
    
    if new_selects:
        async_add_entities(new_selects)


class AreaSceneSelect(CoordinatorEntity, SelectEntity):
    """Representation of a scene select entity for an area."""

    def __init__(
        self,
        coordinator: AreaScenesCoordinator,
        entry_id: str,
        area: ar.AreaEntry,
        scene_entities: list[er.RegistryEntry],
        customization: dict,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self.hass = coordinator.hass
        self._entry_id = entry_id
        self._area = area
        self._customization = customization
        self._is_activating = False  # Flag to prevent feedback loops

        self._attr_name = self._customization.get("name") or f"{self._area.name} Scenes"
        self._attr_unique_id = f"{DOMAIN}_{self._area.id}_scenes"
        self._attr_icon = self._customization.get("icon") or "mdi:palette-outline"
        self._reset_mode = self._customization.get("reset_mode", False)
        self._attr_current_option = RESET_OPTION if self._reset_mode else None
        
        self._update_from_coordinator()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_from_coordinator()
        self.async_write_ha_state()

    def _update_from_coordinator(self):
        """Update the entity's attributes from the coordinator's data."""
        scenes_in_area = self.coordinator.data["scenes"].get(self._area.id, [])
        self._scene_entities = {s.entity_id: s for s in scenes_in_area}
        
        self._scene_name_map = {
            (s.name or s.original_name or "unknown_scene"): s.entity_id
            for s in scenes_in_area
        }
        self._attr_options = list(self._scene_name_map.keys())

        if self._reset_mode:
            self._attr_options.append(RESET_OPTION)

        self._attr_extra_state_attributes = {
            "area_id": self._area.id,
            "color": self._customization.get("color"),
            "reset_mode": self._reset_mode,
            "scene_entities": list(self._scene_entities.keys()),
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self._area.id in self.coordinator.data["areas"]

    @property
    def device_info(self):
        """Return device information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._area.id)},
            "name": f"{self._area.name} Scene Control",
            "suggested_area": self._area.id,
            "manufacturer": "Area Scenes Integration",
            "model": "Scene Selector",
            "via_device": (DOMAIN, self.coordinator.config_entry.entry_id),
        }

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        # Listen for scene activations
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, list(self._scene_entities.keys()), self._handle_scene_event
            )
        )

    @callback
    def _handle_scene_event(self, event):
        """Handle scene activation."""
        if self._is_activating:
            # This activation was triggered by this select, so ignore it
            return

        scene_entity_id = event.data.get("entity_id")
        # Check if the scene was actually activated
        if event.data.get("new_state") is None or event.data.get("old_state") is None:
            return

        if scene_entity_id in self._scene_entities:
            scene_entry = self._scene_entities.get(scene_entity_id)
            if scene_entry:
                scene_name = scene_entry.name or scene_entry.original_name
                _LOGGER.debug(
                    f"Scene '{scene_name}' activated in area '{self._area.name}'. Updating select."
                )
                self._attr_current_option = scene_name
                self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option == self._attr_current_option and option != RESET_OPTION:
            return

        self._is_activating = True
        self._attr_current_option = option
        self.async_write_ha_state()

        if option == RESET_OPTION:
            self._is_activating = False
            return

        target_scene_entity_id = self._scene_name_map.get(option)

        if target_scene_entity_id:
            _LOGGER.info(
                f"Activating scene '{option}' ({target_scene_entity_id}) from select entity."
            )
            # Fire an event that can be used for other automations
            self.hass.bus.async_fire(
                f"{DOMAIN}_scene_selected",
                {
                    "area_id": self._area.id,
                    "scene_name": option,
                    "scene_entity_id": target_scene_entity_id,
                },
            )

            await self.hass.services.async_call(
                SCENE_DOMAIN,
                "turn_on",
                {"entity_id": target_scene_entity_id},
                blocking=True,
            )
        else:
            _LOGGER.warning(f"Could not find a scene named '{option}' to activate.")

        if self._reset_mode:
            # Give HA a moment to process the scene activation before resetting
            self.hass.async_create_task(self._reset_to_none())

        # Reset the flag after a short delay to allow the state to propagate
        self.hass.async_create_task(self._reset_activating_flag())

    async def _reset_activating_flag(self):
        """Reset the activating flag."""
        await sleep(0.2)
        self._is_activating = False

    async def _reset_to_none(self):
        """Reset the select option to None."""
        await sleep(0.1)  # Brief delay
        self._attr_current_option = RESET_OPTION
        self.async_write_ha_state()
