import array
import time

import plotext as plt
import usb.core
import usb.util

INT_TIME = 100_000

dev = usb.core.find(idVendor=0x2457, idProduct=0x101E)
dev.set_configuration()
dev.write(0x01, b"\x01")
dev.write(0x01, b"\x02" + int(INT_TIME).to_bytes(4, 'little'))

try:
    while True:
        t0 = time.monotonic()
        dev.write(0x01, b"\x09")
        # wait for measurement to complete
        time.sleep(INT_TIME / 1_000_000)
        packets = []
        for _ in range(8):
            try:
                packets.append(dev.read(0x82, 512, 100).tobytes())
            except usb.core.USBTimeoutError:
                break
        else:
            packets.append(dev.read(0x82, 1, 100).tobytes())
        assert packets[-1][-1] == 0x69
        t1 = time.monotonic()

        pixels = array.array("H", b"".join(packets[:-1]))

        plt.clf()
        #plt.scatter(pixels[20:], marker='hd', color='black')
        plt.plot(pixels[20:])
        plt.show()
        print(f"Got {len(pixels)} pixels in {t1 - t0:.1f}s.")
except KeyboardInterrupt:
    pass

# Shutdown
print("Shutting down.")
dev.write(0x01, b"\x04\x00\x00")
