from typing import Dict, List
from tqdm import tqdm
import pymssql
import os


def get_creds() -> Dict[str, str]:
    with open('configs/db.txt', 'r') as file:
        rows: List[str] = file.read().split('\n')
        rows: List[List[str]] = [row.split(' = ') for row in rows]
        creds = {chave: valor for chave, valor in rows}
    return creds


def get_data(creds) -> List[str]:
    try:
        # Cria a conexão.
        conn = pymssql.connect(server=creds['s'], user=creds['u'],
                               password=creds['p'], database=creds['d'])
        # Cria o cursor.
        cursor = conn.cursor()
        # Realiza a consulta da tabela da pedidos.
        cursor.execute("""WITH BASE AS (	
                SELECT
                    LAN.EMP_Codigo, LAN.EST_Codigo, LAN.CON_CODIGO
                FROM LAN
                UNION
                SELECT
                    TCF.EMP_Codigo, TCF.EST_Origem, TCF.CON_Origem
                FROM TCF
                UNION 
                SELECT
                    TCF.EMP_Codigo, TCF.EST_Destino, TCF.CON_Destino
                FROM TCF
            )
            SELECT
                CONCAT(EMP.CODIGO, ' - ', EMP.NOME) AS GRUPO,
                CONCAT(EST.CODIGO, ' - ', EST.NOME) AS ESTABELECIMENTO,
                CONCAT(CON.CODIGO, ' - ', CON.NOME) AS CONTA_FINANCEIRA
            FROM BASE
            LEFT JOIN EST
            ON
                EST.CODIGO = BASE.EST_CODIGO
                AND EST.EMP_CODIGO = BASE.EMP_CODIGO
            LEFT JOIN EMP
            ON
                EMP.CODIGO = BASE.EMP_CODIGO
            LEFT JOIN CON
            ON
                CON.CODIGO = BASE.CON_CODIGO
                AND CON.EMP_CODIGO = BASE.EMP_CODIGO
            WHERE EMP.CODIGO NOT IN ('0001', '0007', '0008', '0009', '0010', '0014', '0015', '0021', '0022', '0023', '0025');
            """)
        """
            Criação de uma lista que irá guardar os resultados da consulta, onde cada item do dicionário será
        um dicionário, com as chaves 'ped_codigo', que é o código do pedido, e 'path' que é o caminho até o arquivo
        referente ao pedido.
        """
        data = cursor.fetchall()
        pastas: List[str] = []
        # Formata o nome dos arquivos.
        for row in tqdm(data):
            row = ['GRUPOS'] + [item.translate(str.maketrans({'/': '', '\\': '', '|': ''})) for item in row]
            pasta = '/'.join(row)
            # Cria a pasta.
            os.makedirs(pasta, exist_ok=True)

        # Encerrando a conexão
        conn.close()
        cursor.close()

        return pastas
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")



if __name__ == '__main__':
    try:
        creds = get_creds()
        pastas = get_data(creds)
        for pasta in pastas: print(pasta)
    except Exception as e:
        print(e)
        input()
