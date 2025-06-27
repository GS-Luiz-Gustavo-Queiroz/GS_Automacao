
from configs.processa_arquivos import processa_arquivos
from configs.utils import list_all_files, salva_erros, salva_relatorio
from configs.utils import get_grupos_dir
from configs.arquivo import Arquivo
from configs.atualizar_pastas import atualizar_pastas, get_creds
from datetime import datetime
from tqdm import tqdm
import pandas as pd
import time
import os
import warnings
warnings.simplefilter("ignore", UserWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)



def main() -> None:
    # Caminho para a pasta 'GRUPOS'.
    st = time.time()
    path = get_grupos_dir()
    atualizar_pastas(get_creds(), path)
    if not os.path.exists(path):
        raise Exception('Caminho para a pasta "GRUPOS" não encontrado.')
    files = list_all_files([path])
    data = datetime.now().strftime("%d/%m/%Y")
    exec_time = time.time() - st
    salva_relatorio([[data, 'Extratos Bancários', len(files), exec_time]])
    arquivos_processados = salva_relatorio
    df = processa_arquivos(path)
    df.to_excel('Arquivos_formatados.xlsx', index=False)
    if not os.path.exists('logs'):
        os.mkdir('logs')
    pd.DataFrame(arquivos_processados).to_excel('logs/arquivos_processados.xlsx', index=False)
    pd.DataFrame('logs/arquivos_encontrados.xlsx', index=False)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        input()
