import pandas as pd

def ITAU_VISION(path: str) -> list[dict]:
    df = pd.read_excel(path, skiprows=9, usecols=[0, 4]) #skiprows: linhas que devem ser puladas, usecols: colunas que devem ser usadas.
    df.columns = ['Data', 'Saldo']
    df = df.dropna(subset=['Data', 'Saldo'])
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce', format='%d/%m/%Y').dropna()
    df = df.sort_values(by='Data')
    df_ultimos = df.groupby(df['Data'].dt.date).tail(1)
    df_ultimos['Data'] = pd.to_datetime(df_ultimos['Data']).dt.strftime('%d/%m/%Y')
    return df_ultimos[['Data', 'Saldo']]

