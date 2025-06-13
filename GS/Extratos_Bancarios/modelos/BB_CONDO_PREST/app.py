import pdfplumber
import re
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
import os

def select_pdf_file():
    root = tk.Tk()
    root.withdraw()  
    file_path = filedialog.askopenfilename(
        title="Selecione o arquivo PDF",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )
    root.destroy()
    return file_path

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%d/%m/%Y")
    except ValueError:
        return None

def extract_info_from_pdf(pdf_path):
    data = []
    
    date_pattern = r"\d{2}/\d{2}/\d{4}"
    value_pattern = r"[-]?\d{1,3}(?:\.\d{3})*,\d{2}"
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
                
            lines = text.split("\n")
            for line in lines:
                date_match = re.search(date_pattern, line)
                if date_match:
                    date = parse_date(date_match.group())
                else:
                    date = None
                
                value_matches = re.findall(value_pattern, line)
                value = None
                balance = None
                
                if value_matches:
                    value = value_matches[0].replace(".", "").replace(",", ".")
                    if len(value_matches) > 1:
                        balance = value_matches[-1].replace(".", "").replace(",", ".")
                
                if date or value or balance:
                    data.append({
                        "Data": date,
                        "Valor": float(value) if value else None,
                        "Saldo": float(balance) if balance else None
                    })
    
    return data

def create_excel(data, output_path):
    df = pd.DataFrame(data, columns=["Data", "Valor", "Saldo"])
    
    # Remove linhas onde a coluna "Valor" é nula
    df = df.dropna(subset=["Valor"])
    
    # Remove linhas onde todas as colunas são nulas (opcional, mantido por consistência)
    df = df.dropna(how="all")
    
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