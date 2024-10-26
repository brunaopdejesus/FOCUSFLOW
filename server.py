import csv
from flask import Flask, jsonify, render_template, request, send_file
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import time

app = Flask(__name__)

# Dados dos sensores do circuito
sensor_data = {
    "temperature": None,
    "humidity": None,
    "ldr_value": None
}

# Dados do smartwatch
smartwatch_dados = {
    "pulse": None,
    "myo": None,
    "status_funcionario": None
}

# Caminho para o arquivo CSV do smartwatch
csv_smartwatch_path = './dados_smartwatch.csv'

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

@app.route('/smartwatch')
def smartwatch():
    return render_template('smartwatch.html')

@app.route('/user_smartwatch')
def user_smartwatch():
    return render_template('user-smartwatch.html')

@app.route('/termos')
def termos():
    return render_template('termos_de_servico.html')

@app.route('/privacidade')
def privacidade():
    return render_template('politica_privacidade.html')

@app.route('/visao_computacional')
def visao_computacional():
    return render_template('visao-computacional.html')

# Rota para receber dados do circuito
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

@app.route('/api/smartwatch_dados', methods=['POST'])
def receber_dados_smartwatch():
    dados = request.json
    if 'pulse' in dados and 'status_funcionario' in dados and 'myo' in dados:
        smartwatch_dados['pulse'] = dados['pulse']
        smartwatch_dados['status_funcionario'] = dados['status_funcionario']
        smartwatch_dados['myo'] = dados['myo']
        
        # Salvar no CSV
        salvar_no_csv_smartwatch(dados['pulse'], dados['status_funcionario'], dados['myo'])
        
        return jsonify({'message': 'Dados recebidos com sucesso!'}), 200
    else:
        return jsonify({'error': 'Dados inválidos!'}), 400

@app.route('/api/smartwatch_get_dados', methods=['GET'])
def obter_dados_smartwatch():
    # Retorna os dados atuais do smartwatch
    return jsonify(smartwatch_dados), 200

@app.route('/download_smartwatch')
def download_smartwatch():
    return send_file(csv_smartwatch_path, as_attachment=True)

# Função para salvar dados do smartwatch no CSV
def salvar_no_csv_smartwatch(pulse, status_funcionario, myo):
    file_exists = os.path.isfile(csv_smartwatch_path)
    with open(csv_smartwatch_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['timestamp', 'pulse', 'status_funcionario', 'myo'])
        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), pulse, status_funcionario, myo])

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
    modelo = joblib.load('modelo.pkl')

    file_path = './dataset_estresse_variante.csv'
    data = pd.read_csv(file_path)

    label_encoder = LabelEncoder()
    label_encoder.fit(data['nivel_estresse'])

    novo_dado = pd.read_csv('./dados_predicao.csv')

    previsao_novo_dado = modelo.predict(novo_dado)

    nivel_estresse_previsto = label_encoder.inverse_transform(previsao_novo_dado)[0]

    resultados = {
        "previsao_nivel_estresse": nivel_estresse_previsto,
        "media_batimentos": novo_dado['media_batimentos'].tolist(),
        "menor_batimento": novo_dado['menor_batimento'].tolist(),
        "maior_batimento": novo_dado['maior_batimento'].tolist(),
        "pressao_menor_min": novo_dado['pressao_menor_min'].tolist(),
        "pressao_maior_min": novo_dado['pressao_maior_min'].tolist()
    }

    return jsonify(resultados)

if __name__ == '__main__':
    app.run(debug=True, port=5001)