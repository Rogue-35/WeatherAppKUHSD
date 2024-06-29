import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox


# variables for data storage
dates = []
weatherCode = []
temperatureMax = []
temperatureMin = []
precipitationSum = []
windSpeedMax = []
precipitationProbabilityMax = []


#variables for visualization
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
        'Slight snow, or rain and snow mixed or hail (Hail, small hail, snow pellets) at time of observation Thunderstorm during the preceding hour but not at time of observation',
        'Moderate or heavy snow, or rain and snow mixed or hail(Hail, small hail, snow pellets) at time of observation Thunderstorm during the preceding hour but not at time of observation',
        'Thunderstorm, slight or moderate, without hail(Hail, small hail, snow pellets) but with rain and/or snow at time of observation',
        'Thunderstorm, slight or moderate, with hail(Hail, small hail, snow pellets) at time of observation',
        'Thunderstorm, heavy, without hail (Hail, small hail, snow pellets) but with rain and/or snow at time of observation',
        'Thunderstorm combined with duststorm or sandstorm at time of observation',
        'Thunderstorm, heavy, with hail (Hail, small hail, snow pellets) at time of observation'
        ]


class WeatherApp(tk.Tk):
   def __init__(self):
       tk.Tk.__init__(self)
       # initializes the window
       self.geometry('1600x900')
       self.title('Weather App')
       self.style = ttk.Style()
       self.style.theme_use('clam')
       self.configure(background='grey')


       # file reading
       self.file_path = tk.StringVar()


       upload_button = tk.Button(self, text="Upload", command = self.upload_file)
       upload_button.grid(row = 0, column = 3)


       # creates a button to close - need to figure how move to a specific spot
       close_button = tk.Button(self, text="Close", command = self.destroy)
       close_button.grid(row = 0, column = 4)


       # sets a variable to the textbox
       output_button = tk.Button(self, text="Print", command = self.display_text )
       output_button.grid(row = 0, column = 5)


       dataType_dropdown = tk.OptionMenu(self, self.file_path, 'Temp High', 'Temp Min', 'Precipitation Amount', 'Wind Speed', 'Precipitation Probability')
       dataType_dropdown.grid(row = 0, column = 6)


       # need to find out how to resize
       self.start_Button = tk.Button(self, text='Enter start date', command = self.setStart)
       self.start_Button.grid(row = 0, column = 0)
       self.dateStart_input = tk.Text(self, width = 20, height = 5 )
       self.dateStart_input.grid(row = 1, column = 0)
       self.end_Button = tk.Button(self, text='Enter end date', command = self.setEnd)
       self.end_Button.grid(row = 0, column = 1)
       self.dateEnd_input = tk.Text(self, width = 20, height = 5 )
       self.dateEnd_input.grid(row = 1, column = 1)


       #visualize data
       self.visualizeData_button = tk.Button(self, text = 'Visualize Data', command = self.visualize)
       self.visualizeData_button.grid(row = 5, column = 5)


   # parses file and sorts data by type
   def write_file(self, input):
       global dates, weatherCode, temperatureMax, temperatureMin, precipitationSum, windSpeedMax, precipitationProbabilityMax
       index = 0
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


       print("Dates: ",dates)
       print("Weather Codes: ",weatherCode)
       print("Max Temperatures: ",temperatureMax)
       print("Min Temperatures: ",temperatureMin)
       print("Precipitation Sum: ",precipitationSum)
       print("Max Wind Speed: ",windSpeedMax)
       print("Precipitation Probability Max: ",precipitationProbabilityMax)


   #uploads file
   def upload_file(self):
       file_path = filedialog.askopenfilename()
       if file_path:
           try:
               with open(file_path, 'r') as file:
                   text = file.read()
                   self.write_file(text)
                   messagebox.showinfo(title='File Uploaded', message='File successfully uploaded and parsed.')
           except FileNotFoundError:
               messagebox.showerror(title='Error', message='Womp Womp')


   def display_text(self):
       return 0
   def setStart(self):
       self.startDate = self.dateStart_input.get("1.0", tk.END).strip()
   def setEnd(self):
       self.endDate = self.dateEnd_input.get("1.0", tk.END).strip()
   def visualize(self):
       import tkinter.messagebox as messagebox
       start_date = self.dateStart_input.get("1.0", tk.END).strip()
       end_date = self.dateEnd_input.get("1.0", tk.END).strip()


       if start_date not in dates:
           messagebox.showerror(title='Error', message='Invalid start date entered.')
           return
       if end_date not in dates:
           messagebox.showerror(title='Error', message='Invalid end date entered.')
           return


       start_index = self.dates.index(start_date)
       end_index = self.dates.index(end_date)


app = WeatherApp()
app.mainloop()
