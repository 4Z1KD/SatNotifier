import tkinter as tk
import tkinter.ttk as ttk
import requests
import json
import re
from datetime import datetime, timezone


def send_request(api_key, sat_num, sat_name):
    api_base_url = 'https://api.n2yo.com/rest/v1/satellite/radiopasses/'
    url = f"{api_base_url}{sat_num}/{latitude}/{longitude}/{altitude}/{prediction_duration}/{min_elevation}&apiKey={api_key}"
    
    response = requests.get(url)
    
    # Parse the response JSON
    data = response.json()
    
    passes = data.get("passes", [])
    for pass_info in passes:
        start_az = pass_info.get("startAz", "")
        start_utc = pass_info.get("startUTC", "")
        max_el = pass_info.get("maxEl", "")
        end_az = pass_info.get("endAz", "")
        end_utc = pass_info.get("endUTC", "")
        start_utc_readable = convert_unix_to_utc(start_utc)
        end_utc_readable = convert_unix_to_utc(end_utc)
        # Add a row to the table
        pass_table.insert("", "end", values=(sat_name, start_az, start_utc_readable, max_el, end_az, end_utc_readable))

def validate_numeric_input(P):
    if P == "":
        return True
    return re.match("^[0-9]*\.?[0-9]*$", P) is not None

def convert_unix_to_utc(unix_timestamp):
    utc_time = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    return utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")

# Load satellite data from sats.cfg file
with open('sats.cfg', 'r') as config_file:
    satellite_data = json.load(config_file)

# Create the main window
root = tk.Tk()
root.title("Satellite Radio Passes")
root.geometry("900x600")  # Set window dimensions

# Create a frame to hold the form elements
frame = tk.Frame(root)
frame.pack(padx=10, pady=10, anchor="w")

# Validate input to accept only numeric values
validate_numeric = root.register(validate_numeric_input)

# Create labels and entry fields with margin between labels
latitude_label = tk.Label(frame, text="Latitude:", anchor="w")
latitude_label.grid(row=0, column=0, sticky="w")
latitude_entry = tk.Entry(frame, validate="key", validatecommand=(validate_numeric, "%P"))
latitude_entry.grid(row=0, column=1)

frame.grid_rowconfigure(1, minsize=10)  # Add a 10px gap

longitude_label = tk.Label(frame, text="Longitude:", anchor="w")
longitude_label.grid(row=2, column=0, sticky="w")
longitude_entry = tk.Entry(frame, validate="key", validatecommand=(validate_numeric, "%P"))
longitude_entry.grid(row=2, column=1)

frame.grid_rowconfigure(3, minsize=10)  # Add a 10px gap

min_elevation_label = tk.Label(frame, text="Min Elevation:", anchor="w")
min_elevation_label.grid(row=4, column=0, sticky="w")
min_elevation_entry = tk.Entry(frame, validate="key", validatecommand=(validate_numeric, "%P"))
min_elevation_entry.grid(row=4, column=1)

# Define additional parameters
altitude = 0  # You can adjust this value as needed
prediction_duration = 1  # You can adjust this value as needed
api_key = "X6TE8K-3F6BTP-X6U5VQ-53QU"  # Replace with your actual API key

# Create a frame to hold the button
button_frame = tk.Frame(root)
button_frame.pack(fill="both", padx=10)  # Expand horizontally

# Create the button and align it to the left
submit_button = tk.Button(button_frame, text="Get Radio Passes", command=lambda: get_radio_passes(satellite_data, api_key))
submit_button.pack(side="left", padx=10)

# Create a frame to hold the Treeview widget
table_frame = tk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=10)  # Expand vertically and add padding at the bottom

# Create a Treeview widget to display the pass information
pass_table = ttk.Treeview(table_frame, columns=("Satellite Name", "Start Azimuth", "Start UTC", "Max Elevation", "End Azimuth", "End UTC"), show="headings")
pass_table.heading("#1", text="Sat Name")
pass_table.heading("#2", text="Start Az")
pass_table.heading("#3", text="Start UTC")
pass_table.heading("#4", text="Max El")
pass_table.heading("#5", text="End Az")
pass_table.heading("#6", text="End UTC")

# Pack the Treeview widget and scrollbar
pass_table.pack(side="left", fill="both", expand=True)

# Apply custom styles
style = ttk.Style()
style.theme_use("default")  # Use the default theme
style.configure("Treeview.Heading", background="darkblue", foreground="white")


pass_table.pack(padx=20, pady=20)

def get_radio_passes(satellites, api_key):
    global latitude, longitude, min_elevation
    latitude = latitude_entry.get()
    longitude = longitude_entry.get()
    min_elevation = min_elevation_entry.get()
    
    # Clear the table before populating
    pass_table.delete(*pass_table.get_children())
    
    for satellite in satellites:
        send_request(api_key, satellite["num"], satellite["name"])

# Start the Tkinter event loop
root.mainloop()
