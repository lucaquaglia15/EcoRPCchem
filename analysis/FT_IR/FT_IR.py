#Analyze FT-IT spectra

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path
import math
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.patches import Rectangle

def main():

    peaks_sample1 = [3438.16,2972.48,2858.9,1740.80,1638.42,1384.44,1337.,1261.23,1181.3,1136.02,1029.3,802.27,782.67,726.15,516.32,467.43]
    peaks_sample2 = [3437.37,2892.91,2920.33,2851.89,2383.38,2342.87,2307.63,1740.66,1632.,1541.11,1348.49,1261.24,1116.99,1016.31,647.60,466.37]

    #Path where the files are stored
    FTIR_1 = "/Users/Luca/marieCurie/EcoRPCchem/data/bakelite/FT-IR measurements/FTIR 1_0.5mg.csv"
    FTIR_2 = "/Users/Luca/marieCurie/EcoRPCchem/data/bakelite/FT-IR measurements/FTIR 2_0.05mg.csv"

    df_FTIR_1 = pd.read_csv(FTIR_1, sep=';', header=None,skiprows=2,index_col=0)
    df_FTIR_1.columns = ["counts"]
    df_FTIR_1.index.names = ["wavelength"]
    print(df_FTIR_1)

    df_FTIR_2 = pd.read_csv(FTIR_2, sep=';', header=None,skiprows=2,index_col=0)
    df_FTIR_2.columns = ["counts"]
    df_FTIR_2.index.names = ["wavelength"]
    print(df_FTIR_2)

    # Find the closest measured wavenumber for each peak
    idx1 = df_FTIR_1.index.get_indexer(peaks_sample1, method="nearest")
    idx2 = df_FTIR_2.index.get_indexer(peaks_sample2, method="nearest")

    # Extract the corresponding rows
    peak_data1 = df_FTIR_1.iloc[idx1].reset_index()
    peak_data2 = df_FTIR_2.iloc[idx2].reset_index()

    fig, ax = plt.subplots(figsize=(10,6))

    #Sample #1
    ax.plot(df_FTIR_1.index,df_FTIR_1['counts'],linestyle="-",color="blue",label='Sample 1')
    #sns.scatterplot(data=df_FTIR_1.iloc[peaks_sample1].reset_index(),x="wavelength",y="counts",color="red",label="Sample 1 peaks")
    ax.scatter(peak_data1["wavelength"], peak_data1["counts"],color="red", label="Sample 1 peaks", zorder=3,s=5)
    #Sample 2
    ax.plot(df_FTIR_2.index,df_FTIR_2['counts'],linestyle="-",color="orange",label='Sample 2')
    ax.scatter(peak_data2["wavelength"], peak_data2["counts"],color="green", label="Sample 2 peaks", zorder=3,s=5)

    #ax.set_xlabel("Time [min]")
    #ax.set_ylabel('Counts')
    ax.legend(loc='upper left')
    ax.set_yscale('log')
    ax.grid(True,'both',alpha=0.4)

    ax.set_xlabel("Wavelength [cm$^{-1}$]", fontsize=16)
    ax.set_ylabel("Transmittance %", fontsize=16)
    ax.xaxis.set_inverted(True)
    ax.tick_params(axis='x', labelsize=16, rotation=0)
    ax.tick_params(axis='y', labelsize=16)


    saveFig = True
    if saveFig == True:
        plt.savefig("../../plots/FT_IR_sample_1_sample_2.pdf",bbox_inches='tight',dpi=300)

    plt.show()

if __name__ == "__main__":
    main()