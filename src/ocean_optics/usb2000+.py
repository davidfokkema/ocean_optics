import array
import time

import plotext as plt
import usb.core
import usb.util


class OceanOpticsUSB2000Plus:
    INT_TIME: int = 100_000

    def __init__(self) -> None:
        self.device = usb.core.find(idVendor=0x2457, idProduct=0x101E)
        self.device.reset()
        self.device.set_configuration()
        # Initialize device
        self.device.write(0x01, b"\x01")
        # Set default integration time
        self.device.write(0x01, b"\x02" + int(self.INT_TIME).to_bytes(4, "little"))

    def get_spectrum(self):
        self.device.write(0x01, b"\x09")
        # wait for measurement to complete, integration time is in microseconds.
        time.sleep(self.INT_TIME / 1_000_000)
        packets = []
        for _ in range(8):
            try:
                packets.append(self.device.read(0x82, 512, 100).tobytes())
            except usb.core.USBTimeoutError:
                break
        else:
            packets.append(self.device.read(0x82, 1, 100).tobytes())
        assert packets[-1][-1] == 0x69

        return array.array("H", b"".join(packets[:-1]))

    def close(self) -> None:
        print("Shutting down.")
        self.device.write(0x01, b"\x04\x00\x00")
        print("Done.")


dev = OceanOpticsUSB2000Plus()

pixels = dev.get_spectrum()
plt.clf()
plt.plot(pixels[20:])
plt.show()

dev.close()
