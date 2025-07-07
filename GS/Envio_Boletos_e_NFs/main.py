from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from tkinter import filedialog
from PyPDF2 import PdfReader
from email import encoders
from tqdm import tqdm
from PIL import Image
import tkinter as tk
import pandas as pd
import pytesseract
import numpy as np
import cv2 as cv
import openpyxl 
import smtplib
import shutil
import fitz
import time
import os
import re

class GerenciadorDocumentos:
    def __init__(self):
        self.base_dir = self.selecionar_pasta_base()
        if not self.base_dir:
            print("\nNenhuma pasta selecionada. Encerrando o programa.")
            exit(1)

        self.boletos_dir = os.path.join(self.base_dir, 'BOLETOS')
        self.nfs_dir = os.path.join(self.base_dir, 'NOTAS FISCAIS')
        self.organizados_dir = os.path.join(self.base_dir, 'arquivos_organizados')

        self.CPF_PATTERN = r'\d{3}\.\d{3}\.\d{3}-\d{2}'
        self.CNPJ_PATTERN = r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'
        self.CNPJS_IGNORADOS = {"16707848000195", "16707848000519", "40226542000100", "16./07.848/0001-19"}

        self.CNPJ_PARA_EMAIL = {}  
        self.CNPJ_PARA_DADOS = {}

        self.email_credenciais = self._ler_credenciais_email()
        self.carregar_dados_mes_cliente()

    def selecionar_pasta_base(self) -> Optional[str]:
        root = tk.Tk()
        root.withdraw()
        caminho = filedialog.askdirectory(title="Selecione a pasta base contendo as subpastas (BOLETOS, NOTAS FISCAIS, etc.)")
        root.destroy()
        return caminho

    def _ler_credenciais_email(self, arquivo=None) -> Dict[str, Optional[str]]:
        if arquivo is None:
            arquivo = os.path.join('GS', 'Envio_Boletos_e_NFs', 'readme.txt')

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

    def extrair_cnpj_por_crop_ocr(self, caminho_pdf: str, pagina: int = 0) -> Optional[str]:
        """
        Realiza OCR em uma área fixa do PDF onde o CNPJ costuma estar localizado.
        Retorna o CNPJ com apenas os números.
        """
        try:
            doc = fitz.open(caminho_pdf)
            page = doc.load_page(pagina)
            pix = page.get_pixmap(dpi=300)
            temp_img_path = 'temp_crop_ocr.jpg'
            pix.save(temp_img_path)
            doc.close()

            image = Image.open(temp_img_path)
            cnpj_crop = image.crop((77, 232, 170, 245))
            cnpj_crop_path = "cnpj_crop.jpg"
            cnpj_crop.save(cnpj_crop_path)
            os.remove(temp_img_path)

            img = cv.imread(cnpj_crop_path)
            if img is None:
                print(f"Erro ao abrir imagem para OCR: {cnpj_crop_path}")
                return None
            img = cv.resize(img, (img.shape[1]*2, img.shape[0]*2), interpolation=cv.INTER_LANCZOS4)
            img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            _, img = cv.threshold(img, 150, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

            texto = pytesseract.image_to_string(img, config='--psm 10')
            os.remove(cnpj_crop_path)

            cnpj = re.sub(r'\D', '', texto)
            return cnpj if len(cnpj) == 14 else None

        except Exception as e:
            print(f"\nErro ao extrair CNPJ por coordenada OCR: {e}")
            return None
        
    def extrair_cnpj_boleto_por_imagem(self, caminho_pdf: str, pagina: int = 0) -> Optional[str]:
        
        try:
            doc = fitz.open(caminho_pdf)
            page = doc.load_page(pagina)
            pix = page.get_pixmap()
            temp_img_path = 'temp_boleto.jpg'
            pix.save(temp_img_path)
            doc.close()

            image = Image.open(temp_img_path)
            cnpj_crop = image.crop((175, 720, 400, 740))  
            cnpj_crop_path = 'temp_boleto_crop.jpg'
            cnpj_crop.save(cnpj_crop_path)
            os.remove(temp_img_path)

            img = cv.imread(cnpj_crop_path)
            if img is None:
                print(f"Erro ao abrir imagem para OCR (boleto): {cnpj_crop_path}")
                return None

            scale_percent = 300
            new_width = int(img.shape[1] * scale_percent / 100)
            new_height = int(img.shape[0] * scale_percent / 100)
            img = cv.resize(img, (new_width, new_height), interpolation=cv.INTER_LANCZOS4)
            img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

            texto = pytesseract.image_to_string(img, config='--psm 10')
            os.remove(cnpj_crop_path)

            cnpj = re.sub(r'\D', '', texto)
            return cnpj  


        except Exception as e:
            print(f"\nErro ao extrair CNPJ por imagem do boleto: {e}")
            return None

    def extrair_texto_pdf(self, caminho_pdf: str) -> List[str]:
        try:
            with open(caminho_pdf, 'rb') as f:
                leitor = PdfReader(f)
                texto_completo = ""
                for pagina in leitor.pages:
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto_completo += texto_pagina + "\n"
                linhas = texto_completo.splitlines()
                return linhas
        except Exception as e:
            print(f"\nErro ao extrair texto do PDF {caminho_pdf}: {e}")
            return []

    def limpar_cnpj(self, cnpj: str) -> str:
        return re.sub(r'\D', '', cnpj)

    def limpar_cpf(self, cpf: str) -> str:
        return re.sub(r'\D', '', cpf)

    def encontrar_documento_boleto(self, linhas_texto: List[str]) -> Optional[str]:
        cnpjs = []
        cpfs = []

        for linha in linhas_texto:
            encontrados = re.findall(self.CNPJ_PATTERN, linha)
            for cnpj in encontrados:
                cnpj_limpo = self.limpar_cnpj(cnpj)
                if cnpj_limpo not in self.CNPJS_IGNORADOS:
                    cnpjs.append(cnpj_limpo)

            encontrados_cpfs = re.findall(self.CPF_PATTERN, linha)
            for cpf in encontrados_cpfs:
                cpfs.append(self.limpar_cpf(cpf))

        if len(cnpjs) >= 2:
            return cnpjs[1]
        elif len(cnpjs) == 1:
            return cnpjs[0]
        elif cpfs:
            return cpfs[0]
        return None


    def encontrar_documentos_nf(self, texto: str) -> List[str]:
        documentos = []

        cnpjs = re.findall(self.CNPJ_PATTERN, texto)
        for cnpj in cnpjs:
            cnpj_limpo = self.limpar_cnpj(cnpj)
            if cnpj_limpo not in self.CNPJS_IGNORADOS:
                documentos.append(cnpj_limpo)

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
                    documento = self.extrair_cnpj_boleto_por_imagem(caminho_completo)
                
                if not documento:
                    print(f"\nAtenção: Não foi possível identificar CNPJ/CPF no arquivo {arquivo}")
                    continue
                    
                pasta_documento = os.path.join(destino, documento)
                self.criar_diretorio(pasta_documento)
                shutil.copy2(caminho_completo, os.path.join(pasta_documento, arquivo))

    def organizar_nfs(self) -> None:
            destino = os.path.join(self.organizados_dir, 'nfs_organizados')
            self.criar_diretorio(destino)
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
                        
                    if not documentos:
                        cnpj_crop = self.extrair_cnpj_por_crop_ocr(caminho_completo)
                        if cnpj_crop and cnpj_crop not in self.CNPJS_IGNORADOS:
                            documentos = [cnpj_crop] 

                    if documentos:
                        documento_limpo = documentos[0]  
                        pasta_destino = os.path.join(destino, documento_limpo)
                        self.criar_diretorio(pasta_destino)
                        shutil.copy2(caminho_completo, os.path.join(pasta_destino, arquivo))
                    else:
                        shutil.copy2(caminho_completo, os.path.join(arquivo))
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

    def carregar_dados_mes_cliente(self, caminho='GS/Envio_Boletos_e_NFs/emails.teste.xlsx') -> None:
        if not os.path.exists(caminho):
            print(f"\nAviso: Planilha de dados não encontrada em: {caminho}")
            return

        try:
            df = pd.read_excel(caminho, dtype={'CNPJ': str})
            df['CNPJ'] = df['CNPJ'].str.strip().str.replace(r'\D', '', regex=True)
            df['Mês/Ano'] = df['Mês/Ano'].astype(str).str.strip()
            df['CLIENTE'] = df['CLIENTE'].astype(str).str.strip()
            df['DESTINATARIO'] = df['DESTINATARIO'].astype(str).str.strip()

            df_formatado = pd.DataFrame(columns=df.columns)
            for _, row in df.iterrows():
                emails = row['DESTINATARIO'].split(',')
                if len(emails) == 1:
                    df_formatado.loc[len(df_formatado)] = row
                else:
                    for email in emails:
                        nova_linha = row.copy()
                        nova_linha['DESTINATARIO'] = email.strip()
                        df_formatado.loc[len(df_formatado)] = nova_linha

            for _, linha in df_formatado.iterrows():
                cnpj = linha['CNPJ']
                mes_ano = linha['Mês/Ano']
                cliente = linha['CLIENTE']
                email = linha['DESTINATARIO']

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

            if os.path.exists(destino):
                shutil.rmtree(destino)
            
            shutil.copytree(origem, destino)

        print(f"\nPastas separadas em:\n - Enviados: {enviados_dir}\n - Não enviados: {nao_enviados_dir}")

    def calcular_porcentagem_nfs_enviadas(self) -> None:
        import pandas as pd

        base_separadas = os.path.join(self.organizados_dir, 'Pastas_Separadas')
        enviados_dir = os.path.join(base_separadas, 'enviados')
        nao_enviados_dir = os.path.join(base_separadas, 'nao_enviados')

        def contar_pdfs_nfs_em_pasta(pasta_base: str) -> int:
            total = 0
            if not os.path.exists(pasta_base):
                return 0
            for documento in os.listdir(pasta_base):
                caminho_doc = os.path.join(pasta_base, documento)
                if os.path.isdir(caminho_doc):
                    arquivos_pdf = [f for f in os.listdir(caminho_doc) if f.lower().endswith('.pdf')]
                    total += len(arquivos_pdf)
            return total

        enviados_nfs = contar_pdfs_nfs_em_pasta(enviados_dir)
        nao_enviados_nfs = contar_pdfs_nfs_em_pasta(nao_enviados_dir)
        total_nfs = enviados_nfs + nao_enviados_nfs

        if total_nfs == 0:
            print("\nNenhum arquivo PDF encontrado nas pastas enviados e não enviados para cálculo.")
            return

        pct_enviados = (enviados_nfs / total_nfs) * 100
        pct_nao_enviados = (nao_enviados_nfs / total_nfs) * 100

        df_resumo = pd.DataFrame({
            'Status': ['Enviados', 'Não Enviados', 'Total'],
            'Quantidade': [enviados_nfs, nao_enviados_nfs, total_nfs],
            'Porcentagem (%)': [round(pct_enviados, 2), round(pct_nao_enviados, 2), 100.0]
        })

        arquivo_saida = os.path.join(os.getcwd(), 'GS/envio_boletos_nfs/resumo_nf_enviadas.xlsx')
        try:
            df_resumo.to_excel(arquivo_saida, index=False)
            print(f"\nResumo de NFs enviadas e não enviadas salvo em: {arquivo_saida}")
        except Exception as e:
            print(f"\nErro ao salvar o arquivo Excel: {e}")


    def enviar_emails(self) -> List[str]:
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
        self.calcular_porcentagem_nfs_enviadas()
        return enviados_ids
    
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

            if os.path.exists(destino):
                shutil.rmtree(destino)
            
            shutil.copytree(origem, destino)

        print(f"\nPastas separadas em:\n - Enviados: {enviados_dir}\n - Não enviados: {nao_enviados_dir}")

    def calcular_porcentagem_nfs_enviadas(self) -> None:
        import pandas as pd

        base_separadas = os.path.join(self.organizados_dir, 'Pastas_Separadas')
        enviados_dir = os.path.join(base_separadas, 'enviados')
        nao_enviados_dir = os.path.join(base_separadas, 'nao_enviados')

        def contar_pdfs_nfs_em_pasta(pasta_base: str) -> int:
            total = 0
            if not os.path.exists(pasta_base):
                return 0
            for documento in os.listdir(pasta_base):
                caminho_doc = os.path.join(pasta_base, documento)
                if os.path.isdir(caminho_doc):
                    arquivos_pdf = [f for f in os.listdir(caminho_doc) if f.lower().endswith('.pdf')]
                    total += len(arquivos_pdf)
            return total

        enviados_nfs = contar_pdfs_nfs_em_pasta(enviados_dir)
        nao_enviados_nfs = contar_pdfs_nfs_em_pasta(nao_enviados_dir)
        total_nfs = enviados_nfs + nao_enviados_nfs

        if total_nfs == 0:
            print("\nNenhum arquivo PDF encontrado nas pastas enviados e não enviados para cálculo.")
            return

        pct_enviados = (enviados_nfs / total_nfs) * 100
        pct_nao_enviados = (nao_enviados_nfs / total_nfs) * 100

        df_resumo = pd.DataFrame({
            'Status': ['Enviados', 'Não Enviados', 'Total'],
            'Quantidade': [enviados_nfs, nao_enviados_nfs, total_nfs],
            'Porcentagem (%)': [round(pct_enviados, 2), round(pct_nao_enviados, 2), 100.0]
        })

        arquivo_saida = os.path.join(os.getcwd(), 'GS/envio_boletos_nfs/resumo_nf_enviadas.xlsx')
        try:
            df_resumo.to_excel(arquivo_saida, index=False)
            print(f"\nResumo de NFs enviadas e não enviadas salvo em: {arquivo_saida}")
        except Exception as e:
            print(f"\nErro ao salvar o arquivo Excel: {e}")
    
    

    def criar_diretorio(self, caminho: str) -> None:
        if not os.path.exists(caminho):
            os.makedirs(caminho)

    def executar(self) -> None:
        print("\n=== INÍCIO DO PROCESSAMENTO ===")
        inicio = time.time()
        print("\n Organizando boletos...")
        self.organizar_boletos()
        print("\n Organizando NF-es...")
        self.organizar_nfs()
        print("\n Mesclando pastas com documento correspondente...")
        self.mesclar_pastas()
        print("\n Enviando emails para CNPJs mapeados...")
        enviados_ids = []
        if self.CNPJ_PARA_EMAIL:
           enviados_ids = self.enviar_emails()
        if enviados_ids:
            self.nfs_enviadas = len(enviados_ids)
            self.nfs_nao_enviadas = len([
                doc for doc in os.listdir(os.path.join(self.organizados_dir, 'Pastas_Separadas', 'nao_enviados'))
                if os.path.isdir(os.path.join(self.organizados_dir, 'Pastas_Separadas', 'nao_enviados', doc))])

        else:
            print("\nAviso: Nenhum CNPJ mapeado para envio de emails.")

        

        print("\n=== PROCESSAMENTO CONCLUÍDO ===")
        print(f"Resultados disponíveis em: {os.path.abspath(self.organizados_dir)}")

if __name__ == "__main__":
    gerenciador = GerenciadorDocumentos()
    gerenciador.executar()
