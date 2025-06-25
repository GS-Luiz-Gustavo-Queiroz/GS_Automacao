from typing import List
import pandas as pd
import sys
import os
# Adiciona a raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from configs.utils import dict_to_df, get_text_from_pdf


def eh_registro(row: str) -> bool:
    """Verifica se uma linha segue o padrão dos registros de transação"""
    # Cada linha de registro, começa com um código numérico da transação e termina com ' C'.
    return row[0].isnumeric() and row.endswith(' C')


def SPX_VISION(path: str) -> pd.DataFrame:
    pages: List[List[str]] = get_text_from_pdf(path)
    registros = {}

    for page in pages:
        for row in page:
            if not eh_registro(row):
                continue
            row = row.split()
            # Encontra a data.
            for i in row[::-1]:
                if '/' in i:
                    data = i[-10:]
                    break
            else:
                raise Exception(f'Data não encontrada em {path}.')
            # Encontra e formata o saldo.
            saldo = row[-2][1:]
            saldo = saldo.translate(str.maketrans({'.': '', ',': '.'}))
            saldo = saldo.replace('.', ',')

            registros[data] = saldo

    df = dict_to_df(registros)
    return df
