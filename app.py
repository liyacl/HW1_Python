import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from functions import main_func, get_current_temperature, is_temperature_anomalous

st.title("Домашнее задание 1. Сердюк Лия Игоревна")
st.header("Интерактивное приложение для анализа температур")

all_cities = ['New York', 'London', 'Paris', 'Tokyo', 'Moscow', 'Sydney', 'Berlin', 'Beijing', 'Rio de Janeiro', 'Dubai', 'Los Angeles', 'Singapore', 'Mumbai', 'Cairo', 'Mexico City']
today = datetime.now()
current_season = {12: "winter", 1: "winter", 2: "winter",
                  3: "spring", 4: "spring", 5: "spring",
                  6: "summer", 7: "summer", 8: "summer",
				  9: "autumn", 10: "autumn", 11: "autumn"}[today.month]

# 1. загрузка файла с историческими данными
uploaded_file = st.file_uploader("Выберите CSV-файл", type=['csv'])
if uploaded_file is not None:
	df = pd.read_csv(uploaded_file)
	df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y-%m-%d")
	st.dataframe(df.head())

	# 2. выбор города из списка
	city_name = st.selectbox("Выберите город ", tuple(all_cities))

	# 3. ввод API-ключа
	api = st.text_input('Введите API-ключ OpenWeatherMap')
	if api:
		current_temp = get_current_temperature(city_name, api)
		if current_temp is not None:
			# 4. вывод текущей температуры
			st.write(f"Текущая температура в {city_name}: {current_temp:.2f} °C")
			anomalous = is_temperature_anomalous(current_temp, df[df['city'] == city_name], current_season)
			# 5. проверка: является ли текущая температура аномальной
			if anomalous:
				st.write(f"Текущая температура в {city_name} является аномальной для сезона {current_season}.")
			else:
				st.write(f"Текущая температура в {city_name} находится в пределах нормы для сезона {current_season}.")

			# 6. вывод описательных статистик
			st.subheader(f"Описательные статистики по городу {city_name} за 10 лет")
			st.write(df[df["city"] == city_name][['temperature']].describe())
			ready_dict = main_func(df, city_name)
			if ready_dict:
				# 7. вывод графиков с аномалиями
				st.subheader(f"Временной ряд температур в городе {city_name} с аномалиями")
				anomalies_df = df[df.index.isin(ready_dict['anomalies'])]
				fig1 = px.line(df, x='timestamp', y="temperature", title=f"""График температур в городе {city_name}, ℃""")
				fig2 = px.scatter(anomalies_df, y="temperature", x="timestamp", color_discrete_sequence=["red"])
				st.plotly_chart(fig1.add_trace(fig2.data[0]))
				# 8. вывод сезонного профиля
				st.subheader(f"Сезонный профиль для города {city_name}")
				st.write(ready_dict['season_profile'])
		else:
			st.write({"cod":401, "message": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."})
	# когда апи ключ не введен, данные для текущей погоды не показываются
	else:
		st.text("Без API-ключа статистика по погоде не будет отображена :(")