import binascii

from .rfid_reader import R200


def example_usage():
    """Example of how to use the R200 library"""
    try:
        rfid = R200("/dev/ttyUSB0", 115200, debug=True)  # Linux
        # rfid = R200("COM3", 115200, debug=True)  # Windows

        tags, err = rfid.read_tags()

        if tags:
            print(f"Found {len(tags)} tags:")
            for i, tag in enumerate(tags):
                epc_hex = binascii.hexlify(bytes(tag.epc)).decode()
                print(f"Tag {i+1}:")
                print(f"  EPC: {epc_hex}")
                print(f"  RSSI: {tag.rssi}")
                print(f"  PC: 0x{tag.pc:04x}")
                print(f"  CRC: 0x{tag.crc:04x}")
        elif err:
            print(f"ReadTags error: {err}")
        else:
            print("No tags found")

        rfid.close()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    example_usage()
