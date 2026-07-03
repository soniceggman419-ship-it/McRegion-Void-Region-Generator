# Project Specification: McRegion (.mcr) Void Region Generator

## Overview

Develop a standalone Python utility that generates valid Minecraft
McRegion (`.mcr`) files containing fully generated chunks where every
block is air (a true void region). The generated files should be
compatible with Minecraft versions that use the McRegion format
(primarily Beta-era versions before the Anvil `.mca` format).

The generator should use only Python's standard library.

## Goals

-   Produce valid `.mcr` region files.
-   Generate all 1024 chunks (32×32) within each region.
-   Mark every chunk as generated.
-   Fill every block with air.
-   Follow the McRegion specification exactly.
-   Support arbitrary region coordinates.

## Command Line

``` text
python make_void_region.py --region-x 0 --region-z 0
```

Outputs:

``` text
r.0.0.mcr
```

Optional flags: - `--output` - `--overwrite` - `--verbose` - `--min-x`,
`--max-x` - `--min-z`, `--max-z`

## McRegion Layout

-   8 KiB header.
-   First 4096 bytes: chunk location table.
-   Second 4096 bytes: timestamp table.
-   1024 chunks (32×32).

Each location entry: - 3-byte sector offset - 1-byte sector count

## Chunk Storage

Each chunk consists of: 1. 4-byte big-endian length 2. 1-byte
compression type (`2` = zlib) 3. Compressed NBT payload

## Chunk Coordinates

    chunkX = regionX * 32 + localChunkX
    chunkZ = regionZ * 32 + localChunkZ

## Required NBT Support

Implement a serializer for: - TAG_End - TAG_Byte - TAG_Short - TAG_Int -
TAG_Long - TAG_Float - TAG_Double - TAG_Byte_Array - TAG_String -
TAG_List - TAG_Compound

Root compound contains a `Level` compound.

Required fields: - `xPos` - `zPos` - `Blocks` - `Data` - `SkyLight` -
`BlockLight` - `HeightMap` - `TerrainPopulated` - `LastUpdate`

## Chunk Arrays

### Blocks

-   32768 bytes
-   All values = `0`

### Data

-   16384 bytes
-   All zero

### SkyLight

-   16384 bytes
-   All bytes = `0xFF`

### BlockLight

-   16384 bytes
-   All zero

### HeightMap

-   256 bytes
-   All zero

### TerrainPopulated

-   `1`

### LastUpdate

-   `0`

## Compression

Use `zlib.compress()`.

Store: 1. 4-byte big-endian length 2. Compression type (`2`) 3.
Compressed data

## Sector Packing

-   Chunks begin on 4096-byte sector boundaries.
-   Pad unused bytes with zeros.
-   Populate header offsets and sector counts.

## Timestamp Table

Store either: - Current Unix timestamp - `0`

## Validation

Generated files should: - Load in Beta-era Minecraft. - Contain only
air. - Not regenerate. - Align correctly with neighboring regions.

## Suggested Modules

-   `nbt.py` --- serializer
-   `chunk.py` --- chunk generation
-   `mcregion.py` --- region packing
-   `make_void_region.py` --- CLI

## Deliverables

1.  Standalone Python implementation.
2.  Inline documentation.
3.  README.
4.  Verified sample `r.0.0.mcr`.
