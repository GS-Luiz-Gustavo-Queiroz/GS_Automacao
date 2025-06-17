from typing import Dict
import pandas as pd
import sys
import os
# Adiciona a raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from configs.utils import dict_to_df, eh_data

def bradesco_hisystem(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=';', encoding='latin1', header=1)
    registros: Dict[str, str] = {}
    for _, row in df.iterrows():
        data = row['Data']
        if eh_data(data):
            saldo = row['Saldo (R$)']
            registros[data] = saldo

    df = dict_to_df(registros)
    return df