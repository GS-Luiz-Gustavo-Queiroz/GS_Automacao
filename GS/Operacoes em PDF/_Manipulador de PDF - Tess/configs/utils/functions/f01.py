from typing import Dict, List
from PyPDF2 import PdfReader
from tqdm import tqdm
from PIL import Image
import fitz
import os
from .utils import all_sizes, processa_nfs, processa_outras


def f01() -> int:
    tot_pags = 0
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    cidades = all_sizes.keys()
    nfs: Dict[str, List[str]] = {cidade: [] for cidade in cidades}
    nfs['outras'] = []
    print('Identificando prefeituras...')
    for file in tqdm(files):
        # Verificar se contem texto.
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b).pages[0]
            rows = pdf.extract_text().split('\n')
            if len(rows) > 1:
                nfs['outras'].append(file)
                continue
        # Verifica de qual prefeitura é.
        pdf_document = fitz.open(file)  # Abre a Nota Fiscal.
        page = pdf_document.load_page(0)  # Carrega a página.
        image = page.get_pixmap()  # Converte a página num objeto de imagem.
        image.save('img.png')  # Salva a imagem num arquivo.
        pdf_document.close()  # Fecha o arquivo.
        image = Image.open('img.png')
        for cidade in cidades:
            if image.size in all_sizes[cidade]:
                nfs[cidade].append(file)
                break
    # Processa as notas fiscais.
    for cidade in cidades:
        if len(nfs[cidade]) > 1:
            tot_pags += processa_nfs(cidade, nfs[cidade])
    if nfs['outras']:
        tot_pags += processa_outras(nfs['outras'])
    return tot_pags
