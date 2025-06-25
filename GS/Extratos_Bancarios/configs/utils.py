from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from PyPDF2 import PdfReader
from typing import List, Dict
from .arquivo import Arquivo
from pathlib import Path
import pandas as pd
import os


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
    with open('configs/dir_grupos.txt', 'r', encoding='utf-8') as file:
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

# path = 'arquivo.xlsx'  """ou""" 'arquivo.xls'
# df = pd.read_excel(path)
#
# for index, row in df.iterrows():
#     print(f"Linha {index}: {row.to_dict()}")


#ler txt

# path = 'arquivo.txt'
#
# df = pd.read_csv(path, sep=';', encoding='utf-8') #sep: separa pelo ';'
#
# for index, row in df.iterrows():
#     print(f"Linha {index}: {row.to_dict()}")


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


def EXTRAIR_CSV(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=[0, 2], encoding='utf-8', sep=';')  
    df.columns = ['Data', 'Saldo']
    df = df.dropna(subset=['Data', 'Saldo'])
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce', format='%d/%m/%Y') 
    df = df.dropna(subset=['Data'])  
    df_ultimos = df.groupby(df['Data'].dt.date).tail(1)
    df_ultimos['Data'] = pd.to_datetime(df_ultimos['Data']).dt.strftime('%d/%m/%Y')  
    df_final = df_ultimos[['Data', 'Saldo']]
    return df_final

def salva_erros(erros: List[str]) -> None:
    if not erros:
        return
    with open('erros.txt', 'w') as file:
        for erro in erros:
            file.write(erro + '\n')



def salva_relatorio(row: List[List]):
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    SAMPLE_SPREADSHEET_ID = "15gGHm67_W5maIas-4_YPSzE6R5f_CNJGcza_BJFlNBk"  # Código da planilha
    SAMPLE_RANGE_NAME = "Página1!A{}:D1000"  # Intervalo que será lido
    creds = None
    if os.path.exists("configs/creds/token.json"):
        creds = Credentials.from_authorized_user_file("configs/creds/token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "configs/creds/client.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("configs/creds/token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME.format(2))
            .execute()
        )
        values = result.get("values", [])

        idx = 2 + len(values)

        result = (
            sheet.values()
            .update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME.format(idx),
                    valueInputOption='USER_ENTERED', body={"values": row})
            .execute()
        )

    except HttpError as err:
        print(err)
