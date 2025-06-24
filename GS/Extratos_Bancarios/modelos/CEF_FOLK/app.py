import pandas as pd


def CEF_FOLK(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, skiprows=2, usecols=[0, 5])
    df.columns = ['Data', 'Saldo']
    df = df.dropna(subset=['Data', 'Saldo'])
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce', format='%d/%m/%Y').dropna()
    df_ultimos = df.groupby(df['Data'].dt.date).tail(1)
    df_ultimos['Data'] = pd.to_datetime(df_ultimos['Data']).dt.strftime('%d/%m/%Y')
    df = df_ultimos
    return df
