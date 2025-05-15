# -*- coding: utf-8 -*-
"""
Functions to extract data for Plane Crash Dummy project
https://www.planecrashinfo.com/database.htm
Created on Thu May 15 14:37:31 2025
@author: Ansley Ingram
"""
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Fake a real browser's User-Agent to avoid bot detection
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com",  # Some sites check referer headers
}

def scrape_links(url, outfile, mode):
    """Fetches hyperlinks from a given URL while avoiding bot detection."""
    # mode is w for overwrite or a for append
    try:
        session = requests.Session()
        response = session.get(url, headers=HEADERS)
        response.raise_for_status()  # Check for HTTP errors
        session.cookies.update(response.cookies)

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract all anchor tags with href attributes
        links = [a["href"] for a in soup.find_all("a", href=True)]

        # Save links to a file
        with open(outfile, mode, encoding="utf-8") as file:
            for link in links:
                file.write(link + "\n")

        print(f"Extracted {len(links)} links and saved to {outfile}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        
def process_url_list(input_file, output_file):
    """Reads a list of URLs from a file and extracts links from each."""
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            urls = [line.strip() for line in file if line.strip()]

        domain = "http://www.planecrashinfo.com/"

        for url in urls:
            scrape_links(domain + url, output_file, "a")

        print(f"Finished processing {len(urls)} URLs.")

    except FileNotFoundError:
        print(f"File {input_file} not found.")

def filter_lines(input_file, output_file):
    """Reads a file and removes lines that don't start with 1 or 2."""
    try:
        with open(input_file, "r", encoding="utf-8") as infile:
            lines = infile.readlines()

        # Keep only lines that start with '1' or '2'
        filtered_lines = [
            line for line in lines if line.strip() and line[0] in ("1", "2")
        ]

        with open(output_file, "w", encoding="utf-8") as outfile:
            outfile.writelines(filtered_lines)

        print(
            f"Filtered {len(lines) - len(filtered_lines)} lines. Saved to {output_file}"
        )

    except FileNotFoundError:
        print(f"File {input_file} not found.")

def fix_urls(file_path, output_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    with open(output_path, "w") as file:
        for line in lines:
            line = line.strip()  # Remove leading/trailing whitespace
            if len(line) >= 4:
                modified_line = f"https://www.planecrashinfo.com/{line[:4]}/{line}"
                file.write(modified_line + "\n")
                
def extract_plane_crash_data(url, output_csv):
    """Extracts plane crash data from a given URL and saves it to a CSV file."""
    try:
        # Send request to the webpage
        reqs = requests.get(url)
        reqs.raise_for_status()  # Raise an error for failed requests

        # Parse the HTML
        soup = BeautifulSoup(reqs.text, "html.parser")

        # Find the first table
        table = soup.find_all("table")[0]

        # Extract table headers
        # headers = [header.get_text(strip=True) for header in table.find("tr").find_all("td")]

        # Extract table rows (skipping the header row)
        data = []
        rows = table.find_all("tr")[1:]  # Skip the header row

        # data = []
        # for row in table.find_all("tr")[1:]:
        #     cells = row.find_all("td")  # Or "th" for header cells
        #     row_data = [cell.text.strip() for cell in cells]
        #     data.append(row_data)

        for row in rows:
            columns = row.find_all("td")
            row_data = [col.get_text(strip=True) for col in columns]
            data.append(row_data)

        transposed_data = list(zip(*data))

        # Store data into a Pandas DataFrame
        df = pd.DataFrame(transposed_data)

        print(df)

        # Save to CSV
        # Append to CSV
        if os.path.exists(output_csv):
            df.to_csv(output_csv, mode="a", header=False, index=False)
        else:
            df.to_csv(output_csv, mode="w", header=True, index=False)

        print(f"Data extracted successfully and saved to {output_csv}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
    except IndexError:
        print("Error: No table found on the page.")


def file_to_array(file_path):
    """Reads a file and returns an array where each element is a line from the file.

    Args:
        file_path: The path to the file.

    Returns:
        A list of strings, where each string is a line from the file.
        Returns an empty list if the file is empty or an error occurs.
    """
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            # Remove trailing newline characters from each line
            return [line.rstrip("\n") for line in lines]
    except FileNotFoundError:
        print(f"Error: File not found at path: {file_path}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
                
