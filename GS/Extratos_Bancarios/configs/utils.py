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
