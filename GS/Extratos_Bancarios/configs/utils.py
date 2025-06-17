from PyPDF2 import PdfReader
from typing import List, Dict
import pandas as pd
import os


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



