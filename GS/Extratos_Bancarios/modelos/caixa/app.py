import pandas as pd

def CAIXA(caminho_arquivo: str) -> pd.DataFrame:
    df = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8')
    df['Data_Mov'] = pd.to_datetime(df['Data_Mov'], format='%Y%m%d')
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')

    df['Valor'] = df.apply(lambda row: row['Valor'] if row['Deb_Cred'] == 'C' else -row['Valor'], axis=1)
    df['Data'] = df['Data_Mov'].dt.strftime('%d/%m/%Y')

    df_saldo = df.groupby('Data')['Valor'].sum().reset_index()
    df_saldo = df_saldo.rename(columns={'Valor': 'Saldo'})
    df = df_saldo
    return df


