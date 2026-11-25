import flet as ft
import requests
from datetime import datetime

# --- CONFIGURATION ---
API_KEY = "curl "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m""  
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def main(page: ft.Page):
    page.title = "Weather App (Flet)"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # --- UI COMPONENTS ---
    city_input = ft.TextField(
        hint_text="Enter city name...",
        width=300,
        on_submit=lambda _: fetch_weather(None),
        border_radius=20,
        filled=True,
    )
    
    search_btn = ft.IconButton(
        icon=ft.Icons.SEARCH,
        icon_size=30,
        on_click=fetch_weather,
        tooltip="Search",
    )

    # Weather Display Area
    location_text = ft.Text("", size=28, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    date_text = ft.Text("", size=14, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER)
    weather_icon = ft.Image(src="", width=120, height=120, visible=False)
    temp_text = ft.Text("", size=60, weight=ft.FontWeight.W_200)
    desc_text = ft.Text("", size=18, italic=True, text_align=ft.TextAlign.CENTER)
    
    details_row = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        spacing=20,
    )

    loading = ft.ProgressRing(visible=False)
    error_msg = ft.Text("", color=ft.Colors.RED_400, size=14, text_align=ft.TextAlign.CENTER)

    # --- LOGIC ---
    def fetch_weather(e):
        city = city_input.value.strip()
        if not city:
            error_msg.value = "Please enter a city name."
            page.update()
            return

        if API_KEY == "YOUR_API_KEY_HERE":
            error_msg.value = "Please set your API Key in the code."
            page.update()
            return

        # Reset UI
        error_msg.value = ""
        loading.visible = True
        weather_icon.visible = False
        details_row.controls.clear()
        page.update()

        try:
            # REST API Call using requests
            params = {
                "q": city,
                "appid": API_KEY,
                "units": "metric"  # For Celsius
            }
            response = requests.get(BASE_URL, params=params, timeout=10)
            
            if response.status_code == 404:
                raise Exception("City not found. Please check spelling.")
            elif response.status_code == 401:
                raise Exception("Invalid API Key. Check your configuration.")
            elif response.status_code != 200:
                raise Exception(f"API Error: {response.status_code}")
            
            data = response.json()
            
            # Parse Data
            name = data["name"]
            country = data["sys"]["country"]
            temp = round(data["main"]["temp"])
            feels_like = round(data["main"]["feels_like"])
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            description = data["weather"][0]["description"].capitalize()
            icon_code = data["weather"][0]["icon"]

            # Update UI
            location_text.value = f"{name}, {country}"
            date_text.value = datetime.now().strftime("%A, %d %B %Y")
            temp_text.value = f"{temp}°C"
            desc_text.value = description
            
            # Load Icon from OpenWeatherMap CDN
            weather_icon.src = f"https://openweathermap.org/img/wn/{icon_code}@4x.png"
            weather_icon.visible = True

            # Update Details
            details_row.controls = [
                create_detail("💧", "Humidity", f"{humidity}%"),
                create_detail("💨", "Wind", f"{wind_speed} m/s"),
                create_detail("🌡️", "Feels Like", f"{feels_like}°C"),
            ]

        except Exception as ex:
            error_msg.value = str(ex)
            location_text.value = ""
            temp_text.value = ""
            desc_text.value = ""
        finally:
            loading.visible = False
            page.update()

    def create_detail(icon, label, value):
        return ft.Column(
            [
                ft.Text(icon, size=20),
                ft.Text(label, size=12, color=ft.Colors.GREY_500),
                ft.Text(value, size=16, weight=ft.FontWeight.BOLD),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        )

    # --- PAGE LAYOUT ---
    page.add(
        ft.Column(
            [
                # Search Bar
                ft.Row(
                    [city_input, search_btn],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                error_msg,
                loading,
                # Weather Card
                ft.Container(
                    content=ft.Column(
                        [
                            location_text,
                            date_text,
                            weather_icon,
                            temp_text,
                            desc_text,
                            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                            details_row,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                    ),
                    padding=30,
                    border_radius=30,
                    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                    width=400,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )
    )

    # Load default city on startup
    city_input.value = "London"
    fetch_weather(None)

ft.app(target=main)
