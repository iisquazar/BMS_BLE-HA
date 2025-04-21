"""Module to support QDT10WD BMS."""

import logging
from typing import Any

from bleak.backends.device import BLEDevice
from bleak.uuids import normalize_uuid_str

from custom_components.bms_ble.const import (
    ATTR_BATTERY_CHARGING,
    ATTR_CURRENT,
    ATTR_POWER,
    ATTR_VOLTAGE,
)

from .basebms import BaseBMS, BMSsample

LOGGER = logging.getLogger(__name__)
BAT_TIMEOUT = 10

class BMS(BaseBMS):
    """QDT10WD BMS class implementation."""

    def __init__(self, ble_device: BLEDevice, reconnect: bool = False) -> None:
        """Initialize BMS."""
        LOGGER.debug("%s init(), BT address: %s", self.device_id(), ble_device.address)
        super().__init__("qdt10wd", ble_device, reconnect)

    @staticmethod
    def matcher_dict_list() -> list[dict[str, Any]]:
        """Provide BluetoothMatcher definition."""
        return [{"local_name": "QDT10WD*", "service_uuid": normalize_uuid_str("ffff"), "connectable": True}]

    @staticmethod
    def device_info() -> dict[str, str]:
        """Return device information for the battery management system."""
        return {"manufacturer": "QDT", "model": "QDT10WD"}

    @staticmethod
    def uuid_services() -> list[str]:
        """Return list of 128-bit UUIDs of services required by BMS."""
        return [normalize_uuid_str("0000ffff-0000-1000-8000-00805f9b34fb")]

    @staticmethod
    def uuid_rx() -> str:
        """Return UUID of characteristic that provides notification/read property."""
        return "0000ff02-0000-1000-8000-00805f9b34fb"

    @staticmethod
    def uuid_tx() -> str:
        """Return UUID of characteristic that provides write property."""
        return "0000ff01-0000-1000-8000-00805f9b34fb"

    def _calc_values(self) -> set[str]:
        """Return the set of values this BMS provides."""
        return {
            ATTR_POWER,
            ATTR_BATTERY_CHARGING,
        }

    def _notification_handler(self, _sender, data: bytearray) -> None:
        """Handle the RX characteristics notify event (new data arrives)."""
        LOGGER.debug("%s: Received BLE data: %s", self.name, data.hex(" "))
        # TODO: parse data and store it in self._data
        # self._data = data
        # self._data_event.set()

    async def _async_update(self) -> BMSsample:
        """Update battery status information."""
        LOGGER.debug("(%s) Sending command to UUID %s", self.name, BMS.uuid_tx())

        # Voorbeeld: stuur een commando als dat nodig is
        # await self._client.write_gatt_char(BMS.uuid_tx(), data=b"<command_bytes>")
        # await asyncio.wait_for(self._wait_event(), timeout=BAT_TIMEOUT)

        # TODO: parse real values from self._data (set in _notification_handler)
        return {
            ATTR_VOLTAGE: 12.5,     # Dummy-waarde, pas aan
            ATTR_CURRENT: 1.2,      # Dummy-waarde, pas aan
        }
