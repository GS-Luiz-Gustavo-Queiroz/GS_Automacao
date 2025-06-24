from PyPDF2 import PdfReader
from typing import List, Dict
from .arquivo import Arquivo
from pathlib import Path
import pandas as pd
import os


def processa_arquivos(path: str) -> pd.DataFrame:
    df = pd.DataFrame()
    files = list_all_files([path])
    for file in files:
       arq = Arquivo(file)


def eh_data(data: str) -> bool:
    """Verifica se uma string representa uma data no formato DD/MM/YYYY."""
    if type(data) is not str:
        return False
    return (len(data) == 10) and ([data[2], data[5]] == ['/', '/']) \
           and ((data[:2]+data[3:5]+data[6:]).isnumeric())


def data_to_excel(data: List[List[str]], path: str) -> None:
    """
    Recebe uma lista de registros e a converte para um excel no padrão correto.
    Em data, os valores devem ser [data, saldo].
    :param data: Lista de registros.
    :param path: Caminho até o arquivo.
    """
    df = pd.DataFrame(data, columns=['Data', 'Saldo'])
    new_path = path[:path.rfind('/')+1] + 'formadato ' + ' '.join(path[path.rfind('/')+1:].split()[0:2]) + '.xlsx'
    df.to_excel(new_path, index=False)


def dict_to_df(data: Dict[str, str]) -> pd.DataFrame:
    """
    Recebe um dicionário onde cada chave é uma data, e cada valor é o saldo, e converte em um df.
    :param data: Dicionário de registros.
    :return: DataFrame com as chave e valores do dicionário.
    """
    df = pd.DataFrame(data.items(), columns=['Data', 'Saldo'])
    return df


def get_text_from_pdf(path: str) -> List[List[str]]:
    """
    Extrai o texto de um arquivo pdf.
    :param path: caminho do arquivo pdf.
    :return: Lista com o texto de cada página do pdf.
    """
    with open(path, 'rb') as file_bin:
        pdf = PdfReader(file_bin)
        rows: List[List[str]] = []
        for page in pdf.pages:
            new_rows: List[str] = page.extract_text().split('\n')
            rows.append(new_rows)
    return rows


def get_grupos_dir() -> str:
    """
    Retorna uma string com o caminho para a pasta 'GRUPOS'.
    """
    with open('configs/dir_grupos.txt', 'r') as file:
        path = file.read()
    return path


def list_all_files(paths: List[str] = None) -> List[str]:
    if paths is None:
        paths = ['.']
    all_files = []
    for base_path in paths:
        p = Path(base_path)
        if p.exists() and p.is_dir():
            all_files.extend([str(f) for f in p.rglob('*') if f.is_file()])
        elif p.is_file():
            all_files.append(str(p))
    return all_files

#funçao pra extrair data e saldo do excel

def Extrair_excel(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, skiprows=7, usecols=[0, 9]) #skiprows = pula a quantidade de linha, usecols = pega apenas as colunas.
    df.columns = ['Data', 'Saldo']
    df = df.dropna(subset=['Data', 'Saldo'])
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce', format='%d/%m/%Y').dropna() # verifica a formatação da data
    df_ultimos = df.groupby(df['Data'].dt.date).tail(1)
    df_ultimos['Data'] = pd.to_datetime(df_ultimos['Data']).dt.strftime('%d/%m/%Y') 
    return df_ultimos[['Data', 'Saldo']]

#função para ler a planilha excel

path = 'arquivo.xlsx'  """ou""" 'arquivo.xls'
df = pd.read_excel(path)

for index, row in df.iterrows():
    print(f"Linha {index}: {row.to_dict()}")


#ler txt

path = 'arquivo.txt'

df = pd.read_csv(path, sep=';', encoding='utf-8') #sep: separa pelo ';'

for index, row in df.iterrows():
    print(f"Linha {index}: {row.to_dict()}")


#função pra extrair txt

def EXTRAIR_TXT(caminho_arquivo: str) -> pd.DataFrame:
    df = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8')
    df['Data_Mov'] = pd.to_datetime(df['Data_Mov'], format='%Y%m%d')
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')

    df['Valor'] = df.apply(lambda row: row['Valor'] if row['Deb_Cred'] == 'C' else -row['Valor'], axis=1)
    df['Data'] = df['Data_Mov'].dt.strftime('%d/%m/%Y')

    df_saldo = df.groupby('Data')['Valor'].sum().reset_index()
    df_saldo = df_saldo.rename(columns={'Valor': 'Saldo'})
    df = df_saldo
    return df
