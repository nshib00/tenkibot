from requests_html import HTMLSession
import os
from dotenv import load_dotenv
from datetime import datetime
import pprint

load_dotenv()
OWM_TOKEN = os.getenv('OWM_TOKEN')


def get_weather_response(city: str) -> dict:
    session = HTMLSession()
    response = session.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_TOKEN}&lang=ru&units=metric')
    return response.json()


def count_daylight_hours(sunrise: int, sunset: int) -> str:
    sunrise_datetime = datetime.fromtimestamp(sunrise)
    sunset_datetime = datetime.fromtimestamp(sunset)
    daylight_hours = sunset_datetime - sunrise_datetime
    daylight_time = datetime.strptime(str(daylight_hours), '%H:%M:%S')
    return datetime.strftime(daylight_time, '%H:%M:%S')


def calculate_wind_direction(wind_deg: float) -> str:
    if (337.5 <= wind_deg <= 360) or (0 <= wind_deg <= 22.5):
        return 'северный'
    elif 22.5 <= wind_deg <= 67.5:
        return 'северо-восточный'
    elif 67.5 <= wind_deg <= 112.5:
        return 'восточный'
    elif 112.5 <= wind_deg <= 157.5:
        return 'юго-восточный'
    elif 157.5 <= wind_deg <= 202.5:
        return 'южный'
    elif 202.5 <= wind_deg <= 247.5:
        return 'юго-западный'
    elif 247.5 <= wind_deg <= 292.5:
        return 'западный'
    elif 292.5 <= wind_deg <= 337.5:
        return 'северо-западный'


def timestamp_to_hms(timestamp: datetime.timestamp) -> str:
    dt = datetime.fromtimestamp(timestamp)
    return datetime.strftime(dt, '%H:%M:%S')


def convert_hpa_to_mmrtst(hpa: int) -> int: # перевод гектопаскалей (1 ГПа = 100 Па) в мм рт.ст.
    pa = hpa * 100
    return int(pa / 133.3)


def get_weather_data(city: str) -> dict:
    weather_json = get_weather_response(city)
    weather_data = {
        'place': weather_json['name'] + ', ' + weather_json['sys']['country'],
        'weather_status': weather_json['weather'][0]['main'],
        'weather_description': weather_json['weather'][0]['description'],
        'temp': f"{weather_json['main']['temp']} °С",
        'temp_feels_like': f"{weather_json['main']['feels_like']} °С",
        'wind_speed': f"{weather_json['wind']['speed']} м/с",
        'wind_direction': calculate_wind_direction(wind_deg= weather_json['wind']['deg']),
        'clouds': f"{weather_json['clouds']['all']}%",
        'pressure': f"{convert_hpa_to_mmrtst(weather_json['main']['pressure'])} мм рт.ст.",
        'humidity': f"{weather_json['main']['humidity']}%",
        'sunrise': timestamp_to_hms(weather_json['sys']['sunrise']),
        'sunset': timestamp_to_hms(weather_json['sys']['sunset']),
        'daylight_hours': count_daylight_hours(
                                            sunrise=weather_json['sys']['sunrise'],
                                            sunset=weather_json['sys']['sunset'],
                                            )
    }
    return weather_data


if __name__ == '__main__':
    city = input('Введите город: ')
    pprint.pprint(get_weather_data(city))
