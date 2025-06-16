import pdfplumber
import pandas as pd
import re
import tkinter as tk
from tkinter import filedialog
import os

def selecionar_pdf():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="Selecione um arquivo PDF",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )

def extrair_primeira_data_saldo(caminho_pdf):
    padrao_data = re.compile(r'\b\d{2}/\d{2}/\d{4}\b')
    padrao_saldo = re.compile(r'Saldo[^0-9\-]*([-]?\d[\d.,]*)', re.IGNORECASE)

    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if not texto:
                continue

            data_match = padrao_data.search(texto)
            saldo_match = padrao_saldo.search(texto)

            if data_match and saldo_match:
                data = data_match.group(0)
                saldo_bruto = saldo_match.group(1).replace('.', '').replace(',', '.')
                try:
                    saldo = float(saldo_bruto)
                except ValueError:
                    saldo = None
                return data, saldo
    return None, None

def salvar_em_excel(data, saldo, caminho_pdf):
    if not data or saldo is None:
        print(" Não foi possível extrair data e saldo do PDF.")
        return

    df = pd.DataFrame({'Data': [data], 'Saldo': [saldo]})
    nome_base = os.path.splitext(os.path.basename(caminho_pdf))[0]
    saida = os.path.join(os.path.dirname(caminho_pdf), f"{nome_base}_data_saldo.xlsx")
    df.to_excel(saida, index=False)
    print(f" Planilha criada: {saida}")

def main():
    caminho = selecionar_pdf()
    if not caminho:
        print("Nenhum arquivo selecionado.")
        return

    data, saldo = extrair_primeira_data_saldo(caminho)
    salvar_em_excel(data, saldo, caminho)

if __name__ == "__main__":
    main()
