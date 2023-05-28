import requests
import json
import sqlite3
import schedule
import time
import pandas as pd
import tensorflow as tf
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import matplotlib.pyplot as plt

# Установка соединения с базой данных
conn = sqlite3.connect('example.db')

# Создание объекта курсора
c = conn.cursor()

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

print('you are here')


def show_res():
    # загрузка данных
    data = pd.read_excel('weather_data.xlsx')

    # изменение преобразования данных
    X = data[['temperature', 'humidity', 'pressure', 'wind_speed', 'wind_direction']]
    y = data['temperature_max']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # изменение создания модели
    model = Sequential()
    model.add(Dense(64, activation='relu', input_dim=X_train.shape[1]))
    model.add(Dense(1, activation='linear'))
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])

    # предсказание значений для тестовой выборки
    predictions = model.predict(X_test)

    # создание графиков
    fig, axs = plt.subplots(2, 2)

    axs[0, 0].scatter(X_test['temperature'], y_test, label='Измеренная')
    axs[0, 0].scatter(X_test['temperature'], predictions[:, 0], label='Предсказанная')
    axs[0, 0].set_title('Максимальная температура')
    axs[0, 0].legend()

    axs[0, 1].scatter(X_test['humidity'], y_test)
    axs[0, 1].set_title('Влажность')

    axs[1, 0].scatter(X_test['pressure'], y_test)
    axs[1, 0].set_title('Давление')

    axs[1, 1].scatter(X_test['wind_speed'], y_test)
    axs[1, 1].set_title('Скорость ветра')

    plt.show()


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
            show_res()

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
schedule.every(10).seconds.do(update_weather_data)
schedule.every(10).seconds.do(create_excel_file)

# Бесконечный цикл для выполнения заданий
while True:
    schedule.run_pending()
    time.sleep(1)
