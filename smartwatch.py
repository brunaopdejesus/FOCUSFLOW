import csv
import serial
import time
import requests
import json
import re

# Inicializa a conexão com a porta serial (modifique a porta conforme necessário)
ser = serial.Serial('/dev/tty.usbmodem14101', 9600, timeout=1)

# Lista para armazenar os valores de BPM
bpm_list = []

def salvar_no_csv(media_batimentos, menor_batimento, maior_batimento, pressao_menor_min, pressao_menor_max, pressao_maior_min, pressao_maior_max):
    # Caminho do arquivo CSV
    file_path = './dados_predicao.csv'
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['media_batimentos', 'menor_batimento', 'maior_batimento', 'pressao_menor_min', 'pressao_menor_max', 'pressao_maior_min', 'pressao_maior_max'])
        writer.writerow([media_batimentos, menor_batimento, maior_batimento, pressao_menor_min, pressao_menor_max, pressao_maior_min, pressao_maior_max])

def enviar_dados_para_servidor(pulse, status_funcionario, myo):
    url = 'http://127.0.0.1:5001/api/smartwatch_dados'
    data = {
        'pulse': pulse,
        'status_funcionario': status_funcionario,
        'myo': myo
    }
    print(f"Enviando dados para o servidor: {data}")
    try:
        response = requests.post(url, json=data)
        print(f"Resposta do servidor: {response.json()}")
    except Exception as e:
        print(f"Erro ao enviar dados para o servidor: {e}")

def monitorar_bpm():
    while True:
        if ser.in_waiting > 0:
            linha = ser.readline().decode('utf-8').strip()
            print(f"Dado recebido: {linha}")

            # Usar regex para capturar os dados na linha recebida
            try:
                match = re.match(r"Pulse: (\d+) \| Funcionario: (\w+) \| Myo: (\d+)", linha)
                if match:
                    pulse = int(match.group(1))
                    status_funcionario = match.group(2)
                    myo = int(match.group(3))

                    print(f"Valores extraídos - Pulse: {pulse}, Status: {status_funcionario}, Myo: {myo}")

                    bpm_list.append(pulse)  # Adicionando valor de pulse à lista
                    print(f"Lista de BPMs atualizada: {bpm_list}")

                    # Se tivermos 10 valores, processar os dados
                    if len(bpm_list) >= 2:
                        media_batimentos = sum(bpm_list) / len(bpm_list)
                        menor_batimento = min(bpm_list)
                        maior_batimento = max(bpm_list)

                        pressao_menor_min = 80
                        pressao_menor_max = 85
                        pressao_maior_min = 120
                        pressao_maior_max = 125

                        # Salvar os dados processados no CSV
                        salvar_no_csv(media_batimentos, menor_batimento, maior_batimento, pressao_menor_min, pressao_menor_max, pressao_maior_min, pressao_maior_max)
                        print("Dados salvos no CSV.")

                        # Enviar os dados processados para o servidor
                        enviar_dados_para_servidor(media_batimentos, status_funcionario, myo)

                        # Limpar a lista de BPMs para iniciar nova contagem
                        bpm_list.clear()
                        print("Lista de BPMs foi limpa.")
                else:
                    print("A regex não correspondeu à string recebida. Verifique o formato.")

            except Exception as e:
                print(f"Erro ao processar dados: {e}")

monitorar_bpm()
