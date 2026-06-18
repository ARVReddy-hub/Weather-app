"""
WeatherNow - A Modern Weather App
Built with Python + Tkinter + OpenWeatherMap API
Perfect for First-Year Students
"""

import tkinter as tk
from tkinter import font as tkfont
import urllib.request
import urllib.parse
import json
import datetime
import threading

# ─────────────────────────────────────────────
#  CONFIG  –  Replace with your free API key from
#  https://openweathermap.org/api  (takes ~10 min)
# ─────────────────────────────────────────────
API_KEY = "YOUR_API_KEY_HERE"   # ← paste your key here
BASE_URL = "https://api.openweathermap.org/data/2.5/"

# ─── Colour palette ───────────────────────────
BG_DARK   = "#0f1923"
BG_CARD   = "#1a2634"
BG_ACCENT = "#1e3a5f"
BLUE_LT   = "#4da6ff"
BLUE_MD   = "#2979ff"
WHITE     = "#f0f4ff"
GREY_LT   = "#8899aa"
GREY_DK   = "#445566"
WARN_RED  = "#ff5c5c"
SUCCESS   = "#43d9ad"

# ─── Weather icon map (Unicode emoji fallbacks) ─
WEATHER_ICONS = {
    "Clear":        "☀️",
    "Clouds":       "☁️",
    "Rain":         "🌧️",
    "Drizzle":      "🌦️",
    "Thunderstorm": "⛈️",
    "Snow":         "❄️",
    "Mist":         "🌫️",
    "Fog":          "🌫️",
    "Haze":         "🌫️",
    "Dust":         "💨",
    "Sand":         "💨",
    "Smoke":        "💨",
    "Tornado":      "🌪️",
}

DAY_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


# ─────────────────────────────────────────────
#  API HELPERS
# ─────────────────────────────────────────────

def fetch_json(url: str):
    """Download JSON from url and return parsed dict (or raises exception)."""
    with urllib.request.urlopen(url, timeout=8) as resp:
        return json.loads(resp.read().decode())


def get_current_weather(city: str):
    city_enc = urllib.parse.quote(city)
    url = f"{BASE_URL}weather?q={city_enc}&appid={API_KEY}&units=metric"
    return fetch_json(url)


def get_forecast(city: str):
    city_enc = urllib.parse.quote(city)
    url = f"{BASE_URL}forecast?q={city_enc}&appid={API_KEY}&units=metric"
    return fetch_json(url)


def parse_forecast(data: dict):
    """Collapse 3-hourly forecast into one entry per day (max / min)."""
    days = {}
    for entry in data["list"]:
        date = entry["dt_txt"].split(" ")[0]
        temp = entry["main"]["temp"]
        icon = entry["weather"][0]["main"]
        if date not in days:
            days[date] = {"max": temp, "min": temp, "icon": icon}
        else:
            days[date]["max"] = max(days[date]["max"], temp)
            days[date]["min"] = min(days[date]["min"], temp)
    # Return only the next 5 days (skip today if already have it)
    result = []
    for date_str, vals in list(days.items())[:6]:
        dt = datetime.date.fromisoformat(date_str)
        result.append({
            "day": DAY_ABBR[dt.weekday()],
            "icon": vals["icon"],
            "max": round(vals["max"]),
            "min": round(vals["min"]),
        })
    return result[1:6]   # skip today → 5 future days


# ─────────────────────────────────────────────
#  REUSABLE WIDGETS
# ─────────────────────────────────────────────

def label(parent, text="", size=12, bold=False, color=WHITE, **kwargs):
    weight = "bold" if bold else "normal"
    f = ("Segoe UI", size, weight)
    return tk.Label(parent, text=text, font=f, fg=color,
                    bg=kwargs.pop("bg", parent["bg"]), **kwargs)


def card_frame(parent, **kwargs):
    return tk.Frame(parent, bg=BG_CARD,
                    highlightbackground=GREY_DK, highlightthickness=1,
                    **kwargs)


# ─────────────────────────────────────────────
#  MAIN APPLICATION CLASS
# ─────────────────────────────────────────────

class WeatherApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("WeatherNow")
        self.geometry("520x760")
        self.resizable(False, False)
        self.configure(bg=BG_DARK)

        self._build_header()
        self._build_search()
        self._build_main_card()
        self._build_details_row()
        self._build_forecast_section()
        self._build_footer()

        # Load default city on start
        self.after(300, lambda: self._search("Hyderabad"))

    # ── UI CONSTRUCTION ──────────────────────

    def _build_header(self):
        hdr = tk.Frame(self, bg=BG_DARK)
        hdr.pack(fill="x", padx=20, pady=(18, 4))
        label(hdr, "🌤 WeatherNow", size=16, bold=True, color=BLUE_LT).pack(side="left")
        self.time_lbl = label(hdr, color=GREY_LT, size=10)
        self.time_lbl.pack(side="right")
        self._tick_clock()

    def _build_search(self):
        row = tk.Frame(self, bg=BG_DARK)
        row.pack(fill="x", padx=20, pady=8)

        self.entry = tk.Entry(row, font=("Segoe UI", 12),
                              bg=BG_CARD, fg=WHITE, insertbackground=WHITE,
                              relief="flat", bd=0)
        self.entry.pack(side="left", fill="x", expand=True,
                        ipady=10, ipadx=12)
        self.entry.insert(0, "Search city…")
        self.entry.bind("<FocusIn>",  self._clear_placeholder)
        self.entry.bind("<FocusOut>", self._restore_placeholder)
        self.entry.bind("<Return>",   lambda e: self._on_search())

        btn = tk.Button(row, text="Search", font=("Segoe UI", 11, "bold"),
                        bg=BLUE_MD, fg=WHITE, relief="flat", bd=0,
                        activebackground=BLUE_LT, activeforeground=WHITE,
                        cursor="hand2", command=self._on_search)
        btn.pack(side="right", ipady=10, ipadx=16)

    def _build_main_card(self):
        self.main_card = card_frame(self)
        self.main_card.pack(fill="x", padx=20, pady=(4, 6))

        # City + country
        top = tk.Frame(self.main_card, bg=BG_CARD)
        top.pack(fill="x", padx=20, pady=(16, 0))
        self.city_lbl    = label(top, "—", size=22, bold=True, bg=BG_CARD)
        self.city_lbl.pack(side="left")
        self.country_lbl = label(top, color=GREY_LT, size=11, bg=BG_CARD)
        self.country_lbl.pack(side="left", padx=(6, 0), pady=(6, 0))

        # Icon + temp
        mid = tk.Frame(self.main_card, bg=BG_CARD)
        mid.pack(fill="x", padx=20, pady=4)
        self.icon_lbl  = label(mid, "—", size=52, bg=BG_CARD)
        self.icon_lbl.pack(side="left")
        right_col = tk.Frame(mid, bg=BG_CARD)
        right_col.pack(side="left", padx=16)
        self.temp_lbl  = label(right_col, "—", size=44, bold=True, bg=BG_CARD)
        self.temp_lbl.pack(anchor="w")
        self.feel_lbl  = label(right_col, color=GREY_LT, size=11, bg=BG_CARD)
        self.feel_lbl.pack(anchor="w")

        # Description + date
        bot = tk.Frame(self.main_card, bg=BG_CARD)
        bot.pack(fill="x", padx=20, pady=(0, 16))
        self.desc_lbl = label(bot, color=BLUE_LT, size=13, bold=True, bg=BG_CARD)
        self.desc_lbl.pack(side="left")
        self.date_lbl = label(bot, color=GREY_LT, size=10, bg=BG_CARD)
        self.date_lbl.pack(side="right")

    def _build_details_row(self):
        row = tk.Frame(self, bg=BG_DARK)
        row.pack(fill="x", padx=20, pady=(0, 6))
        row.columnconfigure((0, 1, 2, 3), weight=1, uniform="col")

        self.detail_labels = {}
        specs = [
            ("💧", "Humidity",  "humidity"),
            ("💨", "Wind",      "wind"),
            ("👁", "Visibility","visibility"),
            ("🌡", "Pressure",  "pressure"),
        ]
        for col, (ico, title, key) in enumerate(specs):
            c = card_frame(row)
            c.grid(row=0, column=col, padx=3, pady=0, sticky="nsew")
            label(c, ico, size=16, bg=BG_CARD).pack(pady=(10, 0))
            v = label(c, "—", size=11, bold=True, bg=BG_CARD)
            v.pack()
            label(c, title, size=9, color=GREY_LT, bg=BG_CARD).pack(pady=(0, 10))
            self.detail_labels[key] = v

    def _build_forecast_section(self):
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill="x", padx=20, pady=(6, 4))
        label(header, "5-Day Forecast", size=12, bold=True, color=GREY_LT).pack(side="left")

        self.forecast_frame = tk.Frame(self, bg=BG_DARK)
        self.forecast_frame.pack(fill="x", padx=20)
        for i in range(5):
            self.forecast_frame.columnconfigure(i, weight=1, uniform="fc")
        self.forecast_cards = []
        for i in range(5):
            c = card_frame(self.forecast_frame)
            c.grid(row=0, column=i, padx=3, sticky="nsew")
            day_l  = label(c, "—", size=10, bold=True, color=GREY_LT, bg=BG_CARD)
            ico_l  = label(c, "—", size=20, bg=BG_CARD)
            max_l  = label(c, "—", size=11, bold=True, bg=BG_CARD)
            min_l  = label(c, "—", size=10, color=GREY_LT, bg=BG_CARD)
            day_l.pack(pady=(10, 0))
            ico_l.pack()
            max_l.pack()
            min_l.pack(pady=(0, 10))
            self.forecast_cards.append((day_l, ico_l, max_l, min_l))

    def _build_footer(self):
        self.status_lbl = label(self, "Ready. Search a city to begin.", 
                                size=9, color=GREY_LT)
        self.status_lbl.pack(pady=(10, 6))
        label(self, "Data: OpenWeatherMap • Made with ❤️ in Python",
              size=8, color=GREY_DK).pack(pady=(0, 8))

    # ── CLOCK ────────────────────────────────

    def _tick_clock(self):
        now = datetime.datetime.now().strftime("%a, %d %b  %H:%M")
        self.time_lbl.config(text=now)
        self.after(30_000, self._tick_clock)

    # ── SEARCH ───────────────────────────────

    def _clear_placeholder(self, e):
        if self.entry.get() == "Search city…":
            self.entry.delete(0, tk.END)
            self.entry.config(fg=WHITE)

    def _restore_placeholder(self, e):
        if not self.entry.get():
            self.entry.insert(0, "Search city…")
            self.entry.config(fg=GREY_LT)

    def _on_search(self):
        city = self.entry.get().strip()
        if city and city != "Search city…":
            self._search(city)

    def _search(self, city: str):
        self._set_status("⏳  Fetching weather…", BLUE_LT)
        # Run network call in background thread so UI stays responsive
        t = threading.Thread(target=self._fetch_and_update, args=(city,), daemon=True)
        t.start()

    def _fetch_and_update(self, city: str):
        try:
            current  = get_current_weather(city)
            forecast = get_forecast(city)
            # Schedule UI update back on main thread
            self.after(0, lambda: self._update_ui(current, forecast))
        except urllib.error.HTTPError as e:
            if e.code == 401:
                msg = "❌  Invalid API key. Get a free key at openweathermap.org"
            elif e.code == 404:
                msg = f"❌  City '{city}' not found. Try another name."
            else:
                msg = f"❌  HTTP error {e.code}."
            self.after(0, lambda: self._set_status(msg, WARN_RED))
        except Exception as e:
            self.after(0, lambda: self._set_status(f"❌  {e}", WARN_RED))

    # ── UI UPDATE ────────────────────────────

    def _update_ui(self, current: dict, forecast_raw: dict):
        # ── Current weather ──
        name    = current["name"]
        country = current["sys"]["country"]
        temp    = round(current["main"]["temp"])
        feels   = round(current["main"]["feels_like"])
        desc    = current["weather"][0]["description"].title()
        main    = current["weather"][0]["main"]
        icon    = WEATHER_ICONS.get(main, "🌡")
        humidity   = current["main"]["humidity"]
        wind_spd   = current["wind"]["speed"]
        visibility = current.get("visibility", 0) // 1000   # m → km
        pressure   = current["main"]["pressure"]
        dt = datetime.datetime.fromtimestamp(current["dt"])

        self.city_lbl.config(text=name)
        self.country_lbl.config(text=f"({country})")
        self.temp_lbl.config(text=f"{temp}°C")
        self.feel_lbl.config(text=f"Feels like {feels}°C")
        self.icon_lbl.config(text=icon)
        self.desc_lbl.config(text=desc)
        self.date_lbl.config(text=dt.strftime("%A, %d %b %Y  %H:%M"))

        self.detail_labels["humidity"].config(text=f"{humidity}%")
        self.detail_labels["wind"].config(text=f"{wind_spd} m/s")
        self.detail_labels["visibility"].config(text=f"{visibility} km")
        self.detail_labels["pressure"].config(text=f"{pressure} hPa")

        # ── 5-day forecast ──
        days = parse_forecast(forecast_raw)
        for i, day in enumerate(days):
            d, ico, mx, mn = self.forecast_cards[i]
            d.config(text=day["day"])
            ico.config(text=WEATHER_ICONS.get(day["icon"], "🌡"))
            mx.config(text=f"{day['max']}°")
            mn.config(text=f"{day['min']}°")

        self._set_status(f"✅  Updated for {name}, {country}", SUCCESS)

    def _set_status(self, msg: str, color=GREY_LT):
        self.status_lbl.config(text=msg, fg=color)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
