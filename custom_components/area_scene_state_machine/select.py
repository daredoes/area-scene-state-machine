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

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

RESET_OPTION = "None"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the area scenes select entities from a config entry."""
    area_registry = ar.async_get(hass)
    entity_registry = er.async_get(hass)

    # Get customization from the config entry's options
    area_config = entry.options.get("customize", {})

    scene_entities_to_area_ids = {}
    for entity_entry in entity_registry.entities.values():
        if entity_entry.domain == SCENE_DOMAIN:
            if not scene_entities_to_area_ids.get(entity_entry.area_id):
                scene_entities_to_area_ids[entity_entry.area_id] = []
            scene_entities_to_area_ids[entity_entry.area_id].append(entity_entry)

    selects = []
    for area in area_registry.async_list_areas():
        area_id = area.id
        # Get scene entities in the current area
        scene_entities_in_area = scene_entities_to_area_ids.get(area_id, [])

        if not scene_entities_in_area:
            _LOGGER.debug(
                f"No scenes found in area: {area.name}, skipping select creation."
            )
            continue

        customization = area_config.get(area.id, {})

        selects.append(
            AreaSceneSelect(
                hass,
                entry.entry_id,
                area,
                scene_entities_in_area,
                customization,
            )
        )

    async_add_entities(selects)


class AreaSceneSelect(SelectEntity):
    """Representation of a scene select entity for an area."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        area: ar.AreaEntry,
        scene_entities: list[er.RegistryEntry],
        customization: dict,
    ) -> None:
        """Initialize the select entity."""
        self.hass = hass
        self._entry_id = entry_id
        self._area = area
        self._scene_entities = {s.entity_id: s for s in scene_entities}
        self._customization = customization
        self._is_activating = False  # Flag to prevent feedback loops

        self._attr_name = self._customization.get("name") or f"{self._area.name} Scenes"
        self._attr_unique_id = f"{DOMAIN}_{self._area.id}_scenes"
        self._attr_icon = self._customization.get("icon") or "mdi:palette-outline"

        self._scene_name_map = {
            (s.name or s.original_name or "unknown_scene"): s.entity_id
            for s in scene_entities
        }
        self._attr_options = list(self._scene_name_map.keys())

        self._reset_mode = self._customization.get("reset_mode", False)
        if self._reset_mode:
            self._attr_options.append(RESET_OPTION)

        self._attr_current_option = RESET_OPTION if self._reset_mode else None

        self._attr_extra_state_attributes = {
            "area_id": self._area.id,
            "color": self._customization.get("color"),
            "reset_mode": self._reset_mode,
            "scene_entities": list(self._scene_entities.keys()),
        }

    @property
    def device_info(self):
        """Return device information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._area.id)},
            "name": f"{self._area.name} Scene Control",
            "suggested_area": self._area.id,
            "manufacturer": "Area Scenes Integration",
            "model": "Scene Selector",
            "via_device": (DOMAIN, self._entry_id),
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
