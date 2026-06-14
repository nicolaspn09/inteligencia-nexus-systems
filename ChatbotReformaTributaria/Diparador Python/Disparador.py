import csv
import json
import requests
import time
import os

print(f"########################################")
print(f"######### DISPARADOR CURSODEV ##########")
print(f"########################################")

# Solicita ao usuário as informações necessárias
url = input("Digite a URL da API: ")
api_key = input("Digite a API Key: ")
intervalo_de_espera = int(input("Digite o intervalo de espera entre mensagens (em segundos): "))
mensagem_file_name = "mensagem.txt"  # Nome do arquivo na pasta raiz

# Constrói o caminho completo para o arquivo de texto
script_directory = os.path.dirname(os.path.abspath(__file__))
mensagem_file_path = os.path.join(script_directory, mensagem_file_name)

# Verifica a existência do arquivo de texto
if not os.path.isfile(mensagem_file_path):
    print(f"Arquivo de texto '{mensagem_file_path}' não encontrado.")
    exit()

# Lê o conteúdo do arquivo de texto para a variável mensagem
with open(mensagem_file_path, 'r', encoding='utf-8') as mensagem_file:
    mensagem = mensagem_file.read()

# Dados do cabeçalho (headers)
headers = {
    "Content-Type": "application/json",
    "apikey": api_key
}

# Caminho relativo para o arquivo CSV (no mesmo diretório)
csv_file_path = "numeros.csv"

# Verifica a existência do arquivo CSV
try:
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)

        # Exibe mensagem inicial
        input("Tudo certo, agora precione enter para enviar as mensagens.")

        # Loop para ler cada linha do arquivo CSV
        for row in reader:
            # O número de telefone está na primeira coluna do CSV
            phoneNumber = row[0]

            # Dados do corpo da requisição (body)
            postData = {
                "number": '55{}'.format(phoneNumber),
                "textMessage": {
                    "text": mensagem
                }
            }

            # Converte os dados em JSON
            postDataJson = json.dumps(postData)

            # Define as opções da requisição
            headers["Content-Length"] = str(len(postDataJson))

            try:
                # Executa a requisição e obtém a resposta
                response = requests.post(url, data=postDataJson, headers=headers)
                response.raise_for_status()

                # Add delay para enviar próxima mensagem
                time.sleep(intervalo_de_espera)

            except requests.exceptions.HTTPError as errh:
                print(f"HTTP Error: {errh}")
            except requests.exceptions.ConnectionError as errc:
                print(f"Error Connecting: {errc}")
            except requests.exceptions.Timeout as errt:
                print(f"Timeout Error: {errt}")
            except requests.exceptions.RequestException as err:
                print(f"Request Error: {err}")

        # Exibe mensagem de sucesso
        print("######################################")
        print("### MENSAGENS ENVIADAS COM SUCESSO ###")
        print("######################################")

except FileNotFoundError:
    print(f"Arquivo CSV '{csv_file_path}' não encontrado.")
except Exception as e:
    print(f"Erro durante a execução do script: {str(e)}")
