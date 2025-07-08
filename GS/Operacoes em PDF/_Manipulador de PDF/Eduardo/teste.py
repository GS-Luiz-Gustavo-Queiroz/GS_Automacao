from PyPDF2 import PdfReader
import re
import os
import shutil

#abrindo pdf



with open(f"EUSEBIO/POP EUSEBIO.pdf", "rb") as pdf_nota_fiscal:
    pdf_reader = PdfReader(pdf_nota_fiscal)

    page = pdf_reader.pages[0]
    text = page.extract_text()
    # print("Texto da página: ", page_number + 1, ":", text)
    # num_nota = re.findall(r"\b\d{19}\b", text)[0][9:]
    # pos_inicial_nome_cond = text.find("Optante do Simples") + 21
    # pos_final_nome_cond = text.find("Competência")
    # nome_cond = text[pos_inicial_nome_cond:pos_final_nome_cond]
    # print(f"Nome do condomínio: {nome_cond} - Nº NF: {num_nota}")
    print(text)


    

