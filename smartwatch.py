import csv
import serial
import time
import requests

# Inicializa a conexão com a porta serial (modifique a porta conforme necessário)
ser = serial.Serial('/dev/cu.usbmodem14201', 115200, timeout=1)

# Lista para armazenar os valores de BPM
bpm_list = []

def enviar_dados_para_servidor(media_batimentos, menor_batimento, maior_batimento, pressao_menor_min, pressao_menor_max, pressao_maior_min, pressao_maior_max):
    # URL do servidor Flask na nuvem
    url = "http://35.160.120.126/api/dados"

    # Dados que serão enviados no formato JSON
    payload = {
        "media_batimentos": media_batimentos,
        "menor_batimento": menor_batimento,
        "maior_batimento": maior_batimento,
        "pressao_menor_min": pressao_menor_min,
        "pressao_menor_max": pressao_menor_max,
        "pressao_maior_min": pressao_maior_min,
        "pressao_maior_max": pressao_maior_max
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"Dados enviados com sucesso! Resposta: {response.json()}")
        else:
            print(f"Falha ao enviar dados. Status: {response.status_code}, Resposta: {response.text}")
    except Exception as e:
        print(f"Erro ao enviar dados: {e}")

# Função principal
def monitorar_bpm():
    while True:
        # Ler a linha do Arduino
        if ser.in_waiting > 0:
            linha = ser.readline().decode('utf-8').strip()
            print(f"Dado recebido: {linha}")
            
            # Verificar se o dado é um valor BPM no formato JSON
            try:
                if "BPM" in linha:
                    bpm_data = eval(linha)  # Converte string JSON para dicionário
                    bpm = bpm_data['BPM']
                    bpm_list.append(bpm)
                    print(f"BPM capturado: {bpm}")

                    # Simular uma captura contínua de BPM por um tempo e, depois, calcular os valores
                    if len(bpm_list) >= 10:  # Após 10 valores, enviar para o servidor
                        media_batimentos = sum(bpm_list) / len(bpm_list)
                        menor_batimento = min(bpm_list)
                        maior_batimento = max(bpm_list)

                        # Valores fictícios de pressão arterial (modifique conforme necessário)
                        pressao_menor_min = 80
                        pressao_menor_max = 85
                        pressao_maior_min = 120
                        pressao_maior_max = 125

                        # Enviar os dados para o servidor Flask na nuvem
                        enviar_dados_para_servidor(media_batimentos, menor_batimento, maior_batimento, pressao_menor_min, pressao_menor_max, pressao_maior_min, pressao_maior_max)

                        # Limpar a lista de BPM para capturar novos valores
                        bpm_list.clear()

            except Exception as e:
                print(f"Erro ao processar dados: {e}")

# Chamar a função principal
monitorar_bpm()
