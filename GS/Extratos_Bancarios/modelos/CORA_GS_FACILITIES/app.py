import re
from PyPDF2 import PdfReader
from typing import List, Tuple
import pandas as pd

def CORA_GS_FACILITIES(path: str) -> pd.DataFrame:
    padrao_data = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4})')
    padrao_valor = re.compile(r'(\d{1,3}(?:\.\d{3})*,\d{2})')

    dados_extraidos: List[Tuple[str, str]] = []

    with open(path, 'rb') as file_bin:
        pdf = PdfReader(file_bin)
        for page in pdf.pages:
            texto = page.extract_text()
            if texto:
                linhas = texto.split('\n')
                for linha in linhas:
                    match_data = padrao_data.match(linha)
                    match_valor = padrao_valor.search(linha)
                    if match_data and match_valor:
                        data = match_data.group(1)
                        valor = match_valor.group(1)
                        dados_extraidos.append((data, valor))

    df = pd.DataFrame(dados_extraidos, columns=['Data', 'Saldo'])
    return df
