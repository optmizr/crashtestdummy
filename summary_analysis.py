import pandas as pd
from collections import Counter
import re
import matplotlib.pyplot as plt

# load the data set into a dataframe
file_path = "data/CrashTestInfo_Cleaned.csv"
df = pd.read_csv(file_path)
# make sure the DateTime column is datetime
df["DateTime"] = pd.to_datetime(df["DateTime"])
df["Year"] = df["DateTime"].dt.year

# Combine all summaries into one large text
all_text = " ".join(df["Summary"].dropna()).lower()

# Remove punctuation and split into words
words = re.findall(r"\b\w+\b", all_text)

# Count word frequencies
word_counts = Counter(words)

# Display the most common words
print(word_counts.most_common(50))  # Show top 50 most frequent words


# Define keyword-based crash categories
def categorize_crash(summary):
    summary = str(summary).lower()  # Convert to lowercase

    if any(
        keyword in summary for keyword in ["collision", "midair", "crash into another"]
    ):
        return "Mid-Air Collision"
    elif any(
        keyword in summary
        for keyword in ["engine failure", "mechanical failure", "technical issue"]
    ):
        return "Mechanical Failure"
    elif any(keyword in summary for keyword in ["weather", "storm", "turbulence"]):
        return "Weather-Related"
    elif any(keyword in summary for keyword in ["fire", "explosion", "smoke"]):
        return "Fire/Explosion"
    elif any(
        keyword in summary
        for keyword in ["pilot error", "loss of control", "incorrect maneuver"]
    ):
        return "Pilot Error"
    elif any(keyword in summary for keyword in ["hijacking", "terrorist", "bomb"]):
        return "Hijacking/Terrorism"
    elif any(
        keyword in summary for keyword in ["shot down", "missile", "military attack"]
    ):
        return "Shot Down (War/Conflict)"
    elif any(keyword in summary for keyword in ["runway", "takeoff", "landing"]):
        return "Takeoff/Landing Accident"
    elif any(keyword in summary for keyword in ["fuel exhaustion", "ran out of fuel"]):
        return "Fuel Exhaustion"
    else:
        return "Other/Unknown"


# Apply the categorization function to the dataset
df["Crash_Category"] = df["Summary"].apply(categorize_crash)

print(df["Crash_Category"].value_counts())

df.groupby(["Year", "Crash_Category"]).size().unstack().plot(
    kind="line", figsize=(12, 6), title="Crash Categories Over Time"
)
plt.xlabel("Year")
plt.ylabel("Number of Crashes")
plt.legend(title="Crash Category")
plt.show()
