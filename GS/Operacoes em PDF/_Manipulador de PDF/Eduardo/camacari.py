#CODIGO PARA MUDANCA DE NOME DAS NFS DE BALNEARIO CAMBURIU

from PyPDF2 import PdfReader
import re
import os
import shutil
from tqdm import tqdm

# pasta_blaneario_camburiu = os.getcwd()
# pasta_blaneario_camburiu = os.path.join(pasta_blaneario_camburiu, "BALNEARIO CAMBURIU")
# pasta_blaneario_camburiu = os.path.abspath(pasta_blaneario_camburiu)
# arquivos_pdf = os.listdir(pasta_blaneario_camburiu)

# for arquivo in tqdm(arquivos_pdf, total=len(arquivos_pdf)):

#     with open(f"BALNEARIO CAMBURIU/{arquivo}", "rb") as pdf_nota_fiscal:
#         #LEITURA DO TEXTO DO PDF
#         pdf_reader = PdfReader(pdf_nota_fiscal)
#         page = pdf_reader.pages[0]
#         text = page.extract_text()

#         #BUSCAR NUMERO DA NOTA
#         pos_inicial_nota = text.find("NFS-eNúmero da nota") + len("NFS-eNúmero da nota") + 1
#         pos_final_nota = text.find(" - E") + len(" - E")
#         num_nota = text[pos_inicial_nota:pos_final_nota]

#         #BUSCAR NOME TOMADOR DE SERVICOS
#         for razao_social in re.finditer("Nome/Razão Social: ", text):
#             pos_inicial_razao_social = razao_social.start()
#         pos_inicial_razao_social = pos_inicial_razao_social + len("Nome/Razão Social: ")


#         for razao_social in re.finditer("E-mail", text):
#             pos_final_razao_social = razao_social.start() - 1
        
#         razao_social = text[pos_inicial_razao_social:pos_final_razao_social]

#     try:
#         pasta_atual = os.getcwd()
#         caminho_arquivo = os.path.join(pasta_atual, "BALNEARIO CAMBURIU", arquivo)
#         caminho_arquivo = os.path.abspath(caminho_arquivo)
#         novo_nome = os.path.join(pasta_atual, "BALNEARIO CAMBURIU", f"{razao_social}_{num_nota}.pdf")
#         novo_nome = os.path.abspath(novo_nome)
#         shutil.copyfile(caminho_arquivo, novo_nome)
#         os.remove(caminho_arquivo)
#     except:
#         pass    

nome1 = "1.1NF COND. DO EDF. FABIO.PDF"
nome2 = "2.1NF ASSOC. CONDOMINIO PARAISO DOS LAGOS.PDF"
nome3 = "3.1NF CAPRI FATOR TOWER.PDF"
nome4 = "3.1NF CONDOMINIO PEDRA DO SAL RESIDENCIAS.PDF"
nome5 = "4.1NF CENTRAL PARK-SOHO.PDF"
with open(f"CAMACARI/{nome3}", "rb") as pdf_nota_fiscal:
        #LEITURA DO TEXTO DO PDF
        pdf_reader = PdfReader(pdf_nota_fiscal)
        page = pdf_reader.pages[0]
        text = page.extract_text()
        print(text)

        #BUSCAR NUMERO DA NOTA
        pos_inicial_nota = text.find("Número da Nota") + len("Número da Nota") + 1
        pos_final_nota = pos_inicial_nota
        while(text[pos_final_nota]!= '\n'):
            pos_final_nota += 1
        
        print(text[pos_inicial_nota:pos_final_nota])

        #BUSCAR RAZAO SOCIAL
        