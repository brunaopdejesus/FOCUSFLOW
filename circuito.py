import serial
import requests
import csv
import time
import re

# Configuração da porta serial (Arduino)
try:
    arduino = serial.Serial('/dev/tty.usbmodem14201', 9600)
    print("Conexão com o Arduino estabelecida com sucesso.")
except Exception as e:
    print(f"Erro ao conectar ao Arduino: {e}")

# URL do servidor para onde os dados serão enviados
url = "http://localhost:5001/api/dados"

# Função para salvar os dados em um arquivo CSV
def salvar_dados_csv(temperature, humidity, ldr_value):
    with open('dados_sensores.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), temperature, humidity, ldr_value])

# Função para enviar os dados ao servidor
def enviar_dados_para_localhost(temperature, humidity, ldr_value):
    payload = {
        "temperature": temperature,
        "humidity": humidity,
        "ldr_value": ldr_value
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Dados enviados com sucesso!")
        else:
            print(f"Erro ao enviar dados: {response.status_code}")
    except Exception as e:
        print(f"Erro na conexão com o servidor: {e}")

# Função para extrair números de uma string
def extrair_valor_de_string(data_string):
    return re.findall(r"[-+]?\d*\.\d+|\d+", data_string)

# Loop principal para ler os dados do Arduino
while True:
    try:
        # Ler dados da porta serial
        data = arduino.readline().decode('utf-8').strip()
        print(f"Dados recebidos: {data}")

        # Processar os dados (assumindo que os valores chegam em várias strings)
        if "Umidade:" in data and "Temperatura:" in data:
            valores = extrair_valor_de_string(data)
            humidity = float(valores[0])  # Primeiro valor é a umidade
            temperature = float(valores[1])  # Segundo valor é a temperatura

        elif "Luminosidade" in data:
            valores = extrair_valor_de_string(data)
            ldr_value = int(valores[0])  # Valor da luminosidade

            # Salvar os dados localmente (em CSV)
            salvar_dados_csv(temperature, humidity, ldr_value)

            # Enviar os dados para o servidor
            enviar_dados_para_localhost(temperature, humidity, ldr_value)

    except (IndexError, ValueError) as e:
        print(f"Erro ao processar dados: {e}")
    
    time.sleep(2)  # Atraso para esperar a próxima leitura
