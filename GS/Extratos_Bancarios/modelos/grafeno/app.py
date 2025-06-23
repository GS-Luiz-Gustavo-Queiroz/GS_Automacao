import pandas as pd
import os

dir = os.listdir()


def abrir_excel():
    try:
        df = pd.read_excel('modelos/GRAFENO/HITEC 37 - ABRIL (EXTRATO GRAFENO).xlsx')
        return df
    except FileNotFoundError:
        print(f'arquivo nao encontrado ')
        return None
    except Exception as e:
        print (f'erro ao abrir o arquivo: {e}')
        return None
    

caminho = 'modelos/GRAFENO/HITEC 37 - ABRIL (EXTRATO GRAFENO).xlsx'
dados = abrir_excel(caminho)

if dados is not None:
    print(dados.head())