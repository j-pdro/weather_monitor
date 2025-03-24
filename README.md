# Projeto ETL: Weather Monitor

## Objetivo
Criar um pipeline de dados para monitoramento climático, coletando informações da API OpenWeather, transformando os dados (incluindo tradução e ajuste de formato) e armazenando localmente em um banco de dados SQLite. Além disso, o sistema enviará notificações automáticas via WhatsApp usando Twilio.

## Funcionalidades já implementadas
✅ Extração de Dados: Pergunta ao usuário sua localização (Cidade, Estado, País) e obtém dados climáticos da API OpenWeather.  
✅ Transformação: Converte as informações para um formato estruturado, incluindo tradução da descrição do clima para português.

## Próximos Passos
🔹 Banco de Dados (SQLite) – Load
- Criar weather_data.db para armazenar os últimos 30 dias de registros.
- Campos: id, data_hora, cidade, temperatura, umidade, chance_chuva, descricao.

🔹 Notificação via WhatsApp (Twilio)
- Configurar Twilio para envio automático de mensagens a cada 3 horas.

🔹 Automação do Pipeline
- Agendar a coleta de dados de forma automatizada.

## Status do Projeto
O projeto está em desenvolvimento.
