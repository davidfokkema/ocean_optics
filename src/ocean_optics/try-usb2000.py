import pathlib
import platform
import sys
import time

try:
    import libusb
except ModuleNotFoundError:
    pass

import plotext as plt
import usb.backend.libusb1
import usb.core

INT_TIME = 100

if usb.backend.libusb1.get_backend() is None:
    if platform.system() == "Windows":
        p_path = "x64" if sys.maxsize > 2**32 else "x86"
        dll_path = (
            pathlib.Path(libusb.__file__).parent
            / rf"_platform\_windows\{p_path}\libusb-1.0.dll"
        )
        usb.backend.libusb1.get_backend(find_library=lambda x: dll_path)

dev = usb.core.find(idVendor=0x2457, idProduct=0x1002)
dev.set_configuration()

# initialize device (acquires first spectrum)
dev.write(0x02, b"\x01")
num_packets = 0
while True:
    # unfortunately, sometimes the first data is an extra \x69.
    # keep reading until a timeout occurs.
    try:
        dev.read(0x82, 64)
        num_packets += 1
    except usb.core.USBTimeoutError:
        break
print(f"Read {num_packets} packets of data.")

# set integration time
dev.write(0x02, b"\x02" + int(INT_TIME).to_bytes(2, "little"))

try:
    while True:
        t0 = time.monotonic()
        dev.write(0x02, b"\x09")
        # wait for measurement to complete
        time.sleep(INT_TIME / 1_000)

        packets = []
        for _ in range(64):
            packets.append(dev.read(0x82, 64).tobytes())
        assert dev.read(0x82, 64).tobytes() == b"\x69"

        t1 = time.monotonic()

        pixels = []
        for lsb_packet, msb_packet in zip(packets[0:-1:2], packets[1:-1:2]):
            for lsb, msb in zip(lsb_packet, msb_packet):
                pixels.append(msb * 256 + lsb)

        plt.clf()
        plt.plot(pixels[20:])
        plt.show()
        print(f"Got {len(pixels)} pixels in {t1 - t0:.1f}s.")
except KeyboardInterrupt:
    pass
