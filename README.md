# 🌤 WeatherNow — Python Weather App

A modern, feature-rich weather app built with **Python + Tkinter + OpenWeatherMap API**.
Designed as a first-year student micro-project.

---

## ✨ Features
- 🔍 Search any city worldwide
- 🌡 Current temperature + "feels like"
- 💧 Humidity, 💨 Wind speed, 👁 Visibility, 🌡 Pressure
- 📅 5-Day forecast with daily high/low
- ⏰ Live clock in the header
- 🎨 Modern dark-themed UI
- 🔄 Background threading (UI never freezes)
- ❌ Friendly error messages for bad city / API key

---

## 🚀 How to Run

### Step 1 — Get a Free API Key
1. Go to [https://openweathermap.org/api](https://openweathermap.org/api)
2. Click **Sign Up** → verify email
3. Go to **API keys** tab → copy your key
4. It activates within ~10 minutes

### Step 2 — Install Python
Download from [https://python.org](https://python.org) (Python 3.8+).
Tkinter and urllib come built-in — **no extra installs needed!**

### Step 3 — Add Your API Key
Open `weather_app.py` and replace line 18:
```python
API_KEY = "YOUR_API_KEY_HERE"   # ← paste your key here
```

### Step 4 — Run It!
```bash
python weather_app.py
```

---

## 📁 Project Structure
```
weather_app/
├── weather_app.py   # Main application (all-in-one)
└── README.md        # This file
```

---

## 🧠 Concepts Covered (as per project brief)
| Concept | Where Used |
|---------|-----------|
| APIs | `get_current_weather()`, `get_forecast()` |
| JSON parsing | `parse_forecast()` |
| Tkinter widgets | Labels, Entry, Button, Frame |
| Threading | Background API calls |
| OOP | `WeatherApp(tk.Tk)` class |
| Error handling | `try/except` blocks |

---

## 📸 Preview
Dark UI with city name, large temperature, weather icon, detail cards (humidity/wind/visibility/pressure), and a 5-day forecast strip.

---

## 🙏 Credits
Weather data from [OpenWeatherMap](https://openweathermap.org) (free tier).
