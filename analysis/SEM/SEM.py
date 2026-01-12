import csv
import matplotlib.pyplot as plt
import numpy as np
import scipy as s

def main():

    #Path to x-ray emission lines table
    pathEmission = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/xRayEmissions.txt"

    #Dictionary for x-ray emission energy lines
    emissionDict = dict()
    #List to temporarily store energy values and add them to the dictionary
    tempEn = []

    with open(pathEmission, 'r') as emissions:
        for line in emissions:
        
            line = line.replace("\n", "") #Remove trailing \n
            line = line.split("\t") #Split string in list in correspondence of \t
        
            line.pop(0) #Remove first element (number identifier of the element obtained from website: https://physics.uwo.ca/~lgonchar/courses/p9826/xdb.pdf)
            key = line[0] #Key for dictionary
        
            line.pop(0) #remove element name
           
           #Add all emission energy to a temporary list
            for temp in line:
                if temp != '—':
                    print("temp in loop:",temp)
                    tempEn.append(float(temp))
            print("tempEn:",tempEn)

            emissionDict.update({key: tempEn}) 

            tempEn.clear() 
    
    print(emissionDict)

    #Path to spectrum csv file
    path = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/SEM_measurements_December2025_w49/csvSpectra/S1_G1/Area 1/Full Area 1_1.csv"

    #Load spectrum into np array
    spectrum = np.genfromtxt(path, delimiter = ',')

    energy, counts = np.genfromtxt(path,delimiter=',',unpack=True)

    print(energy)
    print(counts)

    plt.hist(energy,bins=4096,weights=counts,histtype='step')

    plt.xlabel('Energy [keV]')
    plt.ylabel('Counts')
    plt.yscale("log")  # Convert y-axis to logarithmic scale
    plt.show()

if __name__ == "__main__":
    main()