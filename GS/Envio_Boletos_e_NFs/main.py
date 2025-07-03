import os
import re
import shutil
from PyPDF2 import PdfReader
from tqdm import tqdm
from typing import List, Optional, Dict
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd


class GerenciadorDocumentos:
    def __init__(self):
        self.base_dir = 'GS/envio_boletos_nfs/SINGULAR_FACILITIES_CE'
        self.boletos_dir = os.path.join(self.base_dir, 'BOLETOS')
        self.nfs_dir = os.path.join(self.base_dir, 'NOTAS FISCAIS')
        self.organizados_dir = 'GS/arquivos_organizados'

        self.CPF_PATTERN = r'\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11}'
        self.CNPJ_PATTERN = r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{14}'
        self.CNPJ_IGNORADO = "16707848000195"


        self.CNPJ_PARA_EMAIL = {}  
        self.CNPJ_PARA_DADOS = {}

        self.email_credenciais = self._ler_credenciais_email()
        self.carregar_dados_mes_cliente()


    def _ler_credenciais_email(self, arquivo=None) -> Dict[str, Optional[str]]:
        if arquivo is None:
            arquivo = os.path.join('GS', 'envio_boletos_nfs', 'readme.txt')

        credenciais = {'usuario': None, 'senha': None}

        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                for linha in f:
                    linha = linha.strip()
                    if not linha:
                        continue
                    if linha.lower().startswith('usuario'):
                        credenciais['usuario'] = linha.split('=')[1].strip()
                    elif linha.lower().startswith('senha'):
                        credenciais['senha'] = linha.split('=')[1].strip()
                    if credenciais['usuario'] and credenciais['senha']:
                        break
        except FileNotFoundError:
            print(f"\nErro: Arquivo {arquivo} não encontrado!")
        except Exception as e:
            print(f"\nErro ao ler o arquivo de credenciais: {e}")

        return credenciais

    def criar_diretorio(self, caminho: str) -> None:
        os.makedirs(caminho, exist_ok=True)

    def limpar_cnpj(self, cnpj: str) -> str:
        return re.sub(r'\D', '', cnpj)

    def limpar_cpf(self, cpf: str) -> str:
        return re.sub(r'\D', '', cpf)

    def extrair_texto_pdf(self, caminho_pdf: str) -> List[str]:
        if not os.path.exists(caminho_pdf):
            return []
        with open(caminho_pdf, 'rb') as arquivo:
            leitor = PdfReader(arquivo)
            primeira_pagina = leitor.pages[0]
            return primeira_pagina.extract_text().split('\n')

    def encontrar_documento_boleto(self, linhas_texto: List[str]) -> Optional[str]:
        cnpjs = []
        cpfs = []

        for linha in linhas_texto:
            if 'CNPJ:' in linha or 'CPF/CNPJ:' in linha:
                partes = linha.split()
                if partes:
                    doc_bruto = partes[-1]
                    doc_limpo = self.limpar_cnpj(doc_bruto)
                    if len(doc_limpo) == 14:
                        cnpjs.append(doc_limpo)
                    elif len(doc_limpo) == 11:
                        cpfs.append(doc_limpo)

            cpfs_encontrados = re.findall(self.CPF_PATTERN, linha)
            for cpf in cpfs_encontrados:
                cpfs.append(self.limpar_cpf(cpf))

        if cnpjs:
            return cnpjs[1] if len(cnpjs) >= 2 else cnpjs[0]
        elif cpfs:
            return cpfs[0]
        return None

    def encontrar_documentos_nf(self, texto: str) -> List[str]:
        documentos = []

        cnpjs = re.findall(self.CNPJ_PATTERN, texto)
        for cnpj in cnpjs:
            if cnpj != self.CNPJ_IGNORADO:
                documentos.append(self.limpar_cnpj(cnpj))

        cpfs = re.findall(self.CPF_PATTERN, texto)
        for cpf in cpfs:
            documentos.append(self.limpar_cpf(cpf))

        return documentos
    
    def organizar_boletos(self) -> None:
            destino = os.path.join(self.organizados_dir, 'Boletos_organizados')
            self.criar_diretorio(destino)
            arquivos = [f for f in os.listdir(self.boletos_dir) if f.lower().endswith('.pdf')]

            if not arquivos:
                print("\nNenhum arquivo PDF encontrado na pasta de boletos.")
                return

            print("\nOrganizando boletos por CNPJ/CPF...")
            for arquivo in tqdm(arquivos, desc='Processando boletos'):
                caminho_completo = os.path.join(self.boletos_dir, arquivo)
                linhas = self.extrair_texto_pdf(caminho_completo)
                documento = self.encontrar_documento_boleto(linhas)
                
                if not documento:
                    print(f"\nAtenção: Não foi possível identificar CNPJ/CPF no arquivo {arquivo}")
                    continue
                    
                pasta_documento = os.path.join(destino, documento)
                self.criar_diretorio(pasta_documento)
                shutil.copy2(caminho_completo, os.path.join(pasta_documento, arquivo))

    def organizar_nfs(self) -> None:
            destino = os.path.join(self.organizados_dir, 'nfs_organizados')
            self.criar_diretorio(destino)
            destino_sem_documento = os.path.join(destino, 'nfs sem documento')
            self.criar_diretorio(destino_sem_documento)
            arquivos = [f for f in os.listdir(self.nfs_dir) if f.lower().endswith('.pdf')]

            if not arquivos:
                print("\nNenhum arquivo PDF encontrado na pasta de NF-es.")
                return

            print("\nOrganizando NF-es por CNPJ/CPF...")
            for arquivo in tqdm(arquivos, desc='Processando NF-es'):
                caminho_completo = os.path.join(self.nfs_dir, arquivo)
                try:
                    with open(caminho_completo, 'rb') as f:
                        leitor = PdfReader(f)
                        texto = "".join([page.extract_text() or '' for page in leitor.pages])
                    
                    documentos = self.encontrar_documentos_nf(texto)
                    
                    if documentos:
                        documento_limpo = documentos[0]  
                        pasta_destino = os.path.join(destino, documento_limpo)
                        self.criar_diretorio(pasta_destino)
                        shutil.copy2(caminho_completo, os.path.join(pasta_destino, arquivo))
                    else:
                        shutil.copy2(caminho_completo, os.path.join(destino_sem_documento, arquivo))
                except Exception as e:
                    print(f"\nErro ao processar {arquivo}: {e}")
                    

    def mesclar_pastas(self) -> None:
        caminho_boletos = os.path.join(self.organizados_dir, 'Boletos_organizados')
        caminho_nfs = os.path.join(self.organizados_dir, 'nfs_organizados')
        caminho_destino = os.path.join(self.organizados_dir, 'Pastas_Mescladas')
        
        if not os.path.exists(caminho_boletos) or not os.path.exists(caminho_nfs):
            print("\nErro: Pastas de boletos ou NF-es organizadas não encontradas.")
            return
            
        self.criar_diretorio(caminho_destino)

        caminho_sem_documento = os.path.join(caminho_nfs, 'nfs sem documento')
        if os.path.exists(caminho_sem_documento):
            destino_sem_documento = os.path.join(caminho_destino, 'nfs sem documento')
            if os.path.exists(destino_sem_documento):
                shutil.rmtree(destino_sem_documento)
            shutil.copytree(caminho_sem_documento, destino_sem_documento)
            print("\nPasta 'nfs sem documento' copiada para destino.")

        pastas_boletos = set(os.listdir(caminho_boletos))
        pastas_nfs = set(os.listdir(caminho_nfs)) - {'nfs sem documento'}
        pastas_comuns = pastas_boletos & pastas_nfs
        
        if not pastas_comuns:
            print("\nNenhuma pasta com documento correspondente encontrada.")
            return

        print(f"\nMesclando {len(pastas_comuns)} pastas com documento correspondente...")
        for pasta in tqdm(pastas_comuns, desc='Mesclando pastas'):
            pasta_destino = os.path.join(caminho_destino, pasta)
            self.criar_diretorio(pasta_destino)
            
            for origem in [os.path.join(caminho_boletos, pasta), os.path.join(caminho_nfs, pasta)]:
                for item in os.listdir(origem):
                    shutil.copy2(os.path.join(origem, item), pasta_destino)

    def carregar_dados_mes_cliente(self, caminho='GS/envio_boletos_nfs/emails.teste.xlsx') -> None:
        if not os.path.exists(caminho):
            print(f"\nAviso: Planilha de dados não encontrada em: {caminho}")
            return

        try:
            df = pd.read_excel(caminho, dtype={'CNPJ': str})
            df['CNPJ'] = df['CNPJ'].str.strip().str.replace(r'\D', '', regex=True)
            df['Mês/Ano'] = df['Mês/Ano'].astype(str).str.strip()
            df['CLIENTE'] = df['CLIENTE'].astype(str).str.strip()
            df['destinatario'] = df['destinatario'].astype(str).str.strip()

            df_formatado = pd.DataFrame(columns=df.columns)
            for _, row in df.iterrows():
                emails = row['destinatario'].split(',')
                if len(emails) == 1:
                    df_formatado.loc[len(df_formatado)] = row
                else:
                    for email in emails:
                        nova_linha = row.copy()
                        nova_linha['destinatario'] = email.strip()
                        df_formatado.loc[len(df_formatado)] = nova_linha

            for _, linha in df_formatado.iterrows():
                cnpj = linha['CNPJ']
                mes_ano = linha['Mês/Ano']
                cliente = linha['CLIENTE']
                email = linha['destinatario']

                if cnpj and mes_ano and cliente and email:
                    self.CNPJ_PARA_DADOS[cnpj] = (mes_ano, cliente)
                    if cnpj not in self.CNPJ_PARA_EMAIL:
                        self.CNPJ_PARA_EMAIL[cnpj] = []
                    self.CNPJ_PARA_EMAIL[cnpj].append(email)

            print(f"\n{len(self.CNPJ_PARA_DADOS)} registros de Mês/Ano e CLIENTE carregados da planilha.")
        except Exception as e:
            print(f"\nErro ao carregar planilha de dados: {e}")

    def separar_enviados_nao_enviados(self, enviados: List[str]) -> None:
        destino_base = os.path.join(self.organizados_dir, 'Pastas_Separadas')   
        enviados_dir = os.path.join(destino_base, 'enviados')
        nao_enviados_dir = os.path.join(destino_base, 'nao_enviados')

        self.criar_diretorio(enviados_dir)
        self.criar_diretorio(nao_enviados_dir)

        caminho_origem = os.path.join(self.organizados_dir, 'Pastas_Mescladas')
        todas_pastas = [
            pasta for pasta in os.listdir(caminho_origem)
            if os.path.isdir(os.path.join(caminho_origem, pasta)) and pasta != 'nfs sem documento'
        ]

        for pasta in todas_pastas:
            origem = os.path.join(caminho_origem, pasta)
            destino = os.path.join(enviados_dir if pasta in enviados else nao_enviados_dir, pasta)
            shutil.copytree(origem, destino)
        
        print(f"\nPastas separadas em:\n - Enviados: {enviados_dir}\n - Não enviados: {nao_enviados_dir}")



    def enviar_emails(self) -> bool:
        enviados_ids = []
        if not self.email_credenciais['usuario'] or not self.email_credenciais['senha']:
            print("\nErro: Credenciais de email não configuradas corretamente.")
            return False

        pasta_base = os.path.join(self.organizados_dir, 'Pastas_Mescladas')
        if not os.path.exists(pasta_base):
            print(f"\nErro: Pasta base '{pasta_base}' não encontrada!")
            return False

        subpastas = [d for d in os.listdir(pasta_base) if os.path.isdir(os.path.join(pasta_base, d)) and d != 'nfs sem documento']
        if not subpastas:
            print("\nErro: Nenhuma subpasta encontrada na pasta base!")
            return False

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_credenciais['usuario'], self.email_credenciais['senha'])
        except Exception as e:
            print(f"\nErro ao conectar ao servidor SMTP: {e}")
            return False

        enviados = 0
        print("\nIniciando envio de emails...")

        for documento in tqdm(subpastas, desc="Enviando emails", unit="documento"):
            if len(documento) == 14 and documento in self.CNPJ_PARA_EMAIL:
                destinatario = self.CNPJ_PARA_EMAIL[documento]
            else:
                print(f"\nAviso: Documento {documento} não tem e-mail definido - pulando...")
                continue

            mes_ano, cliente = self.CNPJ_PARA_DADOS.get(documento, ("Data não disponível", "Cliente não disponível"))

            pasta_documento = os.path.join(pasta_base, documento)
            arquivos = [f for f in os.listdir(pasta_documento) if os.path.isfile(os.path.join(pasta_documento, f))]

            if not arquivos:
                print(f"\nAviso: Pasta {documento} está vazia - pulando...")
                continue

            msg = MIMEMultipart()
            msg['From'] = self.email_credenciais['usuario']
            msg['To'] = ', '.join(destinatario)
            msg['Subject'] = f"Faturamento {cliente} - {mes_ano}"

            corpo = f"""
Prezados (as),

Anexo o faturamento da competência {mes_ano}. Por favor confirmar o recebimento.

Atenciosamente,
Sistema Automático de envio de Faturamento"""
            msg.attach(MIMEText(corpo, 'plain'))

            anexos_com_sucesso = 0
            for arquivo in arquivos:
                caminho_completo = os.path.join(pasta_documento, arquivo)   
                try:
                    with open(caminho_completo, "rb") as anexo:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(anexo.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename="{arquivo}"')
                        msg.attach(part)
                    anexos_com_sucesso += 1
                except Exception as e:
                    print(f"\nErro ao anexar {arquivo}: {e}")

            if anexos_com_sucesso == 0:
                print(f"\nAviso: Nenhum arquivo válido em {documento} - pulando envio...")
                continue

            try:
                server.sendmail(self.email_credenciais['usuario'], destinatario, msg.as_string())
                print(f"\nEmail enviado para {destinatario} (Documento: {documento})")
                enviados_ids.append(documento)
                enviados += 1
            except Exception as e:
                print(f"\nFalha ao enviar email para {destinatario}: {e}")

        server.quit()
        print(f"\nTotal de emails enviados com sucesso: {enviados}")
        self.separar_enviados_nao_enviados(enviados_ids)
        return enviados > 0


    def executar(self) -> None:
        print("\n=== INÍCIO DO PROCESSAMENTO ===")
        print("\n Organizando boletos...")
        self.organizar_boletos()
        print("\n Organizando NF-es...")
        self.organizar_nfs()
        print("\n Mesclando pastas com documento correspondente...")
        self.mesclar_pastas()
        print("\n Enviando emails para CNPJs mapeados...")
        if self.CNPJ_PARA_EMAIL:
            self.enviar_emails()
        else:
            print("\nAviso: Nenhum CNPJ mapeado para envio de emails.")
        print("\n=== PROCESSAMENTO CONCLUÍDO ===")
        print(f"Resultados disponíveis em: {os.path.abspath(self.organizados_dir)}")


if __name__ == "__main__":
    gerenciador = GerenciadorDocumentos()
    gerenciador.executar()
