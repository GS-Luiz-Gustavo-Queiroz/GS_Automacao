import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os

def selecionar_arquivo():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="Selecione o arquivo",
        filetypes=[("Arquivos Excel/CSV", "*.xls *.xlsx *.csv")]
    )

def ler_arquivo(caminho):
    ext = os.path.splitext(caminho)[1].lower()

    if ext == ".csv":
        try:
            return pd.read_csv(caminho, header=9, encoding="utf-8", sep=None, engine="python")
        except:
            return pd.read_csv(caminho, header=9, encoding="utf-8", sep=";")
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(caminho, header=9)
    else:
        raise ValueError("Formato de arquivo não suportado")

def salvar_em_excel(df, caminho_origem):
    nome_base = os.path.splitext(os.path.basename(caminho_origem))[0]
    pasta = os.path.dirname(caminho_origem)
    saida = os.path.join(pasta, f"{nome_base}_data_saldo.xlsx")
    df.to_excel(saida, index=False)
    print(f"Planilha criada: {saida}")

def processar():
    caminho = selecionar_arquivo()
    if not caminho:
        print("Nenhum arquivo selecionado.")
        return

    try:
        df = ler_arquivo(caminho)

        colunas = df.columns.str.strip().str.lower()
        col_map = dict(zip(colunas, df.columns))

        col_data = next((col_map[c] for c in colunas if "data" in c), None)
        col_saldo = next((col_map[c] for c in colunas if "saldo" in c), None)

        if not col_data or not col_saldo:
            print("Colunas 'data' e 'saldo' não encontradas.")
            print(f"Colunas disponíveis: {list(df.columns)}")
            return

        df_final = df[[col_data, col_saldo]].copy()
        df_final.columns = ["Data", "Saldo"]

        df_final = df_final[df_final["Saldo"].notna() & (df_final["Saldo"] != "")]

        salvar_em_excel(df_final, caminho)

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    processar()
