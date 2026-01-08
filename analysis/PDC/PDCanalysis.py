import h5py
import numpy as np
import matplotlib.pyplot as plt

def get_all(name):
    print(name)

def main():

    path = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/PDC/unaged_old_bakelite"
    name = "bakelite_test_Luca_q_long.hdf5"
    key = "TNone"
    volt = "100V"
    values = "block0_values"
    data = "data_" + key + "_" + volt
    dataPath = key + "/" + volt + "/" + data + "/" + values
    
    #Number of points to be merged
    N = 200

    print(dataPath)

    fileName = path + "/" + name

    with h5py.File(fileName, "r") as f:
        #Print list of keys
        for k in f.keys():
            print(k)

        #print("\n")

        data = f[dataPath][:]
    
        #print("\n")

        #Visit all groups
        #f.visit(get_all)

    # Plot the data without filters
    relTime = data[:,1]
    current = data[:,2]

    print("Size of time:",len(relTime)," size of current:",len(current))

    # Mask rows where either x or y is NaN
    mask = ~np.isnan(relTime) & ~np.isnan(current)

    relTime_clean = relTime[mask]
    current_clean = current[mask]

    t0 = 0 #start
    t1 = 1800 #equilibrium time
    t2 = 1800 + 18000 #polarization
    t3 = 1800 + 18000 + 18000 #de-polarization

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

    polTime_clean = polTime_clean - polTime_clean[0]
    dpolTime_clean = dpolTime_clean - dpolTime_clean[0]

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

    print("Before re-binning:")
    print("Size of equilibrium time:",len(eqTime_clean)," size of eq. current after cleaning:",len(eqCurrent_clean))
    print("Size of polarization time:",len(polTime_clean)," size of pol. current after cleaning:",len(polCurrent_clean))
    print("Size of depolarization time:",len(dpolTime_clean)," size of depol. current after cleaning:",len(dpolCurrent_clean))
 
    print("After re-binning:")
    #print("Size of equilibrium time:",len(eqTime_clean)," size of eq. current after cleaning:",len(eqCurrent_clean))
    print("Size of polarization time:",len(polTime_clean_binned)," size of pol. current after cleaning:",len(polCurrent_clean_binned))
    print("Size of depolarization time:",len(dpolTime_clean_binned)," size of depol. current after cleaning:",len(dpolCurrent_clean_binned))

    #Subtraction
    n = min(len(polCurrent_clean_binned), len(dpolCurrent_clean_binned))
    print("minimum length of the lists:",n)

    timeDiff = polTime_clean_binned[:n]
    PDCcurret = polCurrent_clean_binned[:n] + dpolCurrent_clean_binned[:n]
    print(timeDiff)

    print("Size of timeDiff:",len(timeDiff),", size of current subtraction:",len(PDCcurret))


    #Plot
    """
    plt.figure()
    #plt.plot(polTime_clean_binned, polCurrent_clean_binned, marker="o", linestyle="none")
    #plt.plot(dpolTime_clean_binned, dpolCurrent_clean_binned, marker="o", linestyle="none")
    plt.plot(timeDiff, PDCcurret, marker="o", linestyle="none")
    plt.xlabel("Time [s]")
    plt.ylabel("Current")
    plt.title("Current vs Time")
    plt.grid(True)
    plt.show()
    

    """
    fig, ax_left = plt.subplots()

    # Left y-axis plots
    ax_left.plot(polTime_clean_binned, polCurrent_clean_binned, label="Polarization current", color="C0")
    ax_left.plot(timeDiff, PDCcurret, label="Pol - depolarization currents", color="C2")
    ax_left.set_xlabel("Time [s]")
    ax_left.set_ylabel("Pol / Pol-Dep")

    # Right y-axis
    #ax_right = ax_left.twinx()
    #ax_right.plot(dpolTime_clean_binned, dpolCurrent_clean_binned, label="Depolarization current", color="C1")
    #ax_right.set_ylabel("Depolarization current")

    # Combine legends
    lines_left, labels_left = ax_left.get_legend_handles_labels()
    #lines_right, labels_right = ax_right.get_legend_handles_labels()

    """ax_left.legend(
        lines_left + lines_right,
        labels_left + labels_right,
        loc="best"
    )"""

    plt.title("Polarization, de-polarization currents")
    plt.show()
    

if __name__ == "__main__":
    main()

    
   