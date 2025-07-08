#CODIGO PARA MUDANCA DE NOME DAS NFS DE BALNEARIO CAMBURIU

from PyPDF2 import PdfReader
import re
import os
import shutil

#abrindo pdf

pasta_eusebio = os.getcwd()
pasta_eusebio = os.path.join(pasta_eusebio, "EUSEBIO")
pasta_eusebio = os.path.abspath(pasta_eusebio)
arquivos_pdf = os.listdir(pasta_eusebio)
print(arquivos_pdf)

for arquivo in arquivos_pdf:
    with open(f"EUSEBIO/{arquivo}", "rb") as pdf_nota_fiscal:
        pdf_reader = PdfReader(pdf_nota_fiscal)

        page = pdf_reader.pages[0]
        text = page.extract_text()
        # print("Texto da página: ", page_number + 1, ":", text)
        num_nota = re.findall(r"\b\d{19}\b", text)[0][9:]
        pos_inicial_nome_cond = text.find("Optante do Simples") + 21
        pos_final_nome_cond = text.find("Competência")
        nome_cond = text[pos_inicial_nome_cond:pos_final_nome_cond]
        print(f"Nome do condomínio: {nome_cond} - Nº NF: {num_nota}")

        pasta_atual = os.getcwd()
        caminho_arquivo = os.path.join(pasta_atual, "EUSEBIO", arquivo)
        caminho_arquivo = os.path.abspath(caminho_arquivo)
        novo_nome = os.path.join(pasta_atual, "EUSEBIO", f"{nome_cond}_{num_nota}.pdf")
        novo_nome = os.path.abspath(novo_nome)
        shutil.copyfile(caminho_arquivo, novo_nome)