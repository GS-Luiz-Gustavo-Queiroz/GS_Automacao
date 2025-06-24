from configs.utils import get_grupos_dir, processa_arquivos
from configs.arquivo import Arquivo
from tqdm import tqdm
import pandas as pd
import os


def main() -> None:
    # Caminho para a pasta 'GRUPOS'.
    path = get_grupos_dir()
    if not os.path.exists(path):
        raise Exception('Caminho para a pasta "GRUPOS" não encontrada.')

    path = 'C:\\Users\\Usuario\\OneDrive - KMF - CONSULTORIA EMPRESARIAL E TREINAMENTOS LTDA - ME\\Área de Trabalho\\bots'

    df = processa_arquivos(path)






if __name__ == "__main__":
    try:
        ...
        #main()
    except Exception as e:
        print(e)
        input()


df = pd.read_excel('empresas.xlsx')
l = df[2].unique()
df = pd.DataFrame(l)
df.to_excel('instituicoes_financeiras.xlsx', index=False)