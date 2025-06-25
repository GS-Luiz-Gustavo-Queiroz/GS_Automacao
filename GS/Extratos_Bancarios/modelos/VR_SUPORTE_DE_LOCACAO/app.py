import pandas as pd


def VR_SUPORTE(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=[0, 2], encoding='utf-8', sep=';')  
    df.columns = ['Data', 'Saldo']
    df = df.dropna(subset=['Data', 'Saldo'])
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce', format='%d/%m/%Y') 
    df = df.dropna(subset=['Data'])  
    df_ultimos = df.groupby(df['Data'].dt.date).tail(1)
    df_ultimos['Data'] = pd.to_datetime(df_ultimos['Data']).dt.strftime('%d/%m/%Y')  
    df_final = df_ultimos[['Data', 'Saldo']]
    return df_final