from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from typing import List, Dict
from tqdm import tqdm
from PIL import Image
from sys import exit
import pytesseract
import cv2 as cv
import fitz
import time
import os


pytesseract.pytesseract.tesseract_cmd = 'configs/tess/tesseract.exe'
CONFIGS_DIR = 'configs/configs.txt'


def get_creds(path: str = CONFIGS_DIR) -> Dict[str, str]:
    with open(path, 'r') as file:
        rows: List[str] = file.read().split('\n')
        creds: Dict[str, str] = {row.split('-->')[0]: row.split('-->')[1] for row in rows}
        return creds


def pdf_to_img(path: str, page: int = 0) -> None:
    pdf_document = fitz.open(path)  # Abre o boleto.
    page = pdf_document.load_page(page)  # Carrega a página.
    image = page.get_pixmap()  # Converte a página num objeto de imagem.
    image.save('img.jpg')  # Salva a imagem num arquivo.
    pdf_document.close()  # Fechar o PDF para garantir que o arquivo seja liberado.
    image = Image.open('img.jpg')
    cliente = image.crop((30, 723, 450, 735))
    vencimento = image.crop((330, 105, 410, 125))
    valor = image.crop((70, 105, 180, 120))
    cliente.save('cliente.jpg')
    vencimento.save('vencimento.jpg')
    valor.save('valor.jpg')
    os.remove('img.jpg')  # Apaga o arquivo temporário.


def extract_text(path: str, config='--psm 10') -> str:
    img = cv.imread(path)
    scale_percent = 15  # Aumentar a imagem em 150%
    # Calculando o novo tamanho
    new_width = int(img.shape[1] * scale_percent)
    new_height = int(img.shape[0] * scale_percent)
    # Redimensionar a imagem proporcionalmente
    img = cv.resize(img, (new_width, new_height), interpolation=cv.INTER_LANCZOS4)
    # 1. Conversão para escala de cinza
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Executar o OCR na imagem processada
    text = pytesseract.image_to_string(img, config=config)
    return text


class AutBoletosSPX:
    """
    Classe para realizar a automação de renomear os boletos do banco SPX.
    """
    def __init__(self) -> None:
        self.creds: Dict[str, str] = get_creds()

    def run(self) -> int:
        pasta = self.creds['pasta']
        files: List[str] = [os.path.join(pasta, file) for file in os.listdir(pasta)]
        for file in tqdm(files):
            self.renomeia_boleto(file)
        # Limpa os arquivos residuais.
        os.remove('cliente.jpg')
        os.remove('vencimento.jpg')
        os.remove('valor.jpg')
        return len(files)

    def renomeia_boleto(self, path) -> None:
        pdf_to_img(path)
        cliente: str = extract_text('cliente.jpg', '--psm 7')
        vencimento: str = extract_text('vencimento.jpg', '--psm 7')
        valor: str = extract_text('valor.jpg', '--psm 7')
        # Formata o nome do beneficiário, valor e a data de vencimento.
        cliente = cliente[:-30]
        cliente = cliente.translate(str.maketrans({'\\': '', '/': '', '|': '', ':': '', '\n': ''}))
        vencimento = vencimento.translate(str.maketrans({'/': '-', '\n': ''}))
        valor = valor.replace('\n', '')

        novo_nome = f'{vencimento}-{valor}-{cliente}.pdf'
        novo_nome = os.path.join(self.creds['pasta'], novo_nome)
        # Renomeia o arquivo.
        os.rename(path, novo_nome)


def salva_relatorio(row: List[List]):
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    SAMPLE_SPREADSHEET_ID = "15gGHm67_W5maIas-4_YPSzE6R5f_CNJGcza_BJFlNBk"  # Código da planilha
    SAMPLE_RANGE_NAME = "Página1!A{}:D1000"  # Intervalo que será lido
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


if __name__ == "__main__":
    try:
        data = datetime.now().strftime("%d/%m/%Y")
        st = time.time()
        aut = AutBoletosSPX()
        n_pags = aut.run()
        exec_time = time.time() - st
        salva_relatorio([[data, 'Boletos SPX', n_pags, exec_time]])
    except Exception as e:
        print(e)
        input()
