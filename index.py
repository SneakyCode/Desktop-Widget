import sys
import requests
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

CITY_NAME = "Warsaw"

def get_weather_data(city_name):
    geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}"
    geo_response = requests.get(geocoding_url)
    if geo_response.status_code == 200:
        geo_data = geo_response.json()
        if "results" in geo_data:
            location = geo_data["results"][0]
            latitude = location["latitude"]
            longitude = location["longitude"]
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&temperature_unit=celsius"
            weather_response = requests.get(weather_url)
            if weather_response.status_code == 200:
                weather_data = weather_response.json()["current_weather"]
                return {
                    "temperature": weather_data["temperature"],
                    "wind_speed": weather_data["windspeed"],
                    "weather_code": weather_data["weathercode"],
                }
    return None

def get_weather_icon(weather_code):
    icon_map = {
        0: "https://openweathermap.org/img/wn/01d@2x.png",  # Sunny
        1: "https://openweathermap.org/img/wn/02d@2x.png",  # A bit cloudy
        2: "https://openweathermap.org/img/wn/03d@2x.png",  # Cloudy
        3: "https://openweathermap.org/img/wn/09d@2x.png",  # Raining
    }
    icon_url = icon_map.get(weather_code, icon_map[2])
    response = requests.get(icon_url, stream=True)
    if response.status_code == 200:
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
        return pixmap
    return None

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Weather App")
        self.setGeometry(100, 100, 400, 340)
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.weather_label = QLabel("Loading data...", self)
        self.weather_label.setGeometry(30, 130, 300, 100)
        self.weather_label.setStyleSheet("color: white; font-size: 18px;")
        self.weather_label.setAlignment(Qt.AlignCenter)

        self.icon_label = QLabel(self)
        self.icon_label.setGeometry(130, 30, 130, 130)

        self.city_label = QLabel(f"{CITY_NAME}", self)
        self.city_label.setGeometry(30, 10, 300, 50)
        self.city_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        self.city_label.setAlignment(Qt.AlignCenter)

        self.offset = QPoint()

        QTimer.singleShot(1000, self.refresh_weather)

    def refresh_weather(self):
        weather_data = get_weather_data(CITY_NAME)
        if weather_data:
            temperature = weather_data["temperature"]
            wind_speed = weather_data["wind_speed"]
            weather_code = weather_data["weather_code"]
            self.weather_label.setText(f"Temperature: {temperature}°C\nWind speed: {wind_speed} km/h")
            
            icon = get_weather_icon(weather_code)
            if icon and isinstance(icon, QPixmap):
                self.icon_label.setPixmap(icon)

        QTimer.singleShot(600000, self.refresh_weather)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = event.pos() - self.offset
            self.move(self.pos() + delta)

app = QApplication(sys.argv)
window = WeatherApp()
window.show()
sys.exit(app.exec_())
