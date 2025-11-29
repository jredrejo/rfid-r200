import binascii
import time

from rfid_r200 import R200


def example_usage():
    """Example of how to use the R200 library"""
    rfid = R200("/dev/ttyUSB0", 115200, debug=True)  # Linux
    # rfid = R200("COM3", 115200, debug=True)  # Windows

    info = rfid.hw_info()
    print(info)
    power = rfid.get_power()
    print(f"Current acquire transmit power: {power} dBm")
    # await rfid.set_demodulator_params(mixer_g=2, if_g=7, thrd=100)
    demod_params = rfid.get_demodulator_params()
    print(f"Demodulator parameters: {demod_params}")
    print("Press Ctrl+C to end")
    while True:
        try:
            tags, errs = rfid.read_tags()

            if tags:
                print(f"Found {len(tags)} tags:")
                for i, tag in enumerate(tags):
                    epc_hex = binascii.hexlify(bytes(tag.epc)).decode()
                    print(f"Tag {i + 1}:")
                    print(f"  EPC: {epc_hex}")
                    print(f"  RSSI: {tag.rssi}")
                    print(f"  PC: 0x{tag.pc:04x}")
                    print(f"  CRC: 0x{tag.crc:04x}")
            elif errs:
                print(f"ReadTags error: {errs}".center(80, "="))
            else:
                print("No tags found".center(50, "*"))

            time.sleep(0.5)

        except KeyboardInterrupt:
            rfid.close()
            break


if __name__ == "__main__":
    example_usage()
