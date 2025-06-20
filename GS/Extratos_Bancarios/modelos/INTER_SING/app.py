from typing import Dict
import pandas as pd
import sys
import os
# Adiciona a raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from configs.utils import dict_to_df


def inter_sing(path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=';', skiprows=4)
    # É verificado se a data já existe, pois neste arquivo, o saldo mais recente é o primeiro.
    registros: Dict[str, str] = {}
    for _, row in df.iterrows():
        data = row['Data Lançamento']
        saldo = row['Saldo']
        if data in registros.keys():
            continue
        registros[data] = saldo
    df = dict_to_df(registros)
    return df
