# UV Overlapper

A Blender addon that stacks selected UV islands so every island's centroid lands at their collective center.

## Installation

1. Download or clone this repository
2. In Blender, go to **Edit > Preferences > Add-ons > Install**
3. Select the `uv_overlapper` folder (or zip it first)
4. Enable **UV: UV Overlapper**

## Usage

1. Select your mesh object and enter **Edit Mode**
2. Open the **UV Editor**
3. Select the UV islands you want to overlap
4. Run via either:
   - **UV menu > Overlap Selected Islands**
   - **N-panel > Overlapper tab > Overlap Selected Islands**

All selected islands will be translated so their centroids meet at a single point — useful for stacking repeated geometry (bolts, rivets, tiles, etc.) to share the same UV space.

## Requirements

- Blender 4.0+
