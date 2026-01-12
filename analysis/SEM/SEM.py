import csv
import matplotlib.pyplot as plt
import numpy as np
import scipy as s

def main():

    #If true -> debug printouts enabled
    debug = False

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

    #Path to spectrum csv file
    path = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/SEM_measurements_December2025_w49/csvSpectra/S1_G1/Area 1/Full Area 1_1.csv"

    #Load spectrum into np array
    spectrum = np.genfromtxt(path, delimiter = ',')

    energy, counts = np.genfromtxt(path,delimiter=',',unpack=True)

    if debug:
        print("Energy:",energy)
        print("Counts:",counts)

    plt.hist(energy,bins=4096,weights=counts,histtype='step')

    plt.xlabel("Energy [keV]")
    plt.ylabel("Counts")
    plt.yscale("log")  # Convert y-axis to logarithmic scale
    plt.show()

if __name__ == "__main__":
    main()