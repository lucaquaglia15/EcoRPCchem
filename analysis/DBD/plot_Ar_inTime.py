import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
#To find vertices of quadrilateral
from quadrilateral_fitter import QuadrilateralFitter
from scipy.signal import butter, sosfiltfilt
import os
from pathlib import Path
import sys
import json

def open_files(dataPathC1,dataPathC2,dataPathF1,dataPathF2,timeShift,ampShift):

    print(dataPathC1)

    #exC1 = dataPath + "C1-500-ar-12-slm-00000.csv"
    #exC2 = dataPath + "C2-500-ar-12-slm-00000.csv"
    #exF1 = dataPath + "F1-500-ar-12-slm-00000.csv"
    #exF2 = dataPath + "F2-500-ar-12-slm-00000.csv"

    #Load waveform
    C1 = pd.read_csv(dataPathC1, delimiter = ',',index_col=0,skiprows=5)
    C1.columns = ["Amplitude"]
    C1.index.names = ["Time"]

    C2 = pd.read_csv(dataPathC2, delimiter = ',',index_col=0,skiprows=5)
    C2.columns = ["Amplitude"]
    C2["Amplitude"] = C2["Amplitude"]/10.
    C2.index.names = ["Time"]

    F1 = pd.read_csv(dataPathF1, delimiter = ',',index_col=0,skiprows=5)
    F1.columns = ["Amplitude"]
    F1.index.names = ["Time"]
    
    F2 = pd.read_csv(dataPathF2, delimiter = ',',index_col=0,skiprows=5)
    F2.columns = ["Amplitude"]
    mask = pd.to_numeric(F2["Amplitude"], errors="coerce").isna()
    print(F2.loc[mask, "Amplitude"].map(repr).head(20))
    F2['Amplitude'] = F2['Amplitude'].astype(float)
    F2["Amplitude"] = F2["Amplitude"]/10.
    F2.index.names = ["Time"]

    #Older data only 
    if ampShift:
        C1["Amplitude"] = C1["Amplitude"]+50
        F1["Amplitude"] = F1["Amplitude"]+50
    
    if timeShift:
        C2.index = C2.index + 1.003e-05
        F2.index = F2.index + 1.003e-05

    return C1, C2, F1, F2

#Calculate area inside the parallelogram
def polygon_area(vertices):
    x = vertices[:, 0]
    y = vertices[:, 1]

    return 0.5 * abs(
        np.dot(x, np.roll(y, -1))
        - np.dot(y, np.roll(x, -1))
    )

#Compute intersection between lines
def line_intersection(line1, line2):
    m1, b1 = line1[:2]
    m2, b2 = line2[:2]

    x = (b2 - b1) / (m1 - m2)
    y = m1 * x + b1

    return np.array([x, y])

#Fit each side of the QV plot
def fit_side(x, y, p1, p2, tolerance):
    x1, y1 = p1
    x2, y2 = p2

    dx = x2 - x1
    dy = y2 - y1

    length = np.sqrt(dx**2 + dy**2)

    # Unit vector along the side
    ux = dx / length
    uy = dy / length

    # Vector from p1 to every experimental point
    px = x - x1
    py = y - y1

    # Position of each point along the side
    projection = px * ux + py * uy

    # Perpendicular distance from the line
    distance = np.abs(px * uy - py * ux)

    # Only keep points close to the side AND between its endpoints
    mask = (
        (distance <= tolerance) &
        (projection >= 0) &
        (projection <= length)
    )

    x_selected = x[mask]
    y_selected = y[mask]

    # Linear regression
    m, b = np.polyfit(x_selected, y_selected, 1)

    return m, b, mask

#Body of the code
def main():

    baseDebug = True

    #Startup
    print("DBD setup characterization starting!")

    #Path to files
    #20/10/2026 -> Dry Ar + glass (2mm) + single barrier discharge, measurements at different Ar flows and without flow
    data = "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_Ar_no_gas_flow_single_barrier_glass/"

    fig, ax = plt.subplots()
    jet= plt.get_cmap('jet')
    colors = iter(jet(np.linspace(0,1,11)))

    for i in range(11):
        if i < 10:
            dataC1 = data + "C1-3500-ar-0000" + str(i)  + ".csv"
            dataC2 = data + "C2-3500-ar-0000" + str(i)  + ".csv"
            dataF1 = data + "F1-3500-ar-0000" + str(i)  + ".csv"
            dataF2 = data + "F2-3500-ar-0000" + str(i)  + ".csv"
        else:
            dataC1 = data + "C1-3500-ar-000" + str(i)  + ".csv"
            dataC2 = data + "C2-3500-ar-000" + str(i)  + ".csv"
            dataF1 = data + "F1-3500-ar-000" + str(i)  + ".csv"
            dataF2 = data + "F2-3500-ar-000" + str(i)  + ".csv"

        #Open files and save to df
        #data, timeShift, ampShift
        C1, C2, F1, F2 = open_files(dataC1,dataC2,dataF1,dataF2,True,True)

        #Reduce the data from four periods to one to see if the oscillations in the QV plot are reduced
        reduceToOnePeriod = True
        start = 0.00
        end = 0.0025
    
        if reduceToOnePeriod:
            C1 = C1[(C1.index >= start) & (C1.index <= end)]
            C2 = C2[(C2.index >= start) & (C2.index <= end)]
            F1 = F1[(F1.index >= start) & (F1.index <= end)]
            F2 = F2[(F2.index >= start) & (F2.index <= end)]
            F1.drop(F1.tail(1).index,inplace=True) # drop last n rows

        
        #QV plot with not fits
        ax.plot(F1["Amplitude"], F2["Amplitude"],",",color=next(colors),label="Measurement # " + str(i))
        ax.set_xlabel('Amplitude [V]')
        ax.set_ylabel(r'Charge [$\mu$C]')
        ax.grid(linestyle = '--', color = 'lightgrey')
    

    #Show all plots
    handles, labels = ax.get_legend_handles_labels()
    custom_handles = [Line2D([], [], color=h.get_color(),marker='o',linestyle='None',markersize=6,label=label)
        for h, label in zip(handles, labels)
    ]

    ax.legend(handles=custom_handles)
    plt.show()

if __name__ == "__main__":
    main()