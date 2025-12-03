
import matplotlib.pyplot as plt
from vk4reader.reader import load
from vk4reader.correction import plane_correction

#Path to the data
data = load("/home/luca/cernbox/marieCurie/EcoRPCchem/data/laserMicroscope/Unaged Bakelite measurements/S4_B0/150x_Oiled_defect.vk4")

height = data["height"]
corrected, plane, coeffs = plane_correction(height)

plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.title("Raw height")
plt.imshow(height, cmap="viridis")
plt.colorbar()

plt.subplot(1,2,2)
plt.title("Plane-corrected")
plt.imshow(corrected, cmap="viridis")
plt.colorbar()
plt.show()