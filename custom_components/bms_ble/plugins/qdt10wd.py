"""Module to support QDT10WD BMS over BLE."""

import asyncio
from collections.abc import Callable
from typing import Final

from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.uuids import normalize_uuid_str

from custom_components.bms_ble.const import (
    ATTR_CURRENT,
    ATTR_BATTERY_LEVEL,
    ATTR_VOLTAGE,
    KEY_CELL_VOLTAGE,
)

from .basebms import BaseBMS, BMSsample


class BMS(BaseBMS):
    """QDT10WD BMS BLE class implementation."""

    SERVICE_UUID: Final = normalize_uuid_str("0000ffff-0000-1000-8000-00805f9b34fb")
    CHARACTERISTIC_UUID: Final = normalize_uuid_str("0000ffe1-0000-1000-8000-00805f9b34fb")
    TRIGGER_COMMAND: Final = bytes.fromhex("7E3631303134364237453030323031464431440D")  # ~610146B7...

    def __init__(self, ble_device: BLEDevice, reconnect: bool = False) -> None:
        super().__init__(__name__, ble_device, reconnect)
        self._data_final: bytearray = bytearray()

    @staticmethod
    def matcher_dict_list() -> list[dict]:
        return [{"service_uuid": BMS.SERVICE_UUID, "connectable": True}]

    @staticmethod
    def device_info() -> dict[str, str]:
        return {"manufacturer": "QDT", "model": "QDT10WD"}

    @staticmethod
    def uuid_services() -> list[str]:
        return [BMS.SERVICE_UUID]

    @staticmethod
    def uuid_rx() -> str:
        return BMS.CHARACTERISTIC_UUID

    @staticmethod
    def uuid_tx() -> str:
        return BMS.CHARACTERISTIC_UUID

    def _notification_handler(self, _: BleakGATTCharacteristic, data: bytearray) -> None:
        if data.startswith(b"~61"):
            self._data_final = data
            self._data_event.set()

    async def _async_update(self) -> BMSsample:
        self._data_event.clear()
        await self._client.write_gatt_char(self.uuid_tx(), self.TRIGGER_COMMAND)
        await asyncio.wait_for(self._data_event.wait(), timeout=self.TIMEOUT)

        data = self._data_final

        # Eenvoudige parser op basis van bekende offsets (kan worden uitgebreid)
        voltage = int.from_bytes(data[7:9], byteorder="big") / 100.0
        current = int.from_bytes(data[11:13], byteorder="big", signed=True) / 100.0
        soc = data[7]

        cells = {
            f"{KEY_CELL_VOLTAGE}{i+1}": int.from_bytes(data[112 + i * 2:114 + i * 2], byteorder="big") / 1000
            for i in range(16)
        }

        return {
            ATTR_VOLTAGE: voltage,
            ATTR_CURRENT: current,
            ATTR_BATTERY_LEVEL: soc,
            **cells
        }
