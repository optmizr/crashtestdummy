import pandas as pd
import matplotlib.pyplot as plt

def basic_analysis(file_path):
    df = pd.read_csv(file_path)
    # make sure the DateTime column is datetime
    df["DateTime"] = pd.to_datetime(df["DateTime"])
    # make a column for the year
    df["Year"] = df["DateTime"].dt.year
    
    # crashes per year
    crash_counts = df["Year"].value_counts().sort_index()
    # create a plot
    crash_counts.plot(kind="line", title="Crashes Over Time")
    # show the plot
    plt.show()
    
    # fatalities by year
    fatalities_per_year = df.groupby("Year")["Total_Fatalities"].sum()
    fatalities_per_year.plot(kind="bar", title="Total Fatalities Per Year")
    # show the plot
    plt.show()
    
    # most dangerous locations
    top_locations = df["Location_Cleaned"].value_counts().head(10)
    top_locations.plot(kind="bar", title="Top 10 Locations with Most Crashes")
    plt.show()
    
    # most affected airline
    top_operators = df["Operator_Cleaned"].value_counts().head(10)
    top_operators.plot(kind="bar", title="Top 10 Operators with Most Crashes")
    plt.show()
    
    # severity of crashes
    # Avoid division by zero errors by replacing zeros in Total_Aboard with NaN
    df["Survival_Rate"] = (1 - df["Total_Fatalities"] / df["Total_Aboard"]) * 100
    
    # Replace infinite values (-inf) with NaN, then fill NaN with 0
    df["Survival_Rate"].replace([float("inf"), -float("inf")], float("nan"), inplace=True)
    df["Survival_Rate"].fillna(0, inplace=True)
    
    # Plot the distribution of survival rates
    
    plt.figure(figsize=(10, 5))
    df["Survival_Rate"].hist(bins=20, edgecolor="black")
    plt.title("Distribution of Survival Rates")
    plt.xlabel("Survival Rate (%)")
    plt.ylabel("Number of Crashes")
    plt.show()
    
    # worst disasters
    worst_crashes = df.nlargest(10, "Total_Fatalities")[
        ["DateTime", "Location_Cleaned", "Total_Fatalities", "Summary"]
    ]
    print(worst_crashes)
    
    # Saves the plot
    # plt.savefig("crash_trends.png")
