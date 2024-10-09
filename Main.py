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

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.ttk import Checkbutton

import TKinterModernThemes as TKMT
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import openmeteo_requests
import requests_cache
from retry_requests import retry
from flask import Flask, jsonify, request
import threading
import psutil

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



    def __init__(window, parent, usecommandlineargs=True, usethemeconfigfile=True):
        ttk.Frame.__init__(window)
        window.open = False
        """
        Initialize the frame with given parent widget.

        Args:
            parent (tk.Widget): Parent widget to which this frame belongs.
        """

        window.theme_var = tk.BooleanVar(value=False)  # False for Light Mode
        window.units_var = tk.BooleanVar(value=False)  # False for Imperial Units

        # Make the app responsive
        for index in [0, 1, 2]:
            window.columnconfigure(index=index, weight=1)
            window.rowconfigure(index=index, weight=1)

        # Create lists of data types and categories
        window.data_type_list = ['Temp Low', 'Temp High', 'Precipitation Amount', 'Wind Speed',
                                 'Precipitation Probability']
        window.data_type_list_complete = ['Weather Code', 'Temp Low', 'Temp High', 'Precipitation Amount', 'Wind Speed',
                                          'Precipitation Probability']
        window.data_cat = ['Max', 'Min', 'Mean', 'Single']

        window.precision_slider_stored = 2  # Default value if not called - Prevent errors

        # Set up all widgets within the frame
        window.setup_widgets()

    def setup_widgets(window):
        """
        Set up all widgets within the frame.

        This method initializes and places various widgets including buttons, dropdowns, labels,
        and frames within the main frame of the application.
        """

        # Header frame for upload and close buttons
        window.header_frame = ttk.Frame(window, padding=(20, 10))
        window.header_frame.grid(row=0, column=0, sticky="EW")

        # Upload Button
        window.upload_button = ttk.Button(window.header_frame, text="Upload Input File", command=window.upload_file)
        window.upload_button.grid(row=0, column=0, padx=5, pady=5)

        # Close Button
        window.close_button = ttk.Button(window.header_frame, text="Close", command=window.quitapp)
        window.close_button.grid(row=0, column=2, padx=5, pady=5, sticky='NSE')

        # Body frame for notebook
        window.body_frame = ttk.Frame(window)
        window.body_frame.grid(row=1, column=0, padx=10, pady=10, sticky="NSEW")

        #Settings button
        window.settings_button = ttk.Button(window.header_frame, text="Settings", command=window.settings_window)
        window.settings_button.grid(row=0, column=1, padx=5, pady=5)

        # Notebook widget for tabs
        window.notebook = ttk.Notebook(window.body_frame)
        window.notebook.pack(fill="both", expand=True)

        # Tab #1: Data Output
        window.tab_1 = ttk.Frame(window.notebook)
        window.notebook.add(window.tab_1, text="Data Output")

        # Statistics frame within Tab #1
        window.weather_code_frame = ttk.LabelFrame(window.tab_1, text="Statistics", padding=(20, 10))
        window.weather_code_frame.grid(row=2, column=0, padx=10, pady=10, sticky='NSEW', columnspan=4)

        # Start Date Dropdown
        window.start_date_dropdown = ttk.Combobox(window.tab_1, state="readonly", values=dates)
        window.start_date_dropdown.grid(row=0, column=2, padx=5, pady=5, sticky="W")
        window.start_date_dropdown.bind("<<ComboboxSelected>>", window.data_test)

        # Data Type Dropdown
        window.data_dropdown = ttk.Combobox(window.tab_1, state="readonly", values=window.data_type_list_complete, )
        window.data_dropdown.grid(row=0, column=0, padx=5, pady=5)
        window.data_dropdown.bind("<<ComboboxSelected>>", window.data_test)

        # Output Text Label
        window.output_text = ttk.Label(window.weather_code_frame, text='', wraplength=675)
        window.output_text.grid(row=0, column=0, padx=5, pady=5)

        # Latitude and Longitude Entry Fields
        window.lat = ttk.Entry(window.tab_1, width=30,)
        window.lat.grid(row=1, column=0, padx=5, pady=5, sticky="NSEW", columnspan=2)
        window.lat.bind('<0>', window.lat_long_entry)
        window.lat.bind('<1>', window.lat_long_entry, add="+")
        window.lat.bind('<2>', window.lat_long_entry, add="+")
        window.lat.bind('<3>', window.lat_long_entry, add="+")
        window.lat.bind('<4>', window.lat_long_entry, add="+")
        window.lat.bind('<5>', window.lat_long_entry, add="+")
        window.lat.bind('<6>', window.lat_long_entry, add="+")
        window.lat.bind('<7>', window.lat_long_entry, add="+")
        window.lat.bind('<8>', window.lat_long_entry, add="+")
        window.lat.bind('<9>', window.lat_long_entry, add="+")



        window.long = ttk.Entry(window.tab_1, width=30)
        window.long.grid(row=1, column=2, padx=5, pady=5, sticky="NSEW", columnspan=2)
        window.long.bind('<0>', window.lat_long_entry)
        window.long.bind('<1>', window.lat_long_entry, add="+")
        window.long.bind('<2>', window.lat_long_entry, add="+")
        window.long.bind('<3>', window.lat_long_entry, add="+")
        window.long.bind('<4>', window.lat_long_entry, add="+")
        window.long.bind('<5>', window.lat_long_entry, add="+")
        window.long.bind('<6>', window.lat_long_entry, add="+")
        window.long.bind('<7>', window.lat_long_entry, add="+")
        window.long.bind('<8>', window.lat_long_entry, add="+")
        window.long.bind('<9>', window.lat_long_entry, add="+")

        # Tab #2: Histogram
        window.tab_2 = ttk.Frame(window.notebook)
        window.notebook.add(window.tab_2, text="Histogram")

        # Histogram frame within Tab #2
        window.histogram_frame = ttk.LabelFrame(window.tab_2, text="Histogram")
        window.histogram_frame.grid(row=2, column=0, padx=10, pady=10, sticky="NSEW")

        # Histogram Data Type Dropdown
        window.histogram_data_type_dropdown = ttk.Combobox(
            window.histogram_frame, state="readonly", values=window.data_type_list
        )
        window.histogram_data_type_dropdown.grid(row=0, column=0, pady=10, padx=10)
        window.histogram_data_type_dropdown.bind("<<ComboboxSelected>>", window.plot_histogram)

        # Histogram Start Date Dropdown
        window.histogram_start_date_dropdown = ttk.Combobox(
            window.histogram_frame, state="readonly", values=dates
        )
        window.histogram_start_date_dropdown.grid(row=0, column=1, padx=10, pady=10)
        window.histogram_start_date_dropdown.bind("<<ComboboxSelected>>", window.plot_histogram)

        # Histogram End Date Dropdown
        window.histogram_end_date_dropdown = ttk.Combobox(
            window.histogram_frame, state="readonly", values=dates
        )
        window.histogram_end_date_dropdown.grid(row=0, column=2, padx=10, pady=10)
        window.histogram_end_date_dropdown.bind("<<ComboboxSelected>>", window.plot_histogram)

        # Canvas for Histogram
        window.canvas = None

        # Tab #3: Credits
        window.tab_3 = ttk.Frame(window.notebook)
        window.notebook.add(window.tab_3, text="Credits")

        # Credits frame within Tab #3
        window.credits = ttk.LabelFrame(window.tab_3, text="Credits", padding=(20, 10))
        window.credits.grid(row=0, column=0, padx=10, pady=10)

        # Credits Text Box
        window.credits_textbox = tk.Text(window.credits, wrap='word', height=30, width=90)
        window.credits_textbox.grid(row=0, column=0, padx=10, pady=10, sticky='NSEW', rowspan=2, columnspan=2)

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
        window.credits_textbox.insert('1.0', credits_text)
        window.credits_textbox.config(state='disabled')  # Make the text box read-only

        # Configure grid weight to allow the text box to expand
        window.credits.grid_rowconfigure(0, weight=1)
        window.credits.grid_columnconfigure(0, weight=1)

    class ToggleSwitch(ttk.Checkbutton):
        def __init__(self, master, text, variable, command=None, **kwargs):
            super().__init__(master, style="Switch.TCheckbutton", variable=variable, command=self.toggle, **kwargs)
            self.text = text
            self.variable = variable
            self.user_command = command
            self.update_text()

        def toggle(self):
            self.update_text()
            if self.user_command:
                self.user_command()

        def update_text(self):
            state = "ON" if self.variable.get() else "OFF"
            self.configure(text=f"{self.text}: {state}")

    def setting_track(window):
        window.precision_slider()
        window.evaluate()
        window.open = False
        window.settings_popup.destroy()

    def settings_window(window):
        if window.open:
            return
        window.open = True

        window.settings_popup = tk.Toplevel(window)
        window.settings_popup.title("Settings")
        window.settings_popup.resizable(False, False)
        window.settings_popup.geometry("400x400")
        window.settings_popup.iconbitmap("settings.ico")

        # Configure the grid
        window.settings_popup.grid_columnconfigure(0, weight=1)
        window.settings_popup.grid_rowconfigure(1, weight=1)

        # Create and configure the title style
        title_style = ttk.Style()
        title_style.configure("Title.TLabel", font=("TkDefaultFont", 16, "bold"))

        # Create the title label
        settings_title = ttk.Label(window.settings_popup, text="Settings", style="Title.TLabel")
        settings_title.grid(row=0, column=0, padx=10, pady=10, sticky="N")

        # Create the settings frame
        settings_frame = ttk.Frame(window.settings_popup)
        settings_frame.grid(row=1, column=0, padx=20, pady=10, sticky="NSEW")

        # Create theme switch
        theme_switch = window.ToggleSwitch(settings_frame, text="Dark Mode", variable=window.theme_var)
        theme_switch.grid(row=0, column=0, sticky="W", pady=10)

        # Create units switch
        units_switch = window.ToggleSwitch(settings_frame, text="Imperial Units", variable=window.units_var)
        units_switch.grid(row=1, column=0, sticky="W", pady=10)

        # Create other settings widgets
        styles_label = ttk.Label(settings_frame, state="readonly", text="Style")
        styles_label.grid(row=3, column=0, padx=10, pady=10, sticky="N")
        styles = "Sun-valley", "Park", "Azure"
        Style_dropdown = ttk.Combobox(settings_frame, state="readonly", values=styles)
        Style_dropdown.grid(row=4, column=0, padx=10, pady=10, sticky="NSEW")

        Precision_label = ttk.Label(settings_frame, text="Precision")
        Precision_label.grid(row=5, column=0, padx=10, pady=10, sticky="NW")
        window.Precision_slider = ttk.Scale(settings_frame, value=window.precision_slider_stored, from_=0, to=4, orient='horizontal')
        window.Precision_slider.grid(row=5, column=1, padx=10, pady=10, sticky="NSEW")

        # Create the close button
        window.close_settings_button = ttk.Button(
            window.settings_popup,
            text="Close",
            command=lambda: window.setting_track()  # Use lambda to call setting_track when button is clicked
        )
        window.close_settings_button.grid(row=6, column=0, padx=10, pady=10, sticky="SE")

    def precision_slider(window):

        try:
            window.precision_slider_stored = int(window.Precision_slider.get())
            return window.precision_slider_stored
        except:
            return window.precision_slider_stored

    def curr_theme(window):
        return "Dark" if window.theme_var else "Light"
    def lat_long_entry(window, event):
        """
        Process latitude and longitude values entered by the user.

        This method retrieves latitude and longitude values from Entry widgets
        and calls the evaluate method to process them.

        Args:
            event (tk.Event, optional): The event that triggered this method.
        """
        # Get the latitude and longitude values from the Entry widgets
        if window.lat.get() == '':
            window.latitude_set = 0
        else:
            window.latitude_set = float(window.lat.get())

        if window.long.get() == '':
            window.longitude_set = 0
        else:
            window.longitude_set = float(window.long.get())

        # Call the evaluate method to process the latitude and longitude values
        window.evaluate()

    def data_test(window, event):
        """
        Handle changes when a new data type is selected.

        This method checks if the selected data type is "Weather Code". If it is,
        it hides the data category dropdown and end date dropdown (if they exist).
        Otherwise, it shows the data category dropdown and binds a handler to it.

        Args:
            event (tk.Event, optional): The event that triggered this method.
        """
        # Check if the selected data type is "Weather Code"
        if window.data_dropdown.get() == "Weather Code":
            # Hide data category dropdown if it exists
            if hasattr(window, 'data_cat_dropdown'):
                window.data_cat_dropdown.grid_remove()

            # Hide end date dropdown if it exists
            if hasattr(window, 'end_date_dropdown'):
                window.end_date_dropdown.grid_remove()
        else:
            # If data type is not "Weather Code", show data category dropdown
            if not hasattr(window, 'data_cat_dropdown'):
                window.data_cat_dropdown = ttk.Combobox(
                    window.tab_1, state="readonly", values=window.data_cat
                )
                window.data_cat_dropdown.grid(row=0, column=1, padx=5, pady=5)
                window.data_cat_dropdown.bind("<<ComboboxSelected>>", window.handle_data_category_selection)
                if window.data_dropdown.get() != "single" and not window.data_dropdown.get() == "Weather Code":
                    window.end_date_dropdown.grid(row=0, column=3, padx=5, pady=5)
                    window.end_date_dropdown.bind("<<ComboboxSelected>>", window.data_test)
                else:
                    window.end_date_dropdown.grid_remove()
            else:
                window.data_cat_dropdown.grid()
        window.handle_data_category_selection()
        # Call the evaluate method to process the changes
        window.evaluate()

    def handle_data_category_selection(window, event=None):
        """
        Handle changes when a new data category is selected.

        This method checks if the selected data category is 'Single'. If it is,
        it hides the end date dropdown (if it exists). Otherwise, it shows the
        end date dropdown and binds a handler to it.

        Args:
            event (tk.Event, optional): The event that triggered this method.
        """
        if hasattr(window, 'data_cat_dropdown'):
        # Check if the selected data category is 'Single'
            if window.data_cat_dropdown.get() == 'Single':
                # Hide end date dropdown if it exists
                if hasattr(window, 'end_date_dropdown'):
                    window.end_date_dropdown.grid_remove()
            else:
                # Show end date dropdown if it does not exist
                if not hasattr(window, 'end_date_dropdown'):
                    window.end_date_dropdown = ttk.Combobox(
                        window.tab_1, state="readonly"
                    )
                    window.end_date_dropdown['values'] = dates
                    window.end_date_dropdown.current(1)
                    window.start_date_dropdown.current(0)
                    window.end_date_dropdown.grid(row=0, column=3, padx=5, pady=5)
                    window.end_date_dropdown.bind("<<ComboboxSelected>>", window.data_test)
                else:
                    window.end_date_dropdown.grid()

            # Call the evaluate method to process the changes
        window.evaluate()

    def evaluate(window):
        """
        Sets the output text based on user-selected data category and type.
        """
        data_type = window.data_dropdown.get()
        category = window.data_cat_dropdown.get() if hasattr(window, 'data_cat_dropdown') else None

        if data_type == "Weather Code":
            window._handle_weather_code()
        elif category == "Single":
            window._handle_single_data(data_type)
        elif category in ["Mean", "Max", "Min"]:
            window._handle_aggregate_data(data_type, category)

    def units(window):
        data_type = window.data_dropdown.get()
        if(data_type == "Weather Code"):
            return
        elif data_type == "Temp High" or data_type == "Temp Low":
            return "F"
        elif data_type == "Precipitation Amount":
            return "inches"
        elif data_type == "Wind Speed":
            return "m/h"
        elif data_type == "Precipitation Probability":
            return "%"
    def _handle_weather_code(window):
        selected_date = window.start_date_dropdown.get()
        if selected_date in dates:
            index = dates.index(selected_date)
            weather_code = int(float(weatherCode[index]))
            weather_code_real = window.openMeteoSetup(index, index, "Weather Code", window.latitude_set,
                                                      window.longitude_set)
            window._set_output(f"Input Weather Code: {weather_code} - {window.codes[weather_code]}\n\n"
                               f"Real Weather Code: {int(weather_code_real)} - {window.codes[int(weather_code_real)]}")

    def _handle_single_data(window, data_type):

        selected_date = window.start_date_dropdown.get()
        if selected_date in dates:
            index = dates.index(selected_date)
            real_data = window.openMeteoSetup(index, index, data_type, window.latitude_set, window.longitude_set)
            input_data = window._get_input_data(data_type, index)
            window._set_output(f"Input {data_type}: {(float(input_data)):.{window.precision_slider()}f} {window.units()}\n\nReal {data_type}: {float(real_data):.{window.precision_slider()}f} {window.units()}")

    def _handle_aggregate_data(window, data_type, category):
        start_date = dates.index(window.start_date_dropdown.get())
        end_date = dates.index(window.end_date_dropdown.get())
        input_data = window._calculate_aggregate(window._get_input_data_list(data_type), start_date, end_date, category)
        real_data = window._calculate_aggregate(
            window.openMeteoSetup(start_date, end_date, data_type, window.latitude_set, window.longitude_set),
            0, end_date - start_date, category
        )
        window._set_output(
            f"{category} Input {data_type}: {input_data:.{window.precision_slider()}f} {window.units()}\n\n{category} Real {data_type}: {real_data:.{window.precision_slider()}f} {window.units()}")

    def _get_input_data(window, data_type, index):
        data_mapping = {
            "Temp Low": (temperatureMin),
            "Temp High": (temperatureMax),
            "Precipitation Amount": (precipitationSum),
            "Wind Speed": (windSpeedMax),
            "Precipitation Probability": (precipitationProbabilityMax)
        }
        data_list = data_mapping[data_type]
        return f"{(data_list[index])}"

    def _get_input_data_list(window, data_type):
        return {
            "Temp Low": temperatureMin,
            "Temp High": temperatureMax,
            "Precipitation Amount": precipitationSum,
            "Wind Speed": windSpeedMax,
            "Precipitation Probability": precipitationProbabilityMax
        }[data_type]

    def _calculate_aggregate(window, data_list, start, end, category):
        values = [float(temp) for temp in data_list[start:end + 1]]
        if category == "Mean":
            return sum(values) / len(values)
        elif category == "Max":
            return max(values)
        elif category == "Min":
            return min(values)

    def _set_output(window, text):
        window.output_text.config(text=text, font=("Arial", 20))

    def write_file(window, input):
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

        # will be removed in final edit
        print("Dates: ", dates)
        print("Weather Codes: ", weatherCode)
        print("Max Temperatures: ", temperatureMax + "F")
        print("Min Temperatures: ", temperatureMin + "F")
        print("Precipitation Sum: ", precipitationSum)
        print("Max Wind Speed: ", windSpeedMax + "mph")
        print("Precipitation Probability Max: ", precipitationProbabilityMax + "%")

        window.histogram_start_date_dropdown['values'] = dates
        window.histogram_end_date_dropdown['values'] = dates
        window.start_date_dropdown['values'] = dates
        window.end_date_dropdown['values'] = dates

    def update_api(window):
        """
            Updates the date dropdowns when the REST API is used

            Args: None

        """
        window.start_date_dropdown['values'] = dates
        window.end_date_dropdown['values'] = dates

    # Uploads file
    def upload_file(window):
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
                    window.write_file(text)
            except FileNotFoundError:
                messagebox.showerror(title='Error', message='File Read Error')

    def plot_histogram(window, event):
        """
        Plot a histogram based on selected data type and date range.

        Args:
            event: Event object that triggered the method.

        Retrieves data type, start date, and end date from dropdowns. Constructs a histogram
        using matplotlib based on the selected data type and the corresponding data from
        start date to end date.

        Clears previous plot if it exists and updates the canvas with the new histogram.

        """
        data_type = window.histogram_data_type_dropdown.get()
        start_date = window.histogram_start_date_dropdown.get()
        end_date = window.histogram_end_date_dropdown.get()

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
                if window.canvas:
                    window.canvas.get_tk_widget().destroy()

                window.canvas = FigureCanvasTkAgg(fig, master=window.histogram_frame)
                window.canvas.draw()
                window.canvas.get_tk_widget().grid(row=1, column=0, columnspan=3, pady=10, padx=10)

    def openMeteoSetup(window, start_date, end_date, data_type_input, latitude, longitude):
        """Set up and retrieve weather data from Open-Meteo API."""
        start_date = dates[start_date]
        end_date = dates[end_date]

        client = window._setup_openmeteo_client()
        params = window._build_api_params(start_date, end_date, latitude, longitude)
        response = window._fetch_weather_data(client, params)
        daily_data = window._process_daily_data(response)

        return window._extract_requested_data(daily_data, data_type_input)

    def _setup_openmeteo_client(window):
        """Set up the Open-Meteo API client with cache and retry on error."""
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        return openmeteo_requests.Client(session=retry_session)

    def _build_api_params(window, start_date, end_date, latitude, longitude):
        """Build the parameters for the API request."""
        return {
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

    def _fetch_weather_data(window, client, params):
        """Fetch weather data from the Open-Meteo API."""
        url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
        responses = client.weather_api(url, params=params)
        return responses[0]

    def _process_daily_data(window, response):
        """Process the daily data from the API response."""
        daily = response.Daily()
        return {
            "weather_code": daily.Variables(0).ValuesAsNumpy(),
            "temperature_2m_max": daily.Variables(1).ValuesAsNumpy(),
            "temperature_2m_min": daily.Variables(2).ValuesAsNumpy(),
            "precipitation_sum": daily.Variables(3).ValuesAsNumpy(),
            "precipitation_probability_max": daily.Variables(4).ValuesAsNumpy(),
            "wind_speed_10m_max": daily.Variables(5).ValuesAsNumpy()
        }

    def _extract_requested_data(window, daily_data, data_type_input):
        """Extract the requested data type from the daily data."""
        data_mapping = {
            "Temp Low": "temperature_2m_min",
            "Temp High": "temperature_2m_max",
            "Precipitation Amount": "precipitation_sum",
            "Precipitation Probability": "precipitation_probability_max",
            "Wind Speed": "wind_speed_10m_max",
            "Weather Code": "weather_code"
        }
        return daily_data[data_mapping[data_type_input]]

    def write_file(window, input):
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

        window.histogram_start_date_dropdown['values'] = dates
        window.histogram_end_date_dropdown['values'] = dates
        window.start_date_dropdown['values'] = dates
        if hasattr(window, 'end_date_dropdown'):
            window.end_date_dropdown['values'] = dates


    def quitapp(window):

        for proc in processes:
            try:
                proc.terminate()  # Attempt to terminate the process
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print(f"Failed to terminate {proc.info['name']} with PID {proc.info['pid']}. Access Denied.")

        # window.quit()
        # window.destroy()
        # sys.exit(0000)


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

    app.update_api()
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

    app.update_api()
    return jsonify({"message": "Data updated successfully"})


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

    app.update_api()
    return jsonify({"message": "Data deleted successfully"})


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
    processes = [proc for proc in psutil.process_iter(['pid', 'name']) if 'python.exe' in proc.info['name']]

    # Initialize the main window
    window = TKMT.ThemedTKinterFrame("WeatherAPPKUHSD", "Sun-valley", "dark")
    # root = tk.Tk()
    window.root.title("Weather App")
    window.root.iconbitmap("cloud_icon.ico")

    # Set the theme

    # window.tk.call("source", "azure.tcl")
    # window.tk.call("set_theme", "dark")

    # Create and pack the main application frame
    app = App(window.root)
    app.pack(fill="both", expand=True)

    # Update the window to calculate the minimum size
    window.root.update_idletasks()
    window.root.minsize(window.root.winfo_width(), window.root.winfo_height())

    # Center the window on the screen
    screen_width = window.root.winfo_screenwidth()
    screen_height = window.root.winfo_screenheight()
    window_width = window.root.winfo_width()
    window_height = window.root.winfo_height()
    x_cordinate = (screen_width // 2) - (window_width // 2)
    y_cordinate = (screen_height // 2) - (window_height // 2) - 20
    window.root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

    # Start the Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Start the Tkinter main loop
    window.root.mainloop()
