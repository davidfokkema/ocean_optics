import array
import time

import matplotlib.pyplot as plt
import usb.core
import usb.util

dev = usb.core.find(idVendor=0x2457, idProduct=0x101E)
dev.set_configuration()
dev.write(0x01, b"\x01")
time.sleep(.1)
dev.write(0x01, b"\x09")
packets = []
while True:
    try:
        packets.append(dev.read(0x82, 512).tobytes())
    except usb.core.USBTimeoutError:
        break
assert packets[-1][-1] == 0x69
# Shutdown
dev.write(0x01, b"\x04\x00\x00")

pixels = array.array("H", b"".join(packets[:-1]))

print(f"Got {len(pixels)} pixels")

plt.figure()
plt.plot(pixels[20:])
plt.show()

import plotext as plt
plt.plot(pixels[20:])
plt.show()
