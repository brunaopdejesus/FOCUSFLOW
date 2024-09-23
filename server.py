import csv
from flask import Flask, jsonify, render_template, request, send_file
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import threading  # Adicione esta linha
import joblib
import serial
import time

app = Flask(__name__)

sensor_data = {
    "temperature": None,
    "humidity": None,
    "ldr_value": None
}

# Dados de BPM e UID (segundo circuito - smartwatch)
smartwatch_data = {
    "bpm": None,
    "uid": None
}

# Inicializa a conexão serial para o smartwatch (use a porta correta)
ser = serial.Serial('/dev/cu.usbmodem14201', 115200, timeout=1)

# Lista para armazenar os valores de BPM
bpm_list = []

def salvar_no_csv(media_batimentos, menor_batimento, maior_batimento, pressao_menor_min, pressao_menor_max, pressao_maior_min, pressao_maior_max):
    file_path = './dados_predicao.csv'
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['media_batimentos', 'menor_batimento', 'maior_batimento', 'pressao_menor_min', 'pressao_menor_max', 'pressao_maior_min', 'pressao_maior_max'])
        writer.writerow([media_batimentos, menor_batimento, maior_batimento, pressao_menor_min, pressao_menor_max, pressao_maior_min, pressao_maior_max])

def monitorar_bpm():
    while True:
        if ser.in_waiting > 0:
            linha = ser.readline().decode('utf-8').strip()
            print(f"Dado recebido: {linha}")
            
            try:
                if "BPM" in linha:
                    bpm_data = eval(linha)
                    bpm = bpm_data['BPM']
                    uid = bpm_data.get('UID', 'desconhecido')  # UID opcional
                    
                    # Atualizar os dados globais de BPM e UID
                    smartwatch_data['bpm'] = bpm
                    smartwatch_data['uid'] = uid
                    bpm_list.append(bpm)

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

# Função para iniciar o monitoramento de BPM em segundo plano
def iniciar_monitoramento_smartwatch():
    monitoramento_thread = threading.Thread(target=monitorar_bpm)
    monitoramento_thread.daemon = True
    monitoramento_thread.start()

# Rota para os dados do smartwatch (BPM e UID)
@app.route('/api/get_smartwatch_dados', methods=['GET'])
def get_smartwatch_dados():
    return jsonify(smartwatch_data)

# Rota para os dados do circuito de sensores
@app.route('/api/get_sensor_dados', methods=['GET'])
def get_sensor_dados():
    return jsonify(sensor_data)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/funcionario/<nome>')
def funcionario(nome):
    return render_template('funcionario.html', nome=nome)


@app.route('/perfil')
def perfil():
    return render_template('perfil.html')

@app.route('/user')
def user():
    return render_template('user_funcionario.html')

@app.route('/admin')
def admin():
    return render_template('admin-dashboard.html')

@app.route('/circuito')
def circuito():
    return render_template('circuito.html')

@app.route('/termos')
def termos():
    return render_template('termos_de_servico.html')

@app.route('/privacidade')
def privacidade():
    return render_template('politica_privacidade.html')

@app.route('/visao_computacional')
def visao_computacional():
    return render_template('visao-computacional.html')

@app.route('/api/dados', methods=['POST'])
def receber_dados():
    global sensor_data
    data = request.get_json()
    sensor_data["temperature"] = data.get('temperature')
    sensor_data["humidity"] = data.get('humidity')
    sensor_data["ldr_value"] = data.get('ldr_value')

    print(f"Dados recebidos: Temp={sensor_data['temperature']}°C, Umidade={sensor_data['humidity']}%, Luminosidade={sensor_data['ldr_value']}")

    return jsonify({"status": "sucesso", "dados_recebidos": data})

@app.route('/api/get_dados', methods=['GET'])
def get_dados():
    return jsonify(sensor_data)

@app.route('/atualizar_tabela')
def atualizar_tabela():
    with open('dados_sensores.csv', 'r') as file:
        reader = csv.DictReader(file)
        dados = list(reader)[-1]  

@app.route('/download')
def download_file():
    caminho_arquivo = 'dados_sensores.csv' 
    return send_file(caminho_arquivo, as_attachment=True)

@app.route('/dados')
def dados():
    # Carregar o modelo treinado
    modelo = joblib.load('modelo.pkl')

    # Recriar o LabelEncoder com os dados do dataset
    file_path = './dataset_estresse_variante.csv'
    data = pd.read_csv(file_path)

    # Codificar a coluna 'nivel_estresse'
    label_encoder = LabelEncoder()
    label_encoder.fit(data['nivel_estresse'])

    # Carregar os novos dados para prever
    novo_dado = pd.read_csv('./dados_predicao.csv')

    # Fazer a previsão com o modelo carregado
    previsao_novo_dado = modelo.predict(novo_dado)

    # Decodificar a previsão
    nivel_estresse_previsto = label_encoder.inverse_transform(previsao_novo_dado)[0]

    # Criar um dicionário com os resultados
    resultados = {
        "previsao_nivel_estresse": nivel_estresse_previsto,
        "media_batimentos": novo_dado['media_batimentos'].tolist(),
        "menor_batimento": novo_dado['menor_batimento'].tolist(),
        "maior_batimento": novo_dado['maior_batimento'].tolist(),
        "pressao_menor_min": novo_dado['pressao_menor_min'].tolist(),
        "pressao_maior_min": novo_dado['pressao_maior_min'].tolist()
    }

    return jsonify(resultados)

# Renomeie a função para evitar conflito de nomes
@app.route('/api/dados', methods=['POST'])
def receber_bpm_uid():
    data = request.get_json()
    bpm = data.get('BPM')
    uid = data.get('UID')

    print(f"BPM: {bpm}, UID: {uid}")

    # Aqui você pode salvar os dados em um banco de dados ou processar como necessário
    return jsonify({"status": "sucesso", "BPM": bpm, "UID": uid})


if __name__ == '__main__':
    iniciar_monitoramento_smartwatch()
    app.run(debug=True)