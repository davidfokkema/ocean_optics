import array
import time

import matplotlib.pyplot as plt
import usb.core
import usb.util

dev = usb.core.find(idVendor=0x2457, idProduct=0x1002)
dev.reset()
time.sleep(0.1)
dev.set_configuration()

# dev.write(0x02, b"\xfe")
# print(dev.read(0x87, 16))

# dev.write(0x02, b"\x08")
# print(dev.read(0x87, 16))

dev.write(0x02, b"\x01")
packets = []
for _ in range(64):
    packets.append(dev.read(0x82, 64).tobytes())
assert dev.read(0x82, 1).tobytes() == b"\x69"

pixels = array.array("H", b"".join(packets))
plt.figure()
plt.plot(pixels[2:])
plt.show()
