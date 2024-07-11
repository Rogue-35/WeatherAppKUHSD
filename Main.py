import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import asyncio
from open_meteo import OpenMeteo
from open_meteo.models import DailyParameters
import requests_cache
import pandas as pd
from retry_requests import retry
import requests
import openmeteo_requests

# weather data lists
dates = []
weatherCode = []
temperatureMax = []
temperatureMin = []
precipitationSum = []
windSpeedMax = []
precipitationProbabilityMax = []

# variables for visualization
latitude_set = 0
longitude_set = 0

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
             'Slight snow, or rain and snow mixed or hail(Hail, small hail, snow pellets) at time of observation Thunderstorm during the preceding hour but not at time of observation',
             'Moderate or heavy snow, or rain and snow mixed or hail(Hail, small hail, snow pellets) at time of observation Thunderstorm during the preceding hour but not at time of observation',
             'Thunderstorm, slight or moderate, without hail(Hail, small hail, snow pellets) but with rain and/or snow at time of observation',
             'Thunderstorm, slight or moderate, with hail(Hail, small hail, snow pellets) at time of observation',
             'Thunderstorm, heavy, without hail(Hail, small hail, snow pellets) but with rain and/or snow at time of observation',
             'Thunderstorm combined with duststorm or sandstorm at time of observation',
             'Thunderstorm, heavy, with hail(Hail, small hail, snow pellets) at time of observation'
             ]
    
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        # Make the app responsive
        for index in [0, 1, 2]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        # Create value lists
        self.data_type_list = ['Temp Low', 'Temp High', 'Precipitation Amount', 'Wind Speed', 'Precipitation Probability']
        self.data_type_list_complete = ['Weather Code', 'Temp Low', 'Temp High', 'Precipitation Amount', 'Wind Speed', 'Precipitation Probability']
        self.data_cat = ['Max', 'Min', 'Mean', 'Single']

        # Create widgets
        self.setup_widgets()

    def setup_widgets(self):
        # Create a Frame for input upload button and close button
        self.header_frame = ttk.Frame(self, padding=(20, 10))
        self.header_frame.grid(row=0, column=0, sticky="EW")

        # Upload Button
        self.upload_button = ttk.Button(self.header_frame, text="Upload Input File", command=self.upload_file)
        self.upload_button.grid(row=0, column=0, padx=5, pady=5)

        # Close Button
        self.close_button = ttk.Button(self.header_frame, text="Close", command=self.quit)
        self.close_button.grid(row=0, column=1, padx=5, pady=5)

        # Body frame
        self.body_frame = ttk.Frame(self)
        self.body_frame.grid(
            row=1, column=0, padx=10, pady=10, sticky="NSEW"
        )

        # Notebook
        self.notebook = ttk.Notebook(self.body_frame)
        self.notebook.pack(fill="both", expand=True)

        # Tab #1
        self.tab_1 = ttk.Frame(self.notebook)
        for index in [0, 1]:
            self.tab_1.columnconfigure(index=index, weight=1)
            self.tab_1.rowconfigure(index=index, weight=1)
        self.notebook.add(self.tab_1, text="Tab 1")

        # Date dropdown
        self.weather_code_frame = ttk.LabelFrame(self.tab_1, text="Statistics", padding=(20, 10))
        self.weather_code_frame.grid(row=1, column=0, padx=10, pady=10, sticky = 'NSEW', columnspan = 4)

        self.start_date_dropdown = ttk.Combobox(self.tab_1, state="readonly", values=dates)
        self.start_date_dropdown.grid(row=0, column=2, padx=5, pady=5)
        self.start_date_dropdown.bind("<<ComboboxSelected>>", self.data_test)

        self.data_dropdown = ttk.Combobox(self.tab_1, state="readonly", values=self.data_type_list_complete)
        self.data_dropdown.grid(row=0, column=0, padx=5, pady=5)
        self.data_dropdown.bind("<<ComboboxSelected>>", self.data_test)



        self.output_text = ttk.Label(self.weather_code_frame, text='')
        self.output_text.grid(row=0, column=0, padx=5, pady=5)

        # Tab #2
        self.tab_2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_2, text="Tab 2")

        self.histogram_frame = ttk.LabelFrame(self.tab_2, text="Histogram")
        self.histogram_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nwe")

        # Data type dropdown
        self.histogram_data_type_dropdown = ttk.Combobox(
            self.histogram_frame, state="readonly", values=self.data_type_list
        )
        self.histogram_data_type_dropdown.grid(row=0, column=0, pady=10, padx=10)
        self.histogram_data_type_dropdown.bind("<<ComboboxSelected>>", self.plot_histogram)

        self.histogram_start_date_dropdown = ttk.Combobox(
            self.histogram_frame, state="readonly", values=dates
        )
        self.histogram_start_date_dropdown.grid(row=0, column=1, padx=10, pady=10)
        self.histogram_start_date_dropdown.bind("<<ComboboxSelected>>", self.plot_histogram)
        self.histogram_end_date_dropdown = ttk.Combobox(
            self.histogram_frame, state="readonly", values=dates
        )
        self.histogram_end_date_dropdown.grid(row=0, column=2, padx=10, pady=10)
        self.histogram_end_date_dropdown.bind("<<ComboboxSelected>>", self.plot_histogram)

        self.canvas = None
        # Tab #3
        self.tab_3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_3, text="Tab 3")

    def data_test(self, event):
        if self.data_dropdown.get() == "Weather Code":
            if hasattr(self, 'data_cat_dropdown'):
                self.data_cat_dropdown.grid_remove()
            if hasattr(self, 'end_date_dropdown'):
                self.end_date_dropdown.grid_remove()
        else:
            if not hasattr(self, 'data_cat_dropdown'):
                self.data_cat_dropdown = ttk.Combobox(
                    self.tab_1, state="readonly", values=self.data_cat
                )
                self.data_cat_dropdown.grid(row=0, column=1, padx=5, pady=5)
                self.data_cat_dropdown.bind("<<ComboboxSelected>>", self.stupid)
            else:
                self.data_cat_dropdown.grid()
        self.evaluate()

    def stupid(self, event=None):
        if self.data_cat_dropdown.get() == 'Single':
            if hasattr(self, 'end_date_dropdown'):
                self.end_date_dropdown.grid_remove()
        else:
            if not hasattr(self, 'end_date_dropdown'):
                self.end_date_dropdown = ttk.Combobox(
                    self.tab_1, state="readonly", values=dates
                )
                self.end_date_dropdown.grid(row=0, column=3, padx=5, pady=5)
                self.end_date_dropdown.bind("<<ComboboxSelected>>", self.data_test)
            else:
                self.end_date_dropdown.grid()
        self.evaluate()

    def evaluate(self):
        if self.data_dropdown.get() == "Weather Code":
            selected_date = self.start_date_dropdown.get()
            if selected_date in dates:
                index = dates.index(selected_date)
                weather_code = int(float(weatherCode[index]))
                weather_code_real = self.openMeteoSetup(index, index, "Weather Code" )
                self.output_text.config(text = "Weather Code: {} - {}\nReal Weather Code: {} - {}".format(weather_code, self.codes[weather_code], int(weather_code_real), self.codes[int(weather_code_real)]))
        elif self.data_cat_dropdown.get() == "Single":
            if self.data_dropdown.get() == "Temp Low":
                selected_date = self.start_date_dropdown.get()
                if selected_date in dates:
                    index = dates.index(selected_date)
                    self.output_text.config(text=temperatureMin[index])
            elif self.data_dropdown.get() == "Temp High":
                selected_date = self.start_date_dropdown.get()
                if selected_date in dates:
                    index = dates.index(selected_date)
                    self.output_text.config(text=temperatureMax[index])
            elif self.data_dropdown.get() == "Precipitation Amount":
                selected_date = self.start_date_dropdown.get()
                if selected_date in dates:
                    index = dates.index(selected_date)
                    self.output_text.config(text=precipitationSum[index])
            elif self.data_dropdown.get() == "Wind Speed":
                selected_date = self.start_date_dropdown.get()
                if selected_date in dates:
                    index = dates.index(selected_date)
                    self.output_text.config(text=windSpeedMax[index])
            elif self.data_dropdown.get() == "Precipitation Probability":
                selected_date = self.start_date_dropdown.get()
                if selected_date in dates:
                    index = dates.index(selected_date)
                    self.output_text.config(text=precipitationProbabilityMax[index])
            else:
                return 0
        elif self.data_cat_dropdown.get() == "Mean":
            if self.data_dropdown.get() == "Temp Low":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                mean_temp = sum(float(temp) for temp in temperatureMin[start_date:end_date + 1]) / (end_date - start_date + 1)
                mean_temp_real = sum(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Temp Low" )) / (end_date - start_date + 1)
                self.output_text.config(text="Avg. Input Temp.: {:.4f}\nAvg. Real Temp.: {:.4f}".format(mean_temp, mean_temp_real))
            elif self.data_dropdown.get() == "Temp High":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                mean_temp = sum(float(temp) for temp in temperatureMax[start_date:end_date + 1]) / (end_date - start_date + 1)
                mean_temp_real = sum(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Temp High" )) / (end_date - start_date + 1)
                self.output_text.config(text="Avg. Input Temp.: {:.4f}\nAvg. Real Temp.: {:.4f}".format(mean_temp, mean_temp_real))
            elif self.data_dropdown.get() == "Precipitation Amount":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                mean_temp = sum(float(temp) for temp in precipitationSum[start_date:end_date + 1]) / (end_date - start_date + 1)
                mean_temp_real = sum(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Precipitation Amount" )) / (end_date - start_date + 1)
                self.output_text.config(text="Avg. Input Temp.: {:.4f}\nAvg. Real Temp.: {:.4f}".format(mean_temp, mean_temp_real))
            elif self.data_dropdown.get() == "Wind Speed":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                mean_temp = sum(float(temp) for temp in windSpeedMax[start_date:end_date + 1]) / (end_date - start_date + 1)
                mean_temp_real = sum(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Wind Speed" )) / (end_date - start_date + 1)
                self.output_text.config(text="Avg. Input Temp.: {:.4f}\nAvg. Real Temp.: {:.4f}".format(mean_temp, mean_temp_real))
            elif self.data_dropdown.get() == "Precipitation Probability":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                mean_temp = sum(float(temp) for temp in precipitationProbabilityMax[start_date:end_date + 1]) / (end_date - start_date + 1)
                mean_temp_real = sum(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Precipitation Probability" )) / (end_date - start_date + 1)
                self.output_text.config(text="Avg. Input Temp.: {:.4f}\nAvg. Real Temp.: {:.4f}".format(mean_temp, mean_temp_real))
            else:
                return 0
        elif self.data_cat_dropdown.get() == "Max":
            if self.data_dropdown.get() == "Temp Low":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                max_temp = max(float(temp) for temp in temperatureMin[start_date:end_date + 1])
                max_temp_real = max(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Temp Low" ))
                self.output_text.config(text="Avg. Input Temp.: {:.4f}\nAvg. Real Temp.: {:.4f}".format(max_temp, max_temp_real))
            elif self.data_dropdown.get() == "Temp High":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                max_temp = max(float(temp) for temp in temperatureMax[start_date:end_date + 1])
                max_temp_real = max(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Temp High" ))
                self.output_text.config(text="Avg. Input Temp.: {:.4f}\nAvg. Real Temp.: {:.4f}".format(max_temp, max_temp_real))
            elif self.data_dropdown.get() == "Precipitation Amount":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                max_temp = max(float(temp) for temp in precipitationSum[start_date:end_date + 1])
                max_temp_real = max(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Precipitation Amount" ))
                self.output_text.config(text="Avg. Input Temp.: {:.4f}\nAvg. Real Temp.: {:.4f}".format(max_temp, max_temp_real))
            elif self.data_dropdown.get() == "Wind Speed":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                max_temp = max(float(temp) for temp in windSpeedMax[start_date:end_date + 1])
                max_temp_real = max(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Wind Speed" ))
                self.output_text.config(text="Avg. Input Temp.: {:.4f}\nAvg. Real Temp.: {:.4f}".format(max_temp, max_temp_real))
            elif self.data_dropdown.get() == "Precipitation Probability":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                max_temp = max(float(temp) for temp in precipitationProbabilityMax[start_date:end_date + 1])
                max_temp_real = max(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Precipitation Probability" ))
                self.output_text.config(text="Avg. Input Temp.: {:.4f}\nAvg. Real Temp.: {:.4f}".format(max_temp, max_temp_real))
            else:
                return 0
        elif self.data_cat_dropdown.get() == "Min":
            if self.data_dropdown.get() == "Temp Low":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                min_temp = min(float(temp) for temp in temperatureMin[start_date:end_date + 1])
                min_temp_real = min(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Temp Low" ))
                self.output_text.config(text="Avg. Input Temp.: {:.4f}\nAvg. Real Temp.: {:.4f}".format(min_temp, min_temp_real))
            elif self.data_dropdown.get() == "Temp High":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                min_temp = min(float(temp) for temp in temperatureMax[start_date:end_date + 1])
                min_temp_real = min(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Temp High" ))
                self.output_text.config(text="Avg. Input Temp.: {:.4f}\nAvg. Real Temp.: {:.4f}".format(min_temp, min_temp_real))
            elif self.data_dropdown.get() == "Precipitation Amount":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                min_temp = min(float(temp) for temp in precipitationSum[start_date:end_date + 1])
                min_temp_real = min(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Precipitation Amount"))
                self.output_text.config(text="Avg. Input Temp.: {:.4f}\nAvg. Real Temp.: {:.4f}".format(min_temp, min_temp_real))
            elif self.data_dropdown.get() == "Wind Speed":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                min_temp = min(float(temp) for temp in windSpeedMax[start_date:end_date + 1])
                min_temp_real = min(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Wind Speed" ))
                self.output_text.config(text="Avg. Input Temp.: {:.4f}\nAvg. Real Temp.: {:.4f}".format(min_temp, min_temp_real))
            elif self.data_dropdown.get() == "Precipitation Probability":
                start_date = dates.index(self.start_date_dropdown.get())
                end_date = dates.index(self.end_date_dropdown.get())
                min_temp = min(float(temp) for temp in precipitationProbabilityMax[start_date:end_date + 1])
                min_temp_real = min(float(temp) for temp in self.openMeteoSetup(start_date, end_date, "Precipitation Probability" ))
                self.output_text.config(text="Avg. Input Temp.: {:.4f}\nAvg. Real Temp.: {:.4f}".format(min_temp, min_temp_real))
            else:
                return 0
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

        #needs to be removed in the final edit
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
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    text = file.read()
                    self.write_file(text)
                    # messagebox.showinfo(title='File Uploaded', message='File successfully uploaded and parsed.')
            except FileNotFoundError:
                messagebox.showerror(title='Error', message='Womp Womp')

    def plot_histogram(self, event):
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
                self.raw_data_text = ttk.Label(self.histogram_frame, text=data)
                self.raw_data_text.grid(row=2, column=0, columnspan=3, pady=10, padx=10)

    def openMeteoSetup(self, start_date, end_date, data_type_input):
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
            "latitude": 38.982138,
            "longitude": -94.864437,
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


if __name__ == "__main__":
    # Initialize the main window
    root = tk.Tk()
    root.title("Weather App")

    # Set the theme (do not change theme)
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

    # Start the Tkinter main loop
    root.mainloop()
