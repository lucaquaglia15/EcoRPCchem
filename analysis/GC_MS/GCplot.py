import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import sys


def main():
    #Path where the files are stored
    beforeExposureMain = "/Users/Luca/marieCurie/EcoRPCchem/data/GC_MS_analyses_materialExposure/Unexposed_to_RPC_-_Main.CSV"
    afterExposureMain = "/Users/Luca/marieCurie/EcoRPCchem/data/GC_MS_analyses_materialExposure/Exposed_to_RPC_-_Main.CSV"

    dfBeforeExposureMain = pd.read_csv(beforeExposureMain, sep=',', header=None,skiprows=3,index_col=0)
    dfBeforeExposureMain.columns = ["counts"]
    dfBeforeExposureMain.index.names = ["time"]
    print(dfBeforeExposureMain)

    dfAfterExposureMain = pd.read_csv(afterExposureMain, sep=',', header=None,skiprows=3,index_col=0)
    dfAfterExposureMain.columns = ["counts"]
    dfAfterExposureMain.index.names = ["time"]
    print(dfAfterExposureMain)

    fig, ax = plt.subplots(1,1) 
    ax.plot(dfAfterExposureMain.index,dfAfterExposureMain['counts'],linestyle="-",color="orange",label='After Exposure')
    ax.plot(dfBeforeExposureMain.index,dfBeforeExposureMain['counts'],linestyle="-",color="blue",label='Before Exposure')
    ax.set_yscale('log')
    ax.grid(True, which="both",alpha=0.4)
    ax.set_xlabel("Time")
    ax.set_ylabel('Counts')
    ax.legend()
    plt.show()

if __name__ == "__main__":
    main()