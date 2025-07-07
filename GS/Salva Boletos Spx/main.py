from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from typing import List, Dict, Callable
from selenium import webdriver
from datetime import datetime
from PyPDF2 import PdfReader
from time import sleep
from tqdm import tqdm
import pandas as pd
import os


PATH_CREDS = 'configs.txt'
DIR_BOL = 'boletos'


def init_dir(dir_name: str = DIR_BOL) -> None:
    # Inicializa o diretório de destino dos boletos.
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)


def get_nav():
    # Inicializa o navegador.
    options = Options()
    options.add_experimental_option("prefs", {
        "download.default_directory": f'{os.getcwd()}\\{DIR_BOL}',
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_setting_values.automatic_downloads": 1
    })
    options.add_argument("--disable-blink-features=AutomationControlled")
    nav = webdriver.Edge(service=Service(), options=options)
    return nav


def get_creds(path: str = PATH_CREDS) -> Dict[str, str]:
    with open(path, 'r') as file:
        rows: List[str] = file.read().split('\n')
        creds: Dict[str, str] = {row.split('-->')[0].strip(): row.split('-->')[1].strip() for row in rows}
        return creds


class Aut_Spx:
    def __init__(self) -> None:
        self.nav = get_nav()
        self.wait = WebDriverWait(self.nav, 30)
        self.creds: Dict[str, str] = get_creds()

    def espera_aparecer(self, xpath: str, n: int = 20) -> None:
        """
        Espera n segundos até que determinado item esteja na tela.
        :param xpath: Uma string com o xpath do item que se deseja esperar aperecer.
        :param n: O total de segundos que se deseja esperar.
        """
        for _ in range(n):
            if self.nav.find_elements('xpath', xpath):
                return
            sleep(1)
        raise NoSuchElementException(f'{xpath} não encontrado em {n} segundos de espera')

    def interact(self, action: str, xpath: str, keys: str = None, n_tries: int = 10) -> None:
        """
        Interage com determinado elemento na tela.
        Primeiro chama a função 'espera_aparecer' para não causar erro de Not Found.
        :param xpath: Uma string com o xpath do elemento que se deseja esperar aperecer.
        """
        actions = ['click', 'write', 'clear']
        if action not in actions:
            raise TypeError(f'{action} must be in {actions}')
        self.espera_aparecer(xpath)
        for try_i in range(n_tries):
            try:
                # Find the element.
                element = self.nav.find_element('xpath', xpath)
                # Choose the right action to do.
                if   action == 'click':
                    element.click()
                elif action == 'write':
                    element.send_keys(keys)
                elif action == 'clear':
                    element.clear()
                return
            except NoSuchElementException:
                if try_i == n_tries - 1:
                    print(f'Item com xpath {xpath} não encontrado')
                sleep(1)
            except ElementNotInteractableException:
                if try_i == n_tries - 1:
                    print(f'Elemento com xpath {xpath} indisponível ou oculto.')
                sleep(1)
            except ElementClickInterceptedException:
                if try_i == n_tries - 1:
                    print(f'Elemento com xpath {xpath} interceptado ou sobreposto.')
                sleep(1)
            except UnexpectedAlertPresentException:
                try:
                    alert = self.nav.switch_to.alert
                    alert.dismiss()  # Recusa o alerta.
                except NoAlertPresentException:
                    pass

    def run(self) -> None:
        init_dir()
        self.login()
        self.troca_empresa()
        sleep(2)
        self.goto_tela_boletos()
        sleep(2)
        self.baixa_boletos()
        sleep(50)

    def login(self) -> None:
        # Realiza o login.
        self.nav.get('https://empresa.spxpay.com.br/empresa/pages/main.jsp')
        # Preenche o campo 'Usuário'.
        self.interact('write', '//*[@id="txtLogin"]', self.creds['login'])
        # Preenche o campo 'Senha'.
        self.interact('write', '//*[@id="txtPassword"]', self.creds['senha'])
        # Preenche o campo 'Token'.
        self.interact('write', '//*[@id="txtToken"]', self.creds['token'])
        # Clica em 'ENTRAR'.
        self.espera_aparecer('//*[@id="entrar"]')
        element = self.nav.find_element(By.XPATH, '//*[@id="entrar"]')
        self.nav.execute_script("arguments[0].click();", element)

    def troca_empresa(self) -> None:
        # Clica na aba no topo para trocar de empresa.
        self.interact('click', '//*[@id="header"]/div/div[2]/ul[1]/li')
        # Tabela:
        # //*[@id="formResultado"]
        self.espera_aparecer('//*[@id="formResultado"]/table/tbody/tr[1]/td[3]')
        n = 50
        for i in range(1, n+1):
            empresa = self.nav.find_element(By.XPATH, f'//*[@id="formResultado"]/table/tbody/tr[{i}]/td[3]').text
            if empresa.strip() == self.creds['empresa']:
                self.interact('click', f'//*[@id="formResultado"]/table/tbody/tr[{i}]/td[4]')
                return
        raise Exception(f'Empresa [{self.creds['empresa']}] não encontrada.')

    def goto_tela_boletos(self) -> None:
        # Vai para a tela de boletos.
        # Clica no símbolo '$' (Cobrança).
        self.interact('click', '//*[@id="main-menu"]/li[5]/a/div/i')
        # Clica em 'Boleto'.
        self.interact('click', '//*[@id="menuConsBoleto"]')
        # Preenche o campo 'Data de Vencimento Inicial'.
        self.interact('write', '//input[@name="objetoPesquisa.filtro.dataVencimentoInicial"]', self.creds['data_inicial'])
        # Preenche o campo 'Data de Vencimento Final'.
        self.interact('write', '//input[@name="objetoPesquisa.filtro.dataVencimentoFinal"]', self.creds['data_final'])
        # Clica em 'Pesquisar'.
        self.interact('click', '//*[@id="btn_titulo_pesquisar"]')

    def baixa_boletos(self) -> None:
        # Salva todos os boletos da página.
        botoes = self.nav.find_elements(By.XPATH, '//div[@class="btn-group"]/a[contains(@href, "javascript:gerarRelatorioBoleto")]')
        for botao in botoes:
            self.nav.execute_script("arguments[0].scrollIntoView(true);", botao)
            WebDriverWait(self.nav, 10).until(EC.element_to_be_clickable(botao))
            self.nav.execute_script("arguments[0].click();", botao)
            sleep(2)  # Ajuste conforme necessário

aut = Aut_Spx()
aut.run()
if __name__ == '1__main__':
    try:
        aut = Aut_Spx()
        aut.run()
    except Exception as e:
        print(e)
        input()


