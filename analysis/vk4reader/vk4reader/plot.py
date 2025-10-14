import matplotlib.pyplot as plt

def show(data, layer="height", cmap="viridis"):
    """Display a layer from vk4 data dict"""
    arr = data.get(layer)
    if arr is None:
        raise ValueError(f"No layer named {layer}")
    plt.imshow(arr, cmap=cmap)
    plt.title(layer)
    plt.colorbar()
    plt.show()