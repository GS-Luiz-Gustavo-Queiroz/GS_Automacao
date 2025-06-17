import pdfplumber
import re
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
import os
import unicodedata

def select_pdf_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Selecione o arquivo PDF",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )
    root.destroy()
    return file_path

def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return ''.join(c for c in texto if c.isalnum() or c.isspace()).strip().lower()

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%d/%m/%Y")
    except ValueError:
        return None

def extract_info_from_pdf(pdf_path):
    data = []
    collecting_data = False

    date_pattern = r"\d{2}/\d{2}/\d{4}"
    value_pattern = r"[-]?\d{1,3}(?:\.\d{3})*,\d{2}"

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            lines = text.split("\n")
            for line in lines:
                line_normalized = normalizar_texto(line)
                
                # Ativa a coleta de dados ao encontrar "saldo"
                if "saldo" in line_normalized:
                    collecting_data = True
                    continue
                
                # Para de coletar se encontrar um novo cabeçalho ou fim de seção (ajustável)
                if collecting_data and ("total" in line_normalized or "resumo" in line_normalized):
                    collecting_data = False
                    continue
                
                if collecting_data:
                    date_match = re.search(date_pattern, line)
                    if date_match:
                        date = parse_date(date_match.group())
                    else:
                        date = None

                    value_matches = re.findall(value_pattern, line)
                    if value_matches:
                        for balance in value_matches:
                            balance_clean = balance.replace(".", "").replace(",", ".")
                            try:
                                saldo_float = float(balance_clean)
                                if date:  # Só adiciona se houver uma data válida na mesma linha
                                    data.append({
                                        "Data": date,
                                        "Saldo": saldo_float
                                    })
                            except ValueError:
                                continue

    return data

def create_excel(data, output_path):
    df = pd.DataFrame(data, columns=["Data", "Saldo"])
    df = df.dropna(subset=["Data", "Saldo"])  # Remove linhas com valores ausentes
    df.to_excel(output_path, index=False, engine="openpyxl")
    print(f"Planilha salva em: {output_path}")

def main():
    pdf_path = select_pdf_file()
    if not pdf_path:
        print("Nenhum arquivo selecionado.")
        return

    output_path = os.path.splitext(pdf_path)[0] + "_extraido.xlsx"

    try:
        extracted_data = extract_info_from_pdf(pdf_path)
        create_excel(extracted_data, output_path)
    except FileNotFoundError:
        print(f"Arquivo {pdf_path} não encontrado. Verifique o caminho.")
    except Exception as e:
        print(f"Erro: {str(e)}")

if __name__ == "__main__":
    main()