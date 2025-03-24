import requests
import config  # Importa a API_KEY do arquivo config.py

# Dicionário para traduzir condições meteorológicas
weather_translation = {
    "clear sky": "Céu limpo",
    "few clouds": "Poucas nuvens",
    "scattered clouds": "Nuvens dispersas",
    "broken clouds": "Nuvens quebradas",
    "overcast clouds": "Nublado",
    "shower rain": "Chuva passageira",
    "rain": "Chuva",
    "thunderstorm": "Tempestade",
    "snow": "Neve",
    "mist": "Névoa"
}

# Perguntar ao usuário sua localização
city = input("Digite sua cidade: ")
state = input("Digite seu estado (sigla, ex: SP): ")
country = input("Digite seu país (sigla, ex: BR): ")

# Chave da API
API_KEY = config.API_KEY

# Construir a URL da API
url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={API_KEY}&units=metric"

# Fazer a requisição para a API
response = requests.get(url)
weather_data = response.json()

# Verificar se a resposta foi bem-sucedida
if weather_data.get("cod") != 200:
    print("Erro ao obter dados meteorológicos. Verifique sua cidade e país.")
else:
    # Extrair informações úteis
    temperature = weather_data["main"]["temp"]
    humidity = weather_data["main"]["humidity"]
    clouds = weather_data["clouds"]["all"]  # Cobertura de nuvens (%)
    description = weather_data["weather"][0]["description"]  # Descrição em inglês

    # Traduzir a descrição, se estiver no dicionário
    description_pt = weather_translation.get(description.lower(), description)

    # Estimar a chance de chuva com base na cobertura de nuvens
    if clouds <= 20:
        rain_chance = "Muito baixa"
    elif clouds <= 50:
        rain_chance = "Pequena"
    elif clouds <= 80:
        rain_chance = "Moderada"
    else:
        rain_chance = "Alta"

    # Exibir os dados formatados
    print("\n--- Clima Atual ---")
    print(f"Cidade: {weather_data['name']}, {country}")
    print(f"Temperatura: {temperature}°C")
    print(f"Umidade: {humidity}%")
    print(f"Chance de Chuva: {rain_chance}")
    print(f"Descrição: {description_pt}")
