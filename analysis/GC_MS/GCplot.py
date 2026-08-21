import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import math
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.patches import Rectangle

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

    fig, ax = plt.subplots(figsize=(10,6))

    ax.plot(dfBeforeExposureMain.index,dfBeforeExposureMain['counts'],linestyle="-",color="blue",label='Before Exposure')
    ax.plot(dfAfterExposureMain.index,dfAfterExposureMain['counts'],linestyle="-",color="orange",label='After Exposure')
    #ax.set_xlabel("Time [min]")
    #ax.set_ylabel('Counts')
    ax.legend(loc='upper left')
    ax.set_yscale('log')
    ax.grid(True,'both',alpha=0.4)

    ax.set_xlabel("Time [min]", fontsize=16)
    ax.set_ylabel("Counts", fontsize=16)
    ax.tick_params(axis='x', labelsize=16, rotation=0)
    ax.tick_params(axis='y', labelsize=16)

    axins = inset_axes(ax,width="35%",height="35%",loc="upper right",bbox_to_anchor=(-0.007, 0, 1, 1),bbox_transform=ax.transAxes)
    axins.plot(dfBeforeExposureMain.index,dfBeforeExposureMain['counts'],linestyle="-",color="blue",label='Before Exposure')
    axins.plot(dfAfterExposureMain.index,dfAfterExposureMain['counts'],linestyle="-",color="orange",label='After Exposure')
    axins.set_xlim(2, 6)
    axins.set_ylim(0, 1.5e+4)
    axins.grid(True,'both',alpha=0.4)

    saveFig = True
    if saveFig == True:
        plt.savefig("../../plots/GC_MS_majorPeaks_beforeAfter.pdf",bbox_inches='tight',dpi=300)

    plt.show()

    #Estimate error on area ratio assuming that the counts are Poissonian and their error is sqrt(N), where N = number of counts
    #HFO-ze counts
    countsHFO_bef = 84632683
    errCountsHFO_bef = int(math.sqrt(countsHFO_bef))
    countsHFO_aft = 52145078
    errCountsHFO_aft = int(math.sqrt(countsHFO_aft))

    #CO2 counts
    countsCO2_bef = 9925232
    errCountsCO2_bef = int(math.sqrt(countsCO2_bef))
    countsCO2_aft = 5921988
    errCountsCO2_aft = int(math.sqrt(countsCO2_aft))

    HFO_CO2_ratio_bef = (countsHFO_bef/countsCO2_bef)
    HFO_CO2_ratio_aft = (countsHFO_aft/countsCO2_aft)

    err_ratio_bef = (1/countsCO2_bef)*math.sqrt(errCountsHFO_bef**2  + (countsHFO_bef**2/countsCO2_bef**2)*errCountsCO2_bef**2)
    err_ratio_aft = (1/countsCO2_aft)*math.sqrt(errCountsHFO_aft**2  + (countsHFO_aft**2/countsCO2_aft**2)*errCountsCO2_aft**2)

    print("HFO bef",countsHFO_bef,errCountsHFO_bef) 
    print("HFO aft",countsHFO_aft,errCountsHFO_aft)
    print("CO2 bef",countsCO2_bef,errCountsCO2_bef)
    print("CO2 bef",countsCO2_aft,errCountsCO2_aft) 
    print("Ratio bef",HFO_CO2_ratio_bef,"+-",err_ratio_bef)
    print("Ratio aft",HFO_CO2_ratio_aft,"+-",err_ratio_aft)  

if __name__ == "__main__":
    main()