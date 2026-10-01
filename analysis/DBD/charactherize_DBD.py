import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#To find vertices of quadrilateral
from quadrilateral_fitter import QuadrilateralFitter
from pathlib import Path
import sys
import json

def open_file(filename):
    return 0

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
    """
    Select experimental points close to the quadrilateral side
    between p1 and p2, then perform a linear fit.
    """

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

    #Scope channels: C1 = HV probe, C2 = capacitor, F1 = avg of C1, F2 = avg of C2
    channels = ["C1","C2","F1","F2"]

    #Path to files
    #30/09/2026 -> Dry air + glass (2 mm) + single barrier discharge, wrong avg settings on the scope
    #when triggering on "single" -> the average was calculated on the single trigger hence it was the same 
    #as the "pure" channel data
    #data = "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_air_30_09_single_barrier_glass/"
    #31/09/2026 -> Dry air + glass (2 mm) + single barrier discharge
    data = "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_air_31_09_single_barrier_glass/"
    
    #Open voltages file and save to a list
    print("Opening voltages file")
    voltagePath = data + "voltages.txt"

    #list for voltages
    voltages = []
    with open(voltagePath, 'r') as voltageValues:
        voltageValues.readline()
        for voltage in voltageValues:
            voltage = voltage.replace("\n", "") #Remove trailing \n
            voltages.append(voltage)

    #Loop through all voltages tested
    for volt in voltages:
        print(volt)

    #Open an example file and plot
    exC1 = data + "C1-test-12800-00003.csv"
    exC2 = data + "C2-test-12800-00003.csv"
    exF1 = data + "F1-test-12800-00003.csv"
    exF2 = data + "F2-test-12800-00003.csv"

    #Load waveform
    C1 = pd.read_csv(exC1, delimiter = ',',index_col=0,skiprows=5)
    C1.columns = ["Amplitude"]
    C1.index.names = ["Time"]

    C2 = pd.read_csv(exC2, delimiter = ',',index_col=0,skiprows=5)
    C2.columns = ["Amplitude"]
    C2["Amplitude"] = C2["Amplitude"]/10.
    C2.index.names = ["Time"]

    F1 = pd.read_csv(exF1, delimiter = ',',index_col=0,skiprows=5)
    F1.columns = ["Amplitude"]
    F1.index.names = ["Time"]
    
    F2 = pd.read_csv(exF2, delimiter = ',',index_col=0,skiprows=5)
    F2.columns = ["Amplitude"]
    F2["Amplitude"] = F2["Amplitude"]/10.
    F2.index.names = ["Time"]

    if baseDebug:
        print(C1)

    #QV plot
    plt.plot(F1["Amplitude"], F2["Amplitude"],".",color="black",label="X-Y plot")
    #plt.set_xlabel('Amplitude [V]')
    #plt.set_ylabel(r'Charge [$\mu$C]')

    #Convert to useful format for QuadrilateralFitter library
    x = F1["Amplitude"].to_numpy()
    y = F2["Amplitude"].to_numpy()

    points = np.column_stack((x, y))
    fitter = QuadrilateralFitter(polygon=points)
    quadrilateral = np.array(fitter.fit())

    # Close the quadrilateral
    quad_closed = np.vstack([quadrilateral, quadrilateral[0]])
    #Plot quadrilateral
    #plt.plot(quad_closed[:, 0],quad_closed[:, 1],"-",color="red",linewidth=2,label="Fitted quadrilateral")
    #Plot four corners
    #plt.plot(quadrilateral[:, 0],quadrilateral[:, 1],"o",color="black")

    print("Quadrilateral:",quadrilateral)

    #Extract sides for linear fit
    tolerance = 0.02
    fits = []

    #Loop on all four sides of the parallelogram
    for i in range(4):
        p1 = quadrilateral[i]
        p2 = quadrilateral[(i + 1) % 4]

        m, b, mask = fit_side(x,y,p1,p2,tolerance)

        fits.append((m, b, mask))

        print(
            f"Side {i+1}: "
            f"slope = {m:.6g}, "
            f"intercept = {b:.6g}, "
            f"N = {mask.sum()}"
        )

    for i, (m, b, mask) in enumerate(fits):

        p1 = quadrilateral[i]
        p2 = quadrilateral[(i + 1) % 4]

        #Plot selected points
        plt.plot(x[mask],y[mask],".",markersize=5,label=f"Side {i+1} points")

        #Plot regression line
        x_line = np.linspace(min(p1[0], p2[0]),max(p1[0], p2[0]),100)

        y_line = m * x_line + b

        plt.plot(x_line,y_line,linewidth=2,label=f"Fit {i+1}: m={m:.4g}")
    plt.legend()

    #Calculate area. First we need the "vertices" i.e. intersection between the four linear fits 
    #and then we apply the function to calculate area
    vertices = []
    for i in range(4):
        line1 = fits[i]
        line2 = fits[(i + 1) % 4]

        vertex = line_intersection(line1, line2)
        vertices.append(vertex)

    vertices = np.array(vertices)

    print("vertices",vertices)

    area = polygon_area(vertices)
    print("Area =", area)

    # Plot vertices
    plt.plot(vertices[:, 0],vertices[:, 1],"o",color="yellow",label="Fitted vertices")
        
    """
    #Plot on 4 separate panels
    ax = C1.plot(color="blue",alpha=0.8,label="Ex C1")
    ax = C2.plot(color="red",alpha=0.8,label="Ex C2")
    ax = F1.plot(color="green",alpha=0.8,label="Ex F1")
    ax = F2.plot(color="orange",alpha=0.8,label="Ex F2")
    plt.plot(C2.index, C2["Amplitude"],color="green",label="C2",alpha=0.2)
    ax.legend()
    """

    #C1 and C2 on the same panel
    fig, axs = plt.subplots()

    p1 = axs.plot(F1.index, F1.Amplitude, '-', label = 'F1', c='green')
    ax1 = axs.twinx()
    p2 = ax1.plot(F2.index, F2.Amplitude, '-', label = 'F2', c='red')
    ax1.tick_params(axis='y')
    axs.set_ylabel('Amplitude [V]')
    ax1.set_ylabel(r'Charge [$\mu$C]')
    axs.set_xlabel('Time')

    l = p1 + p2
    labs = [li.get_label() for li in l]
    axs.legend(l, labs, loc='upper left', fontsize = 8)
    axs.grid(linestyle = '--', color = 'lightgrey')

    plt.show()

if __name__ == "__main__":
    main()