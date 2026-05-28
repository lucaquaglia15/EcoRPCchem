import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

day = input("Which day do you want to visualize? (7,17,24)")
month = input("Which month? (Oct,Nov)?")
year = input("Which year? (2025)")

day = "7"
month = "Nov"
year="2025"

path = Path("~/marieCurie/EcoRPCchem/data/vesselFilling_" + str(month) + "_" + str(day) + "_" + str(year) + "/").expanduser()
fileName = "vessel_pressure_" + str(day) + "_" + str(month) + "_" + str(year) + ".csv"

points = [] #  empty regular list

# Load CSV
df = pd.read_csv(str(path) + "/" + fileName, sep=None, engine="python")
df.columns = df.columns.str.strip()

# Convert time to datetime
df["time"] = pd.to_datetime(df["time"], errors="coerce")

# Helper to clean numeric values
def clean_value(val):
    if isinstance(val, str):
        val = (val.replace("mbar", "")
                  .replace("V", "")
                  .replace("uA", "")
                  .strip())
        return float(val) if val else None
    return val

# Clean pressure column
for col in df.columns:
    if "Pressure moving average" in col:
        df[col] = df[col].apply(clean_value)

#Get the number of pressure points for plots with numbers from 0 to N on ax axis
pressSize = len(df)
print("Size:",pressSize)
print("Enumerate:",enumerate(df["Pressure moving average"]))
print("Shape:",df.shape)

for i in range(0,pressSize):
     points.append(i)

# === DEFINE TIME WINDOW ===
# Use None for start/end if you don’t want filtering
time_ranges = {
    #1: ("2025-10-17 12:00:30", "2025-10-17 16:00:00"),  # Time range
    1: (None, None),  # Time range
}

# Plot data with time filter
for i in range(1, 2):
    press_col = f"Pressure moving average"

    if press_col not in df.columns:
        print(f"Skipping, missing data.")
        continue

    # Get range for this channel
    start_time, end_time = time_ranges.get(i, (None, None))

    mask = pd.Series(True, index=df.index)
    if start_time:
        mask &= df["time"] >= pd.to_datetime(start_time)
    if end_time:
        mask &= df["time"] <= pd.to_datetime(end_time)

    df_filtered = df.loc[mask]

    # Extract data
    points = np.array(points) 
    press_vals = pd.to_numeric(df_filtered[press_col], errors="coerce").to_numpy()

    print(df.shape)

    fig, ax1 = plt.subplots(figsize=(8, 6), dpi=150)
    #ax1.set_title(f"Absolute pressure in the vessel in Time\n({start_time} → {end_time})")
    ax1.set_xlabel("Time [s]")

    # Pressure axis
    #ax1.set_ylabel("Absolute pressure [mbar]", color="tab:blue")
    ax1.set_ylabel("Absolute pressure in the vessel [mbar]")
    ax1.plot(points, press_vals, color="tab:blue", label="Pressure")
    #ax1.tick_params(axis="y", labelcolor="tab:blue")

    fig.tight_layout()
    plt.grid(True, alpha=0.3)
    if day == "7" and month == "Nov" and year == "2025":
        plt.text(355, 960, "Vessel evacuations", fontdict=None, ha="center", fontsize = "small")
        plt.text(840, -30, "Pipe evacuation", fontdict=None, ha="center", fontsize = "small")
        plt.text(1530, 885, "Solution and sample\ninsertion", fontdict=None, ha="center", fontsize = "small")
        plt.text(2640, 160, "CO$_{2}$ partial evacuation/filling", fontdict=None, ha="center", fontsize = "small")
        plt.text(3840, 400, "HFO filling", fontdict=None, fontsize = "small")
        plt.text(4000, 600, "Final CO$_{2}$ filling", fontdict=None, fontsize = "small")
    plt.legend()
    
    save = True
    if save:
        plt.savefig("../../plots/vesselFilling_" + day + "_" + month + "_" + year + ".pdf",format="pdf",bbox_inches='tight',dpi=300)
    
    plt.show()
