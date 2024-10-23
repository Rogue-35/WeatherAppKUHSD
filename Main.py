# This project uses the following open-source libraries:
# - Tkinter (standard library)
# - threading (standard library)
# - Matplotlib - https://matplotlib.org/
# - OpenMeteo - https://pypi.org/project/open-meteo/
# - openmeteo_requests - https://pypi.org/project/openmeteo-requests/
# - requests_cache - https://requests-cache.readthedocs.io/
# - pandas - https://pandas.pydata.org/
# - retry_requests - https://pypi.org/project/retry-requests/
# - requests - https://requests.readthedocs.io/
# - Flask - https://flask.palletsprojects.com/
# - psutil - https://pypi.org/project/psutil/
# - click - https://pypi.org/project/click/
# - TKinterModernThemes - https://pypi.org/project/TKinterModernThemes/

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import TKinterModernThemes as TKMT
import matplotlib.pyplot as plt
from click import command
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import openmeteo_requests
import requests_cache
from retry_requests import retry
from flask import Flask, jsonify, request
import threading
import psutil

# import restApi
# import data

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

class App(TKMT.ThemedTKinterFrame):
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

    # Variables for setting the location
    latitude_set = 0
    longitude_set = 0

    def __init__(window, theme, mode, usecommandlineargs=True, usethemeconfigfile=True):
        """
        This is the constructor (initialization function) for the Orion Weather application window.
        It inherits from a base class (likely a custom class for window management) with specific arguments.

        Args:
            window (object): The parent window object.
            theme (str): The theme to use for the application (light, dark, etc.).
            mode (str): The mode to run the application in (unknown purpose in this snippet).
            usecommandlineargs (bool, optional): Whether to use command-line arguments for configuration (default True).
            usethemeconfigfile (bool, optional): Whether to use a theme configuration file (default True).
        """

        super().__init__("Orion Weather", theme, mode, usecommandlineargs=usecommandlineargs,
                         useconfigfile=usethemeconfigfile)

        window.open = False  # Flag to track if the settings window is open
        window.theme = theme  # Store the theme

        window.root.iconbitmap("Icons/weathericonNEW.ico")  # Set the application icon

        window.theme_var = tk.BooleanVar(value=False)  # Variable to track theme preference (False for default theme)
        window.units_var = tk.BooleanVar(value=True)  # Variable to track unit preference (False for Metric, True for Imperial)

        # Make the application window responsive across different screen sizes
        for index in [0, 1, 2]:
            window.root.columnconfigure(index=index, weight=1)
            window.root.rowconfigure(index=index, weight=1)

        # Create lists of data types and categories for weather information
        window.data_type_list = ['Temp Low', 'Temp High', 'Precipitation Amount', 'Wind Speed',
                                 'Precipitation Probability']
        window.data_type_list_complete = ['Weather Code', 'Temp Low', 'Temp High', 'Precipitation Amount', 'Wind Speed',
                                          'Precipitation Probability'] # for histogram
        window.data_cat = ['Max', 'Min', 'Mean', 'Single', "Median", "Mode"]  # Options for how to display data (Max, Min, Average, Single value)

        window.precision_slider_stored = 4  # Default value for decimal precision
        window.setup_widgets()  # Call the function to set up all widgets within the window

    def setup_header(window):
        # Header frame for upload and close buttons
        window.root.header_frame = ttk.Frame(window.root, padding=(20, 10))
        window.root.header_frame.grid(row=0, column=0, sticky="EW")

        # Upload Button to select input file
        window.root.upload_button = ttk.Button(window.root.header_frame, text="Upload Input File",
                                               command=window.upload_file)
        window.root.upload_button.grid(row=0, column=0, padx=5, pady=5)

        # Close Button to close the application
        window.root.close_button = ttk.Button(window.root.header_frame, text="Close", command=window.quitapp)
        window.root.close_button.grid(row=0, column=2, padx=5, pady=5, sticky='NSE')

        # Settings Button to open the settings window
        window.root.settings_button = ttk.Button(window.root.header_frame, text="Settings",
                                                 command=window.settings_window)
        window.root.settings_button.grid(row=0, column=1, padx=5, pady=5)

        window.root.app_title = ttk.Label(window.root.header_frame, text="Orion Weather App", font=("TkDefaultFont", 22, "bold"))
        window.root.app_title.grid(row=0, column=3, padx=25, pady=5, sticky="EW")
    def setup_body(window):
        # Body frame for the notebook widget (tabbed interface)
        window.root.body_frame = ttk.Frame(window.root)


        # Statistics frame within Tab #1 for displaying data
        window.root.start_date_label = ttk.Label(window.root.body_frame, text="Start Date")
        window.root.start_date_label.grid(row=0, column=2, padx=5, pady=5)

        window.root.end_date_label = ttk.Label(window.root.body_frame, text="End Date")
        window.root.end_date_label.grid(row=0, column=3, padx=5, pady=5)

        window.root.data_type_label = ttk.Label(window.root.body_frame, text="Data Type")
        window.root.data_type_label.grid(row=0, column=1, padx=5, pady=5)

        window.root.end_date_label = ttk.Label(window.root.body_frame, text="Data Category")
        window.root.end_date_label.grid(row=0, column=0, padx=5, pady=5)
        
        window.root.output_frame = ttk.Frame(window.root.body_frame)
        window.root.output_frame.grid(row=4, column=0, padx=5, pady=5, sticky="NESW", columnspan=5)
        window.root.output_frame.

        window.root.weather_code_frame_one = ttk.LabelFrame(window.root.output_frame, text="Output 1", padding=(10, 10))
        window.root.weather_code_frame_one.grid(row=0, column=0, padx=10, pady=10, sticky='NSEW', columnspan=3)

        window.root.weather_code_frame_two = ttk.LabelFrame(window.root.output_frame, text="Output 2", padding=(10, 10))
        window.root.weather_code_frame_two.grid(row=0, column=3, padx=10, pady=10, sticky='NSEW', columnspan=3)

        # Start Date Dropdown for selecting the start date
        window.root.start_date_dropdown = ttk.Combobox(window.root.body_frame, state="readonly", values=dates)
        window.root.start_date_dropdown.grid(row=1, column=2, padx=5, pady=5, sticky="W")
        window.root.start_date_dropdown.bind("<<ComboboxSelected>>", window.evaluate)

        # Data Type Dropdown for selecting the type of data
        window.root.data_dropdown = ttk.Combobox(window.root.body_frame, state="readonly",
                                                 values=window.data_type_list_complete)
        window.root.data_dropdown.grid(row=1, column=0, padx=5, pady=5)
        window.root.data_dropdown.bind("<<ComboboxSelected>>", window.evaluate)

        # Data Category Dropdown
        window.root.data_cat_dropdown = ttk.Combobox(window.root.body_frame, state="readonly", values=window.data_cat)
        window.root.data_cat_dropdown.bind("<<ComboboxSelected>>", window.evaluate)
        window.root.data_cat_dropdown.grid(row=1, column=1, padx=5, pady=5)

        # End Date Dropdown
        window.root.end_date_dropdown = ttk.Combobox(window.root.body_frame, state="readonly")
        window.root.end_date_dropdown.grid(row=1, column=3, padx=5, pady=5)
        window.root.end_date_dropdown.bind("<<ComboboxSelected>>", window.evaluate)

        # Output Text Label to display data
        window.root.output_text_one = ttk.Label(window.root.weather_code_frame_one, text='', wraplength=675)
        window.root.output_text_one.grid(row=0, column=0, padx=5, pady=5)

        window.root.output_text_two = ttk.Label(window.root.weather_code_frame_one, text='', wraplength=675)
        window.root.output_text_two.grid(row=0, column=0, padx=5, pady=5)

        # Latitude Entry Field for user to input latitude
        window.root.lat = ttk.Entry(window.root.body_frame)
        window.root.lat.grid(row=2, column=1, padx=5, pady=5, sticky="EW", columnspan=1)

        # Longitude Entry Field for user to input longitude
        window.root.long = ttk.Entry(window.root.body_frame)
        window.root.long.grid(row=3, column=1, padx=5, pady=5, sticky="EW", columnspan=1)

        # titles for longitude and latitude boxes
        window.root.long_title = ttk.Label(window.root.body_frame, text="Longitude")
        window.root.long_title.grid(row=2, column=0, padx=5, pady=5)
        window.root.lat_title = ttk.Label(window.root.body_frame, text="Latitude")
        window.root.lat_title.grid(row=3, column=0, padx=5, pady=5)

        # make the latitude and longitude boxes responsive
        window.root.lat.bind('<0>', window.lat_long_entry, add="+")
        window.root.lat.bind('<1>', window.lat_long_entry, add="+")
        window.root.lat.bind('<2>', window.lat_long_entry, add="+")
        window.root.lat.bind('<3>', window.lat_long_entry, add="+")
        window.root.lat.bind('<4>', window.lat_long_entry, add="+")
        window.root.lat.bind('<5>', window.lat_long_entry, add="+")
        window.root.lat.bind('<6>', window.lat_long_entry, add="+")
        window.root.lat.bind('<7>', window.lat_long_entry, add="+")
        window.root.lat.bind('<8>', window.lat_long_entry, add="+")
        window.root.lat.bind('<9>', window.lat_long_entry, add="+")
        window.root.long.bind('<0>', window.lat_long_entry, add="+")
        window.root.long.bind('<1>', window.lat_long_entry, add="+")
        window.root.long.bind('<2>', window.lat_long_entry, add="+")
        window.root.long.bind('<3>', window.lat_long_entry, add="+")
        window.root.long.bind('<4>', window.lat_long_entry, add="+")
        window.root.long.bind('<5>', window.lat_long_entry, add="+")
        window.root.long.bind('<6>', window.lat_long_entry, add="+")
        window.root.long.bind('<7>', window.lat_long_entry, add="+")
        window.root.long.bind('<8>', window.lat_long_entry, add="+")
        window.root.long.bind('<9>', window.lat_long_entry, add="+")

        # Placeholder for Canvas to display the histogram
        window.root.canvas = None


    def setup_widgets(window):
        """
                Set up all widgets within the frame.

                This method initializes and places various widgets including buttons, dropdowns, labels,
                and frames within the main frame of the application.
        """
        window.setup_body()
        window.setup_header()

        return


    class ToggleSwitch(ttk.Checkbutton):
        """
        A custom toggle switch widget that inherits from ttk.Checkbutton.

        This class allows the creation of a toggle switch with text that updates based
        on the state of the switch. It uses a ttk.Checkbutton styled as a switch.
        """

        def __init__(self, master, text, variable, command=None, **kwargs):
            """
            Initialize the ToggleSwitch.

            Args:
                master (widget): The parent widget.
                text (str): The label text for the toggle switch.
                variable (tk.Variable): A Tkinter variable (e.g., BooleanVar) to track the state.
                command (callable, optional): A command function to execute when the switch is toggled.
                **kwargs: Additional keyword arguments passed to the ttk.Checkbutton initialization.
            """
            # Initialize ttk.Checkbutton with custom style and link the toggle method to command
            super().__init__(master, style="Switch.TCheckbutton", variable=variable, command=self.toggle, **kwargs)

            # Store the text label and the variable tracking the switch's state
            self.text = text
            self.variable = variable
            self.user_command = command  # Store the user-provided command (optional)

            # Update the text displayed on the switch to reflect its current state
            self.update_text()

        def toggle(self):
            """
            Toggle the state of the switch and update the displayed text.

            If a user-defined command was provided, it is also executed after the state update.
            """
            self.update_text()  # Update the displayed text to reflect the new state

            # If a command was provided by the user, execute it
            if self.user_command:
                self.user_command()

        def update_text(self):
            """
            Update the text label of the switch based on its current state (ON/OFF).
            """
            # Determine the current state of the switch and update the text accordingly
            state = "ON" if self.variable.get() else "OFF"
            self.configure(text=f"{self.text}: {state}")  # Update the displayed label

    def setting_track(window):
        """
        Track and apply settings changes for the application.

        This function triggers the necessary functions to apply new settings, such as adjusting
        precision and evaluating data, and then closes the settings popup window.

        """
        # Call the function to adjust the precision slider settings
        window.precision_slider()

        # Call the function to evaluate data based on new settings
        window.evaluate(event="none")

        # Set the open flag to False, indicating that the settings popup is closed
        window.open = False

        # Destroy the settings popup window to close it
        window.root.settings_popup.destroy()

        window.canvas.draw()

    def settings_window(window):
        """
        Open the settings window where the user can adjust various application preferences.

        This function checks if the settings window is already open to prevent multiple instances. It then creates a
        popup window where the user can modify settings like dark mode, units, and precision, and choose different styles.
        """
        # Check if the settings window is already open; if yes, do nothing
        if window.open:
            return

        # Set the flag to indicate that the settings window is now open
        window.open = True

        # Create a new popup window for settings
        window.root.settings_popup = tk.Toplevel(window.root)
        window.root.settings_popup.title("Settings")

        # Make the settings window not resizable
        window.root.settings_popup.resizable(False, False)

        # Set the size of the settings window
        window.root.settings_popup.geometry("400x250")

        # Set the icon for the settings window
        window.root.settings_popup.iconbitmap("Icons/settingsiconNEW.ico")

        # Configure grid columns and rows to allow resizing within the window
        window.root.settings_popup.grid_columnconfigure(0, weight=1)
        window.root.settings_popup.grid_rowconfigure(1, weight=1)

        # Create a style for the title label
        title_style = ttk.Style()
        title_style.configure("Title.TLabel", font=("Comic Sans MS", 16, "bold"))

        # Create and place the title label
        settings_title = ttk.Label(window.root.settings_popup, text="Settings", style="Title.TLabel")
        settings_title.grid(row=0, column=0, padx=10, pady=10, sticky="N")

        # Create a frame to hold the settings options
        settings_frame = ttk.Frame(window.root.settings_popup)
        settings_frame.grid(row=1, column=0, padx=20, pady=10, sticky="NSEW")

        # Create a switch for toggling dark mode
        theme_switch = window.ToggleSwitch(settings_frame, text="Light Mode", variable=window.theme_var,
                                           command=window.update_theme)
        theme_switch.grid(row=0, column=0, sticky="W", pady=10)

        # Create a switch for toggling between Imperial and Metric units
        units_switch = window.ToggleSwitch(settings_frame, text="Imperial Units", variable=window.units_var)
        units_switch.grid(row=1, column=0, sticky="W", pady=10)

        # Create a label and dropdown for selecting a style theme
        #window.root.styles_label = ttk.Label(settings_frame, state="readonly", text="Style")
        #window.root.styles_label.grid(row=3, column=0, padx=10, pady=10, sticky="N")

        # Available styles
        window.root.styles = "Sun-valley", "Park", "Azure"

        # Create the style dropdown menu
        window.root.style_dropdown = ttk.Combobox(settings_frame, state="readonly", values=window.root.styles)
        #window.root.style_dropdown.bind("<<ComboboxSelected>>", window.update_styles())
        #window.root.style_dropdown.grid(row=4, column=0, padx=10, pady=10, sticky="NSEW")

        # Create a label and slider for adjusting precision
        Precision_label = ttk.Label(settings_frame, text="Precision")
        Precision_label.grid(row=5, column=0, padx=10, pady=10, sticky="NW")
        window.root.Precision_slider = ttk.Scale(settings_frame, value=window.precision_slider_stored, from_=0, to=4,
                                                 orient='horizontal')
        window.root.Precision_slider.grid(row=5, column=1, padx=10, pady=10, sticky="NSEW")

        # Create a close button to apply changes and close the settings window
        window.root.close_settings_button = ttk.Button(
            window.root.settings_popup,
            text="Close",
            command=lambda: window.setting_track()  # Use lambda to call setting_track when button is clicked
        )
        window.root.close_settings_button.grid(row=6, column=0, padx=10, pady=10, sticky="SE")

    def precision_slider(window):
        """
        Retrieve and store the current value from the precision slider.

        This function attempts to get the current value from the precision slider. If successful,
        it updates the stored precision value. If an error occurs (e.g., the slider is not accessible),
        the stored precision value remains unchanged.

        Returns:
            int: The stored precision value.
        """
        try:
            # Get the current value from the precision slider and store it as an integer
            window.precision_slider_stored = int(window.root.Precision_slider.get())
            return window.precision_slider_stored
        except:
            # In case of an error, return the previously stored precision value
            return window.precision_slider_stored

    def update_theme(window):
        """
        Update the application theme based on the current state of the theme switch.

        This function checks the value of the theme toggle variable to determine whether dark mode
        should be enabled or light mode should be set. It then updates the application theme accordingly.
        """
        # Set the theme to "dark" if the theme switch is on, otherwise set to "light"
        window.theme = "light" if window.theme_var.get() else "dark"

        # Apply the selected theme to the application
        window.root.tk.call("set_theme", window.theme)

        window.plot_histogram()
        window.root.settings_popup.focus_force()


    def update_styles(window):
        """
        Update the application's style based on the user's selection from the style dropdown.

        This function retrieves the selected style from the dropdown menu and applies it to the
        application by calling the appropriate theme update function.
        """
        # Get the selected style from the style dropdown
        window.mode = window.root.style_dropdown.get()

        # Apply the selected style to the application
        window.root.tk.call("set_theme", window.mode)


    def lat_long_entry(window, event):
        """
        Process latitude and longitude values entered by the user.

        This method retrieves the values from the latitude and longitude entry widgets. If either field
        is empty, it assigns a default value of 0. After retrieving the values, it calls the evaluate
        method to further process the input.

        Args:
            event (tk.Event, optional): The event that triggered this method (e.g., keypress).
        """
        # Retrieve the latitude value, defaulting to 0 if the entry is empty
        if window.root.lat.get() == '':
            window.latitude_set = 0
        else:
            window.latitude_set = float(window.root.lat.get())

        # Retrieve the longitude value, defaulting to 0 if the entry is empty
        if window.root.long.get() == '':
            window.longitude_set = 0
        else:
            window.longitude_set = float(window.root.long.get())

        # Call the evaluate method to process the retrieved latitude and longitude values
        window.evaluate(event='none')

    def evaluate(window, event):
        """
        Evaluate and set the output text based on the user-selected data category and data type.

        This method retrieves the selected data type and category from the dropdowns, and then
        determines the appropriate data handling method to call. It also converts units as needed
        before processing the data.
        """

        window.root.end_date_dropdown['values'] = dates
        window.root.start_date_dropdown['values'] = dates

        # Convert units if necessary
        window.convert_units()
        window.plot_histogram()

        # Retrieve the selected data type and category
        data_type = window.root.data_dropdown.get()
        category = window.root.data_cat_dropdown.get() if hasattr(window.root, 'data_cat_dropdown') else None

        # Handle different data types and categories
        if data_type == "Weather Code":
            # Handle the weather code data type
            window.handle_weather_code()
        elif category == "Single":
            # Handle single data category
            window.handle_single_data(data_type)
        elif category in ["Mean", "Max", "Min", "Median", "Mode"]:
            # Handle aggregate data for mean, max, and min categories
            window.handle_aggregate_data(data_type, category)

    def units(window):
        """
        Determine the appropriate unit of measurement based on the selected data type and user preference for units.

        This method checks the selected data type from the dropdown and the user's choice between Imperial
        and Metric units. It returns the corresponding unit of measurement for temperature, precipitation,
        wind speed, and precipitation probability.

        Returns:
            str: The unit of measurement for the selected data type, or None for non-applicable types.
        """
        # Get the selected data type
        data_type = window.root.data_dropdown.get()

        if window.units_var.get():  # True for Imperial Units
            match data_type:
                case "Weather Code":
                    return  # No units for weather code
                case "Temp High":
                    return "°F"  # Fahrenheit for temperature
                case "Temp Low":
                    return "°F" # Fahrenheit for temperature
                case "Precipitation Amount":
                    return "inches"  # Inches for precipitation
                case "Wind Speed":
                    return "mph"  # Miles per hour for wind speed
                case "Precipitation Probability":
                    return "%"  # Percentage for precipitation probability
        else:  # Metric Units
            match data_type:
                case "Weather Code":
                    return  # No units for weather code
                case "Temp High":
                    return "°C"  # Celsius for temperature
                case "Temp Low":
                    return "°C" # Celsius for temperature
                case "Precipitation Amount":
                    return "mm"  # Millimeters for precipitation
                case "Wind Speed":
                    return "km/h"  # Kilometers per hour for wind speed
                case "Precipitation Probability":
                    return "%"  # Percentage for precipitation probability

    # Set last units to the starting value
    last_unit_type = True

    def convert_units(window):
        """
        Converts weather data between Imperial and Metric units based on user preference.

        The function checks if the user has switched the unit type and performs the necessary
        conversions for temperature, precipitation, and wind speed.

        Args:
            window: The main application window object.
        """
        # Get the current unit type preference from the user's settings
        unit_type = window.units_var.get()

        # If the unit type hasn't changed, no conversion is needed
        if unit_type == window.last_unit_type:
            return

        if not unit_type:  # Converting from Imperial to Metric
            for i in range(len(dates)):
                # Convert temperature from Fahrenheit to Celsius
                temperatureMax[i] = (float(temperatureMax[i]) - 32) * 5 / 9
                temperatureMin[i] = (float(temperatureMin[i]) - 32) * 5 / 9

                # Convert precipitation from inches to millimeters
                precipitationSum[i] = float(precipitationSum[i]) * 25.4

                # Convert wind speed from miles per hour to kilometers per hour
                windSpeedMax[i] = float(windSpeedMax[i]) * 1.60934

            # Update the last unit type to reflect the current setting
            window.last_unit_type = False

        else:  # Converting from Metric to Imperial
            for i in range(len(dates)):
                # Convert temperature from Celsius to Fahrenheit
                temperatureMax[i] = (float(temperatureMax[i]) * 9 / 5) + 32
                temperatureMin[i] = (float(temperatureMin[i]) * 9 / 5) + 32

                # Convert precipitation from millimeters to inches
                precipitationSum[i] = float(precipitationSum[i]) / 25.4

                # Convert wind speed from kilometers per hour to miles per hour
                windSpeedMax[i] = float(windSpeedMax[i]) / 1.60934

            # Update the last unit type to reflect the current setting
            window.last_unit_type = True

    def handle_weather_code(window):
        """
        Handles the retrieval and display of weather codes based on user selection.

        This method retrieves the weather code for the selected date, calls an external method
        to obtain the real weather code, and sets the output text accordingly.
        """
        # Get the selected date from the dropdown
        selected_date = window.root.start_date_dropdown.get()

        # Check if the selected date is valid and exists in the dates list
        if selected_date in dates:
            # Find the index of the selected date
            index = dates.index(selected_date)

            # Retrieve the weather code associated with the selected date
            weather_code = int(float(weatherCode[index]))

            # Call the openMeteoSetup method to get the real weather code
            weather_code_real = window.openMeteoSetup(index, index, "Weather Code", window.latitude_set,
                                                      window.longitude_set)

            # Set the output text with both the input and real weather codes
            window.set_output(f"Input Weather Code: {weather_code} - {window.codes[weather_code]}\n\n"
                              f"Real Weather Code: {int(weather_code_real[0])} - {window.codes[(int(weather_code_real[0]))]}")

    def handle_single_data(window, data_type):
        """
        Handles the retrieval and display of single data values based on user selection.

        This method retrieves the input and real data for the selected date and data type,
        and sets the output text accordingly.

        Args:
            data_type: The type of data being retrieved (e.g., temperaturemin, precipitation).
        """
        # Get the selected date from the dropdown
        selected_date = window.root.start_date_dropdown.get()

        # Check if the selected date is valid and exists in the dates list
        if selected_date in dates:
            # Find the index of the selected date
            index = dates.index(selected_date)

            # Retrieve the real data from the external source
            real_data = window.openMeteoSetup(index, index, data_type, window.latitude_set, window.longitude_set)

            # Get the input data based on the selected data type
            input_data = window.get_input_data(data_type, index)

            # Set the output text with formatted input and real data values
            window.set_output(
                f"Input {data_type}: {(float(input_data)):.{window.precision_slider()}f} {window.units()}\n\n"
                f"Real {data_type}: {float(real_data):.{window.precision_slider()}f} {window.units()}"
            )

    def handle_aggregate_data(window, data_type, category):
        """
        Handles the retrieval and display of aggregated data values based on user selection.

        This method calculates the aggregate input and real data for the specified date range
        and data type, and sets the output text accordingly.

        Args:
            data_type: The type of data being retrieved (e.g., temperaturemin, precipitation).
            category: The type of aggregation to perform (e.g., mean, max, min).
        """
        # Get the indices for the start and end dates from the dropdowns
        if hasattr(window, "start_date_dropdown"):
            start_date = dates.index(window.root.start_date_dropdown.get())
        else:
            start_date = ''
        if hasattr(window, "end_date_dropdown"):
            end_date = dates.index(window.root.end_date_dropdown.get())
        else:
            end_date = ''

        # Calculate the aggregate input data from the user's input list
        input_data = window.calculate_aggregate(
            window.get_input_data_list(data_type), start_date, end_date, category
        )

        # Calculate the aggregate real data from the external source
        real_data = window.calculate_aggregate(
            window.openMeteoSetup(start_date, end_date, data_type, window.latitude_set, window.longitude_set),
            0,
            end_date - start_date,
            category
        )

        # Set the output text with formatted aggregate input and real data values
        window.set_output(
            f"{category} Input {data_type}: {input_data:.{window.precision_slider()}f} {window.units()}\n\n"
            f"{category} Real {data_type}: {real_data:.{window.precision_slider()}f} {window.units()}"
        )

    def get_input_data(window, data_type, index):
        """
        Retrieves a specific data value based on the selected data type and index.

        This function accesses predefined data lists for different types of weather-related
        data and returns the value at the specified index, formatted as a string.

        Args:
            data_type: The type of data being retrieved (e.g., Temp Low, Temp High).
            index: The index of the desired value in the corresponding data list.

        Returns:
            A string representation of the data value at the specified index.
        """
        # Define a mapping of data types to their corresponding data lists
        data_mapping = {
            "Temp Low": temperatureMin,  # Maps "Temp Low" to the temperatureMin data
            "Temp High": temperatureMax,  # Maps "Temp High" to the temperatureMax data
            "Precipitation Amount": precipitationSum,  # Maps "Precipitation Amount" to the precipitationSum data
            "Wind Speed": windSpeedMax,  # Maps "Wind Speed" to the windSpeedMax data
            "Precipitation Probability": precipitationProbabilityMax
            # Maps "Precipitation Probability" to the precipitationProbabilityMax data
        }

        # Retrieve the list of data corresponding to the specified data type
        data_list = data_mapping[data_type]

        # Return the data at the specified index, formatted as a string
        return f"{(data_list[index])}"

    def get_input_data_list(window, data_type):
        """
        Retrieves the list of data values corresponding to the specified data type.

        This function provides access to predefined lists of weather-related data values
        based on the user-selected data type.

        Args:
            data_type: The type of data being retrieved (e.g., Temp Low, Temp High).

        Returns:
            A list of data values associated with the specified data type.
        """
        # Define a mapping of data types to their corresponding data lists and return the relevant list
        return {
            "Temp Low": temperatureMin,  # List of minimum temperature values
            "Temp High": temperatureMax,  # List of maximum temperature values
            "Precipitation Amount": precipitationSum,  # List of total precipitation values
            "Wind Speed": windSpeedMax,  # List of maximum wind speed values
            "Precipitation Probability": precipitationProbabilityMax  # List of precipitation probabilities
        }[data_type]

    def calculate_aggregate(window, data_list, start, end, category):
        """
        Calculates the aggregate value of a specified category from a list of data.

        This function computes the mean, maximum, or minimum value of a subset of data
        defined by the start and end indices.

        Args:
            data_list: A list of numerical data values to aggregate.
            start: The starting index for the subset of data.
            end: The ending index for the subset of data.
            category: The type of aggregation to perform (e.g., Mean, Max, Min).

        Returns:
            The calculated aggregate value based on the specified category.
        """
        # Convert the specified range of data values to floats for calculation
        values = [float(temp) for temp in data_list[start:end + 1]]

        # Calculate and return the aggregate value based on the specified category
        match category:
            case "Mean":
                return sum(values) / len(values) if values else 0  # Prevent division by zero
            case "Max":
                return max(values) if values else float('-inf')  # Return negative infinity if no values
            case "Min":
                return min(values) if values else float('inf')  # Return positive infinity if no values
            case "Mode":
                if not values:
                    return 0
                from collections import Counter
                counts = Counter(values)
                max_count = max(counts.values())
                modes = [values for value, count in counts.items() if count == max_count]
                return modes[0]

    def set_output(window, text):
        """
        Sets the output text in the designated output area of the window.

        This function updates the output text widget to display the provided text
        with a specified font size.

        Args:
            text: The text to display in the output area.
        """
        # Configure the output text widget with the new text and font settings
        window.root.output_text_one.config(text=text, font=("Arial", 20))

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
        # Declare global variables to hold parsed weather data
        global dates, weatherCode, temperatureMax, temperatureMin, precipitationSum, windSpeedMax, precipitationProbabilityMax

        # Split the input data into lines
        lines = input.split('\n')

        # Parse each line and assign values to the corresponding global variable
        for line in lines:
            parts = line.split(': ')
            key = parts[0]  # Extract the key from the line
            values = parts[1].split()  # Extract the values and split them into a list

            match(key):
                case 'date':
                    dates = values
                case 'weather_code':
                    weatherCode = values
                case 'temperature_max':
                    temperatureMax = values
                case  'temperature_min':
                    temperatureMin = values
                case 'precipitation_sum':
                    precipitationSum = values
                case 'wind_speed_max':
                    windSpeedMax = values
                case 'precipitation_probability_max':
                    precipitationProbabilityMax = values


        # Update the dropdown values in the GUI with the parsed dates
        window.root.start_date_dropdown['values'] = dates
        window.root.end_date_dropdown['values'] = dates

    def update_api(window):
        """
        Updates the date dropdowns in the GUI based on the currently available dates.

        This function refreshes the values in the start and end date dropdowns
        to reflect the most recent data  from the REST API.
        """
        # Update the start date dropdown with the available dates
        window.root.start_date_dropdown['values'] = dates

        # Update the end date dropdown with the available dates
        window.root.end_date_dropdown['values'] = dates

    def upload_file(window):
        """
        Open a file dialog to select a file and read its contents.

        The selected file's contents are read and passed to the 'write_file' method
        for further processing. If the file is not found or cannot be read, an error
        message is displayed.

        Raises:
            FileNotFoundError: If the selected file is not found or cannot be read.
        """
        # Open a file dialog for the user to select a file
        file_path = filedialog.askopenfilename()

        # If a file was selected
        if file_path:
            try:
                # Attempt to open and read the contents of the selected file
                with open(file_path, 'r') as file:
                    text = file.read()  # Read the file contents
                    window.write_file(text)  # Pass the contents to the write_file method
            except FileNotFoundError:
                # Show an error message if the file cannot be read
                messagebox.showerror(title='Error', message='File Read Error')

        # Update the layout of the window after file upload
        window.root.close_button.grid(row=0, column=2, padx=5, pady=5, sticky='NSE')
        window.root.body_frame.grid(row=1, column=0, padx=10, pady=10, sticky="NSEW")
        # window.root.notebook.pack(fill="both", expand=True)

    def plot_histogram(window):
        """
        Plot a bar chart based on selected data type and date range.

        Retrieves the data type, start date, and end date from dropdowns. Constructs a bar chart
        using matplotlib based on the selected data type and the corresponding data from
        the start date to the end date.

        Clears the previous plot if it exists and updates the canvas with the new chart.
        """
        # Get the selected data type, start date, and end date from the dropdowns
        data_type = window.root.data_dropdown.get()
        start_date = window.root.start_date_dropdown.get()
        end_date = window.root.end_date_dropdown.get()

        # Convert units as necessary for the plot
        window.convert_units()

        # Proceed only if all necessary selections are made
        if data_type and start_date and end_date:
            # Determine the indices for the selected date range
            start_index = dates.index(start_date)
            end_index = dates.index(end_date) + 1

            # Ensure that the start index is less than the end index
            if start_index < end_index:
                # Retrieve the corresponding data for the selected data type
                data = {
                    'Weather Code': weatherCode[start_index:end_index],
                    'Temp Low': temperatureMin[start_index:end_index],
                    'Temp High': temperatureMax[start_index:end_index],
                    'Precipitation Amount': precipitationSum[start_index:end_index],
                    'Wind Speed': windSpeedMax[start_index:end_index],
                    'Precipitation Probability': precipitationProbabilityMax[start_index:end_index]
                }[data_type]

                # Convert data to float for plotting
                data = [float(d) for d in data]
                plot_dates = dates[start_index:end_index]

                # Set color scheme based on mode
                background = '#1c1c1c'
                graph = '#363636'
                text = '#d1d1d1'
                grid = '#787878'
                bar_color = '#64b5f6'

                #window.update_styles()
                if window.theme == "dark":
                    background = '#1c1c1c'
                    graph = '#363636'
                    text = '#d1d1d1'
                    grid = '#787878'
                    bar_color = '#64b5f6'
                if window.theme == "light":
                    background = '#fafafa'
                    graph = '#f9f9f9'
                    text = '#212121'
                    grid = '#c2c2c2'

                # Create a new figure and axis for the bar plot
                fig, ax = plt.subplots(facecolor=background)

                # Create bar plot with customized appearance
                bars = ax.bar(plot_dates, data, color=bar_color, alpha=0.7, edgecolor=text)

                ax.set_title(f'{data_type} Over Time')
                ax.set_xlabel('Date')
                ax.set_ylabel(f'{data_type} ({window.units()})')
                ax.title.set_color(text)

                # Rotate x-axis labels for better readability
                plt.xticks(rotation=45, ha='right')

                # Aesthetic improvements for the plot
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_color('#DDDDDD')
                ax.tick_params(color=text, which='both', axis='both')
                ax.grid(True, linestyle='--', alpha=0.7, color=grid)
                ax.set_facecolor(color=graph)
                ax.xaxis.label.set_color(color=text)
                ax.yaxis.label.set_color(color=text)
                plt.xticks(color=text)
                plt.yticks(color=text)

                # Optimize layout to fit elements nicely
                fig.tight_layout()

                # Clear the previous plot
                plt.close()

                # Create a new canvas to display the bar plot
                window.canvas = FigureCanvasTkAgg(fig, master=window.root.body_frame)
                window.canvas.draw()
                window.canvas.get_tk_widget().grid(row=2, column=3, columnspan=2, rowspan=2, pady=10, padx=10)

    def openMeteoSetup(window, start_date, end_date, data_type_input, latitude, longitude):
        """
        Set up and retrieve weather data from the Open-Meteo API.

        This function configures the API client, builds the request parameters,
        fetches the weather data, processes it, and extracts the requested data
        based on the specified input.

        Args:
            start_date: The index of the starting date from the dates list.
            end_date: The index of the ending date from the dates list.
            data_type_input: The type of weather data to be retrieved (e.g., temperature, precipitation).
            latitude: The latitude for the weather data request.
            longitude: The longitude for the weather data request.

        Returns:
            The extracted weather data for the specified type over the specified date range.
        """
        # Get the actual start and end dates from the dates list using the provided indices
        start_date = dates[start_date]
        end_date = dates[end_date]

        # Set up the Open-Meteo API client
        client = window._setup_openmeteo_client()

        # Build the request parameters for the API call
        params = window._build_api_params(start_date, end_date, latitude, longitude)

        # Fetch the weather data using the configured client and parameters
        response = window._fetch_weather_data(client, params)

        # Process the daily data retrieved from the API response
        daily_data = window._process_daily_data(response)

        # Extract and return the requested data from the processed daily data
        return window._extract_requested_data(daily_data, data_type_input)

    def _setup_openmeteo_client(window):
        """
        Set up the Open-Meteo API client with caching and retry mechanism on error.

        This function initializes a session that caches API responses to reduce
        the number of requests sent to the Open-Meteo API and includes a retry
        mechanism to handle transient errors.

        Returns:
            An Open-Meteo API client configured with caching and retry capabilities.
        """
        # Create a cached session that stores responses for 1 hour (3600 seconds)
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)

        # Set up a retry session that will attempt up to 5 retries with exponential backoff
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)

        # Return an Open-Meteo client using the configured retry session
        return openmeteo_requests.Client(session=retry_session)

    def _build_api_params(window, start_date, end_date, latitude, longitude):
        """
        Build the parameters for the API request to Open-Meteo.

        This function constructs a dictionary of parameters required to make a request
        to the Open-Meteo API, including geographical coordinates, date range, and
        desired weather data attributes.

        Args:
            start_date: The starting date for the weather data request.
            end_date: The ending date for the weather data request.
            latitude: The latitude coordinate for the location.
            longitude: The longitude coordinate for the location.

        Returns:
            A dictionary containing the parameters for the API request.
        """
        return {
            # Geographical coordinates for the weather data request
            "latitude": latitude,
            "longitude": longitude,

            # Date range for the requested weather data
            "start_date": start_date,
            "end_date": end_date,

            # List of daily weather data attributes to retrieve
            "daily": [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max"
            ],

            # Set temperature unit based on user preference
            "temperature_unit": "fahrenheit" if window.units_var.get() else "celsius",

            # Set wind speed unit based on user preference
            "wind_speed_unit": "mph" if window.units_var.get() else "kmh",

            # Set precipitation unit based on user preference
            "precipitation_unit": "inch" if window.units_var.get() else "mm"
        }

    def _fetch_weather_data(window, client, params):
        """
        Fetch weather data from the Open-Meteo API.

        This function makes a request to the Open-Meteo API using the specified client
        and parameters to retrieve weather data.

        Args:
            client: The Open-Meteo API client used to send the request.
            params: A dictionary of parameters for the API request.

        Returns:
            The first response object containing weather data from the API.
        """
        # Define the URL endpoint for the historical forecast API
        url = "https://historical-forecast-api.open-meteo.com/v1/forecast"

        # Send a request to the Open-Meteo API and retrieve the responses
        responses = client.weather_api(url, params=params)

        # Return the first response from the API
        return responses[0]

    def _process_daily_data(window, response):
        """
        Process the daily data from the API response.

        This function extracts daily weather data from the provided API response
        and organizes it into a dictionary for easier access.

        Args:
            response: The API response object containing weather data.

        Returns:
            A dictionary containing processed daily weather data, with keys for
            various weather attributes and their corresponding values as NumPy arrays.
        """
        # Access the daily data section of the API response
        daily = response.Daily()

        # Extract and return daily weather data as a dictionary
        return {
            # Weather code for the day
            "weather_code": daily.Variables(0).ValuesAsNumpy(),

            # Maximum temperature recorded for the day
            "temperature_2m_max": daily.Variables(1).ValuesAsNumpy(),

            # Minimum temperature recorded for the day
            "temperature_2m_min": daily.Variables(2).ValuesAsNumpy(),

            # Total precipitation for the day
            "precipitation_sum": daily.Variables(3).ValuesAsNumpy(),

            # Maximum probability of precipitation for the day
            "precipitation_probability_max": daily.Variables(4).ValuesAsNumpy(),

            # Maximum wind speed recorded for the day
            "wind_speed_10m_max": daily.Variables(5).ValuesAsNumpy()
        }

    def _extract_requested_data(window, daily_data, data_type_input):
        """
        Extract the requested data type from the daily data.

        This function retrieves specific weather data based on the requested data type
        from the provided daily weather data.

        Args:
            daily_data: A dictionary containing daily weather data.
            data_type_input: A string specifying the type of data to extract.

        Returns:
            The extracted data corresponding to the requested data type.
        """
        # Mapping of user-friendly data type names to actual keys in the daily_data dictionary
        data_mapping = {
            "Temp Low": "temperature_2m_min",
            "Temp High": "temperature_2m_max",
            "Precipitation Amount": "precipitation_sum",
            "Precipitation Probability": "precipitation_probability_max",
            "Wind Speed": "wind_speed_10m_max",
            "Weather Code": "weather_code"
        }

        # Return the data corresponding to the requested data type
        return daily_data[data_mapping[data_type_input]]

    def write_file(window, input):
        """
        Parse input data and assign values to global variables representing weather data.

        This function takes a string input containing weather data in key-value pairs,
        splits it into relevant components, and assigns the parsed values to global variables.
        Additionally, it updates dropdown values in the user interface with the parsed dates.

        Args:
            input (str): Data input in the format of key-value pairs separated by ': '
                         and lines separated by '\n'. Keys include 'date', 'weather_code',
                         'temperature_max', 'temperature_min', 'precipitation_sum',
                         'wind_speed_max', 'precipitation_probability_max'.

        Sets global variables:
            - dates: List of dates parsed from input.
            - weatherCode: List of weather codes parsed from input.
            - temperatureMax: List of maximum temperatures parsed from input.
            - temperatureMin: List of minimum temperatures parsed from input.
            - precipitationSum: List of precipitation amounts parsed from input.
            - windSpeedMax: List of maximum wind speeds parsed from input.
            - precipitationProbabilityMax: List of maximum precipitation probabilities parsed from input.

        Updates combobox values:
            - histogram_start_date_dropdown, histogram_end_date_dropdown, start_date_dropdown,
              end_date_dropdown: Sets their values to the parsed 'dates' list.
        """
        # Declare global variables to hold parsed weather data
        global dates, weatherCode, temperatureMax, temperatureMin, precipitationSum, windSpeedMax, precipitationProbabilityMax

        # Split the input string into lines for processing
        lines = input.split('\n')

        # Iterate through each line and parse key-value pairs
        for line in lines:
            parts = line.split(': ')
            key = parts[0]  # The key (e.g., 'date', 'temperature_max')
            try:
                if parts[1] == 0:
                    break
            except IndexError:
                return
            values = parts[1].split()  # The associated values split into a list - errors

            # Assign values to corresponding global variables based on the key
            match key:
                case 'date':
                    dates = values
                case 'weather_code':
                    weatherCode = values
                case 'temperature_max':
                    temperatureMax = values
                case 'temperature_min':
                    temperatureMin = values
                case 'precipitation_sum':
                    precipitationSum = values
                case 'wind_speed_max':
                    windSpeedMax = values
                case 'precipitation_probability_max':
                    precipitationProbabilityMax = values

        # Update dropdown values in the window based on the parsed dates
        if hasattr(window, "start_date_dropdown"):
            window.root.start_date_dropdown['values'] = dates
        if hasattr(window, "end_date_dropdown"):
            window.end_date_dropdown['values'] = dates

    def quitapp(window):
        """
        Terminate running processes and close the application.

        This function attempts to terminate each process in the `processes` list
        and handles any exceptions that may arise during the termination process.
        If a process cannot be terminated due to access issues, an error message
        is printed to the console.
        """
        # Iterate through each process in the processes list
        for proc in processes:
            try:
                proc.terminate()  # Attempt to terminate the process
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Handle exceptions for processes that cannot be terminated
                print(f"Failed to terminate {proc.info['name']} with PID {proc.info['pid']}. Access Denied.")

        window.root.destroy()  # Close the application window

    # REST API routes
    @flask_app.route('/weather', methods=['GET'])
    def get_weather(self):
        """
        Get weather data for a specified date range and data type.

        This method retrieves weather data based on the provided start date, end date,
        and data type. If any of the required parameters are missing or the date range
        is invalid, it returns an error message.

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

        # Validate the date range by checking indices
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
        if data is None:
            return jsonify({"error": "Invalid data type"}), 400

        # Generate the result dictionary for the specified date range
        result = {dates[i]: data[i] for i in range(start_index, end_index)}

        return jsonify(result)

    @flask_app.route('/weather', methods=['POST'])
    def add_weather(self):
        """
        Add new weather data.

        This method adds new weather data to the existing lists. The new data must
        include a date, and the date must not already exist in the data. If the
        data format is invalid or the date already exists, it returns an error message.

        Returns:
            json: Success message or an error message.
        """
        # Retrieve the new data from the request body
        new_data = request.json

        # Validate the incoming data
        if not new_data or 'date' not in new_data:
            return jsonify({"error": "Invalid data format"}), 400

        # Extract the date from the new data
        date = new_data['date']

        # Check if the date already exists in the dates list
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

        # Update the API to reflect the newly added data
        app.update_api()

        return jsonify({"message": "Data added successfully"}), 201

    @flask_app.route('/weather', methods=['PUT'])
    def update_weather(self):
        """
        Update existing weather data.

        This method updates a specific data point for a given date. The request must
        include the date, data point, and the new value. If the data format is invalid
        or the date is not found, it returns an error message.

        Returns:
            json: Success message or an error message.
        """
        # Retrieve the update information from the request body
        update_info = request.json

        # Validate the incoming update format
        if not update_info or 'date' not in update_info or 'data_point' not in update_info or 'value' not in update_info:
            return jsonify({"error": "Invalid update format"}), 400

        # Extract the date, data point, and value from the update information
        date = update_info['date']
        data_point = update_info['data_point']
        value = update_info['value']

        # Check if the date exists in the dates list
        if date not in dates:
            return jsonify({"error": "Date not found"}), 404

        # Get the index of the date for updating
        index = dates.index(date)

        # Update the corresponding data point based on the specified data point
        match(data_point):
            case 'Weather Code':
                weatherCode[index] = str(value)
            case 'Temp Low':
                temperatureMin[index] = str(value)
            case 'Temp High':
                temperatureMax[index] = str(value)
            case 'Precipitation Amount':
                precipitationSum[index] = str(value)
            case 'Wind Speed':
                windSpeedMax[index] = str(value)
            case 'Precipitation Probability':
                precipitationProbabilityMax[index] = str(value)
            case _:
                return jsonify({"error": "Invalid data point"}), 400

        # Update the API to reflect the changes made
        app.update_api()

        return jsonify({"message": "Data updated successfully"})

    @flask_app.route('/weather', methods=['DELETE'])
    def delete_weather(self):
        """
        Delete weather data for a specific date.

        This method deletes weather data for a given date. The date must be provided
        as a query parameter. If the date is not found, it returns an error message.

        Returns:
            json: Success message or an error message.
        """
        # Retrieve the date from the query parameters
        date = request.args.get('date')

        # Validate the presence of the date parameter
        if not date:
            return jsonify({"error": "Date parameter is required"}), 400

        # Check if the specified date exists in the dates list
        if date not in dates:
            return jsonify({"error": "Date not found"}), 404

        # Get the index of the date for removal
        index = dates.index(date)

        # Remove the data for the specified date from all corresponding lists
        dates.pop(index)
        weatherCode.pop(index)
        temperatureMax.pop(index)
        temperatureMin.pop(index)
        precipitationSum.pop(index)
        windSpeedMax.pop(index)
        precipitationProbabilityMax.pop(index)

        # Update the API to reflect the changes made
        app.update_api()

        return jsonify({"message": "Data deleted successfully"})

    @flask_app.route('/')
    def home(self):
        """
        Home route.

        This method returns a simple message for the home route of the Flask app.

        Returns:
            str: A message indicating the landing page for the weather app.
        """
        return "this is the local host landing page for the weather app"

if __name__ == "__main__":
    # Retrieve a list of currently running Python processes
    processes = [proc for proc in psutil.process_iter(['pid', 'name']) if 'python.exe' in proc.info['name']]

    # Initialize the main application with a title and theme
    app = App("Park", "dark")

    # Start the Flask app in a separate thread to prevent blocking the Tkinter main loop
    flask_thread = threading.Thread(target=flask_app.run, kwargs={'debug': True, 'use_reloader': False})
    flask_thread.start()

    # Start the Tkinter event loop
    app.root.mainloop()
