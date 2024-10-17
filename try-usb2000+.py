import array

import matplotlib.pyplot as plt
import usb.core
import usb.util

dev = usb.core.find(idVendor=0x2457, idProduct=0x101E)
dev.set_configuration()
dev.write(0x01, b"\x01")
dev.write(0x01, b"\x09")
packets = []
for _ in range(8):
    packets.append(dev.read(0x82, 512).tobytes())
assert dev.read(0x82, 1).tobytes() == b"\x69"

pixels = array.array("H", b"".join(packets))
plt.figure()
plt.plot(pixels[2:])
plt.show()
