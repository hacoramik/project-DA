#Прогноз погоды

#Графическое оформление
import tkinter as tk
import matplotlib.pyplot as plt

import io
import plotly.express as px
import plotly.graph_objects as go

#Библиотеки для сбора данных
import pandas as pd
from datetime import datetime, timedelta
import time
from meteostat import Point, Daily
from openpyxl.workbook import Workbook
import os

#Библиотеки для нейросети
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')
from sklearn.metrics import mean_absolute_error

if os.path.exists('weather.xlsx'):
    os.remove('weather.xlsx')

# Обновление данных в excel
def update_weather_data():           

    # Определяем даты сбора для запроса (год, месяц, день)
    start_date = datetime(2023, 1, 1)
    end_date = datetime.now() - timedelta(days=1)

    # Читаем файл с координатами
    coordinates = pd.read_excel('coordinates.xlsx')

    # Создаем список городов для выпадающего списка
    cities = list(coordinates['city'])

    # Определяем функцию для обработки выбора города
    def select_city():
        # Получаем выбранный город из выпадающего списка
        city = city_var.get()

        # Получаем координаты для выбранного города из файла
        row = coordinates.loc[coordinates['city'] == city].iloc[0]
        location = Point(row['latitude'], row['longitude'])

        # Запрашиваем данные о погоде
        data = Daily(location, start_date, end_date).fetch()
        print(data.columns)
        # Формируем столбцы: град Ц, град Ц, град Ц, мм, мм, о, км\ч, км\ч, гПа, м
        data = data[['tavg', 'tmin', 'tmax', 'prcp', 'snow', 'wdir', 'wspd', 'wpgt', 'pres', 'tsun']]

        # Добавляем столбец с датой
        data['date'] = data.index.strftime('%Y.%m.%d')
        print(data)

        # Сохраняем данные в таблицу
        data.to_excel(r'D:\Рабочий стол\weather.xlsx', index=False)

        # Построение ср., мин. и макс. температуры за весь период
        data.plot(y=['tavg', 'tmin', 'tmax'])
        plt.show()

        """# Нейросеть (прогнозирование временных рядов)
        train = data.loc[:'2023-06-13']
        test = data.loc['2023-06-14':]

        train = data[['tavg']]
        train = train.reset_index()
        train.columns = ['ds', 'y']

        model = Prophet()
        model.fit(train)
        future = pd.DataFrame(test.index.values)
        future.columns = ['ds']
        forecast = model.predict(future)

        # calculate MAE between expected and predicted values
        y_true = test['tavg'].values
        y_pred = forecast['yhat'].values
        rmse = math.sqrt(mean_squared_error(y_true, y_pred))
        print('RMSE:', rmse)

        # plot expected vs actual
        plt.plot(y_true, label='Actual')
        plt.plot(y_pred, label='Predicted')
        plt.ylim(ymax=30, ymin=15)
        plt.legend()
        plt.show()"""

    # Создаем графическое окно
    root = tk.Tk()
    root.geometry('300x250')

    # Создаем выпадающий список с городами
    city_var = tk.StringVar()
    city_var.set(cities[0])
    city_dropdown = tk.OptionMenu(root, city_var, *cities)
    city_dropdown.pack()

    # Создаем кнопку для выбора города
    select_button = tk.Button(root, text='Выбрать', command=select_city)
    select_button.pack()

    # Запускаем главный цикл обработки событий
    root.mainloop()

update_weather_data()
