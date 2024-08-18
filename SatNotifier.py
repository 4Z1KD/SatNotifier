import json
import requests
import datetime
from datetime import timedelta
import subprocess
import os


# Read the JSON file
with open('.config', 'r') as file:
    config = json.load(file)

apiKey = config["apiKey"]
lat = config["lat"]
lng = config["lng"]
alt = config["alt"]
prediction_duration = config["prediction_duration"]
min_elevation = config["min_elevation"]

night_start = config["night_start"]
night_end = config["night_end"]
work_start = config["work_start"]
work_end = config["work_end"]

satellite_list = config["satellites"]

# Variable to store all the generated HTML tables
all_tables = []

# API base URL
api_base_url = 'https://api.n2yo.com/rest/v1/satellite/radiopasses/'

all_tables.append('<head><style>table{border-collapse: collapse;width: 100%;}th{background-color: #444444;color:#f2f2f2;text-align: left;padding: 8px;}tr:nth-child(even){background-color: #f2f2f2;}td{padding: 8px;border: 1px solid #dddddd;text-align: left;}tr{margin-bottom: 10px;}</style></head>')

#pass time
night_start_time = datetime.time(night_start, 0)
night_end_time = datetime.time(night_end, 0)
work_start_time = datetime.time(work_start, 0)
work_end_time = datetime.time(work_end, 0)
# Define a timedelta representing 3 hours
time_difference = timedelta(hours=3)
night_pass = False

# Iterate through each satellite and make API calls
for satellite in satellite_list:
    sat_name = satellite['name']
    sat_num = satellite['num']
    sat_uplink = satellite['uplink']
    sat_downlink = satellite['downlink']
    sat_beacon = satellite['beacon']
    sat_mode = satellite['mode']
    
    # Construct the API URL
    api_url = api_base_url + str(sat_num) + f"/{lat}/{lng}/{alt}/{prediction_duration}/{min_elevation}&apiKey={apiKey}"
    
    # Make the API call
    response = requests.get(api_url)
    
    # Process the API response
    if response.status_code == 200:
        api_data = response.json()
        try:
            error = api_data['error']
            print(error)
            continue
        except:
            status = "no error"
        
        # Extract data from the response
        sat_info = api_data['info']
        try:
            sat_passes = api_data['passes']
        except:
            continue
        
        sat_official_name = sat_info['satname']
        # Build HTML table
        table_html = f"<h2><a href='https://www.n2yo.com/?s={sat_num}' target='blank'>{sat_official_name}</a> | {sat_name} | {sat_num} | uplink: {sat_uplink} | downlink: {sat_downlink} | {sat_mode} | beacon: {sat_beacon}</h2><table border='1'><tr><th>Start Time</th><th>Max El</th><th>start Az</th><th>end Az</th><th>End Time</th></tr>"
        
        for pass_info in sat_passes:
            start_time = pass_info['startUTC']
            start_time = datetime.datetime.utcfromtimestamp(start_time) + time_difference
            # Check if the current UTC time is between 21:00 and 03:00
            #free time
            if work_start_time <= start_time.time() and start_time.time() <= work_end_time:
                pass_bgcolor = "FFFDAF"
            #night
            elif night_start_time <= start_time.time() or start_time.time() <= night_end_time:
                pass_bgcolor = "FFCCCB"
            else:
                pass_bgcolor = "90EE90"
            start_azimuth = pass_info['startAz']
            max_elevation = pass_info['maxEl']
            end_azimuth = pass_info['endAz']
            end_time = pass_info['endUTC']
            end_time = datetime.datetime.utcfromtimestamp(end_time) + time_difference
            if (max_elevation < 15):
                elevation_bgcolor = "#FFCCCB"
            elif (max_elevation >= 15 and max_elevation < 50):
                elevation_bgcolor = "#FFFDAF"
            elif (max_elevation >= 50):
                elevation_bgcolor = "#90EE90"
            table_row = f"<tr><td style='background-color:{pass_bgcolor}'>{start_time.time()}</td><td style='background-color:{elevation_bgcolor}'>{max_elevation}</td><td>{start_azimuth}</td><td>{end_azimuth}</td><td>{end_time.time()}</td></tr>"
            table_html += table_row
        
        table_html += "</table>"

        # Add the HTML table to the list
        all_tables.append(table_html)
    else:
        print(f"Error fetching data for Satellite {sat_name} ({sat_num}). Status Code: {response.status_code}")

# Combine all generated tables
combined_tables = '\n'.join(all_tables)
# Save the tables to a file
html_file = 'satellite_tables.html'

with open(html_file, 'w') as output_file:
    output_file.write(combined_tables)

# Command to open Chrome with the HTML file
chrome_command = f'start chrome "{os.path.abspath(html_file)}"'

# Run the command to open Chrome
subprocess.run(chrome_command, shell=True)