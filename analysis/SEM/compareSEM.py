#File to merge all .json outputs from all the spots/areas in a gieven sample and area into a global json file

import json
from pathlib import Path
import os
import pandas as pd
import matplotlib.pyplot as plt

def main():

    p1 = Path("~/marieCurie/EcoRPCchem/data/bakelite/S1/S1_B1/csv_spectra_S1_B1/Area 4 10 kV/Full Area 1_1_cleanSpectrum_df.csv").expanduser() #input file path
    p2 = Path("~/marieCurie/EcoRPCchem/data/bakelite/S1/S1_B3/csv_spectra_S1_B3/Area 6 10 kV/Full Area 1_1_cleanSpectrum_df.csv").expanduser() #input file path

    df_p1 = pd.read_csv(p1, index_col=0)
    df_p2 = pd.read_csv(p2, index_col=0)
    # print(df_p1)

    #Broken y axis
    fig, (ax_top, ax_bot) = plt.subplots(
        2,1,
        sharex=True,
        gridspec_kw={
            'height_ratios': [1,3],
            'hspace': 0.05
        }
    )
    
    for ax in (ax_top, ax_bot):
        ax.plot(df_p1.index,df_p1.Counts,color="blue",label="Before exposuew")
        ax.plot(df_p2.index,df_p2.Counts,color="red",alpha=0.8,linestyle='--',label="After exposure")
        ax.grid(True,'both',alpha=0.4)

    ax_bot.set_ylim(0,500)
    ax_top.set_ylim(6000,16000)
    ax_top.spines["bottom"].set_visible(False)
    ax_bot.spines["top"].set_visible(False)
    ax_top.tick_params(bottom=False)
    ax_top.tick_params(labelbottom=False)
    
    #Create y axis line break
    d = .5
    kwargs = dict(
        marker=[(-1, -d), (1, d)],
        markersize=12,
        linestyle="none",
        color="k",
        mec="k",
        mew=1,
        clip_on=False,
    )

    ax_top.plot([0, 1], [0, 0], transform=ax_top.transAxes, **kwargs)
    ax_bot.plot([0, 1], [1, 1], transform=ax_bot.transAxes, **kwargs)
    
    #Set labels
    ax_bot.set_xlabel("Energy (keV)")
    ax_bot.set_ylabel("Counts")
    plt.xlim(0,8)
    ax_top.legend()
    #Write element names, hardcoded to make it easier since anyway this is only to show one or two examples
    ax_top.text(0.26, 1.41e+4, "C", color="black", fontsize=10, ha='center', va='bottom')
    ax_top.text(0.51, 1e+4, "O", color="black", fontsize=10, ha='center', va='bottom')
    plt.text(0.7, 400, "Fe", color="black", fontsize=10, ha='center', va='bottom')
    plt.text(1.04, 340, "Na", color="black", fontsize=10, ha='center', va='bottom')
    plt.text(6.4, 80, "Fe", color="black", fontsize=10, ha='center', va='bottom')

    save = True
    if save:
            plt.savefig("../../plots/comparison_S1_B1_S1_B3_beforeAfterExposure.pdf",bbox_inches='tight',dpi=300)

    plt.show()

    df_p1_copy = df_p1.copy()
    df_p2_copy = df_p2.copy()
    #counts_p1 = df_p1_copy('Counts')
    #counts_p2 = df_p2_copy('Counts')

    df_p1_copy.Counts = df_p1_copy.Counts/df_p1_copy['Counts'].max()
    df_p2_copy.Counts = df_p2_copy.Counts/df_p2_copy['Counts'].max()


    #df_p1_copy = df_p1_copy[df_p1_copy['Counts']/df_p1_copy['Counts'].max()]
    #df_p2_copy = df_p2_copy[df_p2_copy('Counts')/df_p2_copy['Counts'].max()]
    #counts_norm = counts / counts.max()

    fig, ax = plt.subplots()
    ax.plot(df_p1_copy.index,df_p1_copy.Counts,color="blue",label="Before")
    ax.plot(df_p2_copy.index,df_p2_copy.Counts,color="red",alpha=0.5,label="After")
    ax.set_xlim(0,7)
            
    plt.show()



    """
    #Draw element names
    for peak in validPeakindicesNames:
        x = spectrum.index[peak["idx"]]
        y = cleanSpectrum[peak["idx"]]

        target_ax = ax_top if y > 4000 else ax_bot

        target_ax.scatter(x, y, color="red", s=20)

        target_ax.text(
            x,
            y + (0.1*y),
            peak["element"],
            rotation=90,
            ha="center",
            fontsize=8
        )
    """
    

if __name__ == "__main__":
    main()