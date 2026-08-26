import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from matplotlib import gridspec

def main():

    
    # ================================
    # 1. User settings
    # ================================
    NaF_path = Path("~/marieCurie/EcoRPCchem/data/bakelite/XRD measurements/Entry_00-036-1455.cif").expanduser() #NaF
    NaHF2_path = Path("~/marieCurie/EcoRPCchem/data/bakelite/XRD measurements/Entry_00-074-1612.cif").expanduser() #NaHF2
    samplePath = Path("~/marieCurie/EcoRPCchem/data/bakelite/XRD measurements/yellow_powder.xye").expanduser() #From sample

    wavelength = 1.5406         # Cu K-alpha1 wavelength in Angstroms
    fwhm = 0.15                 # Peak broadening (FWHM in degrees 2theta)

    # ================================
    # 2. Parse the CIF file to extract d and Intensity
    # ================================
    with open(NaF_path, 'r') as f:
        lines_NaF = f.readlines()

    with open(NaHF2_path, 'r') as f:
        lines_NaHF2 = f.readlines()

    #NaF
    d_spacings_NaF = []
    intensities_NaF = []

    #NaHF2
    d_spacings_NaHF2 = []
    intensities_NaHF2 = []

    in_loop = False
    for line in lines_NaF:
        # Detect the start of the peak data loop
        if line.strip().startswith('_pd_peak_d_spacing'):
            in_loop = True
            continue
        # Stop reading if we hit a new data block or comment
        if in_loop and line.strip().startswith('#'):
            break
        if in_loop and line.strip():
            parts = line.split()
            # We expect at least 2 numbers: d and Intensity. 
            # (The 3rd column 'special_details' is usually empty or text)
            if len(parts) >= 2:
                try:
                    d = float(parts[0])
                    i = float(parts[1])
                    d_spacings_NaF.append(d)
                    intensities_NaF.append(i)
                except ValueError:
                    pass  # skip malformed lines

    in_loop = False
    for line in lines_NaHF2:
        # Detect the start of the peak data loop
        if line.strip().startswith('_pd_peak_d_spacing'):
            in_loop = True
            continue
        # Stop reading if we hit a new data block or comment
        if in_loop and line.strip().startswith('#'):
            break
        if in_loop and line.strip():
            parts = line.split()
            # We expect at least 2 numbers: d and Intensity. 
            # (The 3rd column 'special_details' is usually empty or text)
            if len(parts) >= 2:
                try:
                    d = float(parts[0])
                    i = float(parts[1])
                    d_spacings_NaHF2.append(d)
                    intensities_NaHF2.append(i)
                except ValueError:
                    pass  # skip malformed lines

    d_spacings_NaF = np.array(d_spacings_NaF)
    intensities_NaF = np.array(intensities_NaF)

    d_spacings_NaHF2 = np.array(d_spacings_NaHF2)
    intensities_NaHF2 = np.array(intensities_NaHF2)

    # ================================
    # 3. Convert d to 2θ using Bragg's Law: λ = 2d sin(θ)
    # ================================
    # Note: arcsin expects radians, we convert final result to degrees
    theta_NaF = np.arcsin(wavelength / (2 * d_spacings_NaF))
    two_theta_NaF = 2 * theta_NaF * 180 / np.pi

    theta_NaHF2 = np.arcsin(wavelength / (2 * d_spacings_NaHF2))
    two_theta_NaHF2 = 2 * theta_NaHF2 * 180 / np.pi

    # ================================
    # 4. Open the data file and load to a pandas df
    # ================================  
    #dfSample = pd.read_csv(samplePath, sep ='    ')
    dfSample = pd.read_csv(samplePath, sep=r'\s+', header=None, comment='#',names=['x', 'y', 'error'])
    dfSample['y_norm_1000'] = dfSample['y'] / dfSample['y'].max() * 1000
    print(dfSample)

    # ================================
    # 5. Plot the stick pattern
    # ================================
    plt.figure(figsize=(12, 5))
    plt.stem(two_theta_NaF, intensities_NaF, basefmt=" ", linefmt='r--', markerfmt="", label='NaF diffraction pattern')
    plt.stem(two_theta_NaHF2, intensities_NaHF2, basefmt=" ", linefmt='b--', markerfmt="",label='NaHF2 diffraction pattern')
    plt.plot(dfSample.x,dfSample.y_norm_1000)
    plt.xlabel('2θ (degrees)', fontsize=12)
    plt.ylabel('Intensity (a.u.)', fontsize=12)
    #plt.title(f'XRD Pattern from {NaF_path} (Cu Kα, λ={wavelength} Å)', fontsize=14)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()

    save = True
    if save:
        plt.savefig("../../plots/XRD_spectrum_yellowDust.pdf")

    plt.show()
   

if __name__ == "__main__":
    main()