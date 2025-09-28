import asyncio
import binascii

from .async_rfid_reader import R200Async


async def example_usage():
    rfid = R200Async("/dev/ttyUSB0", 115200, debug=True)
    await rfid.connect()
    info = await rfid.hw_info()
    print(info)
    await rfid.set_power(26)
    power = await rfid.get_power()
    print(f"Current acquire transmit power: {power} dBm")
    await rfid.set_demodulator_params(mixer_g=2, if_g=7, thrd=100)

    print("Press Ctrl+C to end")
    while True:
        try:
            tags, errs = await rfid.read_tags()
            if tags:
                print(f"Found {len(tags)} tags:")
                for i, tag in enumerate(tags):
                    epc_hex = binascii.hexlify(bytes(tag.epc)).decode()
                    print(f"Tag {i+1}:")
                    print(f"  EPC: {epc_hex}")
                    print(f"  RSSI: {tag.rssi}")
                    print(f"  PC: 0x{tag.pc:04x}")
                    print(f"  CRC: 0x{tag.crc:04x}")
            elif errs:
                print(f"ReadTags error: {errs}".center(80, "="))
            else:
                print("No tags found".center(50, "*"))
            await asyncio.sleep(0.5)

        except KeyboardInterrupt:
            await rfid.close()
            break


if __name__ == "__main__":
    asyncio.run(example_usage())
