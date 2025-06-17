from typing import List
import pandas as pd


def is_registro(row: str) -> bool:
    ...

def hitec_37_spx(path: str) -> None:
    # Lê a planilha e salva apenas as colunas 2 e 4.
    df = pd.read_html(path)[0][[2, 4]]
    data: List[List[str]] = df.values
    print(df)



hitec_37_spx(path='HITEC 37 - ABRIL (EXTRATO SPX).xls')