import array
import pathlib
import platform
import sys
import time

import libusb
import matplotlib.pyplot as plt
import usb.backend.libusb1
import usb.core

if usb.backend.libusb1.get_backend() is None:
    if platform.system() == "Windows":
        p_path = "x64" if sys.maxsize > 2**32 else "x86"
        dll_path = (
            pathlib.Path(libusb.__file__).parent
            / rf"_platform\_windows\{p_path}\libusb-1.0.dll"
        )
        usb.backend.libusb1.get_backend(find_library=lambda x: dll_path)

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
