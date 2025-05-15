# -*- coding: utf-8 -*-
"""
Scrub Data Functions for Plane Crash Dummy Project

@author: Ansley Ingram
"""
import pandas as pd
import hashlib
import re

# helper functions

# location column isn't standardized (e.g. Near Moscow, Russia vs Moscow, Russia)
# Function to clean and standardize location names
def clean_location(location):
    location = str(location).strip()
    location = location.replace("Near ", "")
    return " ".join(location.split())

# Function to clean and standardize operator names
def clean_operator(operator):
    operator = str(operator).strip()  # Remove leading/trailing spaces
    operator = " ".join(operator.split())  # Normalize extra spaces
    if operator in ["?", "Unknown", "unknown"]:  # Standardize unknown values
        operator = "Unknown Operator"
    return operator

# Function to extract passengers and crew from the Aboard column
def extract_aboard_counts(aboard_text):
    match = re.search(r"(\d+)\s+\(passengers:(\d+)\s+crew:(\d+)\)", str(aboard_text))
    if match:
        total, passengers, crew = match.groups()
        return int(passengers), int(crew)
    return None, None  # Return None if the format is unexpected

# Function to extract passengers and crew fatalities from the Fatalities column
def extract_fatalities(fatalities_text):
    match = re.search(
        r"(\d+)\s+\(passengers:(\d+)\s+crew:(\d+)\)", str(fatalities_text)
    )
    if match:
        total, passengers, crew = match.groups()
        return int(passengers), int(crew)
    return None, None  # Return None if the format is unexpected

# Function to generate a hash from DateTimeNew and Location to use as a unique identifier
def generate_hash(row):
    return hashlib.md5(f"{row['DateTime']}_{row['Location']}".encode()).hexdigest()


def scrub_crash_data(filepath, output_file_path):
    try:
        # load the CSV into a data frame
        df = pd.read_csv(filepath)
    
        # drop rows that contain repeated column headers
        df_cleaned = df.iloc[1::2].reset_index(drop=True)
    
        # rename columns
        df_cleaned.columns = [
            "Date",
            "Time",
            "Location",
            "Operator",
            "Flight #",
            "Route",
            "Aircraft Type",
            "Registration",
            "cn / ln",
            "Aboard",
            "Fatalities",
            "Ground",
            "Summary",
        ]
    
        # drop any remaining rows with header-like attributes
        df_cleaned = df_cleaned[1:].reset_index(drop=True)
    
        # display a preview of the cleaned data set
        #print(df_cleaned.head(10))
    
        # Replace missing times ("?") with "0000"
        df_cleaned["Time"] = df_cleaned["Time"].replace("?", "0000")
        
        # Ensure all times are in HH:MM format
        df_cleaned["Time"] = (
            df_cleaned["Time"].astype(str).str.zfill(4)
        )  # Ensure 4-character format (e.g., '630' -> '0630')
    
        # Fix any formatting issues like "00::00"
        df_cleaned["Time"] = df_cleaned["Time"].str.replace("::", ":", regex=False)
        
        # Create a combined DateTime column
        df_cleaned["DateTime"] = df_cleaned["Date"] + " " + df_cleaned["Time"]
        
        # Convert to proper datetime format
        df_cleaned["DateTime"] = pd.to_datetime(df_cleaned["DateTime"], errors="coerce")
    
    
        # Check for duplicate DateTime entries
        duplicates = df_cleaned["DateTime"].duplicated().sum()
        
        if duplicates == 0:
            print("✅ The DateTime column is unique and can be used as an identifier.")
        else:
            print(f"⚠️ The DateTime column has {duplicates} duplicates. Consider using an additional column for uniqueness.")
        
        
        df_cleaned["UniqueID"] = df_cleaned.apply(generate_hash, axis=1)
        
        # Create a new column with cleaned location names
        df_cleaned["Location_Cleaned"] = df_cleaned["Location"].apply(clean_location)
        
        # Create a new column with cleaned operator names
        df_cleaned["Operator_Cleaned"] = df_cleaned["Operator"].apply(clean_operator)
        
        # Apply function to extract passengers and crew aboard
        df_cleaned[["Passengers_Aboard", "Crew_Aboard"]] = df_cleaned["Aboard"].apply(
            lambda x: pd.Series(extract_aboard_counts(x))
        )
        
        # Fill missing values with 0 in Passengers_Aboard and Crew_Aboard columns
        df_cleaned["Passengers_Aboard"] = df_cleaned["Passengers_Aboard"].fillna(0).astype(int)
        df_cleaned["Crew_Aboard"] = df_cleaned["Crew_Aboard"].fillna(0).astype(int)
        
        # Identify inconsistencies in the Aboard column (entries containing "?")
        inconsistent_aboard_entries = df_cleaned[
            df_cleaned["Aboard"].str.contains(r"\?", na=False)
        ]
        
        # Create a new column that sums Passengers_Aboard and Crew_Aboard
        df_cleaned["Total_Aboard"] = df_cleaned["Passengers_Aboard"] + df_cleaned["Crew_Aboard"]
          
        # Apply function to extract passenger and crew fatalities
        df_cleaned[["Passengers_Fatalities", "Crew_Fatalities"]] = df_cleaned[
            "Fatalities"
        ].apply(lambda x: pd.Series(extract_fatalities(x)))
        
        # Fill missing values with 0
        df_cleaned["Passengers_Fatalities"] = (
            df_cleaned["Passengers_Fatalities"].fillna(0).astype(int)
        )
        df_cleaned["Crew_Fatalities"] = df_cleaned["Crew_Fatalities"].fillna(0).astype(int)
        
        # Create a new column that sums Passengers_Fatalities and Crew_Fatalities
        df_cleaned["Total_Fatalities"] = (
            df_cleaned["Passengers_Fatalities"] + df_cleaned["Crew_Fatalities"]
        )
        
        # Rename the "Ground" column to "Ground_Fatalities"
        df_cleaned = df_cleaned.rename(columns={"Ground": "Ground_Fatalities"})
        
        # Replace "?" with "Unknown" in the Flight # column
        df_cleaned["Flight #"] = df_cleaned["Flight #"].replace("?", "Unknown")
        
        # Replace "?" with "Unknown" in the Route column
        df_cleaned["Route"] = df_cleaned["Route"].replace("?", "Unknown")
        
        # Replace "?" with "Unknown" in the Aircraft Type column
        df_cleaned["Aircraft Type"] = df_cleaned["Aircraft Type"].replace("?", "Unknown")
        
        # Replace "?" with "Unknown" in the Registration column
        df_cleaned["Registration"] = df_cleaned["Registration"].replace("?", "Unknown")
        
        # create a new dataset with just the columns we want to keeps
        df_scrubbed = df_cleaned[
            [
                "UniqueID",
                "DateTime",
                "Location_Cleaned",
                "Operator_Cleaned",
                "Flight #",
                "Route",
                "Aircraft Type",
                "Registration",
                "Total_Aboard",
                "Passengers_Aboard",
                "Crew_Aboard",
                "Total_Fatalities",
                "Passengers_Fatalities",
                "Crew_Fatalities",
                "Summary",
            ]
        ]
        
        # Display the cleaned dataset
        print("Scrubbed Data Summaries")
        print(df_scrubbed.info())
        print(df_scrubbed.head(10))
        print(df_scrubbed.tail(10))
           
        # Write the DataFrame to a CSV file
        df_scrubbed.to_csv(output_file_path, index=False)
        
        # Confirm file creation
        print(f"File saved successfully: {output_file_path}")

    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return None