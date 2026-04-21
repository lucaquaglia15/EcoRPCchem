import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path

#Plot data from elemental map analysis
def main():

    debug = False
    
    path = Path("~/marieCurie/EcoRPCchem/data/bakelite/S1/S1_B1/csv_spectra_S1_B1/Area 5 10 kV/Live Map 1_Roi_C K_ImageView_1.csv").expanduser()

    #Get data in df
    counts = pd.read_csv(path, delimiter = ',', skiprows=4, index_col=0)
    print(counts)

    #Convert index and columns
    counts.index = pd.to_numeric(counts.index, errors="coerce")
    counts.columns = pd.to_numeric(counts.columns, errors="coerce")

    #Convert all values to numeric
    counts = counts.apply(pd.to_numeric, errors="coerce")
    #Drop Nan seen inthe last columns
    counts = counts.dropna(axis=1, how="all")

    if debug:
        print(counts.dtypes)
        print("Any NaNs:", counts.isna().any().any())
    
    #Transpose df because original image is 61x128
    counts_T = counts.T

    if debug:
        print(counts_T)

    #Get values for plot
    x = counts_T.index.to_numpy(float) #x = index of the df
    y = counts_T.columns.to_numpy(float) #y = column of the df
    values = counts_T.to_numpy(float) #values
    values_flipped = np.flipud(values) #flip values to match original image

    #2D histogram
    plt.figure(figsize=(8, 6))
    plt.pcolormesh(y, x, values_flipped, shading='nearest',cmap='nipy_spectral')
    plt.colorbar(label="Counts")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("2D Histogram")
    plt.show()
    
    #gets the i-th row of the df (starting from 0)
    #print(counts.iloc[0]) 

    #This syntax gets the first column of the df
    #print(counts.iloc[:, 0])
    
if __name__ == "__main__":
    main()