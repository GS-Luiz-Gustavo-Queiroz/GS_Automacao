import pandas as pd
import tkinter as tk
from tkinter import filedialog
import unicodedata
import os

def selecionar_arquivo():
    root = tk.Tk()
    root.update()
    root.withdraw()
    caminho = filedialog.askopenfilename(
        title="Selecione o arquivo",
        filetypes=[("Arquivos Excel/CSV/TXT", "*.xlsx *.xls *.csv *.txt"), ("Todos os arquivos", "*.*")]
    )
    root.destroy()
    return caminho

def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return ''.join(c for c in texto if c.isalnum() or c.isspace()).strip().lower()

def detectar_delimitador(arquivo):
    with open(arquivo, 'r', encoding='latin1') as f:
        linha = f.readline()
        for sep in [',', ';', '\t', '|']:
            if sep in linha:
                return sep
    return ','

def carregar_dados_com_linha_2_como_cabecalho(arquivo):
    ext = arquivo.lower().split('.')[-1]
    if ext in ['xls', 'xlsx']:
        return pd.read_excel(arquivo, header=1)
    elif ext in ['csv', 'txt']:
        sep = detectar_delimitador(arquivo)
        return pd.read_csv(arquivo, sep=sep, encoding='latin1', header=1, on_bad_lines='skip')
    else:
        raise ValueError("Formato de arquivo não suportado")

def extrair_colunas_data_saldo(df):
    col_data = col_saldo = None
    for col in df.columns:
        nome_normalizado = normalizar_texto(col)
        if 'data' in nome_normalizado and col_data is None:
            col_data = col
        if 'saldo' in nome_normalizado and col_saldo is None:
            col_saldo = col
    if not col_data or not col_saldo:
        raise ValueError("Colunas 'data' e 'saldo' não encontradas na linha 2.")
    
    df_filtrado = df[[col_data, col_saldo]].copy()
    
    # Converter a coluna 'saldo' para numérico, garantindo que seja uma Series
    df_filtrado[col_saldo] = pd.to_numeric(df_filtrado[col_saldo], errors='coerce')
    
    # Remover linhas com valores NaN na coluna 'saldo'
    df_filtrado = df_filtrado.dropna(subset=[col_saldo])
    
    return df_filtrado

def salvar_arquivo_saida(df_filtrado, caminho_origem):
    base, _ = os.path.splitext(caminho_origem)
    caminho_saida = f"{base}_data_e_saldo.xlsx"
    df_filtrado.to_excel(caminho_saida, index=False)
    print(f"\n✔ Arquivo gerado: {caminho_saida}")

def main():
    caminho = selecionar_arquivo()
    if not caminho:
        print("Nenhum arquivo selecionado.")
        return
    try:
        df = carregar_dados_com_linha_2_como_cabecalho(caminho)
        df_filtrado = extrair_colunas_data_saldo(df)
        salvar_arquivo_saida(df_filtrado, caminho)
    except Exception as e:
        print(f"\n Erro: {e}")

if __name__ == "__main__":
    main()