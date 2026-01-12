import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from peakutils import indexes
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
                    tempEn.append(float(temp)*1e-3)

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
    path = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/SEM_measurements_December2025_w49/csvSpectra/S1_G1/Area 1/Full Area 1_1.csv"

    energy, counts = np.genfromtxt(path,delimiter=',',unpack=True)

    if debug:
        print("Energy:",energy)
        print("Counts:",counts)

    #Load spectrum to find peaks
    spectrum = pd.read_csv(path, delimiter = ',',index_col=0)
    spectrum.columns = ["Counts"]
    spectrum.index.names = ['Energy']
    
    if debug:
        print(spectrum)

    #peak utils peak find parameters
    mdist = 1
    thres_ = 0.03

    p1 = indexes(spectrum.Counts.values, min_dist=mdist,thres=thres_)
    print(spectrum.iloc[p1])

    #Raw spectrum
    #spectrum.plot()

    #With peaks
    spectrum.plot()
    
    sns.scatterplot(data=spectrum.iloc[p1],
                    x = "Energy",
                    y = "Counts",
                    color = "red")
    
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