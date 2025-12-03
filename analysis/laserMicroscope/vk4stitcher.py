import numpy as np
from vk4reader import reader
import glob
import re

# Directory containing your V4x4 files
folder = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/laserMicroscope/Unaged Bakelite measurements/S1_B0/50x_Scratch_1/"

# Pattern to extract Y and X indices
pattern = re.compile(r".*Y(\d+)_X(\d+)\.vk4$", re.IGNORECASE)

files = glob.glob(f"{folder}/*.vk4")

tiles = {}  # (Y,X) → height map
max_y = max_x = 0

for f in files:
    print(f)
    m = pattern.match(f)
    if not m:
        print("Skipping file:", f)
        continue
    
    y = int(m.group(1))
    x = int(m.group(2))

    data = reader.load(f)
    Z = data["height"]   # height matrix (H, W)
    
    tiles[(y, x)] = Z
    max_y = max(max_y, y)
    max_x = max(max_x, x)

# Make sure all tiles have the same shape
H, W = next(iter(tiles.values())).shape
print(f"Tile shape: {H}x{W}")

# Create big stitched matrix
Z_big = np.zeros((max_y * H, max_x * W))

for (y, x), Z in tiles.items():
    row_start = (y - 1) * H
    col_start = (x - 1) * W
    Z_big[row_start : row_start + H, col_start : col_start + W] = Z

print("Stitched grid shape:", Z_big.shape)
