# weather.py
import requests
import config
import database # Importa módulo de banco de dados
import logging
# from datetime import datetime # datetime não é mais usado diretamente neste arquivo
import notifier # Importa módulo de notificação (Twilio)
import schedule # Para agendamento de tarefas
import time     # Para o loop de agendamento

# --- Configurações ---

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Dicionário de tradução para descrever o clima
weather_translation = {
    "clear sky": "Céu limpo", "few clouds": "Poucas nuvens",
    "scattered clouds": "Nuvens dispersas", "broken clouds": "Nuvens quebradas",
    "overcast clouds": "Nublado", "shower rain": "Chuva passageira",
    "rain": "Chuva", "thunderstorm": "Tempestade", "snow": "Neve", "mist": "Névoa"
    # Adicionar mais traduções conforme necessário
}

# --- Funções de Coleta e Processamento (como antes) ---

def get_weather(city, country, api_key):
    """Busca dados meteorológicos da API OpenWeather."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={api_key}&units=metric&lang=pt_br"
    logging.info(f"Buscando dados para {city}, {country}...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        weather_data = response.json()
        logging.info(f"Dados recebidos com sucesso para {city}, {country}.")
        return weather_data
    except requests.exceptions.Timeout:
        logging.error(f"Timeout ao conectar com OpenWeather API para {city}, {country}.")
        return None
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"Erro HTTP ao buscar dados para {city}, {country}: {http_err} - {response.text}")
        return None
    except requests.exceptions.RequestException as req_err:
        logging.error(f"Erro de requisição ao buscar dados para {city}, {country}: {req_err}")
        return None
    except Exception as e:
        logging.error(f"Erro inesperado ao buscar dados para {city}, {country}: {e}", exc_info=True)
        return None


def process_data(weather_data, city_name):
    """Processa os dados brutos da API e retorna um dicionário limpo."""
    if not weather_data or weather_data.get("cod") != 200:
        logging.warning(f"Dados inválidos ou erro na resposta da API para {city_name}. Código: {weather_data.get('cod')}")
        return None
    try:
        main_data = weather_data.get("main", {})
        cloud_data = weather_data.get("clouds", {})
        weather_info = weather_data.get("weather", [{}])[0]

        temperature = main_data.get("temp")
        humidity = main_data.get("humidity")
        clouds_percent = cloud_data.get("all")
        description_api = weather_info.get("description", "N/A")
        description_pt = weather_translation.get(description_api.lower(), description_api)

        if clouds_percent is None:
             rain_chance = "Indisponível"
        elif clouds_percent <= 20:
            rain_chance = "Muito baixa"
        elif clouds_percent <= 50:
            rain_chance = "Baixa"
        elif clouds_percent <= 80:
            rain_chance = "Moderada"
        else:
            rain_chance = "Alta"

        processed = {
            "cidade": weather_data.get("name", city_name),
            "temperatura": temperature,
            "umidade": humidity,
            "chance_chuva": rain_chance,
            "descricao": description_pt,
            "nuvens_percentual": clouds_percent
        }
        if processed["temperatura"] is None or processed["umidade"] is None:
             logging.warning(f"Dados essenciais (temp/umidade) ausentes para {city_name}.")
             return None
        return processed
    except (KeyError, IndexError, TypeError) as e:
        logging.error(f"Erro ao processar dados para {city_name}: {e}. Dados recebidos: {weather_data}", exc_info=True)
        return None

# --- Funções de Job para Agendamento ---

def job_collect_and_save_weather_data():
    """Tarefa agendada para coletar, processar, salvar dados meteorológicos e limpar registros antigos."""
    logging.info("JOB: Iniciando coleta e salvamento de dados meteorológicos...")
    TARGET_CITY = config.CITY
    TARGET_COUNTRY = config.COUNTRY
    API_KEY = config.API_KEY

    raw_data = get_weather(TARGET_CITY, TARGET_COUNTRY, API_KEY)
    if raw_data:
        processed_data = process_data(raw_data, TARGET_CITY)
        if processed_data:
            database.save_weather_data(
                cidade=processed_data["cidade"],
                temperatura=processed_data["temperatura"],
                umidade=processed_data["umidade"],
                chance_chuva=processed_data["chance_chuva"],
                descricao=processed_data["descricao"],
                nuvens_percentual=processed_data["nuvens_percentual"]
            )
            # Exibe os dados formatados no console (útil para ver o job rodando)
            print("\n--- Clima Atual Salvo (Job Agendado) ---")
            print(f"Cidade: {processed_data['cidade']}")
            print(f"Temperatura: {processed_data['temperatura']}°C")
            print(f"Umidade: {processed_data['umidade']}%")
            print(f"Chance de Chuva: {processed_data['chance_chuva']} ({processed_data['nuvens_percentual']}% nuvens)")
            print(f"Descrição: {processed_data['descricao']}\n")

            # Limpa registros antigos após salvar novos dados
            logging.info("JOB: Verificando registros antigos após coleta...")
            database.delete_old_records(days=config.DAYS_TO_KEEP_RECORDS) # Usando config para dias
        else:
            logging.error("JOB: Falha ao processar os dados meteorológicos.")
    else:
        logging.error("JOB: Falha ao obter os dados meteorológicos da API.")
    logging.info("JOB: Coleta e salvamento de dados meteorológicos concluído.")


def job_send_notification():
    """Tarefa agendada para enviar notificação via WhatsApp."""
    logging.info("JOB: Iniciando envio de notificação WhatsApp...")
    success = notifier.send_whatsapp_notification()
    if success:
        logging.info("JOB: Envio de notificação WhatsApp concluído com sucesso.")
    else:
        logging.warning("JOB: Envio de notificação WhatsApp falhou ou não havia dados.")


# --- Execução Principal com Agendamento ---

if __name__ == "__main__":
    logging.info("=================================================")
    logging.info("   INICIALIZANDO WEATHER MONITOR COM AGENDAMENTO   ")
    logging.info("=================================================")

    # 1. Garante que a tabela do banco de dados exista ao iniciar
    logging.info("Verificando estrutura do banco de dados...")
    database.create_table()

    # --- Configuração dos Agendamentos ---
    # Intervalos de produção:
    schedule.every(config.FETCH_INTERVAL_HOURS).hours.do(job_collect_and_save_weather_data)
    schedule.every(config.NOTIFY_INTERVAL_HOURS).hours.do(job_send_notification)

    # Para testes rápidos
    # logging.warning("MODO DE TESTE: Usando intervalos em minutos para agendamento.")
    # schedule.every(1).minutes.do(job_collect_and_save_weather_data)
    # schedule.every(2).minutes.do(job_send_notification)

    logging.info("Agendamentos configurados:")
    # Mostra os intervalos reais que serão usados (de config ou de teste)
    for job in schedule.jobs:
        logging.info(f" - Próxima execução de '{job.job_func.__name__}': {job.next_run.strftime('%Y-%m-%d %H:%M:%S')} (Intervalo: {job.interval} {job.unit})")


    # Executar uma vez no início para ter dados imediatos e testar
    # Isso garante que você tenha dados e uma notificação (se aplicável) logo ao iniciar.
    logging.info("Executando coleta inicial de dados ao iniciar o script...")
    job_collect_and_save_weather_data()

    # Decide se envia notificação inicial baseado em uma configuração
    if getattr(config, 'SEND_NOTIFICATION_ON_STARTUP', False): # Default é não enviar no startup
        logging.info("Executando envio de notificação inicial ao iniciar o script (configurado)...")
        job_send_notification()
    else:
        logging.info("Envio de notificação inicial desabilitado (SEND_NOTIFICATION_ON_STARTUP=False em config.py ou não definido).")


    logging.info("Iniciando loop de agendamento. Pressione Ctrl+C para sair.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1) # Verifica a cada segundo
    except KeyboardInterrupt:
        logging.info("Loop de agendamento interrompido pelo usuário (Ctrl+C). Encerrando...")
    except Exception as e:
        logging.error(f"Erro inesperado no loop de agendamento: {e}", exc_info=True)
    finally:
        logging.info("Weather Monitor encerrado.")