import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

#Linear fit
def linear(x, a, b):
    return a * x + b

#Convert time to datetime
def convertTime(df):
    #df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df.index = pd.to_datetime(df.index,errors="coerce",dayfirst=True)
    
    df["date"] = pd.to_datetime(
    df["date"],
    format="%d/%m/%Y %H:%M"
)
    return df

def main():

    #Path to data file
    file_name = "~/marieCurie/EcoRPCchem/data/resistance/resistivity.xlsx" # path to file + file nam
    
    #Names of the sheets
    sSpacers = "Spacers"
    sNewDrying = "New Bakelite drying"
    sOldHumidAir = "Old bakelite humid air"
    sOldWater = "Old bakelite in water"
    sOldAmbient = "Old bakelite ambient"
    sAgedRPC = "Aged RPC"
    sMatExposure = "Material exposure"

    #Load each sheet in a pandas df
    dfSpacers = pd.read_excel(file_name, sheet_name=sSpacers,index_col=0,skiprows=1,usecols="A:N")
    dfNewDrying= pd.read_excel(file_name, sheet_name=sNewDrying,index_col=0,skiprows=1,usecols="A:N") #Ok
    dfOldHumidAir = pd.read_excel(file_name, sheet_name=sOldHumidAir,index_col=0,skiprows=1,usecols="A:N") #Ok
    dfOldWater = pd.read_excel(file_name, sheet_name=sOldWater,index_col=0,skiprows=1,usecols="A:N") #Ok
    dfOldAmbient = pd.read_excel(file_name, sheet_name=sOldAmbient,index_col=0,skiprows=1,usecols="A:N")
    dfAgedRPC_S6_B3 = pd.read_excel(file_name, sheet_name=sAgedRPC,index_col=0,skiprows=1,usecols="A:N")
    dfAgedRPC_S7_B3 = pd.read_excel(file_name, sheet_name=sAgedRPC,index_col=0,skiprows=1,usecols="Q:AD")
    dfMatExposure_S2_B0 = pd.read_excel(file_name, sheet_name=sMatExposure,index_col=0,skiprows=1,usecols="A:N")
    dfMatExposure_S3_B0 = pd.read_excel(file_name, sheet_name=sMatExposure,index_col=0,skiprows=1,usecols="Q:AD")
    dfMatExposure_S8_B4 = pd.read_excel(file_name, sheet_name=sMatExposure,index_col=0,skiprows=1,usecols="AG:AT")

    print(dfOldWater)  # print first 5 rows of the dataframe

    #Index column + column names
    #2025 bakelite drying
    dfNewDrying.index.names = ["date"]
    dfNewDrying.columns = ["resistance","current","avgRes","errAvgRes","resistivity","avgResistivity","errAvgResistivity","voltage",
                            "RH","T","elTime","area","thickness"]
    
    convertTime(dfNewDrying)
    dfNewDrying = dfNewDrying.apply(pd.to_numeric)
    dfNewDrying = dfNewDrying.dropna()

    #Index column + column names
    #Old bakelite in humid air
    dfOldHumidAir.index.names = ["date"]
    dfOldHumidAir.columns = ["resistance","current","avgRes","errAvgRes","resistivity","avgResistivity","errAvgResistivity","voltage",
                            "RH","T","elTime","area","thickness"]
    
    convertTime(dfOldHumidAir)
    dfOldHumidAir = dfOldHumidAir.apply(pd.to_numeric)
    dfOldHumidAir = dfOldHumidAir.dropna()

    #Index column + column names
    #Old bakelite in water
    dfOldWater.index.names = ["date"]
    dfOldWater.columns = ["resistance","current","avgRes","errAvgRes","resistivity","avgResistivity","errAvgResistivity","voltage",
                            "RH","T","elTime","area","thickness"]

    convertTime(dfOldWater)
    dfOldWater = dfOldWater.apply(pd.to_numeric)
    dfOldWater = dfOldWater.dropna()

    #Index column + column names
    #Old bakelite in air reference
    dfOldAmbient.index.names = ["date"]
    dfOldAmbient.columns = ["resistance","current","avgRes","errAvgRes","resistivity","avgResistivity","errAvgResistivity","voltage",
                            "RH","T","elTime","area","thickness"]

    convertTime(dfOldAmbient)
    dfOldAmbient = dfOldAmbient.apply(pd.to_numeric)
    dfOldAmbient = dfOldAmbient.dropna()

    #Index column + column names
    #Aged RPC, S6_B3 S7_B3 
    dfAgedRPC_S6_B3.index.names = ["date"]
    dfAgedRPC_S6_B3.columns = ["resistance","current","avgRes","errAvgRes","resistivity","avgResistivity","errAvgResistivity","voltage",
                            "RH","T","elTime","area","thickness"]

    convertTime(dfAgedRPC_S6_B3)
    dfAgedRPC_S6_B3 = dfAgedRPC_S6_B3.apply(pd.to_numeric)
    dfAgedRPC_S6_B3 = dfAgedRPC_S6_B3.dropna()

    dfAgedRPC_S7_B3.index.names = ["date"]
    dfAgedRPC_S7_B3.columns = ["resistance","current","avgRes","errAvgRes","resistivity","avgResistivity","errAvgResistivity","voltage",
                            "RH","T","elTime","area","thickness"]

    convertTime(dfAgedRPC_S7_B3)
    dfAgedRPC_S7_B3 = dfAgedRPC_S7_B3.apply(pd.to_numeric)
    dfAgedRPC_S7_B3 = dfAgedRPC_S7_B3.dropna()

    #Index column + column names
    #Material exposure
    dfMatExposure_S2_B0.index.names = ["date"]
    dfMatExposure_S2_B0.columns = ["resistance","current","avgRes","errAvgRes","resistivity","avgResistivity","errAvgResistivity","voltage",
                            "RH","T","elTime","area","thickness"]

    convertTime(dfMatExposure_S2_B0)
    dfMatExposure_S2_B0 = dfMatExposure_S2_B0.apply(pd.to_numeric)
    dfMatExposure_S2_B0 = dfMatExposure_S2_B0.dropna()

    dfMatExposure_S3_B0.index.names = ["date"]
    dfMatExposure_S3_B0.columns = ["resistance","current","avgRes","errAvgRes","resistivity","avgResistivity","errAvgResistivity","voltage",
                            "RH","T","elTime","area","thickness"]

    convertTime(dfMatExposure_S3_B0)
    dfMatExposure_S3_B0 = dfMatExposure_S3_B0.apply(pd.to_numeric)
    dfMatExposure_S3_B0 = dfMatExposure_S3_B0.dropna()

    dfMatExposure_S8_B4.index.names = ["date"]
    dfMatExposure_S8_B4.columns = ["resistance","current","avgRes","errAvgRes","resistivity","avgResistivity","errAvgResistivity","voltage",
                            "RH","T","elTime","area","thickness"]

    convertTime(dfMatExposure_S8_B4)
    dfMatExposure_S8_B4 = dfMatExposure_S8_B4.apply(pd.to_numeric)
    dfMatExposure_S8_B4 = dfMatExposure_S8_B4.dropna()

    #print(dfOldWater)

    #Plot data
    #Avg of 
    ax = dfOldWater.plot(y="avgRes", marker="o", linestyle="none",c="green",label="Sample 1")
    ax.plot(dfMatExposure_S2_B0["avgRes"], marker="o", linestyle="none",c="blue",label="Sample 2")
    ax.plot(dfMatExposure_S3_B0["avgRes"], marker="o", linestyle="none",c="pink",label="Sample 3")
    ax.plot(dfMatExposure_S8_B4["avgRes"], marker="o", linestyle="none",c="red",label="Sample 4")
    #ax.errorbar(dfOldWater.index,dfOldWater["avgRes"],yerr=dfOldWater["errAvgRes"],fmt="none",ecolor="green",capsize=3)
    ax.set_yscale('log')
    plt.grid()
    plt.show()
    
    """
    ax.errorbar(dfDryingData.index,dfDryingData["avgS9"],yerr=dfDryingData["errAvgS9"],fmt="none",ecolor="green",capsize=3)

    #Clean up data in S10 there are some 0 so we change them to none for visualization purposes
    dfDryingDataClean = dfDryingData.assign(S10_clean=dfDryingData.iloc[:, 3].replace(0, np.nan),
                                            S10Error_clean=dfDryingData.iloc[:, 4].replace(0, np.nan),
                                            moistureS9_clean=dfDryingData.iloc[:, 7].replace(-1.0, np.nan),
                                            moistureS10_clean=dfDryingData.iloc[:, 8].replace(-1.0, np.nan),)
    
    #ax.plot(dfDryingDataClean["sqrtT"],dfDryingDataClean["S10_clean"],marker="o",color="red",label="S10",linestyle="none")
    ax.plot(dfDryingDataClean["S10_clean"],marker="o",color="red",label="Sample 2",linestyle="none")
    #ax.errorbar(dfDryingDataClean["sqrtT"],dfDryingDataClean["S10_clean"],yerr=dfDryingDataClean["S10Error_clean"],fmt="none",ecolor="red",capsize=3)
    ax.errorbar(dfDryingData.index,dfDryingDataClean["S10_clean"],yerr=dfDryingDataClean["S10Error_clean"],fmt="none",ecolor="red",capsize=3)
    ax.set_xlabel('Date')
    ax.set_ylabel('Weight [g]')
    plt.grid()
    plt.legend()
    plt.savefig("../../plots/weightInTimeDry.png",bbox_inches='tight',dpi=300)
    plt.show()

    ax1 = dfDryingDataClean.plot(x="sqrtT",y="moistureS9_clean", marker="o", linestyle="none",c="green",label="Moisture content S9")
    ax1.plot(dfDryingDataClean["sqrtT"],dfDryingDataClean["moistureS10_clean"], marker="o", linestyle="none",c="red",label="Moisture content S10")

    #Path to data file glass
    pathGlass = "../../data/sample_conditioning/dryingGlassSummary.csv"

    #Read as pd 
    dfDryingDataGlass = pd.read_csv(pathGlass, sep=',', header=None,skiprows=1,index_col=0)

    #Index column + column names
    dfDryingDataGlass.index.names = ["date"]
    dfDryingDataGlass.columns = ["avgS1_G2","errAvgS1_G2","moistureS1_G2","sqrtT"]

    #Convert index colum to date/time and other columns to numbers
    convertTime(dfDryingDataGlass)
    dfDryingDataGlass = dfDryingDataGlass.apply(pd.to_numeric)

    print(dfDryingDataGlass)
    print(dfDryingDataGlass.iloc[:, 3])
    """

if __name__ == "__main__":
	main()