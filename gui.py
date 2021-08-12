import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import askstring
from fnc import btn_pressed


class MainWindow(tk.Tk):
    def __init__(self, threadworker):
        super().__init__()
        self.title('WeatherTk')
        
        # the following dict is used to cache icons in memory
        # this is only a "temporary" solution and will be changed "soon"
        self.icon_cache = dict()

        self.threadworker = threadworker
        self.protocol("WM_DELETE_WINDOW", self.on_close_button_pressed)

        self.WEATHER_CURRENT_URL = "http://api.openweathermap.org/data/2.5/weather?"
        self.WEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/onecall?"
        self.UNIT = "metric"    # TODO: add option in the gui to change the unit
        self.API_KEY = self.init_api_key()
        self.history = self.load_history()

        self.lab1 = tk.Label(self)
        self.lab1.configure(text="Enter city:")
        self.lab1.pack()

        self.input_frame = InputFrame(self, self.history)
        self.input_frame.pack()

        self.status_label = tk.Label(self)
        self.status_label.pack()

        self.current_weather_frame = CurrentWeatherFrame(self)
        self.current_weather_frame.pack()
        self.space_label = tk.Label(self, text = " ")
        self.space_label.pack()
        # this label is used to create e bit of space between the two frames
        self.forecast_daily_frame = ForecastDailyFrame(self)
        self.forecast_daily_frame.pack()

    def init_api_key(self):
        # reads openweathermap api key
        # from a file named api_key.txt in the same directory where the main script of the app is run from
        # it must be a plain text file, only containing the api key
        # TODO: just realized that I should not be openning a file from tkinter's main thread, will fix it "soon"

        # if the file is not found then the user is prompted to enter an api key
        # TODO: save the user entered api key to api_key.txt after a successful paste
        # TODO: probably add test to determine if it's a "correct" api key

        try:
            with open("api_key.txt") as keyfile:
                api_key = keyfile.read().rstrip("\n")    # striping it in case there's an empty line at the end of the file
        except:
            self.status_label.configure(text = "error openning api_key.txt")    # asking the user to enter the key in the next line
            api_key = askstring(title = "api_key.txt not found", prompt = "Please enter api key: ", parent = self)
            if api_key is None or api_key == "":
                # if api_key.txt not found and user enters no key:
                self.input.get_btn.configure(state=tk.DISABLED)
                self.status_label.configure(text = "No API key provided")
            else:
                # if the user enters the key:
                self.status_label.configure(text = "")
        return api_key

    def load_history(self):
        history = []
        try:
            with open("history.txt") as hist:
                for line in hist.readlines():
                    history.append(line.rstrip("\n"))
            return history
        except:
            print("history.txt not found")
            return ["London"]

    def save_history(self):
        try:
            with open("history.txt", "w") as hist:
                hist.write("\n".join(self.history))
        except:
            print("failed to save history.txt")

    def on_close_button_pressed(self):
        self.save_history()
        self.destroy()


class InputFrame(ttk.Frame):
    def __init__(self, parent, history):
        super().__init__(parent)
        self.history = history

        self.input_combobox = ttk.Combobox(self, values=self.history)
        self.input_combobox.current(0)
        self.input_combobox.grid(row=0,column=1)
        self.input_combobox.bind('<Return>', lambda x: parent.threadworker.submit(btn_pressed, parent, self.input_combobox.get()))

        self.get_btn = ttk.Button(self, text="Submit", command=lambda: parent.threadworker.submit(btn_pressed, parent, self.input_combobox.get()))
        self.get_btn.grid(row=0,column=2)


class CurrentWeatherFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        #self['bg'] = '#CCCCCC'    # to have a bit of contrast with the openweathermap icons

        self.city_lab = tk.Label(self)
        self.city_lab.grid(row=0, column=0, sticky='W')

        self.temp_lab = tk.Label(self)
        self.temp_lab.grid(row=1,column=0, sticky='W')

        self.feels_lab = tk.Label(self)
        self.feels_lab.grid(row=2, column=0, sticky='W')

        self.humid_lab = tk.Label(self)
        self.humid_lab.grid(row=3, column=0, sticky='W')

        self.icon_code = None

        self.icon_label = tk.Label(self)
        self.icon_label.grid(row=0, column=1, rowspan=3)

        self.desc_lab = tk.Label(self)
        self.desc_lab.grid(row=2,column=1, rowspan=2)

        self.wind_speed_lab = tk.Label(self)
        self.wind_speed_lab.grid(row=0, column=2, sticky='E')

        self.clouds_lab = tk.Label(self)
        self.clouds_lab.grid(row=1, column=2, sticky='E')

        self.sunrise_lab = tk.Label(self)
        self.sunrise_lab.grid(row=2, column=2, sticky='E')

        self.sunset_lab = tk.Label(self)
        self.sunset_lab.grid(row=3, column=2, sticky='E')

        # change background color of all child widgets
        #for widget in self.children.values():
            #widget['bg'] = "#CCCCCC"


class ForecastDailyFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        #self['bg'] = '#CCCCCC'

        self.forecast_day_list = list()

        for i in range(7):
            self.forecast_day_list.append(ForecastDayFrame(self))
            self.forecast_day_list[i].grid(row=0, column=i)


class ForecastDayFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.day_label = tk.Label(self, text = "")
        self.day_label.grid(row=0, column=0)

        self.icon_code = None

        self.icon_label = tk.Label(self)
        self.icon_label.grid(row=1, column=0)

        self.weather_desc_label = tk.Label(self)
        self.weather_desc_label.grid(row=2, column=0)

        self.temp_max_label = tk.Label(self)
        self.temp_max_label.grid(row=3, column=0)

        self.temp_min_label = tk.Label(self)
        self.temp_min_label.grid(row=4, column=0)

    def change_bg(self):
        self['bg'] = '#CCCCCC'
        for widget in self.children.values():
            widget['bg'] = "#CCCCCC"
