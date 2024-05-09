import time
import data
from opcua import Server, ua
import sqlite3

# Configurações do servidor OPC-UA
opcua_address = "opc.tcp://localhost:4840/freeopcua/server/"  # Substitua pelo endereço desejado

# Configurações do banco de dados SQLite
db_path = "database.db"
opcua_table_name = "opcua_data"

# Função para obter a temperatura da CPU (substitua pelo seu código real)
def get_cpu_temperature():
    data.get_cpu_temperature()

# Função para obter o uso da CPU (substitua pelo seu código real)
def get_cpu_usage():
    data.get_cpu_usage()

# Callback chamada quando o valor de uma variável OPC-UA é alterado
def datachange_notification(var, val, data):
    # Conecta ao banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Obtém o timestamp atual
        timestamp = time.time()

        # Insere os dados no banco de dados
        if var.get_full_name() == "2:Temperature":
            temperature = float(val)
            cursor.execute(f"INSERT INTO {opcua_table_name} (timestamp, temperature) VALUES (?, ?)", (timestamp, temperature))
        elif var.get_full_name() == "2:CpuUsage":
            cpu_usage = float(val)
            cursor.execute(f"INSERT INTO {opcua_table_name} (timestamp, cpu_usage) VALUES (?, ?)", (timestamp, cpu_usage))

        # Commit da transação
        conn.commit()

    except Exception as e:
        print(f"Erro ao inserir dados no banco de dados: {e}")

    finally:
        # Fecha a conexão com o banco de dados
        conn.close()


# Cria um servidor OPC-UA
server = Server()
server.set_endpoint(opcua_address)

# Cria um objeto de espaço de nomes para variáveis OPC-UA
uri = "http://example.org"
idx = server.register_namespace(uri)

# Cria variáveis para temperatura e uso da CPU
temperature_var = server.nodes.objects.add_variable(idx, "Temperature", 0.0)
cpu_usage_var = server.nodes.objects.add_variable(idx, "CpuUsage", 0.0)

# Configura a função de callback para alterações de dados
handler = server.nodes.objects.add_method(idx, "DataChangeNotification", datachange_notification, [ua.VariantType.Float, ua.VariantType.Float])


# Loop principal
def main():
    try:
        # Inicia o servidor OPC-UA
        server.start()

        while True:
            # Obtém a temperatura e o uso da CPU
            temperature = get_cpu_temperature()
            cpu_usage = get_cpu_usage()

            # Atualiza os valores das variáveis OPC-UA
            temperature_var.set_value(temperature)
            cpu_usage_var.set_value(cpu_usage)

            # Aguarda um intervalo (por exemplo, 5 segundos) antes de atualizar novamente
            time.sleep(5)

    except KeyboardInterrupt:
        print("Programa encerrado pelo usuário.")
    finally:
        # Para o servidor OPC-UA
        server.stop()
