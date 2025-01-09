import usb.core
import usb.util

device = usb.core.find(idVendor=0x2457, idProduct=0x101E)
print(f"{device.get_active_configuration()=}")
# device.set_configuration()


command = b"\x05\x00"
device.write(0x01, command)
try:
    v = device.read(0x81, 17).tobytes()
except usb.core.USBTimeoutError:
    print("Reading config failed")
else:
    print(f"Read {len(v)} bytes of config data.")


device.write(0x01, b"\x09")
data = device.read(0x82, 1_000_000, 100)
print(f"Read {len(data)} bytes of spectrum data.")
