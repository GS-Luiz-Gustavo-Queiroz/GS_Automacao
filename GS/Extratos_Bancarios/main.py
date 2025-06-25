from configs.processa_arquivos import processa_arquivos
from configs.utils import get_grupos_dir
from configs.arquivo import Arquivo
from tqdm import tqdm
import pandas as pd
import os
import warnings
warnings.simplefilter("ignore", UserWarning)



def main() -> None:
    # Caminho para a pasta 'GRUPOS'.
    # path = get_grupos_dir()
    # if not os.path.exists(path):
    #     raise Exception('Caminho para a pasta "GRUPOS" não encontrada.')

    path = 'C:\\Users\\User132\\Downloads\\GRUPOS'

    df = processa_arquivos(path)
    df.to_excel('Arquivos_formatados.xlsx', index=False)



main()
# if __name__ == "__main__":
#     try:
#         main()
#     except Exception as e:
#         print(e)
#         input()
