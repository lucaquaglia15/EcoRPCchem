import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

#Linear fit
def linear(x, a, b):
    return a * x + b

#Convert time to datetime
def convertTime(df):
    #df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df.index = pd.to_datetime(df.index,errors="coerce")
    return df

def main():

    #Path to data file, bakelite
    path = "../../data/sample_conditioning/dryingSummary.csv"

    #Read as pd 
    dfDryingData = pd.read_csv(path, sep=',', header=None,skiprows=1,index_col=0)

    #Index column + column names
    dfDryingData.index.names = ["date"]
    dfDryingData.columns = ["avgS9","errAvgS9","moistureS9","avgS10","errAvgS10","moistureS10","sqrtT","moistureS9","moistureS10"]

    #Convert index colum to date/time and other columns to numbers
    convertTime(dfDryingData)
    dfDryingData = dfDryingData.apply(pd.to_numeric)

    print(dfDryingData)
    print(dfDryingData.iloc[:, 3])

    #Plot data
    #Avg of S9 +- err on S9 and S10 +- err on S10
    #ax = dfDryingData.plot(x="sqrtT",y="avgS9", marker="o", linestyle="none",c="green")
    ax = dfDryingData.plot(y="avgS9", marker="o", linestyle="none",c="green",label="Sample 1")
    #ax.errorbar(dfDryingData["sqrtT"],dfDryingData["avgS9"],yerr=dfDryingData["errAvgS9"],fmt="none",ecolor="green",capsize=3)
    ax.errorbar(dfDryingData.index,dfDryingData["avgS9"],yerr=dfDryingData["errAvgS9"],fmt="none",ecolor="green",capsize=3)

    #Clean up data in S10 there are some 0 so we change them to none for visualization purposes
    dfDryingDataClean = dfDryingData.assign(S10_clean=dfDryingData.iloc[:, 3].replace(0, np.nan),
                                            S10Error_clean=dfDryingData.iloc[:, 4].replace(0, np.nan),
                                            moistureS9_clean=dfDryingData.iloc[:, 7].replace(-1.0, np.nan),
                                            moistureS10_clean=dfDryingData.iloc[:, 8].replace(-1.0, np.nan),)
    
    #ax.plot(dfDryingDataClean["sqrtT"],dfDryingDataClean["S10_clean"],marker="o",color="red",label="S10",linestyle="none")
    ax.plot(dfDryingDataClean["S10_clean"],marker="o",color="red",label="Sample 2",linestyle="none")
    #ax.errorbar(dfDryingDataClean["sqrtT"],dfDryingDataClean["S10_clean"],yerr=dfDryingDataClean["S10Error_clean"],fmt="none",ecolor="red",capsize=3)
    ax.errorbar(dfDryingData.index,dfDryingDataClean["S10_clean"],yerr=dfDryingDataClean["S10Error_clean"],fmt="none",ecolor="red",capsize=3)
    ax.set_xlabel('Date')
    ax.set_ylabel('Weight [g]')
    plt.grid()
    plt.legend()
    plt.savefig("../../plots/weightInTimeDry.png",bbox_inches='tight',dpi=300)
    plt.show()

    ax1 = dfDryingDataClean.plot(x="sqrtT",y="moistureS9_clean", marker="o", linestyle="none",c="green",label="Moisture content S9")
    ax1.plot(dfDryingDataClean["sqrtT"],dfDryingDataClean["moistureS10_clean"], marker="o", linestyle="none",c="red",label="Moisture content S10")

    #Linear fit
    x = dfDryingDataClean["sqrtT"].values
    y = dfDryingDataClean["moistureS10_clean"].values
    x_min, x_max = 0, 12   # choose your range
    mask = (x >= x_min) & (x <= x_max)
    x_fit = x[mask]
    y_fit = y[mask]
    popt, pcov = curve_fit(linear, x_fit, y_fit)
    a, b = popt
    a_err, b_err = np.sqrt(np.diag(pcov))
    print("a",a,"b",b)
    print("a err",a_err,"b err",b_err)

    x_line = np.linspace(x_fit.min(), x_fit.max(), 200)  # 200 points for a smooth line
    y_line = linear(x_line, a, b)   # linear(x, a, b) = a*x + b
    ax1.plot(x_line, y_line, "k--")  # "k--" = black dashed line

    ax1.set_xlabel(r"$\sqrt{t}$ [h$^{0.5}$]")
    ax1.set_ylabel('Moisture content')
    plt.grid()
    plt.legend()
    plt.savefig("../../plots/moistureContentDrying.png",bbox_inches='tight',dpi=300)
    plt.show()

    #Path to data file glass
    pathGlass = "../../data/sample_conditioning/dryingGlassSummary.csv"

    #Read as pd 
    dfDryingDataGlass = pd.read_csv(pathGlass, sep=',', header=None,skiprows=1,index_col=0)

    #Index column + column names
    dfDryingDataGlass.index.names = ["date"]
    dfDryingDataGlass.columns = ["avgS1_G2","errAvgS1_G2","moistureS1_G2","sqrtT"]

    #Convert index colum to date/time and other columns to numbers
    convertTime(dfDryingDataGlass)
    dfDryingDataGlass = dfDryingDataGlass.apply(pd.to_numeric)

    print(dfDryingDataGlass)
    print(dfDryingDataGlass.iloc[:, 3])

    #Plot data
    #Avg of S1_G2 +- err on S1_G2
    ax = dfDryingDataGlass.plot(y="avgS1_G2", marker="o", linestyle="none",c="green",label="Glass sample")
    ax.errorbar(dfDryingDataGlass.index,dfDryingDataGlass["avgS1_G2"],yerr=dfDryingDataGlass["errAvgS1_G2"],fmt="none",ecolor="green",capsize=3)

    ax.set_xlabel('Date')
    ax.set_ylabel('Weight [g]')
    plt.grid()
    plt.legend()
    plt.savefig("../../plots/weightInTimeDryGlass.png",bbox_inches='tight',dpi=300)
    plt.show()


if __name__ == "__main__":
	main()