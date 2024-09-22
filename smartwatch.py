import csv
import serial
import time

# Inicializa a conexão com a porta serial (modifique a porta conforme necessário)
ser = serial.Serial('/dev/cu.usbmodem14201', 115200, timeout=1)

# Lista para armazenar os valores de BPM
bpm_list = []

def salvar_no_csv(media_batimentos, menor_batimento, maior_batimento, pressao_menor_min, pressao_menor_max, pressao_maior_min, pressao_maior_max):
    # Caminho do arquivo CSV
    file_path = './dados_predicao.csv'

    # Escrever os dados no arquivo CSV
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['media_batimentos', 'menor_batimento', 'maior_batimento', 'pressao_menor_min', 'pressao_menor_max', 'pressao_maior_min', 'pressao_maior_max'])
        writer.writerow([media_batimentos, menor_batimento, maior_batimento, pressao_menor_min, pressao_menor_max, pressao_maior_min, pressao_maior_max])

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
                    if len(bpm_list) >= 10:  # Suponha que após 10 valores, você quer salvar
                        media_batimentos = sum(bpm_list) / len(bpm_list)
                        menor_batimento = min(bpm_list)
                        maior_batimento = max(bpm_list)

                        # Definir os valores de pressão arterial (pode modificar conforme necessário)
                        pressao_menor_min = 80  # Exemplo de pressão
                        pressao_menor_max = 85
                        pressao_maior_min = 120
                        pressao_maior_max = 125

                        # Salvar no CSV
                        salvar_no_csv(media_batimentos, menor_batimento, maior_batimento, pressao_menor_min, pressao_menor_max, pressao_maior_min, pressao_maior_max)
                        print("Dados salvos no CSV com sucesso!")

                        # Limpar a lista de BPM para capturar novos valores
                        bpm_list.clear()

            except Exception as e:
                print(f"Erro ao processar dados: {e}")

# Chamar a função principal
monitorar_bpm()

