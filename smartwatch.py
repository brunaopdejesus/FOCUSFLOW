import csv
import serial
import time
import os

# Verifica se o ambiente é de produção (por exemplo, se está rodando no Render)
IS_RENDER = os.getenv('RENDER') is not None

# Inicializa a conexão com a porta serial, ou simula se estiver no Render
if not IS_RENDER:
    ser = serial.Serial('/dev/cu.usbmodem14201', 115200, timeout=1)
else:
    ser = None  # No ambiente de deploy (Render), sem porta serial

# Lista para armazenar os valores de BPM
bpm_list = []

def salvar_no_csv(media_batimentos, menor_batimento, maior_batimento, pressao_menor_min, pressao_menor_max, pressao_maior_min, pressao_maior_max):
    file_path = './dados_predicao.csv'
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(['media_batimentos', 'menor_batimento', 'maior_batimento', 'pressao_menor_min', 'pressao_menor_max', 'pressao_maior_min', 'pressao_maior_max'])
        writer.writerow([media_batimentos, menor_batimento, maior_batimento, pressao_menor_min, pressao_menor_max, pressao_maior_min, pressao_maior_max])

# Função principal
def monitorar_bpm():
    while True:
        if not IS_RENDER:
            # Ler dados do Arduino se está rodando localmente
            if ser and ser.in_waiting > 0:
                linha = ser.readline().decode('utf-8').strip()
                print(f"Dado recebido: {linha}")
                processar_linha(linha)
        else:
            # Simula dados no ambiente de deploy (Render)
            linha_simulada = '{"BPM": 75}'
            print(f"Simulando dado recebido: {linha_simulada}")
            processar_linha(linha_simulada)
            time.sleep(5)

def processar_linha(linha):
    try:
        if "BPM" in linha:
            bpm_data = eval(linha)
            bpm = bpm_data['BPM']
            bpm_list.append(bpm)
            print(f"BPM capturado: {bpm}")
            
            if len(bpm_list) >= 10:
                media_batimentos = sum(bpm_list) / len(bpm_list)
                menor_batimento = min(bpm_list)
                maior_batimento = max(bpm_list)
                pressao_menor_min = 80
                pressao_menor_max = 85
                pressao_maior_min = 120
                pressao_maior_max = 125

                salvar_no_csv(media_batimentos, menor_batimento, maior_batimento, pressao_menor_min, pressao_menor_max, pressao_maior_min, pressao_maior_max)
                print("Dados salvos no CSV com sucesso!")
                bpm_list.clear()

    except Exception as e:
        print(f"Erro ao processar dados: {e}")

# Chamar a função principal
monitorar_bpm()
