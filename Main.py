# This project uses the following open source libraries:
# - Tkinter (standard library)
# - threading (standard library)
# - asyncio (standard library)
# - Matplotlib (version 3.9.1) - https://matplotlib.org/
# - OpenMeteo (version 0.3.1) - https://pypi.org/project/open-meteo/
# - openmeteo_requests (version 1.2.0) - https://pypi.org/project/openmeteo-requests/
# - requests_cache (version 1.2.1) - https://requests-cache.readthedocs.io/
# - pandas (version 2.2.2) - https://pandas.pydata.org/
# - retry_requests (version 2.0.0) - https://pypi.org/project/retry-requests/
# - requests (version 2.32.3) - https://requests.readthedocs.io/
# - Flask (version 3.0.3) - https://flask.palletsprojects.com/
# - Azure-ttk-theme - https://github.com/rdbende/Azure-ttk-theme

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import asyncio
from open_meteo import OpenMeteo
from open_meteo.models import DailyParameters
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import requests
from flask import Flask, jsonify, request
import threading

# Initialize Flask app
flask_app = Flask(__name__)

# Global variables to store weather data
dates = []
weatherCode = []
temperatureMax = []
temperatureMin = []
precipitationSum = []
windSpeedMax = []
precipitationProbabilityMax = []

class App(ttk.Frame):
    # lookup table for weather code
    codes = ['Cloud development not observed or not observable during the past hour',
             'Clouds generally dissolving or becoming less developed during the past hour',
             'State of sky on the whole unchanged during the past hour',
             'Clouds generally forming or developing during the past hour',
             'Visibility reduced by smoke, e.g. veldt or forest fires, industrial smoke or volcanic ashes',
             'Haze',
             'Widespread dust in suspension in the air, not raised by wind at or near the station at the time of observation',
             'Dust or sand raised by wind at or near the station at the time of observation, but no well developed dust whirl(s) or sand whirl(s), and no duststorm or sandstorm seen',
             'Well developed dust whirl(s) or sand whirl(s) seen at or near the station during the preceding hour or at the time ot observation, but no duststorm or sandstorm',
             'Duststorm or sandstorm within sight at the time of observation, or at the station during the preceding hour',
             'Mist',
             'Patches shallow fog or ice fog at the station, whether on land or sea, not deeper than about 2 metres on land or 10 metres at sea',
             'More or less continuous shallow fog or ice fog at the station, whether on land or sea, not deeper than about 2 metres on land or 10 metres at sea',
             'Lightning visible, no thunder heard',
             'Precipitation within sight, not reaching the ground or the surface of the sea',
             'Precipitation within sight, reaching the ground or the surface of the sea, but distant, i.e. estimated to be more than 5 km from the station',
             'Precipitation within sight, reaching the ground or the surface of the sea, near to, but not at the station',
             'Thunderstorm, but no precipitation at the time of observation',
             'Squalls at or within sight of the station during the preceding hour or at the time of observation',
             'Funnel cloud(s) (Tornado cloud or water-spout) at or within sight of the station during the preceding hour or at the time of observation',
             'Drizzle (not freezing) or snow grains not falling as shower(s)',
             'Rain (not freezing) not falling as shower(s)',
             'Snow not falling as shower(s)',
             'Rain and snow or ice pellets not falling as shower(s)',
             'Freezing drizzle or freezing rain not falling as shower(s)',
             'Shower(s) of rain',
             'Shower(s) of snow, or of rain and snow',
             'Shower(s) of hail, or of rain and hail (Hail, small hail, snow pellets)',
             'fog or ice fog',
             'Thunderstorm (with or without precipitation)',
             'Slight or moderate duststorm or sandstorm has decreased during the preceding hour',
             'Slight or moderate duststorm or sandstorm no appreciable change during the preceding hour',
             'Slight or moderate duststorm or sandstorm has begun or has increased during the preceding hour',
             'Severe duststorm or sandstorm has decreased during the preceding hour',
             'Severe duststorm or sandstorm no appreciable change during the preceding hour',
             'Severe duststorm or sandstorm has begun or has increased during the preceding hour',
             'Slight or moderate blowing snow generally low (below eye level)',
             'Heavy drifting snow generally low (below eye level)',
             'Slight or moderate blowing snow generally high (above eye level)',
             'Heavy drifting snow generally high (above eye level)',
             'Fog or ice fog at a distance at the time of observation, but not at the station during the preceding hour, the fog or ice fog extending to a level above that of the observer',
             'Fog or ice fog in patches',
             'Fog or ice fog, sky visible has become thinner during the preceding hour',
             'Fog or ice fog, sky invisible has become thinner during the preceding hour',
             'Fog or ice fog, sky visible no appreciable change during the preceding hour',
             'Fog or ice fog, sky invisible no appreciable change during the preceding hour',
             'Fog or ice fog, sky visible has begun or has become thicker during the preceding hour',
             'Fog or ice fog, sky invisible has begun or has become thicker during the preceding hour',
             'Fog, depositing rime, sky visible',
             'Fog, depositing rime, sky invisible',
             'Drizzle, not freezing, intermittent slight at time of observation',
             'Drizzle, not freezing, continuous slight at time of observation',
             'Drizzle, not freezing, intermittent moderate at time of observation',
             'Drizzle, not freezing, continuous moderate at time of observation',
             'Drizzle, not freezing, intermittent heavy (dense) at time of observation',
             'Drizzle, not freezing, continuous heavy (dense) at time of observation',
             'Drizzle, freezing, slight',
             'Drizzle, freezing, moderate or heavy (dense)',
             'Drizzle and rain, slight',
             'Drizzle and rain, moderate or heavy',
             'Rain, not freezing, intermittent slight at time of observation',
             'Rain, not freezing, continuous slight at time of observation',
             'Rain, not freezing, intermittent moderate at time of observation',
             'Rain, not freezing, continuous moderate at time of observation',
             'Rain, not freezing, intermittent heavy at time of observation',
             'Rain, not freezing, continuous heavy at time of observation',
             'Rain, freezing, slight',
             'Rain, freezing, moderate or heavy (dense)',
             'Rain or drizzle and snow, slight',
             'Rain or drizzle and snow, moderate or heavy',
             'Intermittent fall of snowflakes slight at time of observation',
             'Continuous fall of snowflakes slight at time of observation',
             'Intermittent fall of snowflakes moderate at time of observation',
             'Continuous fall of snowflakes moderate at time of observation',
             'Intermittent fall of snowflakes heavy at time of observation',
             'Continuous fall of snowflakes heavy at time of observation',
             'Diamond dust (with or without fog)',
             'Snow grains (with or without fog)',
             'Isolated star-like snow crystals (with or without fog)',
             'Ice pellets',
             'Rain shower(s), slight',
             'Rain shower(s), moderate or heavy',
             'Rain shower(s), violent',
             'Shower(s) of rain and snow mixed, slight',
             'Shower(s) of rain and snow mixed, moderate or heavy',
             'Snow shower(s), slight',
             'Snow shower(s), moderate or heavy',
             'Shower(s) of snow pellets or small hail, with or without rain or rain and snow mixed slight',
             'Shower(s) of snow pellets or small hail, with or without rain or rain and snow mixed moderate or heavy',
             'Shower(s) of hail, with or without rain or rain and snow mixed, not associated with thunder slight',
             'Shower(s) of hail, with or without rain or rain and snow mixed, not associated with thunder moderate or heavy',
             'Slight rain at time of observation Thunderstorm during the preceding hour but not at time of observation',
             'Moderate or heavy rain at time of observation Thunderstorm during the preceding hour but not at time of observation',
             'Slight snow, or rain and snow mixed or hail (Hail, small hail, snow pellets) at time of observation Thunderstorm during the preceding hour but not at time of observation',
             'Moderate or heavy snow, or rain and snow mixed or hail (Hail, small hail, snow pellets) at time of observation Thunderstorm during the preceding hour but not at time of observation',
             'Thunderstorm, slight or moderate, without hail (Hail, small hail, snow pellets) but with rain and/or snow at time of observation',
             'Thunderstorm, slight or moderate, with hail (Hail, small hail, snow pellets) at time of observation',
             'Thunderstorm, heavy, without hail (Hail, small hail, snow pellets) but with rain and/or snow at time of observation',
             'Thunderstorm combined with duststorm or sandstorm at time of observation',
             'Thunderstorm, heavy, with hail (Hail, small hail, snow pellets) at time of observation'
             ]

    # variables for setting the location
    latitude_set = 0
    longitude_set = 0

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        """
        Initialize the frame with given parent widget.

        Args:
            parent (tk.Widget): Parent widget to which this frame belongs.
        """
        # Make the app responsive
        for index in [0, 1, 2]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        # Create lists of data types and categories
        self.data_type_list = ['Temp Low', 'Temp High', 'Precipitation Amount', 'Wind Speed',
                               'Precipitation Probability']
        self.data_type_list_complete = ['Weather Code', 'Temp Low', 'Temp High', 'Precipitation Amount', 'Wind Speed',
                                        'Precipitation Probability']
        self.data_cat = ['Max', 'Min', 'Mean', 'Single']

        # Set up all widgets within the frame
        self.setup_widgets()

    def setup_widgets(self):
        """
        Set up all widgets within the frame.

        This method initializes and places various widgets including buttons, dropdowns, labels,
        and frames within the main frame of the application.
        """
        # Header frame for upload and close buttons
        self.header_frame = ttk.Frame(self, padding=(20, 10))
        self.header_frame.grid(row=0, column=0, sticky="EW")

        # Upload Button
        self.upload_button = ttk.Button(self.header_frame, text="Upload Input File", command=self.upload_file)
        self.upload_button.grid(row=0, column=0, padx=5, pady=5)

        # Close Button
        self.close_button = ttk.Button(self.header_frame, text="Close", command=self.quit)
        self.close_button.grid(row=0, column=1, padx=5, pady=5)

        # Body frame for notebook
        self.body_frame = ttk.Frame(self)
        self.body_frame.grid(row=1, column=0, padx=10, pady=10, sticky="NSEW")

        # Notebook widget for tabs
        self.notebook = ttk.Notebook(self.body_frame)
        self.notebook.pack(fill="both", expand=True)

        # Tab #1: Data Output
        self.tab_1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_1, text="Data Output")

        # Statistics frame within Tab #1
        self.weather_code_frame = ttk.LabelFrame(self.tab_1, text="Statistics", padding=(20, 10))
        self.weather_code_frame.grid(row=2, column=0, padx=10, pady=10, sticky='NSEW', columnspan=4)

        # Start Date Dropdown
        self.start_date_dropdown = ttk.Combobox(self.tab_1, state="readonly", values=dates)
        self.start_date_dropdown.grid(row=0, column=2, padx=5, pady=5, sticky="W")
        self.start_date_dropdown.bind("<<ComboboxSelected>>", self.data_test)

        # Data Type Dropdown
        self.data_dropdown = ttk.Combobox(self.tab_1, state="readonly", values=self.data_type_list_complete)
        self.data_dropdown.grid(row=0, column=0, padx=5, pady=5)
        self.data_dropdown.bind("<<ComboboxSelected>>", self.data_test)

        # Output Text Label
        self.output_text = ttk.Label(self.weather_code_frame, text='', wraplength=675)
        self.output_text.grid(row=0, column=0, padx=5, pady=5)

        # Latitude and Longitude Entry Fields
        self.lat = ttk.Entry(self.tab_1, width=30)
        self.lat.grid(row=1, column=0, padx=5, pady=5, sticky="NSEW", columnspan=2)
        self.lat.bind("<FocusOut>", self.lat_long_entry)

        self.long = ttk.Entry(self.tab_1, width=30)
        self.long.grid(row=1, column=2, padx=5, pady=5, sticky="NSEW", columnspan=2)
        self.long.bind("<FocusOut>", self.lat_long_entry)

        # Tab #2: Histogram
        self.tab_2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_2, text="Histogram")

        # Histogram frame within Tab #2
        self.histogram_frame = ttk.LabelFrame(self.tab_2, text="Histogram")
        self.histogram_frame.grid(row=2, column=0, padx=10, pady=10, sticky="NSEW")

        # Histogram Data Type Dropdown
        self.histogram_data_type_dropdown = ttk.Combobox(
            self.histogram_frame, state="readonly", values=self.data_type_list
        )
        self.histogram_data_type_dropdown.grid(row=0, column=0, pady=10, padx=10)
        self.histogram_data_type_dropdown.bind("<<ComboboxSelected>>", self.plot_histogram)

        # Histogram Start Date Dropdown
        self.histogram_start_date_dropdown = ttk.Combobox(
            self.histogram_frame, state="readonly", values=dates
        )
        self.histogram_start_date_dropdown.grid(row=0, column=1, padx=10, pady=10)
        self.histogram_start_date_dropdown.bind("<<ComboboxSelected>>", self.plot_histogram)

        # Histogram End Date Dropdown
        self.histogram_end_date_dropdown = ttk.Combobox(
            self.histogram_frame, state="readonly", values=dates
        )
        self.histogram_end_date_dropdown.grid(row=0, column=2, padx=10, pady=10)
        self.histogram_end_date_dropdown.bind("<<ComboboxSelected>>", self.plot_histogram)

        # Canvas for Histogram
        self.canvas = None

        # Tab #3: Credits
        self.tab_3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_3, text="Credits")

        # Credits frame within Tab #3
        self.credits = ttk.LabelFrame(self.tab_3, text="Credits", padding=(20, 10))
        self.credits.grid(row=0, column=0, padx=10, pady=10)

        # Credits Text Box
        self.credits_textbox = tk.Text(self.credits, wrap='word', height=30, width=90)
        self.credits_textbox.grid(row=0, column=0, padx=10, pady=10, sticky='NSEW', rowspan=2, columnspan=2)

        # Inserting Credits Information
        credits_text = (
            "This application uses the following open source libraries:\n"
            "- Tkinter - A Python binding to the Tk GUI toolkit.\n"
            "- Matplotlib - A comprehensive library for creating static, animated, and interactive visualizations in Python.\n"
            "- asyncio - Asynchronous I/O, event loop, coroutines, and tasks.\n"
            "- OpenMeteo - A Python client for the Open-Meteo weather API.\n"
            "- openmeteo_requests - A Python client for the Open-Meteo weather API using requests.\n"
            "- requests_cache - A transparent persistent cache for the requests library.\n"
            "- pandas - A fast, powerful, flexible, and easy-to-use open source data analysis and data manipulation library built on top of the Python programming language.\n"
            "- retry_requests - A Python library to automatically retry failed HTTP requests using the requests library.\n"
            "- requests - A simple, yet elegant HTTP library.\n"
            "- Azure-ttk-theme - A modern theme for the Tkinter/ttk widgets."
        )
        self.credits_textbox.insert('1.0', credits_text)
        self.credits_textbox.config(state='disabled')  # Make the text box read-only

        # Configure grid weight to allow the text box to expand
        self.credits.grid_rowconfigure(0, weight=1)
        self.credits.grid_columnconfigure(0, weight=1)

    def lat_long_entry(self, event):
        """
        Process latitude and longitude values entered by the user.

        This method retrieves latitude and longitude values from Entry widgets
        and calls the evaluate method to process them.

        Args:
            event (tk.Event, optional): The event that triggered this method.
        """
        # Get the latitude and longitude values from the Entry widgets
        self.latitude_set = float(self.lat.get())
        self.longitude_set = float(self.long.get())

        # Call the evaluate method to process the latitude and longitude values
        self.evaluate()

    def data_test(self, event):
        """
        Handle changes when a new data type is selected.

        This method checks if the selected data type is "Weather Code". If it is,
        it hides the data category dropdown and end date dropdown (if they exist).
        Otherwise, it shows the data category dropdown and binds a handler to it.

        Args:
            event (tk.Event, optional): The event that triggered this method.
        """
        # Check if the selected data type is "Weather Code"
        if self.data_dropdown.get() == "Weather Code":
            # Hide data category dropdown if it exists
            if hasattr(self, 'data_cat_dropdown'):
                self.data_cat_dropdown.grid_remove()

            # Hide end date dropdown if it exists
            if hasattr(self, 'end_date_dropdown'):
                self.end_date_dropdown.grid_remove()
        else:
            # If data type is not "Weather Code", show data category dropdown
            if not hasattr(self, 'data_cat_dropdown'):
                self.data_cat_dropdown = ttk.Combobox(
                    self.tab_1, state="readonly", values=self.data_cat
                )
                self.data_cat_dropdown.grid(row=0, column=1, padx=5, pady=5)
                self.data_cat_dropdown.bind("<<ComboboxSelected>>", self.handle_data_category_selection)
            else:
                self.data_cat_dropdown.grid()

        # Call the evaluate method to process the changes
        self.evaluate()

    def handle_data_category_selection(self, event=None):
        """
        Handle changes when a new data category is selected.

        This method checks if the selected data category is 'Single'. If it is,
        it hides the end date dropdown (if it exists). Otherwise, it shows the
        end date dropdown and binds a handler to it.

        Args:
            event (tk.Event, optional): The event that triggered this method.
        """
        # Check if the selected data category is 'Single'
        if self.data_cat_dropdown.get() == 'Single':
            # Hide end date dropdown if it exists
            if hasattr(self, 'end_date_dropdown'):
                self.end_date_dropdown.grid_remove()
        else:
            # Show end date dropdown if it does not exist
            if not hasattr(self, 'end_date_dropdown'):
                self.end_date_dropdown = ttk.Combobox(
                    self.tab_1, state="readonly"
                )
                self.end_date_dropdown['values'] = dates
                self.end_date_dropdown.grid(row=0, column=3, padx=5, pady=5)
                self.end_date_dropdown.bind("<<ComboboxSelected>>", self.data_test)
            else:
                self.end_date_dropdown.grid()

        # Call the evaluate method to process the changes
        self.evaluate()

    def evaluate(self):
        """
           Sets the output text based on user-selected data category and type.

           - Weather Code: Displays input and real weather codes for a selected date.
           - Single (Temp Low, Temp High, Precipitation Amount, Wind Speed, Precipitation Probability):
             Compares input and real data for a single date.
           - Mean (Temp Low, Temp High, Precipitation Amount, Wind Speed, Precipitation Probability):
             Calculates and displays average input and real data over a date range.
           - Max (Temp Low, Temp High, Precipitation Amount, Wind Speed, Precipitation Probability):
             Displays maximum input and real data over a date range.
           - Min (Temp Low, Temp High, Precipitation Amount, Wind Speed, Precipitation Probability):
             Displays minimum input and real data over a date range.
           """
        # sets the output for when Weather Code is selected
        if self.data_dropdown.get() == "Weather Code":
            selected_date = self.start_date_dropdown.get()
            if selected_date in dates:
                index = dates.index(selected_date)
                weather_code = int(float(weatherCode[index]))
                weather_code_real = self.openMeteoSetup(index, index, "Weather Code", self.latitude_set, self.longitude_set )
                self.output_text.config(text = "Input Weather Code: {} - {}\n\nReal Weather Code: {} - {}".format(weather_code, self.codes[weather_code], int(weather_code_real), self.codes[int(weather_code_real)]))
                self.output_text.config(font=("Arial", 20))

        # sets the output for when single is selected
        elif self.data_cat_dropdown.get() == "Single":
            self.output_text.config(font=("Arial", 20))
            if self.data_dropdown.get() == "Temp Low":
                selected_date = self.start_date_dropdown.get()
                if selected_date in dates:
                    index = dates.index(selected_date)
                    low_temp = self.openMeteoSetup(index, index, "Temp Low", self.latitude_set, self.longitude_set  )
                    self.output_text.config(text = "Input Low Temperature: {}C\n\nReal Low Temperature: {}F".format(int(round(float(temperatureMin[index]), 0)), int(low_temp)))
            elif self.data_dropdown.get() == "Temp High":
                selected_date = self.start_date_dropdown.get()
                if selected_date in dates:
                    index = dates.index(selected_date)
                    high_temp = self.openMeteoSetup(index, index, "Temp High", self.latitude_set, self.longitude_set  )
                    self.output_text.config(text = "Input High Temperature: {}C\n\nReal High Temperature: {}F".format(int(round(float(temperatureMax[index]),0)), int(high_temp)))
            elif self.data_dropdown.get() == "Precipitation Amount":
                selected_date = self.start_date_dropdown.get()
                if selected_date in dates:
                    index = dates.index(selected_date)
                    precip_sum = self.openMeteoSetup(index, index, "Precipitation Amount", self.latitude_set, self.longitude_set  )
                    self.output_text.config(text = "Input Precipitation Amount: {} inches\n\nReal Precipitation Amount: {} inches".format(int(round(float(precipitationSum[index]),0)), int(precip_sum)))
            elif self.data_dropdown.get() == "Wind Speed":
                selected_date = self.start_date_dropdown.get()
                if selected_date in dates:
                    index = dates.index(selected_date)
                    wind_speed = self.openMeteoSetup(index, index, "Wind Speed", self.latitude_set, self.longitude_set  )
                    self.output_text.config(text = "Input Max Wind Speed: {} mph\n\nReal Max Wind Speed: {} mph".format(int(round(float(windSpeedMax[index]), 0)), int(wind_speed)))
            elif self.data_dropdown.get() == "Precipitation Probability":
                selected_date = self.start_date_dropdown.get()
                if selected_date in dates:
                    index = dates.index(selected_date)
                    precip_chance = self.openMeteoSetup(index, index, "Precipitation Probability", self.latitude_set, self.longitude_set   )
                    self.output_text.config(text = "Input Precipitation Percent Chance: {}%\n\nReal Precipitation Percent Chance: {}%".format(int(round(float(precipitationProbabilityMax[index]),0)), int(precip_chance)))

        # sets the output for when Mean is selected
        elif self.data_cat_dropdown.get() == "Mean":
            self.output_text.config(font=("Arial", 20))
            if self.data_dropdown.get() == "Temp Low":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                mean_temp = sum(float(temp) for temp in temperatureMin[start_date:end_date + 1]) / (end_date - start_date + 1)
                mean_temp_real = sum(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Temp Low", self.latitude_set, self.longitude_set )) / (end_date - start_date + 1)
                self.output_text.config(text="Average Input Low Temperature: {:.0f} C\n\nAverage Real Low Temperature: {:.0f} F".format(mean_temp, mean_temp_real))
            elif self.data_dropdown.get() == "Temp High":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                mean_temp = sum(float(temp) for temp in temperatureMax[start_date:end_date + 1]) / (end_date - start_date + 1)
                mean_temp_real = sum(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Temp High", self.latitude_set, self.longitude_set )) / (end_date - start_date + 1)
                self.output_text.config(text="Average Input High Temperature: {:.0f} C\n\nAverage Real High Temperature: {:.0f} F".format(mean_temp, mean_temp_real))
            elif self.data_dropdown.get() == "Precipitation Amount":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                mean_temp = sum(float(temp) for temp in precipitationSum[start_date:end_date + 1]) / (end_date - start_date + 1)
                mean_temp_real = sum(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Precipitation Amount", self.latitude_set, self.longitude_set )) / (end_date - start_date + 1)
                self.output_text.config(text="Average Input Precipitation Amount: {:.0f} inches\n\nAverage Real Precipitation Amount: {:.0f} inches".format(mean_temp, mean_temp_real))
            elif self.data_dropdown.get() == "Wind Speed":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                mean_temp = sum(float(temp) for temp in windSpeedMax[start_date:end_date + 1]) / (end_date - start_date + 1)
                mean_temp_real = sum(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Wind Speed", self.latitude_set, self.longitude_set )) / (end_date - start_date + 1)
                self.output_text.config(text="Average Input Max Wind Speed: {:.0f} mph\n\nAverage Real Max Wind Speed: {:.0f} mph".format(mean_temp, mean_temp_real))
            elif self.data_dropdown.get() == "Precipitation Probability":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                mean_temp = sum(float(temp) for temp in precipitationProbabilityMax[start_date:end_date + 1]) / (end_date - start_date + 1)
                mean_temp_real = sum(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Precipitation Probability", self.latitude_set, self.longitude_set)) / (end_date - start_date + 1)
                self.output_text.config(text="Average Input Precipitation Percent Chance: {:.0f}%\n\nAverage Real Precipitation Percent Chance: {:.0f}%".format(mean_temp, mean_temp_real))

        # sets the output for when Max is selected
        elif self.data_cat_dropdown.get() == "Max":
            self.output_text.config(font=("Arial", 20))
            if self.data_dropdown.get() == "Temp Low":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                max_temp = max(float(temp) for temp in temperatureMin[start_date:end_date + 1])
                max_temp_real = max(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Temp Low", self.latitude_set, self.longitude_set ))
                self.output_text.config(text="Maximum Input Low Temperature: {:.0f} C\n\nMaximum Real Low Temperature: {:.0f} F".format(max_temp, max_temp_real))
            elif self.data_dropdown.get() == "Temp High":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                max_temp = max(float(temp) for temp in temperatureMax[start_date:end_date + 1])
                max_temp_real = max(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Temp High", self.latitude_set, self.longitude_set ))
                self.output_text.config(text="Maximum Input High Temperature: {:.0f} C\n\nMaximum Real High Temperature: {:.0f} F".format(max_temp, max_temp_real))
            elif self.data_dropdown.get() == "Precipitation Amount":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                max_temp = max(float(temp) for temp in precipitationSum[start_date:end_date + 1])
                max_temp_real = max(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Precipitation Amount", self.latitude_set, self.longitude_set ))
                self.output_text.config(text="Maximum Input Precipitation Amount: {:.0f} inches\n\nMaximum Real Precipitation Amount: {:.0f} inches".format(max_temp, max_temp_real))
            elif self.data_dropdown.get() == "Wind Speed":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                max_temp = max(float(temp) for temp in windSpeedMax[start_date:end_date + 1])
                max_temp_real = max(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Wind Speed",  self.latitude_set, self.longitude_set ))
                self.output_text.config(text="Maximum Input Wind Speed: {:.0f} mph\n\nMaximum Real Wind Speed: {:.0f} mph".format(max_temp, max_temp_real))
            elif self.data_dropdown.get() == "Precipitation Probability":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                max_temp = max(float(temp) for temp in precipitationProbabilityMax[start_date:end_date + 1])
                max_temp_real = max(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Precipitation Probability", self.latitude_set, self.longitude_set ))
                self.output_text.config(text="Maximum Input Precipitation Probability: {:.0f}%\n\nMaximum Real Precipitation Probability: {:.0f}%".format(max_temp, max_temp_real))

        # sets the output for when Min is selected
        elif self.data_cat_dropdown.get() == "Min":
            self.output_text.config(font=("Arial", 20))
            if self.data_dropdown.get() == "Temp Low":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                min_temp = min(float(temp) for temp in temperatureMin[start_date:end_date + 1])
                min_temp_real = min(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Temp Low", self.latitude_set, self.longitude_set ))
                self.output_text.config(text="Minimum Input Low Temperature: {:.0f} C\n\nMinimum Real Low Temperature: {:.0f} F".format(min_temp, min_temp_real))
            elif self.data_dropdown.get() == "Temp High":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                min_temp = min(float(temp) for temp in temperatureMax[start_date:end_date + 1])
                min_temp_real = min(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Temp High", self.latitude_set, self.longitude_set ))
                self.output_text.config(text="Minimum Input High Temperature: {:.0f} C\n\nMinimum Real High Temperature: {:.0f} F".format(min_temp, min_temp_real))
            elif self.data_dropdown.get() == "Precipitation Amount":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                min_temp = min(float(temp) for temp in precipitationSum[start_date:end_date + 1])
                min_temp_real = min(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Precipitation Amount",self.latitude_set, self.longitude_set ))
                self.output_text.config(text="Minimum Input Precipitation Amount: {:.0f} inches\n\nMinimum Real Precipitation Amount: {:.0f} inches".format(min_temp, min_temp_real))
            elif self.data_dropdown.get() == "Wind Speed":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                min_temp = min(float(temp) for temp in windSpeedMax[start_date:end_date + 1])
                min_temp_real = min(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Wind Speed", self.latitude_set, self.longitude_set))
                self.output_text.config(text="Minimum Input Max Wind Speed: {:.0f} mph\n\nMinimum Real Max Wind Speed: {:.0f} mph".format(min_temp, min_temp_real))
            elif self.data_dropdown.get() == "Precipitation Probability":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                min_temp = min(float(temp) for temp in precipitationProbabilityMax[start_date:end_date + 1])
                min_temp_real = min(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Precipitation Probability", self.latitude_set, self.longitude_set ))
                self.output_text.config(text="Minimum Input Precipitation Probability: {:.0f}%\n\nMinimum Real Precipitation Probability: {:.0f}%".format(min_temp, min_temp_real))

    def write_file(self, input):
        """
        Parse input data and assign values to global variables representing weather data.

        Args:
            input (str): Data input in the format of key-value pairs separated by ': ' and lines separated by '\n'.
                         Keys include 'date', 'weather_code', 'temperature_max', 'temperature_min',
                         'precipitation_sum', 'wind_speed_max', 'precipitation_probability_max'.

        Sets global variables:
            - dates: List of dates parsed from input.
            - weatherCode: List of weather codes parsed from input.
            - temperatureMax: List of maximum temperatures parsed from input.
            - temperatureMin: List of minimum temperatures parsed from input.
            - precipitationSum: List of precipitation amounts parsed from input.
            - windSpeedMax: List of maximum wind speeds parsed from input.
            - precipitationProbabilityMax: List of maximum precipitation probabilities parsed from input.

        Updates combobox values:
            - histogram_start_date_dropdown, histogram_end_date_dropdown, start_date_dropdown, end_date_dropdown:
              Sets their values to the parsed 'dates' list.
        """
        global dates, weatherCode, temperatureMax, temperatureMin, precipitationSum, windSpeedMax, precipitationProbabilityMax
        lines = input.split('\n')
        for line in lines:
            parts = line.split(': ')
            key = parts[0]
            values = parts[1].split()
            if key == 'date':
                dates = values
            elif key == 'weather_code':
                weatherCode = values
            elif key == 'temperature_max':
                temperatureMax = values
            elif key == 'temperature_min':
                temperatureMin = values
            elif key == 'precipitation_sum':
                precipitationSum = values
            elif key == 'wind_speed_max':
                windSpeedMax = values
            elif key == 'precipitation_probability_max':
                precipitationProbabilityMax = values

        #will be removed in final edit
        print("Dates: ", dates)
        print("Weather Codes: ", weatherCode)
        print("Max Temperatures: ", temperatureMax)
        print("Min Temperatures: ", temperatureMin)
        print("Precipitation Sum: ", precipitationSum)
        print("Max Wind Speed: ", windSpeedMax)
        print("Precipitation Probability Max: ", precipitationProbabilityMax)

        self.histogram_start_date_dropdown['values'] = dates
        self.histogram_end_date_dropdown['values'] = dates
        self.start_date_dropdown['values'] = dates
        self.end_date_dropdown['values'] = dates

    # Uploads file
    def upload_file(self):
        """
        Open a file dialog to select a file and read its contents.

        The selected file's contents are read and passed to the 'write_file' method
        for further processing.

        If the file is not found or cannot be read, an error message is displayed.

        This method is typically used to upload a file containing weather data.

        Raises:
            FileNotFoundError: If the selected file is not found or cannot be read.

        """
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    text = file.read()
                    self.write_file(text)
            except FileNotFoundError:
                messagebox.showerror(title='Error', message='File Read Error')

    def plot_histogram(self, event):
        """
        Plot a histogram based on selected data type and date range.

        Args:
            event: Event object that triggered the method.

        Retrieves data type, start date, and end date from dropdowns. Constructs a histogram
        using matplotlib based on the selected data type and the corresponding data from
        start date to end date.

        Clears previous plot if it exists and updates the canvas with the new histogram.

        """
        data_type = self.histogram_data_type_dropdown.get()
        start_date = self.histogram_start_date_dropdown.get()
        end_date = self.histogram_end_date_dropdown.get()

        if data_type and start_date and end_date:
            start_index = dates.index(start_date)
            end_index = dates.index(end_date) + 1

            if start_index < end_index:
                data = {
                    'Temp Low': temperatureMin[start_index:end_index],
                    'Temp High': temperatureMax[start_index:end_index],
                    'Precipitation Amount': precipitationSum[start_index:end_index],
                    'Wind Speed': windSpeedMax[start_index:end_index],
                    'Precipitation Probability': precipitationProbabilityMax[start_index:end_index]
                }[data_type]

                data = [float(d) for d in data]

                # Plot data against dates
                fig, ax = plt.subplots()
                ax.plot(dates[start_index:end_index], data, marker="D")
                ax.set_title(f'{data_type} over Time')
                ax.set_xlabel('Date')
                ax.set_ylabel(data_type)
                plt.xticks(rotation=30)

                # Aesthetics improvements
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_color('#DDDDDD')
                ax.tick_params(colors='#777777', which='both')
                ax.xaxis.label.set_color('#777777')
                ax.yaxis.label.set_color('#777777')
                ax.set_facecolor('#EEEEEE')

                fig.tight_layout()

                # Clear previous plot
                if self.canvas:
                    self.canvas.get_tk_widget().destroy()

                self.canvas = FigureCanvasTkAgg(fig, master=self.histogram_frame)
                self.canvas.draw()
                self.canvas.get_tk_widget().grid(row=1, column=0, columnspan=3, pady=10, padx=10)

    def openMeteoSetup(self, start_date, end_date, data_type_input, latitude, longitude):
        """
        Set up and retrieve weather data from Open-Meteo API.

        Args:
            start_date (int): Index of the start date in the `dates` list.
            end_date (int): Index of the end date in the `dates` list.
            data_type_input (str): Type of weather data to retrieve ('Temp Low', 'Temp High',
                                   'Precipitation Amount', 'Precipitation Probability', 'Wind Speed',
                                   'Weather Code').
            latitude (float): Latitude coordinate for the weather location.
            longitude (float): Longitude coordinate for the weather location.

        Returns:
            list or numpy.ndarray: Weather data based on the `data_type_input` parameter.

        Sets up an Open-Meteo API client with caching and retries on error. Retrieves daily weather
        data for the specified location and date range, converting it into a pandas DataFrame. Returns
        the specific weather data type based on the `data_type_input`.
        """
        start_date = dates[start_date]
        end_date = dates[end_date]
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "precipitation_sum",
                      "precipitation_probability_max", "wind_speed_10m_max"],
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch"
        }
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation {response.Elevation()} m asl")
        print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        # Process daily data. The order of variables needs to be the same as requested.
        daily = response.Daily()
        daily_weather_code = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
        daily_precipitation_sum = daily.Variables(3).ValuesAsNumpy()
        daily_precipitation_probability_max = daily.Variables(4).ValuesAsNumpy()
        daily_wind_speed_10m_max = daily.Variables(5).ValuesAsNumpy()

        daily_data = {
            "date": pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left"
            ).tolist(),
            "weather_code": daily_weather_code,
            "temperature_2m_max": daily_temperature_2m_max,
            "temperature_2m_min": daily_temperature_2m_min,
            "precipitation_sum": daily_precipitation_sum,
            "precipitation_probability_max": daily_precipitation_probability_max,
            "wind_speed_10m_max": daily_wind_speed_10m_max
        }

        daily_dataframe = pd.DataFrame(data=daily_data)
        if(data_type_input == "Temp Low"):
            return daily_temperature_2m_min
        elif(data_type_input == "Temp High"):
            return daily_temperature_2m_max
        elif(data_type_input == "Precipitation Amount"):
            return daily_precipitation_sum
        elif(data_type_input == "Precipitation Probability"):
            return daily_precipitation_probability_max
        elif(data_type_input == "Wind Speed"):
            return daily_wind_speed_10m_max
        elif(data_type_input == "Weather Code"):
            return daily_weather_code


    def write_file(self, input):
        global dates, weatherCode, temperatureMax, temperatureMin, precipitationSum, windSpeedMax, precipitationProbabilityMax
        lines = input.split('\n')
        for line in lines:
            parts = line.split(': ')
            key = parts[0]
            values = parts[1].split()
            if key == 'date':
                dates = values
            elif key == 'weather_code':
                weatherCode = values
            elif key == 'temperature_max':
                temperatureMax = values
            elif key == 'temperature_min':
                temperatureMin = values
            elif key == 'precipitation_sum':
                precipitationSum = values
            elif key == 'wind_speed_max':
                windSpeedMax = values
            elif key == 'precipitation_probability_max':
                precipitationProbabilityMax = values

        self.histogram_start_date_dropdown['values'] = dates
        self.histogram_end_date_dropdown['values'] = dates
        self.start_date_dropdown['values'] = dates
        self.end_date_dropdown['values'] = dates

# REST API routes
@flask_app.route('/weather', methods=['GET'])
def get_weather():
   """
   Get weather data for a specified date range and data type.

   This method retrieves weather data based on the provided start date, end date,
   and data type. If any of the required parameters are missing or the date range
   is invalid, it returns an error message.

   Args:
       None

   Returns:
       json: Weather data for the specified date range and data type, or an error message.
   """
   # Retrieve query parameters from the request
   start_date = request.args.get('start_date')
   end_date = request.args.get('end_date')
   data_type = request.args.get('data_type')

   # Check if any required parameters are missing
   if not start_date or not end_date or not data_type:
       return jsonify({"error": "Missing required parameters"}), 400

   # Validate the date range
   try:
       start_index = dates.index(start_date)
       end_index = dates.index(end_date) + 1
   except ValueError:
       return jsonify({"error": "Invalid date range"}), 400

   # Map the data type to the corresponding data list
   data = {
       'Weather Code': weatherCode,
       'Temp Low': temperatureMin,
       'Temp High': temperatureMax,
       'Precipitation Amount': precipitationSum,
       'Wind Speed': windSpeedMax,
       'Precipitation Probability': precipitationProbabilityMax
   }.get(data_type)

   # Check if the data type is valid
   if not data:
       return jsonify({"error": "Invalid data type"}), 400

   # Generate the result dictionary for the specified date range
   result = {dates[i]: data[i] for i in range(start_index, end_index)}
   return jsonify(result)



@flask_app.route('/weather', methods=['POST'])
def add_weather():
   """
   Add new weather data.

   This method adds new weather data to the existing lists. The new data must
   include a date, and the date must not already exist in the data. If the
   data format is invalid or the date already exists, it returns an error message.

   Args:
       None

   Returns:
       json: Success message or an error message.
   """
   # Retrieve the new data from the request body
   new_data = request.json
   if not new_data or 'date' not in new_data:
       return jsonify({"error": "Invalid data format"}), 400

   # Extract the date from the new data
   date = new_data['date']
   # Check if the date already exists
   if date in dates:
       return jsonify({"error": "Date already exists"}), 400

   # Append the new data to the corresponding lists
   dates.append(date)
   weatherCode.append(str(new_data.get('weather_code', '')))
   temperatureMax.append(str(new_data.get('temperature_max', '')))
   temperatureMin.append(str(new_data.get('temperature_min', '')))
   precipitationSum.append(str(new_data.get('precipitation_sum', '')))
   windSpeedMax.append(str(new_data.get('wind_speed_max', '')))
   precipitationProbabilityMax.append(str(new_data.get('precipitation_probability_max', '')))

   return jsonify({"message": "Data added successfully"}), 201


@flask_app.route('/weather', methods=['PUT'])
def update_weather():
   """
   Update existing weather data.

   This method updates a specific data point for a given date. The request must
   include the date, data point, and the new value. If the data format is invalid
   or the date is not found, it returns an error message.

   Args:
       None

   Returns:
       json: Success message or an error message.
   """
   # Retrieve the update information from the request body
   update_info = request.json
   if not update_info or 'date' not in update_info or 'data_point' not in update_info or 'value' not in update_info:
       return jsonify({"error": "Invalid update format"}), 400

   # Extract the date, data point, and value from the update information
   date = update_info['date']
   data_point = update_info['data_point']
   value = update_info['value']

   # Check if the date exists
   if date not in dates:
       return jsonify({"error": "Date not found"}), 404

   # Get the index of the date
   index = dates.index(date)
   # Update the corresponding data point
   if data_point == 'Weather Code':
       weatherCode[index] = str(value)
   elif data_point == 'Temp Low':
       temperatureMin[index] = str(value)
   elif data_point == 'Temp High':
       temperatureMax[index] = str(value)
   elif data_point == 'Precipitation Amount':
       precipitationSum[index] = str(value)
   elif data_point == 'Wind Speed':
       windSpeedMax[index] = str(value)
   elif data_point == 'Precipitation Probability':
       precipitationProbabilityMax[index] = str(value)
   else:
       return jsonify({"error": "Invalid data point"}), 400

   return jsonify({"message": "Data updated successfully"})
   self.end_date_dropdown['values'] = dates
   self.start_date_dropdown['values'] = dates

@flask_app.route('/weather', methods=['DELETE'])
def delete_weather():
   """
   Delete weather data for a specific date.

   This method deletes weather data for a given date. The date must be provided
   as a query parameter. If the date is not found, it returns an error message.

   Args:
       None

   Returns:
       json: Success message or an error message.
   """
   # Retrieve the date from the query parameters
   date = request.args.get('date')
   if not date:
       return jsonify({"error": "Date parameter is required"}), 400

   # Check if the date exists
   if date not in dates:
       return jsonify({"error": "Date not found"}), 404

   # Get the index of the date
   index = dates.index(date)
   # Remove the data for the specified date
   dates.pop(index)
   weatherCode.pop(index)
   temperatureMax.pop(index)
   temperatureMin.pop(index)
   precipitationSum.pop(index)
   windSpeedMax.pop(index)
   precipitationProbabilityMax.pop(index)

   return jsonify({"message": "Data deleted successfully"})
   self.end_date_dropdown['values'] = dates
   self.start_date_dropdown['values'] = dates

@flask_app.route('/')
def home():
   """
   Home route.

   This method returns a simple message for the home route of the Flask app.

   Args:
       None

   Returns:
       str: A message indicating the landing page for the weather app.
   """
   return "this is the local host landing page for the weather app"


def run_flask():
   """
   Run the Flask app.

   This method starts the Flask application with debugging enabled and without
   the reloader.

   Args:
       None

   Returns:
       None
   """
   flask_app.run(debug=True, use_reloader=False)

if __name__ == "__main__":
    # Initialize the main window
    root = tk.Tk()
    root.title("Weather App")

    # Set the theme
    root.tk.call("source", "azure.tcl")
    root.tk.call("set_theme", "dark")

    # Create and pack the main application frame
    app = App(root)
    app.pack(fill="both", expand=True)

    # Update the root window to calculate the minimum size
    root.update_idletasks()
    root.minsize(root.winfo_width(), root.winfo_height())

    # Center the window on the screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    x_cordinate = (screen_width // 2) - (window_width // 2)
    y_cordinate = (screen_height // 2) - (window_height // 2) - 20
    root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

    # Start the Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Start the Tkinter main loop
    root.mainloop()
