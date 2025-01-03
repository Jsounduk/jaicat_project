import asyncio
from bleak import BleakScanner, BleakClient

class BluetoothService:
    def __init__(self):
        self.nearby_devices = []

    async def discover_devices(self):
        """Discover nearby Bluetooth devices."""
        try:
            scanner = BleakScanner()
            await scanner.start()
            await asyncio.sleep(5.0)  # Scanning for 5 seconds
            await scanner.stop()

            self.nearby_devices = scanner.discovered_devices
            return self.nearby_devices
        except Exception as e:
            return f"Error discovering Bluetooth devices: {str(e)}"

    async def connect_device(self, device_address):
        """Connect to a specific Bluetooth device."""
        try:
            async with BleakClient(device_address) as client:
                print("Connected!")

                # Example: Read a characteristic
                # Replace 'your_characteristic_uuid' with the actual UUID
                characteristic_uuid = "your_characteristic_uuid"
                characteristic_value = await client.read_gatt_char(characteristic_uuid)
                print(f"Read characteristic: {characteristic_value}")

                # Example: Write to a characteristic
                # Replace 'your_data' with the data you want to send
                await client.write_gatt_char(characteristic_uuid, b"your_data")
                print("Data written to characteristic.")

                return f"Connected to {device_address}"
        except Exception as e:
            return f"Error connecting to {device_address}: {str(e)}"

# Example usage
async def main():
    bluetooth_service = BluetoothService()

    # Discover devices
    devices = await bluetooth_service.discover_devices()
    print("Nearby devices:", devices)

    if devices:
        # Replace with the actual address of the device you want to connect to
        device_address = devices[0].address
        connection_response = await bluetooth_service.connect_device(device_address)
        print(connection_response)

asyncio.run(main())
