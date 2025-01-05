import warnings
warnings.filterwarnings('ignore')
from sklearn.linear_model import LinearRegression
import requests
import numpy as np

def main_func(data, city):
    # 1. рассчитываем скользящее среднее
    mean_rolling30 = data['temperature'].rolling(window=30).mean()
    std_rolling30 = data['temperature'].rolling(window=30).std()

    # 2. выявляем аномалии
    upper_bound = mean_rolling30 + 2 * std_rolling30
    lower_bound = mean_rolling30 - 2 * std_rolling30
    anomalies = data[(data['temperature'] > upper_bound) | 
                           (data['temperature'] < lower_bound)]
    all_anomalies = anomalies.index.tolist()

    # 3. делаем там же groupby по сезону и считаете mean и std для исходной температуры, чтобы получить профиль сезона
    season_profile = data.groupby('season')['temperature'].agg(['mean', 'std'])

    # 4. ищем тренд
    X = np.array(range(len(data))).reshape(-1, 1)
    y = data['temperature'].values
    lr_model = LinearRegression().fit(X, y)
    trend = "positive" if lr_model.coef_[0] > 0 else "negative"
    slope = lr_model.coef_[0]

    # 5. вычисляем среднюю, мин и макс температуру за всё время
    average_temp = data['temperature'].mean()
    min_temp = data['temperature'].min()
    max_temp = data['temperature'].max()

    return {
        "city": city,
        "average_temp": average_temp,
        "min_temp": min_temp,
        "min_temp": max_temp,
        "season_profile": season_profile.to_dict(),
        "trend": trend,
        "trend_slope": slope,
        "anomalies": all_anomalies
    }

# получаем текущую температуру через OpenWeatherMap API (синхронно)
def get_current_temperature(city, api_key):
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data["main"]["temp"]
    else:
        print(f"Ошибка: {response.status_code}, {response.json()}")
        return None

# провеярем аномальность текущей температуры
def is_temperature_anomalous(current_temp, historical_data, season):
    season_data = historical_data[historical_data['season'] == season]
    mean_temp = season_data['temperature'].mean()
    std_temp = season_data['temperature'].std()

    lower_bound = mean_temp - 2 * std_temp
    upper_bound = mean_temp + 2 * std_temp

    print(f"Время года: {season}, Средняя температура: {mean_temp:.2f}, Стандартное отклонение: {std_temp:.2f}")
    print(f"Диапазон нормальной температуры: [{lower_bound:.2f}, {upper_bound:.2f}]")

    return not (lower_bound <= current_temp <= upper_bound)