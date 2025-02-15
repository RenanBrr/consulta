import os
os.environ['PYTHONWARNINGS'] = 'ignore'

import warnings
warnings.filterwarnings('ignore', category=Warning)
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import csv
import glob

app = Flask(__name__, static_folder='static')
CORS(app)

# Desativa logs do Flask
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

# Configuração padrão para leitura dos arquivos
CONFIG_PADRAO = {
    'delimiter': ';',
    'quoting': csv.QUOTE_ALL,
    'encoding': 'latin1'
}

# Dicionário para armazenar os DataFrames
dfs = {}

print("\nCarregando dados...")

# Diretório base onde estão as pastas dos estados
base_dir = "SUPER LISTA"

# Lista todos os arquivos CSV em todas as pastas
for arquivo_csv in glob.glob(os.path.join(base_dir, "**/*.csv"), recursive=True):
    try:
        # Extrai o estado do nome do diretório pai
        estado = os.path.basename(os.path.dirname(arquivo_csv)).split('-')[0].upper()
        
        print(f"Carregando arquivo: {arquivo_csv}")
        
        df = pd.read_csv(
            arquivo_csv,
            delimiter=CONFIG_PADRAO['delimiter'],
            encoding=CONFIG_PADRAO['encoding'],
            dtype=str,
            quoting=CONFIG_PADRAO['quoting']
        )
        
        # Remove espaços em branco e aspas dos campos relevantes
        colunas = ['CEP', 'NUM_LOGRADOURO', 'VIABILIDADE', 'LOGRADOURO', 'BAIRRO', 'MUNICIPIO', 'UF']
        for coluna in colunas:
            if coluna in df.columns:
                df[coluna] = df[coluna].str.strip().str.replace('"', '')
        
        if 'COMPLEMENTO' in df.columns:
            df['COMPLEMENTO'] = df['COMPLEMENTO'].str.strip().str.replace('"', '')
        
        # Se já existe um DataFrame para este estado, concatena com o novo
        if estado in dfs:
            dfs[estado] = pd.concat([dfs[estado], df], ignore_index=True)
            # Remove duplicatas se houver
            dfs[estado] = dfs[estado].drop_duplicates(subset=['CEP', 'NUM_LOGRADOURO'], keep='last')
        else:
            dfs[estado] = df
        
        print(f"Estado {estado}: {len(df):,} registros carregados do arquivo {os.path.basename(arquivo_csv)}")
        
    except Exception as e:
        print(f"ERRO ao carregar arquivo {arquivo_csv}: {str(e)}")
        continue

# Imprime resumo final
for estado, df in dfs.items():
    print(f"\nEstado {estado}: Total de {len(df):,} registros")

print(f"\nTotal de estados carregados: {len(dfs)}")
print("\nServidor iniciado em http://127.0.0.1:5000")

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/consulta', methods=['POST'])
def consulta_viabilidade():
    data = request.json
    estado = data.get("estado", "").strip().upper()
    cep = data.get("cep", "").strip()
    numero = data.get("numero", "").strip()
    
    if estado not in dfs:
        return jsonify({
            "viavel": False,
            "mensagem": f"Estado {estado} não configurado no sistema"
        })
    
    df = dfs[estado]
    
    # Primeiro verifica se o CEP existe
    enderecos_cep = df[df['CEP'] == cep].copy()
    
    if enderecos_cep.empty:
        return jsonify({
            "viavel": False,
            "mensagem": f"O CEP {cep} Não Possui Viabilidade"
        })
    
    # Se número não foi fornecido, retorna todos os endereços do CEP
    if not numero:
        # Converte NUM_LOGRADOURO para número para ordenação correta
        enderecos_cep['NUM_LOGRADOURO_INT'] = pd.to_numeric(enderecos_cep['NUM_LOGRADOURO'], errors='coerce')
        enderecos_cep = enderecos_cep.sort_values('NUM_LOGRADOURO_INT')
        
        enderecos_lista = []
        for _, row in enderecos_cep.iterrows():
            complemento = ""
            if 'COMPLEMENTO' in row and pd.notna(row['COMPLEMENTO']) and row['COMPLEMENTO'].strip():
                complemento = f", {row['COMPLEMENTO']}"
            
            endereco = f"{row['LOGRADOURO']}, {row['NUM_LOGRADOURO']}{complemento}, {row['BAIRRO']}, {row['MUNICIPIO']} {row['UF']}"
            enderecos_lista.append(endereco)
        
        return jsonify({
            "viavel": True,
            "tem_superlista": True,
            "enderecos": enderecos_lista
        })
    
    # Se número foi fornecido, busca o endereço específico
    resultado = enderecos_cep[enderecos_cep['NUM_LOGRADOURO'] == numero]
    
    if not resultado.empty:
        viavel = resultado.iloc[0]['VIABILIDADE'] == "1"
        
        if viavel:
            complemento = ""
            if 'COMPLEMENTO' in resultado.iloc[0] and pd.notna(resultado.iloc[0]['COMPLEMENTO']) and resultado.iloc[0]['COMPLEMENTO'].strip():
                complemento = f", {resultado.iloc[0]['COMPLEMENTO']}"
            
            endereco = f"{resultado.iloc[0]['LOGRADOURO']}, Número {resultado.iloc[0]['NUM_LOGRADOURO']}{complemento}, {resultado.iloc[0]['BAIRRO']}, {resultado.iloc[0]['MUNICIPIO']} {resultado.iloc[0]['UF']}, CEP {resultado.iloc[0]['CEP']}"
            
            return jsonify({
                "viavel": True,
                "tem_superlista": True,
                "endereco": endereco,
                "numero_invalido": False
            })
        else:
            return jsonify({
                "viavel": False,
                "mensagem": f"O CEP {cep} Não Possui Viabilidade"
            })
    else:
        return jsonify({
            "viavel": True,
            "tem_superlista": True,
            "numero_invalido": True,
            "mensagem": f"Fachada nº {numero} INVIÁVEL"
        })

if __name__ == "__main__":
    app.run(debug=False) 