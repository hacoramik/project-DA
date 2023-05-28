import requests
import json
import sqlite3
import schedule
import time
import pandas as pd
import tensorflow as tf
import numpy as np

# Установка соединения с базой данных
conn = sqlite3.connect('example.db')

# Создание объекта курсора
c = conn.cursor()
# test
# Создание таблицы
c.execute('''CREATE TABLE IF NOT EXISTS weather (city TEXT,
            year INTEGER,
            time TEXT,
            temperature FLOAT,
            temperature_min FLOAT,
            temperature_max FLOAT,
            humidity FLOAT,
            pressure FLOAT,
            wind_speed FLOAT,
            wind_direction FLOAT,
            description TEXT)''')

# Чтение Excel файла
city_frame = pd.read_excel("cities.xlsx")

# Получение списка городов из столбца в DataFrame
cities = city_frame["City"].tolist()

# Мой api ключ и адрес обращения
api = "9e36367c58e9665759a2a78b30140f09"
url = 'http://api.openweathermap.org/data/2.5/weather'


def update_weather_data():
    # Инициализация переменной-счетчика
    if not hasattr(update_weather_data, "index"):
        update_weather_data.index = 0

    # Получение следующего города согласно индексу
    city = cities[update_weather_data.index]

    params = {'APPID': api, 'q': city, 'units': 'metric', 'lang': 'ru'}
    result = requests.get(url, params=params)

    if result.status_code == 200:
        data = result.json()
        if "main" in data and "weather" in data and "wind" in data:
            temperature = data["main"]["temp"]
            temperature_min = data["main"]["temp_min"]
            temperature_max = data["main"]["temp_max"]
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            wind_speed = data["wind"]["speed"]
            wind_direction = data["wind"]["deg"]
            description = data["weather"][0]["description"]
            year = time.localtime().tm_year
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            conn.execute("""
                        INSERT INTO weather VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                city, year, time_str, temperature, temperature_min, temperature_max, humidity, pressure, wind_speed,
                wind_direction, description))
            conn.commit()
            print("Weather data updated successfully for ", city)
            print(data)
        else:
            print("Error: invalid response from server")

    else:
        print("Error: failed to fetch weather data for ", city)

    # Увеличение индекса на 1
    update_weather_data.index = (update_weather_data.index + 1) % len(cities)


# Функция для создания excel файла с данными погоды
def create_excel_file():
    # Запрос данных из таблицы weather
    df = pd.read_sql_query("SELECT * from weather", conn)
    # Создание excel файла
    writer = pd.ExcelWriter('weather_data.xlsx')
    # Запись данных в excel файл
    df.to_excel(writer, index=False)
    writer._save()
    print("Excel file created successfully")


# Создание заданий для выполнения каждую минуту
schedule.every(5).seconds.do(update_weather_data)
schedule.every(5).seconds.do(create_excel_file)

# Бесконечный цикл для выполнения заданий
while True:
    schedule.run_pending()
    time.sleep(1)

# Закрытие соединения с базой данных
conn.close()
