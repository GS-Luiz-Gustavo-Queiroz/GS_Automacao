from typing import List, Dict
import pandas as pd
import sys
import os
# Adiciona a raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from configs.utils import dict_to_df, get_text_from_pdf


def eh_data(data: str) -> bool:
    """Verifica se uma string representa uma data no formato DD/MM/YYYY."""
    return (len(data) == 10) and ([data[2], data[5]] == ['/', '/']) \
           and ((data[:2]+data[3:5]+data[6:]).isnumeric())


def eh_registro(row: str) -> bool:
    """Verifica se uma linha segue o padrão dos registros de transação"""
    # Cada linha de registro, começa com uma data e termina com ' C' ou 'D'.
    return eh_data(row.split()[0]) and (row.endswith(' C') or row.endswith(' D'))


def bb_condoprest(path: str) -> pd.DataFrame:
    pages: List[List[str]] = get_text_from_pdf(path)
    registros: Dict[str, str] = {}
    for page in pages:
        for i, row in enumerate(page):
            if eh_registro(row):
                data = row.split()[0]
                saldo = row.split()[-2]
                registros[data] = saldo

    df = dict_to_df(registros)
    return df
