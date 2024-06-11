import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

class WeatherApp(tk.Tk):
  def __init__(self):
    tk.Tk.__init__(self)
    self.geometry('500x500')
    self.title('Weather App')
    self.style = ttk.Style()
    self.style.theme_use('clam')

    # Override close action with custom function (properly indented)
    self.protocol("", self.on_closing)

  def on_closing(self):
    # Ask for confirmation and close window if confirmed
    if messagebox.askquestion("Quit", "Are you sure you want to quit?"):
      self.destroy()  # Ensure this line is called to close the window

app = WeatherApp()
app.mainloop()
