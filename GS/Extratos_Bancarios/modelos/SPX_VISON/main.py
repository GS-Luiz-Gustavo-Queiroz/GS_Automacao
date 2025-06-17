from typing import List
import pandas as pd
import sys
import os
# Adiciona a raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from configs.utils import data_to_excel, get_text_from_pdf


def eh_registro(row: str) -> bool:
    """Verifica se uma linha segue o padrão dos registros de transação"""
    # Cada linha de registro, começa com um código numérico da transação e termina com ' C'.
    return row[0].isnumeric() and row.endswith(' C')


def spx_vision(path: str) -> None:
    pages: List[List[str]] = get_text_from_pdf(path)
    registros: List[List[str]] = []

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

            registros.append([data, saldo])
            print([data, saldo])

    data_to_excel(registros, path)
