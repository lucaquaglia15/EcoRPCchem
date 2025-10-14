import numpy as np
from pathlib import Path
from . import vk4extract  # will be added next

def load(filepath):
    """
    Load a .vk4 file and return a dict with height, light, and color layers.

    Returns:
        {
          "height": np.ndarray,
          "light": np.ndarray,
          "color": np.ndarray,
          "meta": dict
        }
    """
    filepath = Path(filepath)
    with open(filepath, "rb") as f:
        offsets = vk4extract.extract_offsets(f)

        # Extract layers
        height = vk4extract.extract_img_data(offsets, "height", f)
        light = vk4extract.extract_img_data(offsets, "light", f)
        color = vk4extract.extract_color_data(offsets, "peak", f)

        # reshape into matrices
        def make_mat(d):

            if not d or "data" not in d:
                return None
            
            arr = d["data"]
            h, w = d["height"], d["width"]
            total = h * w

            # Handle multi-channel data (e.g. RGB)
            if arr.size == total:
                return arr.reshape(h, w)
            elif arr.size % total == 0:
                n_channels = arr.size // total
                return arr.reshape(h, w, n_channels)
            else:
                raise ValueError(
                    f"Unexpected data size {arr.size} for image {h}x{w} (={total})"
                )

        return {
            "height": make_mat(height),
            "light": make_mat(light),
            "color": make_mat(color),
            "meta": {
                "width": height.get("width"),
                "height": height.get("height"),
                "scaling": height.get("scaling", None),
                "offsets": offsets,
            },
        }
