import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

#variables for data storage
dates = []
weatherCode = []
temperatureMax = []
temperatureMin = []
precipitationSum = []
windSpeedMax = []
precipitationProbabilityMax = []

#lookup table - not done
codes = ['']

class WeatherApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        #initializes the window
        self.geometry('1600x900')
        self.title('Weather App')
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure(background='grey')

        #file reading
        self.file_path = tk.StringVar()

        upload_button = tk.Button(self, text="Upload", command=self.upload_file)
        upload_button.pack()

        #creates a button to close - need to figre how move to a specific spot
        close_button = tk.Button(self, text="Close", command=self.destroy)
        close_button.pack()

        #creates a text box - need to figure out how to size
        self.text_input = tk.Text(self)
        self.text_input.pack()

        #sets a variable to the textbox
        print_button = tk.Button(self, text="Print", command=self.print_text)
        print_button.pack()

    #parses file and sorts data by type
    def write_file(self, input):
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
        self.file_path.set(filedialog.askopenfilename())
        if self.file_path.get():
            try:
                with open(self.file_path.get(), 'r') as file:
                    text = file.read()
                    self.text_input.delete("1.0", tk.END)
                    self.text_input.insert(tk.END, text)
                    self.write_file(text)
            except FileNotFoundError:
                messagebox.showerror(title='Error', message='Womp Womp')

    def print_text(self):
        text_to_print = self.text_input.get("1.0", tk.END)
        print(text_to_print)

app = WeatherApp()
app.mainloop()
