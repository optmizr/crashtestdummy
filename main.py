# -*- coding: utf-8 -*-
"""
Main Pipeline for Plane Crash Dummy Project

@author: Ansley Ingram
"""
import os
import time
from getdata import scrape_links, process_url_list, filter_lines, fix_urls, extract_plane_crash_data, file_to_array

# set the working directory
os.chdir("D:\Projects\crashtest_env")
print("Current directory:", os.getcwd())

# get links from the main list of years and save to yearindex.txt
scrape_links("https://www.planecrashinfo.com/database.htm", "data/yearindex.txt", "w")

# loop through yearindex.txt and extract urls from each page, append them to crashpages.txt
process_url_list("data/yearindex.txt", "data/crashpages.txt")

# some links reference other pages on the site that we don't want to crawl/scrape
# all individual crash pages start with the year (e.g. 1920 - 2025)
# function is hard coded to remove any line that doesn't start with 1 or 2
filter_lines("data/crashpages.txt", "data/crashpages_clean.txt")

# urls were relative so this will make them absolute
fix_urls("data/crashpages_clean.txt", "data/crashurls.txt")

# test run
# extract_plane_crash_data(
#     "https://www.planecrashinfo.com/1976/1976-1.htm", "data/crashtestdummy.csv"
# )

# loop through every html file in crashurls.txt and extract data / append to CSV
text_array = file_to_array("data/crashurls.txt")

if text_array:
    for line in text_array:
        #         print(line)
        extract_plane_crash_data(line, "data/crashtestdummy.csv")
        time.sleep(0.5)
else:
    print("No data was read from the file.")




