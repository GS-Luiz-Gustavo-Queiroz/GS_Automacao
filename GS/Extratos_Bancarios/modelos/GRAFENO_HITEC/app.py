import pandas as pd

def GRAFENO_HITEC(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, skiprows=7, usecols=[0, 9])
    df.columns = ['Data', 'Saldo']
    df = df.dropna(subset=['Data', 'Saldo'])
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce', format='%d/%m/%Y').dropna()
    df = df.sort_values(by='Data')
    df_ultimos = df.groupby(df['Data'].dt.date).tail(1)
    df_ultimos['Data'] = pd.to_datetime(df_ultimos['Data']).dt.strftime('%d/%m/%Y')
    
    return df_ultimos[['Data', 'Saldo']]
