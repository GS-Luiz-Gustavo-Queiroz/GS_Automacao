try:
    from configs.processa_arquivos import processa_arquivos
    from configs.utils import get_grupos_dir
    from configs.arquivo import Arquivo
    from configs.atualizar_pastas import atualizar_pastas, get_creds
    from tqdm import tqdm
    import pandas as pd
    import os
    import warnings
    warnings.simplefilter("ignore", UserWarning)
    warnings.simplefilter(action='ignore', category=FutureWarning)
except Exception as e:
    print(e)
    input()


def main() -> None:
    atualizar_pastas(get_creds())
    # Caminho para a pasta 'GRUPOS'.
    path = get_grupos_dir()
    if not os.path.exists(path):
        raise Exception('Caminho para a pasta "GRUPOS" não encontrado.')

    df = processa_arquivos(path)
    df.to_excel('Arquivos_formatados.xlsx', index=False)



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        input()
