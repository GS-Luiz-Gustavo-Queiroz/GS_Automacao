from typing import Dict
import pandas as pd
import sys
import os
import re
# Adiciona a raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from configs.utils import dict_to_df, get_text_from_pdf


def e_data(data: str) -> bool: 
  
    padrao_data = r'\b\d{2}/\d{2} '
    return bool(re.match(padrao_data, data))

def formatar_saldo(saldo: str) -> str:
    saldo_formatado = saldo.replace('.', '')
    saldo_formatado = saldo_formatado.replace(',','.')
    saldo_formatado = [char for char in saldo_formatado if char.isnumeric() or char == '.']
    saldo_formatado = ''.join(saldo_formatado)
    return saldo_formatado

def sicoob_js_adm(path: str) -> pd.DataFrame:
    pages = get_text_from_pdf(path)
    registros = {}
    for page in pages:
        for row in page:
            if e_data(row):
                data: str = row.split()[0]
                saldo: str = row.split()[-1]
                saldo = formatar_saldo(saldo)
                if data not in registros.keys():
                    registros[data] = saldo

    df = dict_to_df(registros)
    return df
                            

