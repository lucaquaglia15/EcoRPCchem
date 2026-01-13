import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from peakutils import indexes
from peakutils import baseline
from scipy.signal import find_peaks as fp

def main():

    #If true -> debug printouts enabled
    debug = False

    ##############################
    # Load energy emission lines #
    ##############################

    #Path to x-ray emission lines table
    pathEmission = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/xRayEmissions.txt"

    #Dictionary for x-ray emission energy lines
    emissionDict = dict()
    #List to temporarily store energy values and add them to the dictionary
    tempEn = []

    with open(pathEmission, 'r') as emissions:
        for element in emissions:
        
            element = element.replace("\n", "") #Remove trailing \n
            element = element.split("\t") #Split string in list in correspondence of \t
        
            element.pop(0) #Remove first element (number identifier of the element obtained from website: https://physics.uwo.ca/~lgonchar/courses/p9826/xdb.pdf)
            key = element[0] #Key for dictionary
        
            element.pop(0) #remove element name
           
           #Add all emission energy to a temporary list
            for temp in element:
                if temp != '—':
                    tempEn.append(float(temp))

            #Add list to dictionary, key is element name
            emissionDict[key] = tempEn.copy()

            #Clear list for next element
            tempEn.clear() 
    
    if debug:
        print(emissionDict)

    #############################
    # Load spectra from samples #
    #############################

    #Path to spectrum csv file to draw histo
    #path = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/SEM_measurements_December2025_w49/csvSpectra/S1_G1/Area 1/Full Area 1_1.csv"
    path = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/SEM_measurements_December2025_w49/csvSpectra/S1_G1/Area 2/Full Area 1_1.csv"

    energy, counts = np.genfromtxt(path,delimiter=',',unpack=True)

    if debug:
        print("Energy:",energy)
        print("Counts:",counts)

    #Load spectrum to find peaks
    spectrum = pd.read_csv(path, delimiter = ',',index_col=0)
    spectrum.columns = ["Counts"]
    spectrum.index.names = ["Energy"]
    
    if debug:
        print(spectrum)

    #peak utils peak find, not used for now
    """
    mdist = 1
    thres_ = 0.025

    p1 = indexes(spectrum.Counts.values, min_dist=mdist,thres=thres_)
    print(spectrum.iloc[p1])
    """

    #Compute baseline
    deg = 8 #Was 7
    bl = baseline(spectrum.Counts, deg=deg)

    #scipy peak find
    h = 175
    prom = 75 #Was 100 but not working as good
    dist = None #Was 5 but not working as good either

    peakList, _ = fp(x=spectrum.Counts,
               height=h,
               prominence=prom,
               distance=dist)
    
    #Energy values of peaks (in eV)
    peakValues = []
    possibleElements = []
    
    for peak in peakList:
        val = spectrum.index[peak]*1e3
        peakValues.append(val)
        print("values:",val, val - 0.05*val, val + 0.05*val)
        #Identify peaks
        for elName, elEmission in emissionDict.items():
            if any((val - 0.03*val) <= emEnergy <= (val + 0.03*val) for emEnergy in elEmission):
                print("peak index:",peak,"peak value:",val,"eV")
                possibleElements.append(elName)

        print("peak index:",peak,"peak value:",val,"eV. Possible elements:",possibleElements)
        possibleElements.clear()
    
    #Draw with peaks
    spectrum.plot(alpha = 0.5)
    
    sns.scatterplot(data=spectrum.iloc[peakList].reset_index(),
                    x = "Energy",
                    y = "Counts",
                    color = "red", alpha = 0.5)
    
    #Plot baseline
    #plt.plot(spectrum.index.to_numpy(), np.asarray(bl), alpha = 0.2)
    #Plot data - baseline
    #plt.plot(spectrum.index.to_numpy(), np.asarray(spectrum.Counts - bl))
    
    plt.show()

    """
    #Draw histo
    plt.hist(energy,bins=4096,weights=counts,histtype='step')

    plt.xlabel("Energy [keV]")
    plt.ylabel("Counts")
    plt.yscale("log")  # Convert y-axis to logarithmic scale
    plt.show()
    """

if __name__ == "__main__":
    main()