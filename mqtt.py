# MQTT COMMUNICATION
# Author: Mauricio Neves Junior
# Version: 1.0
# Date: 07/12/2023

# Libraries
import time
import paho.mqtt.client as mqtt
import data
import sqlite3

# Broker Settings
broker_address = "broker.hivemq.com"  # Substitua pelo endereço do seu broker
port = 1883
topic_temperature = "cpu_test/temperature"
topic_cpu_usage = "cpu_test/usage"

# Database Path
database_path = "database.db"

# Broker Connection
client = mqtt.Client()
on_connect = client.on_connect
client.connect(broker_address, port, 60)
client.loop_start()


# Callback for broker connection
def on_connect(client, userdata, flags, rc):
    client.subscribe(topic_temperature)
    client.subscribe(topic_cpu_usage)


# Callback for Topic Message
def on_message(client, userdata, msg):
    # Conecta ao banco de dados
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        # Get Timestamp
        timestamp = time.time()

        # Insert data on database
        if msg.topic == topic_temperature:
            temperature = float(msg.payload)
            cursor.execute("INSERT INTO temperature_data (timestamp, temperature) VALUES (?, ?)",
                           (timestamp, temperature))
        elif msg.topic == topic_cpu_usage:
            cpu_usage = float(msg.payload)
            cursor.execute("INSERT INTO cpu_usage_data (timestamp, cpu_usage) VALUES (?, ?)", (timestamp, cpu_usage))

        # Transaction Commit
        conn.commit()

    # Exception if there is any errors
    except Exception as e:
        print(f"Erro ao inserir dados no banco de dados: {e}")

    finally:
        # Close connection
        conn.close()


# Function for database tables creation
def create_table():
    # Connection with database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS temperature_data
                    (timestamp REAL, temperature REAL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS cpu_usage_data
                    (timestamp REAL, cpu_usage REAL)''')

    # Transaction Commit
    conn.commit()

    # Close Connection
    conn.close()

# Main Code
def main():
    try:
        # Open connection with MQTT Broker and Create Table in Database
        client.loop_start()
        create_table()

        while True:
            # CPU Temperature and Usage Variables
            temperature = data.get_cpu_temperature()
            cpu_usage = data.get_cpu_usage()

            # Publish the CPU temperature and Usage in the broker
            client.publish(topic_temperature, temperature)
            client.publish(topic_cpu_usage, cpu_usage)
            print("Tópicos publicados!")

            # Wait 5 seconds before send the data again (If you want real time monitoring, delete this function or
            # insert a lower time)
            time.sleep(5)

    # Close the program when user closes the prompt or uses Ctrl + C
    except KeyboardInterrupt:
        print("Programa encerrado pelo usuário.")

    finally:
        # Disconnects from broker when the program is closed
        client.loop_stop()
        client.disconnect()
