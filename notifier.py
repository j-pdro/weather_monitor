# notifier.py
from twilio.rest import Client
import database
import config
import logging
from datetime import datetime
import pytz # Necessário para conversão de fuso horário

# Obter um logger específico para este módulo ANTES de usá-lo
logger = logging.getLogger(__name__)
# Defina o fuso horário para o qual você quer converter a exibição
# No futuro, isso pode vir do config.py ou ser mais dinâmico
TARGET_TIMEZONE_STR = getattr(config, 'DISPLAY_TIMEZONE', 'America/Sao_Paulo') # Pega de config ou usa default

try:
    TARGET_TIMEZONE = pytz.timezone(TARGET_TIMEZONE_STR)
    logger.info(f"Fuso horário de exibição definido como: {TARGET_TIMEZONE_STR}")
except pytz.exceptions.UnknownTimeZoneError:
    logger.error(f"Fuso horário desconhecido: {TARGET_TIMEZONE_STR}. Usando UTC como fallback.")
    TARGET_TIMEZONE = pytz.utc
except AttributeError: # Caso DISPLAY_TIMEZONE não exista em config
    logger.warning(f"DISPLAY_TIMEZONE não encontrado em config.py. Usando 'America/Sao_Paulo' como padrão.")
    TARGET_TIMEZONE_STR = 'America/Sao_Paulo'
    TARGET_TIMEZONE = pytz.timezone(TARGET_TIMEZONE_STR)


def send_whatsapp_notification():
    """
    Busca os dados meteorológicos mais recentes (que estão em UTC no banco),
    converte o timestamp para o fuso horário local de exibição e envia
    uma notificação via WhatsApp.
    """
    logger.info("Tentando enviar notificação via WhatsApp...")
    latest_data = database.get_latest_weather_record()

    if latest_data:
        logger.info(f"Dados recuperados do banco para notificação: {latest_data}")
        try:
            # latest_data['data_hora'] é uma string de um datetime UTC do banco
            # Ex: "2025-05-06 18:30:00.123456" ou "2025-05-06 18:30:00"

            # 1. Converter a string do banco para um objeto datetime "naive"
            dt_str_from_db = latest_data['data_hora']
            if not dt_str_from_db: # Checagem extra para string vazia ou None
                logger.error("Timestamp 'data_hora' está vazio ou ausente nos dados do banco.")
                return False

            try:
                if '.' in dt_str_from_db:
                    dt_naive_utc = datetime.strptime(dt_str_from_db, '%Y-%m-%d %H:%M:%S.%f')
                else:
                    dt_naive_utc = datetime.strptime(dt_str_from_db, '%Y-%m-%d %H:%M:%S')
            except ValueError as ve:
                logger.error(f"Erro ao converter string de data/hora '{dt_str_from_db}' do banco: {ve}")
                return False

            # 2. Tornar o datetime "aware" (consciente) de que ele é UTC
            # Isso assume que o datetime que o Python salvou no banco era UTC.
            dt_aware_utc = pytz.utc.localize(dt_naive_utc)

            # 3. Converter para o fuso horário alvo para exibição
            dt_target_tz_display = dt_aware_utc.astimezone(TARGET_TIMEZONE)

            # 4. Formatar para exibição
            formatted_time = dt_target_tz_display.strftime('%d/%m %H:%M')
            # timezone_abbr = dt_target_tz_display.strftime('%Z') # Abreviação do fuso, ex: -03 ou BRT

            message_body = (
                f"🌦️ *Clima Atual em {latest_data.get('cidade', 'N/A')}* ({formatted_time}) 🌦️\n\n"
                f"🌡️ Temperatura: {latest_data.get('temperatura', 'N/A')}°C\n"
                f"💧 Umidade: {latest_data.get('umidade', 'N/A')}%\n"
                f"☔ Chance de Chuva: {latest_data.get('chance_chuva', 'N/A')}\n"
                f"📝 Descrição: {latest_data.get('descricao', 'N/A')}"
            )

            # Inicializar cliente Twilio
            client = Client(config.TWILIO_SID, config.TWILIO_AUTH_TOKEN)

            # Enviar mensagem
            message = client.messages.create(
                body=message_body,
                from_=config.TWILIO_WHATSAPP_NUMBER,
                to=config.YOUR_WHATSAPP_NUMBER
            )

            logger.info(f"Notificação enviada com sucesso via WhatsApp! SID: {message.sid}")
            return True # Indica sucesso

        except Exception as e:
            # Usar exc_info=True para logar o traceback completo do erro
            logger.error(f"Falha ao processar ou enviar notificação via WhatsApp: {e}", exc_info=True)
            return False # Indica falha

    else:
        logger.warning("Nenhum dado meteorológico recente encontrado no banco para enviar notificação.")
        return False # Indica falha (sem dados)
    # --- Fim da função send_whatsapp_notification ---
    # --- Fim do módulo notifier.py ---