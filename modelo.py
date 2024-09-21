import pandas as pd
from sklearn.preprocessing import LabelEncoder
import joblib

# Carregar o modelo treinado
modelo = joblib.load('modelo.pkl')

# Recriar o LabelEncoder com os dados do dataset (você precisará do dataset novamente)
file_path = './dataset_estresse_variante.csv'
data = pd.read_csv(file_path)

# Codificar a coluna 'nivel_estresse'
label_encoder = LabelEncoder()
label_encoder.fit(data['nivel_estresse'])

# Carregar os novos dados para prever
novo_dado = pd.read_csv('./dados_predicao.csv')

# Garantir que as colunas correspondam ao formato de treinamento
# No caso da pressão, os valores devem estar no mesmo formato que no treinamento (por exemplo, '120/85')
# Verifique se o arquivo CSV de previsão contém as colunas: media_batimentos, menor_batimento, maior_batimento, pressao_menor, pressao_maior

# Fazer a previsão com o modelo carregado
previsao_novo_dado = modelo.predict(novo_dado)

# Decodificar a previsão
nivel_estresse_previsto = label_encoder.inverse_transform(previsao_novo_dado)[0]
print("\nNível de estresse previsto para o novo dado:", nivel_estresse_previsto)

# Alerta preventivo
if nivel_estresse_previsto == "Alto":
    print("Alerta: Funcionário está se aproximando de níveis de estresse críticos. Sugerir medidas preventivas.")
