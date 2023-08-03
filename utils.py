def get_city_emoji() -> str:
    from datetime import datetime
    now = datetime.now()
    if 4 <= now.hour <= 11:
        return '🌇'
    elif 18 <= now.hour <= 22:
        return '🌆'
    else:
        return '🏙'


owm_keys_translation = {
    'place': '📍Место',
    'temp': 'Температура',
    'temp_feels_like': 'Ощущается как',
    'wind_speed': 'Скорость ветра',
    'wind_direction': 'Направление ветра',
    'clouds': 'Облачность',
    'pressure': 'Давление воздуха',
    'humidity': 'Влажность воздуха',
    'sunrise': 'Время рассвета',
    'sunset': 'Время заката',
    'daylight_hours': 'Световой день',
}

gismeteo_keys_translation = {
    'city': f'{get_city_emoji()} Город',
    'time': 'Время',
    'humidity': 'Влажность воздуха',
    'pressure': 'Давление воздуха',
    'temperature_now': 'Температура',
    'temperature_feeled': 'Ощущается как',
    'water_temperature': 'Температура воды',
    'wind': 'Ветер',
    'gm_activity': 'Геомагнитная активность',
}
    

def get_weather_emoji(weather_status: str) -> str:
    weather_emojis = {
        'Thunderstorm': '\U0001F329',
        'Drizzle': '\U0001F327',
        'Rain': '\U0001F327',
        'Snow': '\U0001F328',
        'Clear': '\U00002600',
        'Clouds': '\U00002601',
        'Mist': '\U0001F32B',
    }
    if weather_status not in weather_emojis.keys():
        return ''
    return weather_emojis[weather_status]


def make_owm_weather_data_string(weather_data: dict) -> str:
    weather_data_str = ''
    for key, value in weather_data.items():
        if key != 'weather_status':
            if key == 'weather_description':
                emoji = get_weather_emoji(weather_status=weather_data['weather_status'])
                if emoji:
                    weather_data_str += f'{emoji} {value.capitalize()}\n'
                else:
                    weather_data_str += value.capitalize() + '\n'
            elif key == 'place':
                weather_data_str += f'<b>{owm_keys_translation[key]}:</b> {value}\n\n'
            else:
                weather_data_str += f'<b>{owm_keys_translation[key]}:</b> {value}\n'
    return weather_data_str


def make_gismeteo_weather_data_string(weather_data: dict) -> str:
    weather_data_str = ''
    for key, value in weather_data.items():
        weather_data_str += f'<b>{gismeteo_keys_translation[key]}:</b> {value}\n'
    return weather_data_str
