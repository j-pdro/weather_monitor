# 🌦️ Weather Monitor – ETL com Notificação Agendada via WhatsApp

## 📌 Visão Geral

Este projeto implementa um pipeline **ETL (Extract, Transform, Load)** que coleta dados meteorológicos atuais da API OpenWeather, os processa, armazena em um banco de dados SQLite local e envia notificações periódicas via WhatsApp utilizando a API da Twilio. O sistema é projetado para rodar continuamente, com tarefas de coleta e notificação agendadas.

---

## ✨ Funcionalidades Principais

-   **Coleta Automatizada de Dados:** Busca dados meteorológicos (temperatura, umidade, descrição do tempo, percentual de nuvens) da API OpenWeather para uma cidade configurada.
-   **Processamento e Tradução:** Os dados da API são processados e a descrição do tempo é traduzida para o português.
-   **Armazenamento Local:** Os dados coletados são armazenados em um banco de dados SQLite.
-   **Retenção de Dados:** O banco de dados mantém automaticamente apenas os registros dos últimos 30 dias (configurável).
-   **Notificações Agendadas via WhatsApp:** Envia resumos do clima atual via WhatsApp em intervalos configuráveis, utilizando a Twilio API.
-   **Agendamento de Tarefas:**
    -   Coleta de dados meteorológicos: A cada 1 hora (configurável).
    -   Envio de notificações via WhatsApp: A cada 3 horas (configurável).
-   **Logging Detalhado:** Registra as principais operações, coletas, envios de notificação e possíveis erros.
-   **Configuração Flexível:** Chaves de API, tokens, cidade alvo e intervalos de agendamento são gerenciados através de um arquivo de configuração.
-   **Tratamento de Erros:** Inclui tratamento básico para falhas de API e outros problemas de execução.

---

## 💻 Tecnologias Utilizadas

-   **Python 3**
-   **Bibliotecas Python:**
    -   `requests`: Para realizar chamadas HTTP à API OpenWeather.
    -   `schedule`: Para agendamento das tarefas de coleta e notificação.
    -   `twilio`: Para interagir com a API da Twilio e enviar mensagens via WhatsApp.
    -   `sqlite3`: Para interação com o banco de dados SQLite (parte da biblioteca padrão do Python).
    -   `pytz`: Para manipulação correta de fusos horários.
-   **APIs Externas:**
    -   OpenWeather API
    -   Twilio API for WhatsApp
-   **Banco de Dados:**
    -   SQLite

---

## 🚀 Como Configurar e Rodar

### 1. Pré-requisitos

-   Python 3.8 ou superior.
-   Conta na [OpenWeather](https://openweathermap.org/appid) para obter uma API Key.
-   Conta na [Twilio](https://www.twilio.com/try-twilio) com um número de telefone habilitado para WhatsApp (ou o sandbox da Twilio configurado). Você precisará do seu Account SID, Auth Token, e o número de WhatsApp da Twilio.

### 2. Clonando o Repositório

```bash
git clone https://github.com/j-pdro/weather_monitor 
cd weather_monitor
```

### 3. Configurando o Ambiente Virtual e Dependências

É altamente recomendável usar um ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate  # No Linux/macOS
# venv\Scripts\activate   # No Windows
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

### 4. Configurando as Credenciais e Parâmetros

Crie o arquivo de configuração: Copie o arquivo de exemplo config.py.example para config.py:

```bash
cp config.py.example config.py
```

Edite config.py: Abra o arquivo config.py em um editor de texto e preencha TODAS as informações solicitadas com suas chaves de API, tokens, números de telefone, cidade desejada e fuso horário.

```python
# config.py
# OpenWeather API Configuration
API_KEY = "SUA_API_KEY_OPENWEATHER"
CITY = "Sao Paulo"  # Ex: "London", "New York"
COUNTRY = "BR"  # Ex: "GB", "US"

# Twilio Configuration
TWILIO_ACCOUNT_SID = "SEU_TWILIO_ACCOUNT_SID"
TWILIO_AUTH_TOKEN = "SEU_TWILIO_AUTH_TOKEN"
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"  # Número Twilio (Sandbox ou comprado)
YOUR_WHATSAPP_TO = "whatsapp:+SEUNUMEROPESSOALCOMCODIGOPAIS"  # Seu WhatsApp

# Scheduling Intervals
FETCH_INTERVAL_HOURS = 1
NOTIFY_INTERVAL_HOURS = 3

# Data Retention
DAYS_TO_KEEP_RECORDS = 30

# Behavior on Startup
SEND_NOTIFICATION_ON_STARTUP = False
DISPLAY_TIMEZONE = 'America/Sao_Paulo'  # Seu fuso horário local
```

### 5. Executando o Monitor

#### a) Via Terminal

Com o ambiente virtual ativado e o config.py preenchido, execute o script principal:

```bash
python3 weather.py
```

O script começará a rodar, exibindo logs no terminal. Ele realizará uma coleta inicial de dados e, em seguida, seguirá os agendamentos definidos. Para parar o script, pressione Ctrl+C no terminal.

#### b) (Opcional) Criando um Atalho na Área de Trabalho (Linux, como eu uso atualmente)

Para executar o monitor com um clique no Linux:

1. Identifique os caminhos:
    - Com o venv ativado: `which python` (anote o caminho para o python do venv).
    - Caminho completo para `weather.py` (ex: `/home/seu_usuario/weather_monitor/weather.py`).
    - Caminho completo para o diretório do projeto (ex: `/home/seu_usuario/weather_monitor/`).

2. Crie o arquivo `.desktop`: Crie um arquivo chamado `weather_monitor.desktop` (por exemplo, em `~/.local/share/applications/`) com o seguinte conteúdo, substituindo os placeholders pelos seus caminhos:

```desktop
[Desktop Entry]
Version=1.0
Name=Weather Monitor
Comment=Monitora o clima e envia notificações via WhatsApp
Exec=<CAMINHO_PYTHON_VENV> <CAMINHO_WEATHER.PY>
Path=<CAMINHO_DIRETORIO_PROJETO>
Icon=utilities-terminal # Ou o caminho para um ícone customizado
Terminal=true
Type=Application
Categories=Utility;Application;
```

Exemplo:

```desktop
Exec=/home/j-pdro/weather_monitor/venv/bin/python /home/j-pdro/weather_monitor/weather.py
Path=/home/j-pdro/weather_monitor/
```

3. Torne-o executável (se necessário):

```bash
chmod +x ~/.local/share/applications/weather_monitor.desktop
```

O atalho deve aparecer no seu menu de aplicativos. Você pode precisar fazer logout/login. Para tê-lo na área de trabalho, copie o arquivo `.desktop` para sua pasta `~/Desktop` e marque-o como "confiável" se solicitado. Clicar nele abrirá um terminal e executará o script.

---

## 📁 Estrutura do Projeto

```plaintext
weather_monitor/
│
├── weather.py             # Script principal: orquestra coleta, agendamento e inicialização
├── database.py            # Módulo para todas as interações com o banco de dados SQLite
├── notifier.py            # Módulo para formatação e envio de notificações via Twilio
├── config.py              # Configurações do usuário (API keys, cidade, etc. - NÃO VERSIONADO)
├── config.py.example      # Arquivo de exemplo para config.py (VERSIONADO)
├── requirements.txt       # Lista de dependências Python
├── .gitignore             # Arquivos e pastas ignoradas pelo Git
├── LICENSE                # Arquivo de licença do projeto (MIT)
└── README.md              # Documentação do projeto
```

O arquivo `weather_data.db` será criado no diretório raiz quando o script for executado pela primeira vez.

---

## ⚙️ Detalhes da Implementação

### Coleta de Dados (OpenWeather)

- Utiliza a API "Current Weather Data" da OpenWeather.
- Os dados são requisitados em formato JSON e incluem temperatura, umidade, descrição do tempo e percentual de nuvens.
- A descrição do tempo é traduzida para português usando um dicionário interno.

### Armazenamento de Dados (SQLite)

- Um banco de dados SQLite (`weather_data.db`) é usado para persistir os dados.
- **Tabela `weather_log`:**
    - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
    - `timestamp` (TEXT, em UTC 'YYYY-MM-DD HH:MM:SS')
    - `cidade` (TEXT)
    - `temperatura` (REAL)
    - `umidade` (REAL)
    - `chance_chuva` (TEXT)
    - `descricao` (TEXT)
    - `nuvens_percentual` (INTEGER)
- Índices são criados nas colunas `timestamp` e `cidade` para otimizar consultas.
- Registros mais antigos que `DAYS_TO_KEEP_RECORDS` (definido em `config.py`) são automaticamente excluídos.

### Notificações (Twilio WhatsApp)

- O módulo `notifier.py` busca o registro meteorológico mais recente no banco.
- Formata uma mensagem amigável com os dados do clima, convertendo o timestamp para o fuso horário local especificado em `config.py` (`DISPLAY_TIMEZONE`).
- Envia a mensagem para o número de WhatsApp configurado (`YOUR_WHATSAPP_TO`) usando as credenciais da Twilio.

### Agendamento de Tarefas

- A biblioteca `schedule` é usada para rodar `job_collect_and_save_weather_data` e `job_send_notification` nos intervalos definidos em `config.py`.

### Tratamento de Erros e Logging

- O módulo `logging` do Python é usado para registrar informações, avisos e erros durante a execução.
- Blocos `try-except` são usados para capturar exceções durante chamadas de API e outras operações críticas.

---
## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🤝 Contribuição

Este projeto foi desenvolvido como um exercício prático e para fins de portfólio. Sinta-se à vontade para clonar, modificar e usar como base para seus próprios projetos. Pull requests com melhorias ou correções são bem-vindos.
