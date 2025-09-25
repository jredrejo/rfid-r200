import asyncio
import binascii

from .async_rfid_reader import R200Async


async def example_usage():
    rfid = R200Async("/dev/ttyUSB0", 115200, debug=True)
    await rfid.connect()
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
            print(f"ReadTags error: {errs}")
        else:
            print("No tags found")
    finally:
        await rfid.close()


if __name__ == "__main__":
    asyncio.run(example_usage())
