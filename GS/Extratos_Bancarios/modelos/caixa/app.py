from typing import List, Dict
import pandas as pd
import sys
import os
# Adiciona a raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from configs.utils import dict_to_df, get_text_from_pdf, eh_data


def eh_registro(row: str) -> bool:
    """
    Verifica se a linha é um registro, ou seja, começa com uma data no formato dd/mm/AAAA, tem como
    penúltimo item um valor numérico e termina com 'C' ou 'D'.
    """
    try:
        result = eh_data(row.split()[0]) and (row.endswith('C') or row.endswith('D')) \
           and (row.split()[-2].translate(str.maketrans({',': '', '.': ''})).isnumeric())
    except Exception as e:
        return False
    return result

def caixa(path: str) -> pd.DataFrame:
    registros: Dict[str, str] = {}
    pages: List[List[str]] = get_text_from_pdf(path)
    for page in pages:
        for row in page:
            if eh_registro(row):
                data = row.split()[0]
                valor = row.split()[-2]
                registros[data] = valor
    df = dict_to_df(registros)
    return df
