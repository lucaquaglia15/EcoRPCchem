import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from numpy import genfromtxt

#Convert time to datetime
def convertTime(df):
    #df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df.index = pd.to_datetime(df.index,errors="coerce")
    return df
      
#Clean values and remove unit of measure
def cleanValues(dfCol,ext):
    dfCol = dfCol.replace(ext,'', regex=True)
    dfCol = dfCol.astype(float)
    return dfCol

#Apply time filter to data
def timeFilter(df,start,end):
    mask = pd.Series(True, index=df.index)
    if start:
        mask &= df.index >= pd.to_datetime(start)
    if end:
        mask &= df.index <= pd.to_datetime(end)
    
    df_filtered = df.loc[mask]

    return df_filtered

# Main
def main():
    print("Vessel conditions")

    press = "mbar"
    temp = "°C"
    RH = "%"

    vessel_P = "../../data/Absolute pressure in the vessel.csv"
    vessel_RH = "../../data/RH in the vessel.csv"
    vessel_T = "../../data/Temperature inside the vessel.csv"
    lab_P = "../../data/Pressure in the lab.csv"
    lab_T = "../../data/Temperature inside the lab.csv"
    lab_RH = "../../data/RH in the lab.csv"

    #Load CSV files
    #Vessel P
    dfVessel_P = pd.read_csv(vessel_P, sep=',', header=None,skiprows=1,index_col=0)
    dfVessel_P.columns = ["vesselP"]
    dfVessel_P.index.names = ["date"]
    print(dfVessel_P)
    #Vessel RH
    dfVessel_RH = pd.read_csv(vessel_RH, sep=',', header=None,skiprows=1,index_col=0)
    dfVessel_RH.columns = ["vesselRH"]
    dfVessel_RH.index.names = ["date"]
    #Vessel T
    dfVessel_T = pd.read_csv(vessel_T, sep=',', header=None,skiprows=1,index_col=0)
    dfVessel_T.columns = ["vesselT"]
    dfVessel_T.index.names = ["date"]
    #Env pressure
    dfLab_P = pd.read_csv(lab_P, sep=',', header=None,skiprows=1,index_col=0)
    dfLab_P.columns = ["labP"]
    dfLab_P.index.names = ["date"]
    #Env RH
    dfLab_RH = pd.read_csv(lab_RH, sep=',', header=None,skiprows=1,index_col=0)
    dfLab_RH.columns = ["labRH"]
    dfLab_RH.index.names = ["date"]
    #Env T
    dfLab_T = pd.read_csv(lab_T, sep=',', header=None,skiprows=1,index_col=0)
    dfLab_T.columns = ["labT"]
    dfLab_T.index.names = ["date"]

    #Convert time to datetime
    convertTime(dfVessel_P)
    convertTime(dfVessel_RH)
    convertTime(dfVessel_T)
    convertTime(dfLab_P)
    convertTime(dfLab_RH)
    convertTime(dfLab_T)

    #Clean up df values
    for col in dfVessel_P.columns:
        if "vesselP" in col:
            print(col)
            dfVessel_P[col] = cleanValues(dfVessel_P[col],press)
            
    for col in dfVessel_RH.columns:
        if "vesselRH" in col:
            print(col)
            dfVessel_RH[col] = cleanValues(dfVessel_RH[col],RH)
    
    for col in dfVessel_T.columns:
        if "vesselT" in col:
            print(col)
            dfVessel_T[col] = cleanValues(dfVessel_T[col],temp)
    
    for col in dfLab_P.columns:
        if "labP" in col:
            print(col)
            dfLab_P[col] = cleanValues(dfLab_P[col],press)
            
    for col in dfLab_RH.columns:
        if "labRH" in col:
            print(col)
            dfLab_RH[col] = cleanValues(dfLab_RH[col],RH)
    
    for col in dfLab_T.columns:
        if "labT" in col:
            print(col)
            dfLab_T[col] = cleanValues(dfLab_T[col],temp)

    #Time range cut
    time_ranges = {
        1: ("2025-11-08 00:00:00", "2026-02-06 18:00:00"),  #Time range
        #1: (None, None),  #No cut
    }
    start_time, end_time = time_ranges.get(1, (None, None))
   
    #Filter df
    df_filtered_P_vessel = timeFilter(dfVessel_P,start_time,end_time)
    df_filtered_RH_vessel = timeFilter(dfVessel_RH,start_time,end_time)
    df_filtered_T_vessel = timeFilter(dfVessel_T,start_time,end_time)
    df_filtered_P_lab = timeFilter(dfLab_P,start_time,end_time)
    df_filtered_RH_lab = timeFilter(dfLab_RH,start_time,end_time)
    df_filtered_T_lab = timeFilter(dfLab_T,start_time,end_time)

    print(dfVessel_P)

    fig, axes = plt.subplots(nrows=3, ncols=1)

    df_filtered_P_vessel.plot(ax=axes[0],color="blue",label="Pressure in the vessel",grid=True)
    axes[0].legend(["Vessel absolute pressure"])
    axes[0].tick_params(labelrotation=0)
    axes[0].set_ylabel('Pressure [mbar]')
    df_filtered_RH_vessel.plot(ax=axes[1],color="red",label="RH in the vessel",grid=True)
    axes[1].legend(["Vessel RH"])
    axes[1].tick_params(labelrotation=0)
    axes[1].set_ylabel('RH [%]')
    df_filtered_T_vessel.plot(ax=axes[2],color="green",label="Temperature in the vessel",grid=True)
    axes[2].legend(["Vessel temperature"])
    axes[2].tick_params(labelrotation=0)
    axes[2].set_ylabel('Temperature [°C]')
    
    plt.subplots_adjust(left=0.05, right=0.994, 
                    top=0.986, bottom=0.065, 
                    wspace=0.4, hspace=0.250)

    plt.show()

    fig1, axes1 = plt.subplots(nrows=3, ncols=1)

    df_filtered_P_lab.plot(ax=axes1[0],color="blue",label="Pressure in the vessel",grid=True)
    axes1[0].legend(["Lab pressure"])
    axes1[0].tick_params(labelrotation=0)
    axes1[0].set_ylabel('Pressure [mbar]')
    df_filtered_RH_lab.plot(ax=axes1[1],color="red",label="RH in the vessel",grid=True)
    axes1[1].legend(["Lab RH"])
    axes1[1].tick_params(labelrotation=0)
    axes1[1].set_ylabel('RH [%]')
    df_filtered_T_lab.plot(ax=axes1[2],color="green",label="Temperature in the vessel",grid=True)
    axes1[2].legend(["Lab temperature"])
    axes1[2].tick_params(labelrotation=0)
    axes1[2].set_ylabel('Temperature [°C]')
    
    plt.subplots_adjust(left=0.05, right=0.994, 
                    top=0.986, bottom=0.065, 
                    wspace=0.4, hspace=0.250)

    plt.show()

if __name__ == "__main__":
	main()