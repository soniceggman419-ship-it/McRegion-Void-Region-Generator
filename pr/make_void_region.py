#!/usr/bin/env python3
import argparse
import math
import os
import sys

from chunk import make_chunk
from mcregion import pack_region, fill_missing_in_region

REGION_BLOCKS = 512
DEFAULT_WORLD_DIR = "world"


def region_path(rx, rz, base_dir):
    if base_dir == ".":
        return f"r.{rx}.{rz}.mcr"
    return os.path.join(base_dir, "region", f"r.{rx}.{rz}.mcr")


def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def block_to_region(block_coord):
    return block_coord // REGION_BLOCKS


def generate_one(rx, rz, base_dir, overwrite, skip_existing, fill_missing,
                 chunk_filter, verbose):
    output_path = region_path(rx, rz, base_dir)
    if skip_existing and os.path.exists(output_path):
        if verbose:
            print(f"  Skipped {output_path} (already exists)")
        return
    if fill_missing and os.path.exists(output_path):
        out_dir = os.path.dirname(output_path)
        if out_dir:
            ensure_dir(output_path)
        result = fill_missing_in_region(output_path, rx, rz, make_chunk)
        if verbose:
            size = os.path.getsize(result)
            print(f"  Filled {result} ({size} bytes)")
        else:
            print(f"Filled {result}")
        return
    out_dir = os.path.dirname(output_path)
    if out_dir:
        ensure_dir(output_path)
    result = pack_region(
        rx, rz, make_chunk,
        output_path=output_path, overwrite=overwrite,
        chunk_filter=chunk_filter,
    )
    if verbose:
        size = os.path.getsize(result)
        print(f"  Created {result} ({size} bytes)")
    else:
        print(f"Created {result}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate void McRegion (.mcr) files"
    )
    parser.add_argument("--region-x", type=int, default=None)
    parser.add_argument("--region-z", type=int, default=None)
    parser.add_argument("--pos-x", type=float, default=None)
    parser.add_argument("--pos-z", type=float, default=None)
    parser.add_argument("--radius", type=float, default=None)
    parser.add_argument("--cwd", action="store_true",
                        help="save region files in current directory instead of world/region/")
    parser.add_argument("--spawn", action="store_true",
                        help="generate the 4 spawn regions (r.-1.-1 through r.0.0)")
    parser.add_argument("--nextspawn", action="store_true",
                        help="generate the 12 regions surrounding the spawn regions")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--skip-existing", action="store_true",
                        help="skip region files that already exist")
    parser.add_argument("--fill-missing", action="store_true",
                        help="fill empty chunk slots in existing region files with air")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--min-x", type=int, default=None)
    parser.add_argument("--max-x", type=int, default=None)
    parser.add_argument("--min-z", type=int, default=None)
    parser.add_argument("--max-z", type=int, default=None)
    args = parser.parse_args()

    use_regions = args.region_x is not None and args.region_z is not None
    use_pos = args.pos_x is not None and args.pos_z is not None and args.radius is not None
    use_spawn = args.spawn
    use_nextspawn = args.nextspawn

    if use_regions and use_pos:
        parser.error(
            "Use either --region-x/--region-z or --pos-x/--pos-z/--radius, not both"
        )
    if not use_regions and not use_pos and not use_spawn and not use_nextspawn:
        parser.error(
            "Provide --region-x/--region-z, --pos-x/--pos-z/--radius, "
            "--spawn, or --nextspawn"
        )

    base_dir = "." if args.cwd else DEFAULT_WORLD_DIR

    chunk_filter = None
    if any(v is not None for v in (args.min_x, args.max_x, args.min_z, args.max_z)):
        def chunk_filter(cx, cz):
            if args.min_x is not None and cx < args.min_x:
                return False
            if args.max_x is not None and cx > args.max_x:
                return False
            if args.min_z is not None and cz < args.min_z:
                return False
            if args.max_z is not None and cz > args.max_z:
                return False
            return True

    if use_regions or use_pos:
        if use_pos:
            min_bx = math.floor(args.pos_x - args.radius)
            max_bx = math.floor(args.pos_x + args.radius)
            min_bz = math.floor(args.pos_z - args.radius)
            max_bz = math.floor(args.pos_z + args.radius)
            min_rx = block_to_region(min_bx)
            max_rx = block_to_region(max_bx)
            min_rz = block_to_region(min_bz)
            max_rz = block_to_region(max_bz)
            if args.verbose:
                total = (max_rx - min_rx + 1) * (max_rz - min_rz + 1)
                print(
                    f"Player at ({args.pos_x}, {args.pos_z}), radius {args.radius} blocks\n"
                    f"  Block area: ({min_bx}, {min_bz}) to ({max_bx}, {max_bz})\n"
                    f"  Region range: ({min_rx}, {min_rz}) to ({max_rx}, {max_rz})\n"
                    f"  Output dir: {base_dir}/region/\n"
                    f"  Generating {total} region{'s' if total != 1 else ''} ..."
                )
            count = 0
            total = (max_rx - min_rx + 1) * (max_rz - min_rz + 1)
            for rz in range(min_rz, max_rz + 1):
                for rx in range(min_rx, max_rx + 1):
                    count += 1
                    if args.verbose:
                        print(f"  [{count}/{total}] ", end="", flush=True)
                    generate_one(rx, rz, base_dir, args.overwrite,
                                 args.skip_existing, args.fill_missing,
                                 chunk_filter, args.verbose)
        else:
            generate_one(args.region_x, args.region_z, base_dir,
                         args.overwrite, args.skip_existing,
                         args.fill_missing, chunk_filter, args.verbose)
        return

    if use_spawn or use_nextspawn:
        spawn_min_rx = -1
        spawn_max_rx = 0
        spawn_min_rz = -1
        spawn_max_rz = 0

        if use_spawn and use_nextspawn:
            min_rx = spawn_min_rx - 1
            max_rx = spawn_max_rx + 1
            min_rz = spawn_min_rz - 1
            max_rz = spawn_max_rz + 1
            label = "Spawn + next spawn regions"
        elif use_spawn:
            min_rx, max_rx = spawn_min_rx, spawn_max_rx
            min_rz, max_rz = spawn_min_rz, spawn_max_rz
            label = "Spawn regions"
        else:
            min_rx = spawn_min_rx - 1
            max_rx = spawn_max_rx + 1
            min_rz = spawn_min_rz - 1
            max_rz = spawn_max_rz + 1
            label = "Next spawn regions"

            def region_filter(rx, rz):
                return not (spawn_min_rx <= rx <= spawn_max_rx and
                            spawn_min_rz <= rz <= spawn_max_rz)

            regions_to_gen = [(rx, rz) for rz in range(min_rz, max_rz + 1)
                              for rx in range(min_rx, max_rx + 1)
                              if region_filter(rx, rz)]
            total = len(regions_to_gen)
            if args.verbose:
                print(
                    f"{label}: generating {total} region{'s' if total != 1 else ''} "
                    f"from range ({min_rx}, {min_rz}) to ({max_rx}, {max_rz})\n"
                    f"  Output dir: {base_dir}/region/\n"
                )
            for idx, (rx, rz) in enumerate(regions_to_gen, 1):
                if args.verbose:
                    print(f"  [{idx}/{total}] ", end="", flush=True)
                generate_one(rx, rz, base_dir, args.overwrite,
                             args.skip_existing, args.fill_missing,
                             chunk_filter, args.verbose)
            return

        total = (max_rx - min_rx + 1) * (max_rz - min_rz + 1)
        if args.verbose:
            print(
                f"{label}: generating regions in range "
                f"({min_rx}, {min_rz}) to ({max_rx}, {max_rz})\n"
                f"  Output dir: {base_dir}/region/\n"
                f"  Generating {total} region{'s' if total != 1 else ''} ..."
            )
        count = 0
        for rz in range(min_rz, max_rz + 1):
            for rx in range(min_rx, max_rx + 1):
                count += 1
                if args.verbose:
                    print(f"  [{count}/{total}] ", end="", flush=True)
                generate_one(rx, rz, base_dir, args.overwrite,
                             args.skip_existing, args.fill_missing,
                             chunk_filter, args.verbose)
        return


if __name__ == "__main__":
    main()
