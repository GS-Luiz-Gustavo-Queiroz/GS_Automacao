import pandas as pd
import sys
import os
# Adiciona a raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from configs.utils import dict_to_df


def eh_data(data: str) -> bool:
    return (len(str(data)) == 10) and \
        (data[:2] + data[3:5] + data[6:]).isnumeric() and \
        (data[2] + data[5] == '//')


def banestes(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df.columns = ['Data', '1', '2', 'Valor']
    registros = {}
    for i, row in df.iterrows():
        data = row['Data']
        if eh_data(data):
            registros[data] = row['Valor']
    df = dict_to_df(registros)
    return df
