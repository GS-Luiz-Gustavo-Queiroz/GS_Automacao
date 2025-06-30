
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
    erros = []
    path = get_grupos_dir()
    if not os.path.exists(path):
        raise Exception('Caminho para a pasta "GRUPOS" não encontrado.')
    arquivos_processados = processa_arquivos(path)
    atualizar_pastas(get_creds(), path)
    print(path)
    files = list_all_files([path])
    print(files)
    data = datetime.now().strftime("%d/%m/%Y")
    exec_time = time.time() - st
    print(data)
    print(exec_time)
    if not os.path.exists('logs'):
        os.mkdir('logs')
    relatorio = ([[data, 'Extratos Bancários', 'Arquivos_formatados.xlsx', len(files), arquivos_processados, exec_time, erros]])
    print(relatorio)
    # salva_relatorio(relatorio)
    pd.DataFrame(relatorio, columns=['Data', 'Tipo', 'Arquivo', 'Qtd Arquivos', 'arquivos_processados', 'Tempo Execução', 'Erros']).to_excel(
    'logs/arquivos_processados.xlsx', index=False)
main()


# if __name__ == "__main__":
#     try:
#         main()
#     except Exception as e:
#         print(e)
#         input()
