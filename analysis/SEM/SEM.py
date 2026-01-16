import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from peakutils import indexes
from peakutils import baseline
from scipy.signal import find_peaks as fp
from scipy.signal import savgol_filter
from scipy import sparse
from scipy.sparse.linalg import spsolve

#ALS filter from https://stackoverflow.com/questions/29156532/python-baseline-correction-library
def baseline_als(y, lam, p, niter=10):
  L = len(y)
  D = sparse.diags([1,-2,1],[0,-1,-2], shape=(L,L-2))
  w = np.ones(L)
  for i in range(niter):
    W = sparse.spdiags(w, 0, L, L)
    Z = W + lam * D.dot(D.transpose())
    z = spsolve(Z, w*y)
    w = p * (y > z) + (1-p) * (y < z)
  return z

#Main function
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
    #path = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/glass/S1/S1_G1/csv_spectra_S1_G1/Area 1/Full Area 1_1.csv"
    #path = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/bakelite/S8/S8_B1/csv_spectra_S8_B1/Area 1 10 kV/Full Area 1_1.csv"
    path = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/glass/S1/S1_G1/csv_spectra_S1_G1/Area 4_30kV/Full Area 1_1.csv"

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


    ##########################
    # Sav Gol filter on data #
    ##########################
    windowLength = 11 #was 8
    polyOrder = 5 #was 4
    yFilter = savgol_filter(spectrum.Counts,window_length=windowLength,polyorder=polyOrder) 
    print(savgol_filter)
    
    ####################
    # Compute baseline #
    ####################
    #1e+4, 0.01
    bl = baseline_als(yFilter, 1e+4, 0.001, niter=10) 
    cleanSpectrum = yFilter - bl  

    ##################################
    # Find peaks with scipy baseline #
    ##################################

    h = 30 #Was 175 and working good
    prom = 60 #Was 75 and working good
    dist = None #Was 5 but not working as good either

    peakList, info = fp(x=cleanSpectrum,
               height=h,
               prominence=prom,
               distance=dist)
    
    print(info)

    #Energy values of peaks (in eV)
    peakValues = []
    possibleElements = []

    #Check if all elements of emission energy list for one element
    #are present in peak list
    for peak in peakList:
        val = spectrum.index[peak]*1e3
        peakValues.append(val)
        print("values:",val, val - 0.08*val, val + 0.08*val)


    for elName, elEmission in emissionDict.items():
        print("Element:",elName)
        print("peakVlues:",peakValues)

        if all(any(abs(p - r) / r <= 0.08 for p in peakValues)for r in elEmission):
            print("It's a match")
            possibleElements.append(elName)
        else:
            continue
    
    print("Possible elements:",possibleElements)
    
    """
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
    """
    
    #Integrate peaks
    for peakNum in range(len(peakList)):
        lower = info["left_bases"][peakNum]
        upper = info["right_bases"][peakNum]
        print("Peak #:",peakNum,"lower:",lower,"upper:",upper,"area:",np.trapz(spectrum.Counts[lower:upper]))

    #Draw raw spectrum
    spectrum.plot(color="blue",alpha=0.2)
    #Draw with Sav-Gol filter
    plt.plot(spectrum.index.to_numpy(), np.asarray(yFilter),color="green")
    #Draw baseline
    plt.plot(spectrum.index.to_numpy(), np.asarray(bl),color="pink",alpha = 0.2)
    #Plot data - baseline
    plt.plot(spectrum.index.to_numpy(), np.asarray(yFilter - bl),color="grey")
    
    clean_df = pd.DataFrame({"Energy": spectrum.index.values,"Counts": cleanSpectrum})

    sns.scatterplot(data=clean_df.iloc[peakList].reset_index(),
                    x = "Energy",
                    y = "Counts",
                    color = "red")
    
    """
    spectrum.plot(alpha = 0.5)
    
    #2sns.scatterplot(data=spectrum.iloc[peakList].reset_index(),
    #                x = "Energy",
    #                y = "Counts",
    #                color = "red", alpha = 0.5)
    
    sns.scatterplot(data=cleanSpectrum.iloc[peakList].reset_index(),
                    x = "Energy",
                    y = "Counts",
                    color = "red", alpha = 0.5)
    
    #Plot baseline
    plt.plot(spectrum.index.to_numpy(), np.asarray(bl), alpha = 0.2)
    #Plot data - baseline
    plt.plot(spectrum.index.to_numpy(), np.asarray(spectrum.Counts - bl))
    """
    plt.show()

if __name__ == "__main__":
    main()