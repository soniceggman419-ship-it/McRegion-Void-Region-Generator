# McRegion Void Region Generator

Generates valid Minecraft Beta-era `.mcr` region files where every block is air. Uses only Python's standard library.

## Quick Start

```bash
# Generate the 4 spawn regions (-1,-1 to 0,0)
python3 make_void_region.py --spawn

# Add the 12 surrounding regions (no gaps)
python3 make_void_region.py --nextspawn

# Or generate all 16 at once
python3 make_void_region.py --spawn --nextspawn
```

Files are saved to `world/region/` by default, matching the Minecraft world save layout.

## Modes

| Mode | What it generates |
|---|---|
| `--spawn` | 4 regions around world origin (r.-1.-1 through r.0.0) — full 1024 chunks each |
| `--nextspawn` | 12 regions immediately surrounding the spawn regions (no holes) |
| `--spawn --nextspawn` | All 16 regions from -2,-2 to 1,1 |
| `--region-x N --region-z N` | A single specific region |
| `--pos-x X --pos-z Z --radius R` | All regions covering a player position plus a radius in blocks |

## Output

Default: `world/region/r.{x}.{z}.mcr`

```
world/
  region/
    r.-1.-1.mcr
    r.-1.0.mcr
    r.0.-1.mcr
    r.0.0.mcr
    ...
```

Copy the `world/` folder into your Minecraft Beta saves directory.

## Flags

| Flag | Effect |
|---|---|
| `--overwrite` | Replace existing region files |
| `--skip-existing` | Leave existing region files untouched |
| `--fill-missing` | Fill empty chunk slots in existing regions with air (preserves existing chunks) |
| `--cwd` | Save files in the current directory instead of `world/region/` |
| `--verbose` | Show progress and file sizes |
| `--min-x`, `--max-x`, `--min-z`, `--max-z` | Only generate chunks within the given chunk coordinate range |

## Examples

```bash
# Single region
python3 make_void_region.py --region-x 0 --region-z 0

# Player at in-game coords, 500 block radius
python3 make_void_region.py --pos-x 100 --pos-z -200 --radius 500

# Only spawn chunks, then fill the rest of the region later
python3 make_void_region.py --spawn --min-x -8 --max-x -5 --min-z -8 --max-z -5
python3 make_void_region.py --spawn --fill-missing

# Flat output in current directory
python3 make_void_region.py --spawn --cwd

# Skip regions that already exist
python3 make_void_region.py --nextspawn --skip-existing

# Step by step: spawn, then surrounding, then more
python3 make_void_region.py --spawn
python3 make_void_region.py --nextspawn --skip-existing
python3 make_void_region.py --pos-x 0 --pos-z 0 --radius 1500 --skip-existing
```

## Files

| File | Purpose |
|---|---|
| `make_void_region.py` | CLI entry point |
| `mcregion.py` | McRegion format packing and fill-missing |
| `chunk.py` | Void air chunk assembly |
| `nbt.py` | NBT serializer (all tag types) |

## Technical Notes

- Each region contains 32x32 = 1024 chunks (512x512 blocks)
- Chunks use zlib compression (type 2)
- All blocks are air (ID 0), skylight is max (0xFF)
- Compatible with Minecraft Beta 1.3 through 1.7.3 (pre-Anvil format)
