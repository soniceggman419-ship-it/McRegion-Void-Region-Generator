from nbt import (
    TAG_BYTE, TAG_INT, TAG_LONG, TAG_BYTE_ARRAY, TAG_COMPOUND,
    serialize_nbt,
)


def make_chunk(chunk_x, chunk_z):
    blocks = b'\x00' * 32768
    data = b'\x00' * 16384
    skylight = b'\xff' * 16384
    blocklight = b'\x00' * 16384
    heightmap = b'\x00' * 256

    level = [
        (TAG_INT, "xPos", chunk_x),
        (TAG_INT, "zPos", chunk_z),
        (TAG_BYTE_ARRAY, "Blocks", blocks),
        (TAG_BYTE_ARRAY, "Data", data),
        (TAG_BYTE_ARRAY, "SkyLight", skylight),
        (TAG_BYTE_ARRAY, "BlockLight", blocklight),
        (TAG_BYTE_ARRAY, "HeightMap", heightmap),
        (TAG_BYTE, "TerrainPopulated", 1),
        (TAG_LONG, "LastUpdate", 0),
    ]
    root = [
        (TAG_COMPOUND, "Level", level),
    ]
    return serialize_nbt(root)
