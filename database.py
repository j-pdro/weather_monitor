# database.py
import sqlite3
from datetime import datetime, timedelta, timezone
import logging # Adicionar logging para erros

DB_NAME = "weather_data.db"

def execute_query(query, params=(), fetch_one=False, fetch_all=False):
    """Função auxiliar para executar queries e lidar com conexões."""
    conn = None # Inicializa conn como None
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            logging.debug(f"Query executada com sucesso: {query[:50]}...") # Log de debug

            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
            # Retorna o ID da linha inserida, se for um INSERT
            return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Erro no banco de dados ao executar '{query[:50]}...': {e}")
        # Se a conexão foi estabelecida antes do erro, o 'with' garante o rollback/close.
        # Se o erro foi ao conectar, conn ainda será None ou a conexão falhou.
        return None # Retorna None em caso de erro

def create_table():
    """Cria a tabela 'weather_log' se ela não existir"""
    query = """
        CREATE TABLE IF NOT EXISTS weather_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora DATETIME NOT NULL,
            cidade TEXT NOT NULL,
            temperatura REAL,
            umidade REAL,
            chance_chuva TEXT, -- Ou REAL se for armazenar % numérica
            descricao TEXT,
            nuvens_percentual REAL -- Adicionado para referência
        )
    """
    execute_query(query)
    # Criar índices para otimizar consultas e exclusões
    execute_query("CREATE INDEX IF NOT EXISTS idx_data_hora ON weather_log (data_hora);")
    execute_query("CREATE INDEX IF NOT EXISTS idx_cidade ON weather_log (cidade);")
    logging.info("Tabela 'weather_log' e índices verificados/criados.")

def save_weather_data(cidade, temperatura, umidade, chance_chuva, descricao, nuvens_percentual):
    """Salva um novo registro de dados meteorológicos no banco."""
    query = """
        INSERT INTO weather_log (cidade, temperatura, umidade, chance_chuva, descricao, nuvens_percentual)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    params = (cidade, temperatura, umidade, chance_chuva, descricao, nuvens_percentual)
    record_id = execute_query(query, params)
    if record_id:
        logging.info(f"Dados meteorológicos salvos para {cidade}. ID: {record_id}")
    else:
        logging.warning(f"Falha ao salvar dados meteorológicos para {cidade}.")


def delete_old_records(days=30):
    """Remove registros mais antigos que o número especificado de dias."""
    try:
        cutoff_date_utc = datetime.now(timezone.utc) - timedelta(days=days)
        query = "DELETE FROM weather_log WHERE data_hora < ?"

        with sqlite3.connect(DB_NAME) as conn:
             cursor = conn.cursor()
             cursor.execute(query, (cutoff_date_utc.isoformat(),))
             rows_deleted = cursor.rowcount # Verifica quantas linhas foram afetadas
             conn.commit()
             if rows_deleted > 0:
                 logging.info(f"{rows_deleted} registro(s) antigo(s) removido(s) (anteriores a {cutoff_date_utc.strftime('%Y-%m-%d %H:%M UTC')}).")
             else:
                 logging.info("Nenhum registro antigo para remover (baseado em UTC).")

    except sqlite3.Error as e:
        logging.error(f"Erro ao deletar registros antigos: {e}")


def get_latest_weather_record():
    """Busca o registro meteorológico mais recente do banco de dados."""
    query = "SELECT cidade, temperatura, umidade, chance_chuva, descricao, data_hora FROM weather_log ORDER BY data_hora DESC LIMIT 1"
    try:
        # Usando a função auxiliar para executar a query
        # e buscar o último registro
        result = execute_query(query, fetch_one=True)
        if result:
            # Retorna como um dicionário para facilitar o acesso
            columns = ["cidade", "temperatura", "umidade", "chance_chuva", "descricao", "data_hora"]
            return dict(zip(columns, result))
        else:
            logging.info("Nenhum registro encontrado no banco de dados.")
            return None
    except Exception as e:
        logging.error(f"Erro ao buscar último registro: {e}")
        return None
    # --- Inicialização ---
# Comentado para evitar execução automática na importação, chamar explicitamente no script principal
# create_table()