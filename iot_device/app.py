import paho.mqtt.client as mqtt
import time
import json
import random
import os
import hashlib
import socket

def cpu_stress_test(iterations=100000):
    for i in range(iterations):
        s = str(random.random()).encode('utf-8')
        hashlib.sha256(s).hexdigest()

def generate_lixeira_payload():
    return { "nivel_percent": random.randint(5, 100), "bateria_v": round(random.uniform(3.3, 4.2), 2) }

def generate_poluicao_payload():
    return { "ozone": random.randint(20, 100), "particulate_matter": random.randint(50, 150), "carbon_monoxide": random.randint(10, 50), "sulfure_dioxide": random.randint(10, 50), "nitrogen_dioxide": random.randint(10, 40) }

def generate_agua_payload():
    return { "temperatura_C": round(random.uniform(18, 28), 2), "salinidade_psu": round(random.uniform(20, 35), 2), "oxigenio_dissolvido_mgL": round(random.uniform(4, 8), 2), "ph": round(random.uniform(7.5, 8.5), 2), "nitrato_mgL": round(random.uniform(0.1, 0.5), 2), "amonia_mgL": round(random.uniform(0.05, 0.2), 2) }

DEVICE_PROFILE = os.getenv('DEVICE_PROFILE', 'lixeira_inteligente')
SEND_INTERVAL = int(os.getenv('SEND_INTERVAL', 600))
CLIENT_ID = f"iot_device_{DEVICE_PROFILE}_{socket.gethostname()}"

if DEVICE_PROFILE == 'lixeira_inteligente':
    payload_function = generate_lixeira_payload
    MQTT_TOPIC_DATA = "sensores/lixeiras"
elif DEVICE_PROFILE == 'poluicao_station':
    payload_function = generate_poluicao_payload
    MQTT_TOPIC_DATA = "sensores/poluicao"
elif DEVICE_PROFILE == 'agua_station':
    payload_function = generate_agua_payload
    MQTT_TOPIC_DATA = "sensores/qualidade_agua"
else:
    payload_function = generate_lixeira_payload
    MQTT_TOPIC_DATA = "sensores/default"

MQTT_BROKER_HOST = os.getenv('MQTT_BROKER_HOST', 'mosquitto')
MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT', 1883))

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Cliente '{CLIENT_ID}' conectado ao Broker MQTT com sucesso!")
    else:
        print(f"Falha ao conectar, código de retorno: {rc}")

def connect_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
    client.on_connect = on_connect
    connected = False
    while not connected:
        try:
            client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
            connected = True
        except Exception as e:
            print(f"Erro ao conectar: {e}. Tentando novamente em 5 segundos...")
            time.sleep(5)
    return client

def main():
    print(f"Iniciando dispositivo. Perfil: {DEVICE_PROFILE}, Intervalo: {SEND_INTERVAL}s, Tópico: {MQTT_TOPIC_DATA}")
    client = connect_mqtt()
    client.loop_start()

    while True:
        try:
            if DEVICE_PROFILE == 'agua_station':
                cpu_stress_test(iterations=200000)
            elif DEVICE_PROFILE == 'poluicao_station' and random.random() < 0.5:
                cpu_stress_test(iterations=100000)
            
            sensor_data = payload_function()
            payload = json.dumps(sensor_data)
            client.publish(MQTT_TOPIC_DATA, payload)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Dados enviados para '{MQTT_TOPIC_DATA}'")
            time.sleep(SEND_INTERVAL)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Ocorreu um erro no loop principal: {e}")
            time.sleep(10)
    
    client.loop_stop()
    client.disconnect()

if __name__ == '__main__':
    main()
