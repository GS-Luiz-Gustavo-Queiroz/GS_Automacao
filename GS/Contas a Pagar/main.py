from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from typing import Dict, List
from datetime import datetime
from tqdm import tqdm
import pandas as pd
import openpyxl
import pymssql
import shutil
import psutil
import time
import os


class Aut:
    def __init__(self, dir_dest: str = 'Arquivos'):
        self.dir_dest = dir_dest
        self.creds: Dict[str, str] = self.get_creds()
        self.vencimento: str = self.get_vencimento()
        self.informes: List[str] = []
        self.df: pd.DataFrame = self.get_data()
        self.erros: List[List[str]] = []
        self.discos: List[str] = self.listar_discos()

    def get_creds(self) -> Dict[str, str]:
        with open('configs/db.txt', 'r') as file:
            rows: List[str] = file.read().split('\n')
            rows: List[List[str]] = [row.split(' = ') for row in rows]
            creds = {chave: valor for chave, valor in rows}
        return creds

    def get_vencimento(self) -> str:
        with open('configs/configuracoes.txt', 'r') as file:
            rows: List[str] = file.read().split('\n')
            rows: List[List[str]] = [row.split(' = ') for row in rows]
            creds = {chave: valor for chave, valor in rows}
        return creds['data_vencimento']

    def get_data(self) -> pd.DataFrame:
        try:
            # Cria a conexão.
            conn = pymssql.connect(server=self.creds['s'], user=self.creds['u'],
                                   password=self.creds['p'], database=self.creds['d'])
            # Cria o cursor.
            cursor = conn.cursor()
            # Realiza a consulta da tabela da pedidos.
            cursor.execute("""
                SELECT
                    EMP.Nome,
                    PED.EST_Codigo,
                    EST.Nome AS EST_Nome,
                    FRN.NOME AS FORNECEDOR,
                    EST.CNPJCPF AS CNPJ,
                    CASE
                        WHEN PED.STATUS = 2 THEN 'REJEITADO'
                        WHEN PED.STATUS = 1 THEN 'APROVADO'
                        WHEN PED.STATUS = 0 THEN 'AGUARDANDO APROVACAO'
                        ELSE 'OUTRO' 
                    END AS STATUS,
                    PED.[DATA] AS DT_PEDIDO,
                    CASE
                        WHEN VCP.[Data] IS NOT NULL
                            THEN VCP.[Data]
                        ELSE VCP_ENT.[Data]
                    END AS DT_VENCIMENTO,
                    DPE.[Path] AS CAMINHO_ARQUIVO,
                    PED.CondicaoPagamento AS CONDICAO_PAGAMENTO,
                    CPG.DOCUMENTO AS DOC,
                    CPG.ValorBruto AS VALOR_BRUTO,
                    PED.CODIGO AS CODIGO_PEDIDO,
                    CONCAT(CPG.Codigo, ENT.CPG_CODIGO) AS CODIGO_CONTAS_PAGAR,
                    CONCAT( VCP.Sequencial, VCP_ENT.Sequencial ) AS SEQUENCIAL_CONTAS_PAGAR,
                    PED.CampoExtra3 AS CONTAS_AVULSAS,
                    PED.CampoExtra2 AS FORMA_PAGAMENTO,
                    PED.CampoExtra1 AS NOTA,
                    PED.CampoExtra4 AS SETOR,
                    PED.CAMPOEXTRA6 AS TIPO,
                    CASE
                        WHEN ENT.CODIGO IS NOT NULL
                            THEN 'PEDIDO COM NOTA'
                        ELSE 'PEDIDO AVULSO'
                    END AS TIPO_PEDIDO    
                FROM PED	
                LEFT JOIN DPE 				 ON DPE.EMP_Codigo = PED.EMP_CODIGO 				AND DPE.PED_Codigo = PED.CODIGO
                LEFT JOIN CPG 				 ON CPG.EMP_Codigo = PED.EMP_CODIGO 				AND CPG.Codigo = PED.CPG_CODIGO
                LEFT JOIN VCP 				 ON VCP.EMP_Codigo = CPG.EMP_Codigo 				AND VCP.CPG_Codigo = CPG.Codigo
                LEFT JOIN EST 				 ON EST.EMP_Codigo = PED.EMP_Codigo 				AND EST.Codigo = PED.EST_Codigo
                LEFT JOIN EMP 				 ON EST.EMP_Codigo = EMP.Codigo
                LEFT JOIN ENT 				 ON ENT.EMP_Codigo = PED.EMP_CODIGO         AND ENT.PED_CODIGO = PED.CODIGO
                LEFT JOIN CPG CPG_ENT  ON CPG_ENT.EMP_CODIGO = ENT.EMP_CODIGO     AND CPG_ENT.CODIGO = ENT.CPG_CODIGO
                LEFT JOIN VCP VCP_ENT  ON VCP_ENT.EMP_Codigo = CPG_ENT.EMP_Codigo AND VCP_ENT.CPG_Codigo = CPG_ENT.Codigo
                LEFT JOIN FRN          ON PED.EMP_Codigo = FRN.EMP_Codigo			    AND PED.FRN_Codigo = FRN.Codigo;
                """)
            """
                Criação de uma lista que irá guardar os resultados da consulta, onde cada item do dicionário será
            um dicionário, com as chaves 'ped_codigo', que é o código do pedido, e 'path' que é o caminho até o arquivo
            referente ao pedido.
            """
            columns = ['Grupo', 'EST_Codigo', 'EST_nome', 'fornecedor', 'cnpj', 'status','dt_pedido', 'dt_vencimento', 'path', 'cond_pag', 'num_nota', 'valor', 'cod_ped', 'COD_cpg', 'sequencial', 'cont_avuls', 'form_pag', 'nota', 'setor', 'tipo', 'tipo_pedido']
            df = pd.DataFrame(cursor.fetchall(), columns=columns)
            # df.to_excel("todas_contas_a_pagar.xlsx", index=False)
            # filtra os dados com valores de vencimento igual ao especificado
            df = self.filtra_data(df)
            # Corrige a coluna dt_vencimento.
            df['dt_vencimento'] = df['dt_vencimento'].dt.strftime('%d-%m-%Y')
            # df.to_excel("contas_a_pagar_filtrados_data.xlsx", index=False)
            # Encerrando a conexão
            conn.close()
            cursor.close()

            #GERANDO LOG INFORMATIVO QUANTIDADE DE ARQUIVOS E QUANTIDADE DE PEDIDOS
            qtdd_arquivos = len(df['cod_ped'])
            qtdd_pedidos = len(df['cod_ped'].unique())

            # self.informes.append(f"Quantidade de pedidos: {qtdd_pedidos}")
            # self.informes.append(f"Quantidade de arquivos copiados: {qtdd_arquivos}")

            # print(f"Quantidade de pedidos: {qtdd_pedidos}")
            # print(f"Quantidade de arquivos a serem copiados: {qtdd_arquivos}")
            #FIM DO CODIGO DO LOG

            return df
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def listar_discos(self) -> List[str]:
        # Lista todos os discos e servidores disponíveis.
        return [part.mountpoint for part in psutil.disk_partitions(all=True)]

    def troca_disco(self, path: str, disco: str, ocorrencia: int) -> str:
        # Troca o nome do disco, ex: C:\\ para D:\\ no nome do arquivo.
        if ocorrencia == 2:
            path = path[path.find('\\')+1:]  # Remove o nome do disco.
        return disco + path[path.find('\\')+1:]

    def init_dir(self, diretorio: str) -> None:
        """Inicializa o diretório de destino dos arquivos."""
        if not os.path.exists(diretorio):
            os.mkdir(diretorio)

    def run(self) -> None:
        self.init_dir(self.dir_dest)  # Cria a pasta de destino dos arquivos.
        st = time.time()
        self.processa_arquivos()
        exec_time = time.time() - st  # Calcula o tempo de execução do código.
        data = datetime.now().strftime("%d/%m/%Y")
        values = [[data, 'Contas a Pagar', len(self.df), exec_time]]  # Valores para serem salvos no relatório.
        self.salva_relatorio(values)
        self.mostra_erros()
        # self.mostra_informes()

    def filtra_data(self, df: pd.DataFrame) -> pd.DataFrame:
        data = pd.to_datetime(self.vencimento, format="%d/%m/%Y")
        return df[df['dt_vencimento'] == data]

    def processa_arquivos(self) -> None:
        for _, row in tqdm(self.df.iterrows(), total=len(self.df)):
            path_orig: str = row['path']
            try:
                # Verifica se o arquivo existe em cada disco.
                all_possible_paths: List[str] = [path_orig] + \
                                                [self.troca_disco(path_orig, disco, 1) for disco in self.discos] + \
                                                [self.troca_disco(path_orig, disco, 2) for disco in self.discos]
                for path in all_possible_paths:
                    if not os.path.exists(path) or not os.path.isfile(path):
                        continue
                    grupo: str = row['Grupo']
                    estabelecimento: str = row['EST_nome']
                    vencimento: str = row['dt_vencimento']
                    cod_cpg: str = row['COD_cpg']
                    cnpj: str = row['cnpj']
                    data = self.vencimento.replace("/", "-")
                    valor = row['valor']
                    fornecedor = row['fornecedor']
                    num_nota = row['num_nota']

                    dir_grupo: str = f'{self.dir_dest}/{grupo}'
                    dir_est: str = f'{dir_grupo}/{estabelecimento} - {cnpj}'
                    dir_ven: str = f'{dir_est}/{vencimento}'
                    
                    # Verifica se já existe a pasta do grupo, estabelecimento e vencimento.
                    self.init_dir(dir_grupo)
                    self.init_dir(dir_est)
                    self.init_dir(dir_ven)

                    # Define o novo caminho do arquivo.
                    nome = path.split('\\')[-1]  # Acessa o nome do arquivo.
                    extensao = nome[nome.rfind('.'):]  # Acessa a extensão do arquivo.
                    nome = nome[:nome.rfind('.')]  # Remove a extensão do nome do arquivo.
                    # Define o nome junto do codigo do CPG, nome antigo e o vencimento.
                    # novo_nome = f'{cod_cpg} - {nome} - {vencimento}{extensao}'
                    novo_nome = f'{grupo} - R$ {valor} - {fornecedor} - {num_nota}{extensao}'.replace("/", "")
                    new_path = f'{dir_ven}/{novo_nome}'  # Junta o novo nome com o diretório de destino do vencimento.
                    new_path = os.path.join(new_path)
                    new_path = '\\\\?\\' + os.path.abspath(new_path)

                    try:
                        shutil.copy(path, new_path)
                        break
                    except FileNotFoundError:
                        # Pode ocorrer file not found error quando o nome do arquivo é muito grande.
                        # Então vai ser tentado apenas diminuir o tamanho do arquivo.
                        # O i cria um id para os arquivos, para não haver arquivos de mesmo nome.
                        i = len(os.listdir(dir_ven))
                        novo_nome = f'{dir_ven}/R$ {valor} - {fornecedor} - {num_nota}({i}){extensao}'.replace("/", "")
                        new_path = os.path.join(novo_nome)
                        new_path = '\\\\?\\' + os.path.abspath(new_path)
                        try:
                            shutil.copy(path, new_path)
                        except FileNotFoundError:
                            # Se o erro persistir, o arquivo será ignorado.
                            self.erros.append([path, new_path])
                    except PermissionError:
                        self.erros.append(['Permissão negada', path])

                else:
                    self.erros.append(['não encontrado', path_orig])
            except:
                pass

    def mostra_erros(self) -> None:
        if self.erros:
            with open('erros.txt', 'w') as file:
                for erro in self.erros:
                    file.write(f'{erro[0]} -> {erro[1]}\n')
            os.startfile('erros.txt')
        else:
            print('Sem erros ocorridos.')
        input('Digite enter para encerrar.')
    
    def mostra_informes(self) -> None: #EXIBE O LOG INFORMATIVO QUANTIDADE DE ARQUIVOS / QUANTIDADE DE PEDIDOS
        with open('informes.txt', 'w') as file:
            file.write(self.informes[0])
            file.write('\n')
            file.write(self.informes[1])
        os.startfile('informes.txt')

    def salva_relatorio(self, row: List[List]):
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        SAMPLE_SPREADSHEET_ID = "15gGHm67_W5maIas-4_YPSzE6R5f_CNJGcza_BJFlNBk"  # Código da planilha
        SAMPLE_RANGE_NAME = "Página1!A{}:D100000"  # Intervalo que será lido
        creds = None
        if os.path.exists("configs/token.json"):
            creds = Credentials.from_authorized_user_file("configs/token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "configs/client.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("configs/token.json", "w") as token:
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


if __name__ == '__main__':
    try:
        print("Aguarde alguns segundos...")
        aut = Aut()
        aut.run()
    except Exception as e:
        print(e)
        input()