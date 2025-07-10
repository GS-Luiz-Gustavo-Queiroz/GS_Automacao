from PIL import Image
from tqdm import tqdm
import fitz
import os

from .utils import extract_text, limpa_residuos


def f07() -> int:
    tot_pags = 0
    # Cria a pasta de destino dos arquivos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for i, file in enumerate(files):
        pdf = fitz.open(file)  # Abre o arquivo pdf.
        # Atualiza o contador de páginas
        tot_pags += len(pdf)
        for i in tqdm(range(len(pdf))):
            page = pdf.load_page(i)  # Carrega a página.
            image = page.get_pixmap()  # Converte a página num objeto de imagem.
            image.save('img.jpg')  # Salva a imagem num arquivo.
            image = Image.open('img.jpg')
            """
                Pode ocorrer de a página atual ser continuação do arquivo anterior, então é necessário fazer uma verificação.
                Nas páginas de continuação, a parte inferior da página é totalmente branca, então será tentado extrair o
            texto desta seção e caso não retorne nenhum texto, a página será considerada continuação do documento anterior.
            """
            verificacao = image.crop((10, 500, 600, 750))
            verificacao.save('verificacao.jpg')
            verificacao: str = extract_text('verificacao.jpg', config='--psm 6').strip()
            # Este if irá entrar em caso o texto de verificação seja igual a '', indicando que a página é uma continuação.
            if not verificacao:
                """
                    Para evitar conflitos, é necessário primeiro abrir o arquivo anterior, em seguida criar um novo
                arquivo pdf e copiar o anterior para o novo pdf, em seguida fechar e excluir o arquivo anterior,
                e então adicionar a nova página e salvar o novo pdf.
                """
                pdf_ant = fitz.open(file_name)
                novo_pdf = fitz.open()
                novo_pdf.insert_pdf(pdf_ant)
                pdf_ant.close()
                os.remove(file_name)
                novo_pdf.insert_pdf(pdf, from_page=i, to_page=i)
                novo_pdf.save(file_name)
                continue
                #                  l     u    r    d
                # nome = image.crop((150, 185, 550, 198))
            cpf = image.crop((45, 185, 130, 198))
            # cnpj = image.crop((35, 147, 130, 160))
            # nome.save('nome.jpg')
            cpf.save('cpf.jpg')
            # cnpj.save('cnpj.jpg')

            # nome: str = extract_text('nome.jpg', config='--psm 7').strip()
            cpf: str = extract_text('cpf.jpg', config='--psm 13 -c tessedit_char_whitelist=0123456789').strip()
            # cnpj: str = extract_text('cnpj.jpg', config='--psm 13 -c tessedit_char_whitelist=0123456789').strip()
            # Remove a / do cnpj que é identificada como um '1'.
            # if len(cnpj) == 15:
            #    cnpj = cnpj[:8] + cnpj[9:]

            # file_name = 'Arquivos/' + '-'.join([nome, cpf, cnpj]) + '.pdf'
            # file_name = re.sub(r'[^a-zA-Z0-9\s./\\-]', '', file_name)
            file_name = f'Arquivos/{cpf}.pdf'
            novo_pdf = fitz.open()
            novo_pdf.insert_pdf(pdf, from_page=i, to_page=i)
            novo_pdf.save(file_name)
        pdf.close()  # Fechar o PDF para garantir que o arquivo seja liberado
    limpa_residuos()
    return tot_pags
