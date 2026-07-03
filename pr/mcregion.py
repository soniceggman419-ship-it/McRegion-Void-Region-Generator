import os
import struct
import zlib

SECTOR_SIZE = 4096
HEADER_SIZE = 8192
CHUNKS_PER_REGION = 1024
CHUNKS_PER_DIM = 32


def pack_region(region_x, region_z, chunk_data_func, output_path=None,
                overwrite=False, chunk_filter=None):
    if output_path is None:
        output_path = f"r.{region_x}.{region_z}.mcr"

    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(
            f"{output_path} exists (use --overwrite to force)"
        )

    locations = [0] * CHUNKS_PER_REGION
    timestamps = [0] * CHUNKS_PER_REGION
    chunk_records = []

    for local_z in range(CHUNKS_PER_DIM):
        for local_x in range(CHUNKS_PER_DIM):
            idx = local_z * CHUNKS_PER_DIM + local_x
            chunk_x = region_x * CHUNKS_PER_DIM + local_x
            chunk_z = region_z * CHUNKS_PER_DIM + local_z

            if chunk_filter is not None and not chunk_filter(chunk_x, chunk_z):
                chunk_records.append(None)
                continue

            nbt_data = chunk_data_func(chunk_x, chunk_z)
            compressed = zlib.compress(nbt_data)
            payload = struct.pack('>B', 2) + compressed
            chunk_bytes = struct.pack('>I', len(payload)) + payload
            chunk_records.append(chunk_bytes)

    with open(output_path, 'wb') as f:
        f.write(b'\x00' * HEADER_SIZE)

        current_sector = 2
        for idx, record in enumerate(chunk_records):
            if record is None:
                continue

            pos = f.tell()
            if pos % SECTOR_SIZE != 0:
                f.write(b'\x00' * (SECTOR_SIZE - pos % SECTOR_SIZE))

            sector_offset = current_sector
            f.write(record)

            end_pos = f.tell()
            if end_pos % SECTOR_SIZE != 0:
                f.write(b'\x00' * (SECTOR_SIZE - end_pos % SECTOR_SIZE))

            sector_count = (f.tell() - sector_offset * SECTOR_SIZE) // SECTOR_SIZE
            locations[idx] = (sector_offset << 8) | (sector_count & 0xFF)
            current_sector += sector_count

        f.seek(0)
        for loc in locations:
            f.write(struct.pack('>I', loc))
        for ts in timestamps:
            f.write(struct.pack('>I', ts))

    return output_path


def fill_missing_in_region(region_path, region_x, region_z, chunk_data_func):
    with open(region_path, 'rb') as f:
        file_data = f.read()

    if len(file_data) < HEADER_SIZE:
        file_data += b'\x00' * (HEADER_SIZE - len(file_data))

    locations = []
    for i in range(1024):
        loc = struct.unpack('>I', file_data[i*4:(i+1)*4])[0]
        locations.append(loc)

    timestamps = []
    for i in range(1024):
        ts = struct.unpack('>I', file_data[4096+i*4:4096+(i+1)*4])[0]
        timestamps.append(ts)

    existing = {}
    for idx, loc in enumerate(locations):
        if loc == 0:
            continue
        off = loc >> 8
        cnt = loc & 0xFF
        start = off * SECTOR_SIZE
        end = (off + cnt) * SECTOR_SIZE
        if start < len(file_data):
            existing[idx] = file_data[start:end]

    locations_out = [0] * CHUNKS_PER_REGION
    tmp_path = region_path + '.tmp'

    with open(tmp_path, 'wb') as f:
        f.write(b'\x00' * HEADER_SIZE)
        current_sector = 2

        for idx in range(CHUNKS_PER_REGION):
            if idx in existing:
                chunk_bytes = existing[idx]
            else:
                local_z = idx // CHUNKS_PER_DIM
                local_x = idx % CHUNKS_PER_DIM
                chunk_x = region_x * CHUNKS_PER_DIM + local_x
                chunk_z = region_z * CHUNKS_PER_DIM + local_z
                nbt_data = chunk_data_func(chunk_x, chunk_z)
                compressed = zlib.compress(nbt_data)
                payload = struct.pack('>B', 2) + compressed
                chunk_bytes = struct.pack('>I', len(payload)) + payload

            pos = f.tell()
            if pos % SECTOR_SIZE != 0:
                f.write(b'\x00' * (SECTOR_SIZE - pos % SECTOR_SIZE))

            sector_offset = current_sector
            f.write(chunk_bytes)

            end_pos = f.tell()
            if end_pos % SECTOR_SIZE != 0:
                f.write(b'\x00' * (SECTOR_SIZE - end_pos % SECTOR_SIZE))

            sector_count = (f.tell() - sector_offset * SECTOR_SIZE) // SECTOR_SIZE
            locations_out[idx] = (sector_offset << 8) | (sector_count & 0xFF)
            current_sector += sector_count

        f.seek(0)
        for loc in locations_out:
            f.write(struct.pack('>I', loc))
        for ts in timestamps:
            f.write(struct.pack('>I', ts))

    os.replace(tmp_path, region_path)
    return region_path
