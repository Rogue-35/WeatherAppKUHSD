import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

dates = []
weatherCode = []
temperatureMax = []
temperatureMin = []
precipitationSum = []
windSpeedMax = []
precipitationProbabilityMax = []
# variables for visualization
endDate = -1
startDate = -1
# lookup table
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

class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        # Make the app responsive
        for index in [0, 1, 2]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        # Create value lists
        self.data_type_list = ['Temp Min', 'Temp High', 'Precipitation Amount', 'Wind Speed', 'Precipitation Probability']

        # Create widgets
        self.setup_widgets()

    def setup_widgets(self):
        # Create a Frame for input widgets
        self.header_frame = ttk.Frame(self, padding=(10, 10, 110, 10))
        self.header_frame.grid(
            row=0, column=0, padx=10, pady=(30, 10), sticky="nsew", rowspan=3
        )
        self.header_frame.columnconfigure(index=0, weight=1)

        # Upload Button
        self.upload_button = ttk.Button(self.header_frame, text="Upload", command=self.upload_file)
        self.upload_button.grid(row=0, column=0, padx=5, pady=2)

        # Close Button
        self.close_button = ttk.Button(self.header_frame, text="Close", command=self.destroy)  # currently just closes setup instead of the whole App
        self.close_button.grid(row=0, column=99, padx=5, pady=2, sticky="nsew")

        # Body frame
        self.body_frame = ttk.Frame(self, padding=(10, 10, 10, 10))
        self.body_frame.grid(
            row=1, column=0, padx=10, pady=(30, 10), columnspan=10, sticky="nsew", rowspan=8
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
        self.weather_code_frame = ttk.LabelFrame(self.tab_1, text="Weather Code")
        self.weather_code_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.date_dropdown = ttk.Combobox(
            self.tab_1, state="readonly", values=dates
        )
        self.date_dropdown.grid(row=0, column=0, sticky="ew")
        self.date_dropdown.bind("<<ComboboxSelected>>", self.set_code)

        self.weather_code_text = ttk.Label(self.weather_code_frame, text='')
        self.weather_code_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Data type dropdown
        self.data_type_dropdown = ttk.Combobox(
            self.tab_1, state="readonly", values=self.data_type_list
        )
        self.data_type_dropdown.grid(row=2, column=0, padx=5, pady=90)
        # Tab #2
        self.tab_2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_2, text="Tab 2")

        # Tab #3
        self.tab_3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_3, text="Tab 3")

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

        print("Dates: ", dates)
        print("Weather Codes: ", weatherCode)
        print("Max Temperatures: ", temperatureMax)
        print("Min Temperatures: ", temperatureMin)
        print("Precipitation Sum: ", precipitationSum)
        print("Max Wind Speed: ", windSpeedMax)
        print("Precipitation Probability Max: ", precipitationProbabilityMax)

        self.date_dropdown['values'] = dates

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

    def set_code(self, event):
        selected_date = self.date_dropdown.get()
        if selected_date in dates:
            index = dates.index(selected_date)
            weather_code = int(float(weatherCode[index]))
            self.weather_code_text.config(text=codes[weather_code])

if __name__ == "__main__":
    root = tk.Tk()
    root.title("")

    # Set the theme
    root.tk.call("source", "azure.tcl")
    root.tk.call("set_theme", "dark")

    app = App(root)
    app.pack(fill="both", expand=True)

    # Set a minsize for the window, and place it in the middle
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    root.geometry("+{}+{}".format(x_cordinate, y_cordinate - 20))
    root.geometry('800x600')
    root.title('Weather App')

    root.mainloop()
