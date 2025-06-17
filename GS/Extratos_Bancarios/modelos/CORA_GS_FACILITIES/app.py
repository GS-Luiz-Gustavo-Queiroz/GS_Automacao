import pdfplumber
import pandas as pd
import re
import os

def extrair_dados_do_pdf(caminho_pdf):
    dados = []

    padrao_data = re.compile(r'\b\d{2}/\d{2}/\d{4}\b')
    padrao_saldo = re.compile(r'(?i)saldo[^\d\-]*([-]?\d[\d.,]*)')
    palavra_chave = re.compile(r'transações', re.IGNORECASE)

    comecar_a_extrair = False

    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if not texto:
                continue

            if not comecar_a_extrair:
                match = palavra_chave.search(texto)
                if match:
                    comecar_a_extrair = True
                    texto = texto[match.end():]
                else:
                    continue

            datas = padrao_data.findall(texto)
            saldos = padrao_saldo.findall(texto)

            for i in range(min(len(datas), len(saldos))):
                data = datas[i]
                saldo = saldos[i].replace('.', '').replace(',', '.')
                try:
                    saldo = float(saldo)
                except ValueError:
                    continue
                dados.append({'Data': data, 'Saldo': saldo})

    return dados

def salvar_em_excel(dados, caminho_pdf):
    if not dados:
        print("Nenhum dado foi extraído.")
        return

    df = pd.DataFrame(dados)
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Data'])
    df['Data'] = df['Data'].dt.strftime("%d/%m/%Y")

    caminho_excel = os.path.join(os.path.dirname(caminho_pdf), "dados_extraidos_do_pdf.xlsx")
    df.to_excel(caminho_excel, index=False)
    print(f"\nArquivo salvo com sucesso em: {caminho_excel}")

def CORA_GS_FACILITIES(path: str):
    if os.path.isfile(path):
        print(f"\nArquivo PDF recebido: {path}")
        dados_extraidos = extrair_dados_do_pdf(path)
        salvar_em_excel(dados_extraidos, path)
    else:
        print(f"Arquivo não encontrado: {path}")
