import asyncio
from bleak import BleakScanner, BleakClient

class BluetoothService:
    def __init__(self):
        self.nearby_devices = []
        self.selected_device = None

    async def scan_devices(self):
        """Scan for nearby Bluetooth devices."""
        scanner = BleakScanner()
        await scanner.start()
        await asyncio.sleep(5.0)  # Scanning for 5 seconds
        await scanner.stop()

        self.nearby_devices = scanner.discovered_devices
        return self.nearby_devices

    async def connect_device(self, device_address):
        """Connect to a specific Bluetooth device."""
        async with BleakClient(device_address) as client:
            print("Connected!")
            self.selected_device = client
            return client

    def get_devices(self):
        """Return the list of nearby devices."""
        return self.nearby_devices

    def get_selected_device(self):
        """Return the selected device."""
        return self.selected_device