import pandas as pd
import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import load_model
import plotly.graph_objs as go

# Функция для изменения значений
def convert_to_float(x):
    try:
        return float(x)
    except ValueError:
        return 0


# Функция для обработки данных для обучения модели
def prepare_data(file_name):
    df = pd.read_excel(file_name)

    df = df.drop(columns=['Часы', 'Минуты', 'Po', 'Pa', 'U'])
    df = df.fillna(method="ffill")
    df["Дата"] = pd.to_datetime(df["Дата"], format="%d.%m.%Y")

    le = LabelEncoder()
    df["Дата"] = le.fit_transform(df["Дата"])

    df["RRR"] = df["RRR"].apply(convert_to_float)

    X = df.drop(columns=['T'])
    y = df['T']

    sc = StandardScaler()
    X = sc.fit_transform(X)

    return X, y, le, sc


# Функция для обучения модели и сохранения ее в файл
def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = Sequential()
    model.add(Dense(units=64, activation="relu", input_dim=X_train.shape[1]))
    model.add(Dense(units=1, activation="linear"))

    model.compile(optimizer="adam", loss="mean_squared_error")
    model.fit(X_train, y_train, epochs=100, batch_size=32, verbose=1)

    model.save("weather_model.h5")

    return model


# Функция для загрузки модели из файла и предсказания погоды на новых данных
def predict_weather(file_name, model_file):
    new_df = pd.read_excel(file_name)

    new_df['Дата'] = pd.to_datetime(new_df['Дата'], format='%Y-%m-%d').dt.strftime('%d.%m.%Y')
    le = LabelEncoder()
    le.fit(new_df["Дата"])
    new_df["Дата"] = le.transform(new_df["Дата"])

    sc = StandardScaler()
    X_new = new_df.drop(columns=['T'])
    X_new = sc.fit_transform(X_new)

    model = load_model(model_file)
    y_pred = model.predict(X_new)

    return y_pred


# Обработка данных для обучения модели
X, y, le, sc = prepare_data("data_many_daya.xlsx")

# Обучение модели и сохранение ее в файл
# train_model(X, y) # убрать решетку если надо обучить по-новой

# Предсказание погоды на новых данных
y_pred = predict_weather("moscow_weather.xlsx", "weather_model.h5")
print(y_pred)


def graph_plot():
    df = pd.read_excel("moscow_weather.xlsx")

    # создание графика
    fig = go.Figure()

    # добавление исходных данных на график
    fig.add_trace(go.Scatter(x=df["Дата"], y=df["T"], mode="lines", name="Исходные данные"))

    # добавление предсказанных значений на график
    fig.add_trace(go.Scatter(x=df["Дата"], y=y_pred.flatten(), mode="lines", name="Предсказанные значения"))

    # отображение графика
    fig.show()

graph_plot()
