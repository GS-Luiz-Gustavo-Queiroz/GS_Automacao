import pandas as pd
import sys
import os
# Adiciona a raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from configs.utils import dict_to_df


def vr(path: str) -> pd.DataFrame:
    registros = {}
    df = pd.read_csv(path, sep=';')
    for _, row in df.iterrows():
        data = row['Data']
        if data not in registros.keys():
            registros['Data'] = row['Valor']
    df = dict_to_df(registros)
    return df
