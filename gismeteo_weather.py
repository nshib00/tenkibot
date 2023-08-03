from requests_html import HTMLSession, Element
from dataclasses import dataclass
import logging
import time

logger = logging.getLogger('gismeteo_weather')
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


@dataclass
class Weather:
    city: str|None = None
    data: str|None = None
    time: str|None = None
    temperature_now: str|None = None
    temperature_feeled: str|None = None
    wind: str|None = None
    humidity: str|None = None
    pressure: str|None = None
    gm_activity: str|None = None
    water_temperature: str|None = None

weather = Weather()


def get_weather_data(city: str) -> None:
    session = HTMLSession()
    response = session.get('https://www.gismeteo.ru/')
    weather.data = response.html.find('div.current-weather', first=True)
    if weather.data:
        logger.info('Данные о погоде получены успешно.')
    else:
        logger.warning('Данные о погоде не найдены.')


def get_wind_data(wind_weather_item) -> str:
    wind_m_s = wind_weather_item.find('span.unit.unit_wind_m_s', first=True).text.replace('\xa0', ' ')
    wind_direction = wind_m_s.split(',')[-1].strip()
    wind_m_s = wind_m_s.replace(wind_direction, '').replace(', ', '')
    wind_km_h = wind_weather_item.find('span.unit.unit_wind_km_h', 
                                       first=True).text.replace('\xa0', ' ').replace(wind_direction, '').replace(', ', '')
    return f'{wind_m_s} ({wind_km_h}), {wind_direction}'


def parse_weather_data() -> None:
    weather_items = weather.data.find('div.item-value')
    weather.city = weather.data.find('a.city-link.link', first=True).text
    weather.time = weather.data.find('div.current-time', first=True).text
    weather.temperature_now = weather.data.find('span.unit.unit_temperature_c', first=True).text
    weather.temperature_feeled = weather_items[0].find('span.unit.unit_temperature_c', first=True).text
    weather.wind = get_wind_data(wind_weather_item=weather_items[1])
    weather.pressure = weather_items[2].find('span.unit.unit_pressure_mm_hg_atm', first=True).text.replace('\xa0', ' ')
    weather.humidity = weather_items[3].text.replace('\xa0', ' ')
    weather.gm_activity = weather_items[4].text.replace('\xa0', ' ')
    weather.water_temperature = weather_items[5].find('span.unit.unit_temperature_c', first=True).text

    logger.info('Информация о погоде успешно извлечена из полученной HTML-страницы.')


def get_weather(city: str) -> dict[str]:
    get_weather_data(city)
    parse_weather_data()
    
    weather_data_dict = {}
    weather_attrs = []
    for attr in dir(weather):
        if not attr.startswith('__') and not attr.endswith('__'):
            weather_attrs.append(attr)

    # Изменение порядка, в котором будут отображаться данные о погоде. 
    # Температура фактическая (weather_attrs[1]) и по ощущению (weather_attrs[2]) поставлены выше по списку для удобства.
    weather_attrs[1], weather_attrs[6] = weather_attrs[6], weather_attrs[1]
    weather_attrs[5], weather_attrs[2] = weather_attrs[2], weather_attrs[5]
    
    for attr in weather_attrs:
        if attr != 'data':
            weather_data_dict[attr] = getattr(weather, attr)
    return weather_data_dict

def main():
    get_weather()


if __name__ == '__main__':
    try:
        start = time.perf_counter()
        main()
        end = time.perf_counter()
        logger.info(f'Парсинг выполнен за {round(end - start, ndigits=2)} с.')
    except Exception as exc:
        logger.error(f'Возникла ошибка. {exc.__class__.__name__}: {exc}.')
