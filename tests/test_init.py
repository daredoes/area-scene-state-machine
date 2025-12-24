"""Test the Area Scene State Machine integration."""

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.area_scene_state_machine.const import DOMAIN


async def test_async_setup(hass: HomeAssistant) -> None:
    """Test the component gets setup."""
    assert await async_setup_component(hass, DOMAIN, {}) is True
