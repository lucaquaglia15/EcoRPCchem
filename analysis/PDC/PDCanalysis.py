import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import json
import math 

#Show all the keys withing the hdf5 file
def get_all(name):
    print(name)

#Get electrode area
def electrodeArea(diameter):
    return math.pi*((diameter/2)**2)

#Calculate resistivity
def computeResistivity(area, pdc, thickness, voltage):
    res = (area*voltage)/(thickness*pdc)
    return res

#Main
def main():

    path = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/PDC/unaged_old_bakelite"
    #name = "bakelite_test_Luca_q_long.hdf5"
    name = "bakelite_test_Luca_q_500V.hdf5"
    key = "TNone"
    values = "block0_values"
    keyAdditional = "measurement_fixtures" #Key for the additional data (eq time, polarization time, depolarization time, voltage)
    
    #Number of points to be merged
    N = 100

    #Name of HDF5 file
    fileName = path + "/" + name

    with h5py.File(fileName, "r") as f:
        for k in f.keys():
            print(k)
            
        volt = next(iter(f[key]))

        dataPath = f"{key}/{volt}/data_{key}_{volt}/{values}"

        #Load measurement data
        data = f[dataPath][:]

        #Load additional information about the measurement (useful to extract polarization, de-polarization and eq time of the measurement)
        rawAdditionalData = f[keyAdditional][()]

    #Convert additional info to json
    if isinstance(rawAdditionalData, (bytes, bytearray)):
        rawAdditionalData = rawAdditionalData.decode("utf-8")

    additionalData = json.loads(rawAdditionalData)

    #Extract data
    queue = additionalData["MEASUREMENT_QUEUE"][0]

    time_eq   = int(queue["TIME_EQ"])
    time_pol  = int(queue["TIME_POL"])
    time_dpol = int(queue["TIME_DPOL"])
    voltage = float(queue["VOLTAGE_DC"])

    print(time_eq,time_pol,time_dpol,voltage)

    #Thickness of sample directly from data
    thickness = float(additionalData["SAMPLE_THICKNESS_UM"])*1e-3 #in um

    print("Sample thickness from file:",thickness,"mm")

    # All data without filters
    relTime = data[:,1]
    current = data[:,2]

    print("Size of time:",len(relTime)," size of current:",len(current))

    # Mask rows where either x or y is NaN
    mask = ~np.isnan(relTime) & ~np.isnan(current)

    relTime_clean = relTime[mask]
    current_clean = current[mask]

    t0 = 0 #start
    t1 = time_eq #equilibrium time
    t2 = time_eq + time_pol #polarization
    t3 = time_eq + time_pol + time_dpol #de-polarization

    print("Size of time after cleaning:",len(relTime_clean)," size of current after cleaning:",len(current_clean))

    # Interval 1: 0 → 1800
    mask1 = (relTime_clean >= t0) & (relTime_clean < t1)
    # Interval 2: 1800 → 19800
    mask2 = (relTime_clean >= t1) & (relTime_clean < t2)
    # Interval 3: 19800 → 37800
    mask3 = (relTime_clean >= t2) & (relTime_clean < t3)

    eqTime_clean, eqCurrent_clean = relTime_clean[mask1], current_clean[mask1]
    polTime_clean, polCurrent_clean = relTime_clean[mask2], current_clean[mask2]
    dpolTime_clean, dpolCurrent_clean = relTime_clean[mask3], current_clean[mask3]

    #Rescale so that all times start from 0
    polTime_clean = polTime_clean - polTime_clean[0]
    dpolTime_clean = dpolTime_clean - dpolTime_clean[0]

    print("Before moving average:")
    print("Size of equilibrium time:",len(eqTime_clean)," size of eq. current after cleaning:",len(eqCurrent_clean))
    print("Size of polarization time:",len(polTime_clean)," size of pol. current after cleaning:",len(polCurrent_clean))
    print("Size of depolarization time:",len(dpolTime_clean)," size of depol. current after cleaning:",len(dpolCurrent_clean))

    #Moving average every N samples for polarization current
    nPolTime = len(polTime_clean) // N
    nPolCurrent = len(polCurrent_clean) // N
    polTime_clean_trim = polTime_clean[:nPolTime * N]
    polCurrent_clean_trim = polCurrent_clean[:nPolCurrent * N]
    polTime_clean_binned = np.nanmean(polTime_clean_trim.reshape(nPolTime, N), axis=1)
    polCurrent_clean_binned = np.nanmean(polCurrent_clean_trim.reshape(nPolCurrent, N), axis=1)

    #Moving average every N samples for de-polarization current
    ndPolTime = len(dpolTime_clean) // N
    ndPolCurrent = len(dpolCurrent_clean) // N
    dpolTime_clean_trim = dpolTime_clean[:ndPolTime * N]
    dpolCurrent_clean_trim = dpolCurrent_clean[:ndPolCurrent * N]
    dpolTime_clean_binned = np.nanmean(dpolTime_clean_trim.reshape(ndPolTime, N), axis=1)
    dpolCurrent_clean_binned = np.nanmean(dpolCurrent_clean_trim.reshape(ndPolCurrent, N), axis=1)

    print("After moving average:")
    #print("Size of equilibrium time:",len(eqTime_clean)," size of eq. current after cleaning:",len(eqCurrent_clean))
    print("Size of polarization time:",len(polTime_clean_binned)," size of pol. current after cleaning:",len(polCurrent_clean_binned))
    print("Size of depolarization time:",len(dpolTime_clean_binned)," size of depol. current after cleaning:",len(dpolCurrent_clean_binned))
    print("Last x value of pol current after rebin:",polTime_clean_binned[-1])
    print("Last x value of dpol current after rebin:",dpolTime_clean_binned[-1])

    #Subtraction. 
    #Get the avergae of pol current over the last 1000 seconds
    #Seconds in which to get average
    DT = 1000

    tPolCurrEnd = polTime_clean_binned[-1]
    tPolCurrStart = tPolCurrEnd - DT

    maskPolCurr = polTime_clean_binned >= tPolCurrStart

    polcurrentLast = polCurrent_clean_binned[maskPolCurr]

    mean_polCurr = np.nanmean(polcurrentLast)
    n_points_meanPolcurr = len(polcurrentLast)

    #Get the avergae of dpol current over the last 1000 seconds
    tdPolCurrEnd = dpolTime_clean_binned[-1]
    tdPolCurrStart = tdPolCurrEnd - DT

    maskdPolCurr = dpolTime_clean_binned >= tdPolCurrStart

    dpolcurrentLast = dpolCurrent_clean_binned[maskdPolCurr]

    mean_dpolCurr = np.nanmean(dpolcurrentLast)
    n_points_meandPolcurr = len(dpolcurrentLast)

    #PDC current
    pdc = mean_polCurr-mean_dpolCurr

    #Calculate resistivity
    area = electrodeArea(8.4) #Diameter in cm
    resistivity = computeResistivity(area, pdc, thickness*1e-1, voltage)

    #Printouts
    print("Mean pol current:",mean_polCurr,"with number of points:",n_points_meanPolcurr)
    print("Mean dpol current:",mean_dpolCurr,"with number of points:",n_points_meandPolcurr)
    print("PDC current:",pdc)
    print("Resistivity:","{:e}".format(resistivity),"Ohm*cm")

    """
    n = min(len(polCurrent_clean_binned), len(dpolCurrent_clean_binned))
    print("minimum length of the lists:",n)

    timeDiff = polTime_clean_binned[:n]
    PDCcurret = polCurrent_clean_binned[:n] + dpolCurrent_clean_binned[:n]
    print(timeDiff)

    print("Size of timeDiff:",len(timeDiff),", size of current subtraction:",len(PDCcurret))
    """
    
    #Plot
    fig = plt.figure()
    ax = fig.add_subplot(111)
    axes = plt.gca()
    plt.plot(polTime_clean_binned, polCurrent_clean_binned, marker="o", linestyle="none",c="green",alpha=0.5,label="Polarization current")
    plt.plot(dpolTime_clean_binned, dpolCurrent_clean_binned, marker="o", linestyle="none",c="red",alpha=0.5,label="Depolarization current")
    #plt.plot(timeDiff, PDCcurret, marker="o", linestyle="none",c="blue")
    maxY = axes.get_ylim()[1]
    minY = axes.get_ylim()[0]
    rect1 = matplotlib.patches.Rectangle((tPolCurrStart,float(minY)),DT,float(maxY-minY),color="grey",alpha=0.2)
    ax.add_patch(rect1)
    ax.legend()
    
    plt.xlabel("Time [s]")
    plt.ylabel("Current [A]")
    plt.grid(True)
    plt.title("Polarization, de-polarization currents")
    plt.show()
    
if __name__ == "__main__":
    main()

    
   