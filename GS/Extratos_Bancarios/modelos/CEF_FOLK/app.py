import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os

def selecionar_arquivo():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="Selecione o arquivo Excel ou CSV",
        filetypes=[("Arquivos Excel/CSV", "*.xls *.xlsx *.csv")]
    )

def extrair_e_salvar_colunas(caminho_arquivo):
    extensao = os.path.splitext(caminho_arquivo)[1].lower()

    try:
        if extensao == '.csv':
            df = pd.read_csv(caminho_arquivo, header=1)
        elif extensao in ['.xls', '.xlsx']:
            df = pd.read_excel(caminho_arquivo, header=1)
        else:
            print("Formato de arquivo não suportado.")
            return

        if 'Data Lançamento' not in df.columns or 'Saldo' not in df.columns:
            print("As colunas 'Data Lançamento' e 'Saldo' devem estar presentes.")
            return

        df = df[['Data Lançamento', 'Saldo']].rename(columns={'Data Lançamento': 'Data'})

        df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Data'])

        df['Data'] = df['Data'].dt.date

        df_final = df.sort_values('Data').groupby('Data', as_index=False).last()

        df_final['Data'] = df_final['Data'].apply(lambda x: x.strftime("%d/%m/%Y"))

        novo_caminho = os.path.join(os.path.dirname(caminho_arquivo), 'dados_extraidos.xlsx')
        df_final.to_excel(novo_caminho, index=False)

        print(f"Arquivo salvo com sucesso em: {novo_caminho}")

    except Exception as e:
        print("Erro ao processar o arquivo:", e)

if __name__ == "__main__":
    caminho = selecionar_arquivo()
    if caminho:
        extrair_e_salvar_colunas(caminho)
