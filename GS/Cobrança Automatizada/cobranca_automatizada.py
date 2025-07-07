import pandas as pd
import smtplib
from ler_credenciais import ler_credenciais_remet, ler_credenciais_db
from data_venc import data_venc
from tqdm import tqdm
from tratar_email import tratar_email
from salvar_relatorio import salvar_relatorio
from datetime import datetime
import time
from get_data import get_data
from enviar_email import enviar_email

#get_data é a função referente a captura de dados de acordo com o necessário (ex.:2 dias antes do venc)
#enviar_email é a função referente ao envio de e-mail de acordo com o necessário (com adiantamento ou atraso)
def cobranca_automatizada(dias):

    tempo_inicio = time.time() #guarda o tempo de inicio de execução do codigo
    
    creds_db = ler_credenciais_db()
    df = get_data(creds_db['server'], creds_db['username'], creds_db['password'], creds_db['database'], dias)

    creds_remet = ler_credenciais_remet()

    #BLOCO DE TESTES# APAGAR DEPOIS
    for _, i in df.iterrows():
        i['email_cli'] = 'ti.automacao03@gscsc.com.br'
    #FIM DO BLOCO DE TESTES#

    try:
        #configurando servidor de e-mail
        servidor_email = smtplib.SMTP('smtp.gmail.com', 587)
        #iniciando servidor de e-mail
        servidor_email.starttls()
        #logando e-mail
        servidor_email.login(creds_remet['usuario'], creds_remet['senha'])

        creds_remet = creds_remet['usuario']
        for _, registro in tqdm(df.iterrows(), total=len(df)):
            emails_dest = tratar_email(registro['email_cli'])
            num_nota = registro['num_titulo']
            data = data_venc(registro['dt_vencimento'])

            enviar_email(servidor_email, creds_remet, emails_dest, num_nota, data, dias)
    
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
    finally:
        servidor_email.quit()
    
    tempo_fim = time.time()
    exec_time = tempo_fim - tempo_inicio  # Calcula o tempo de execução do código.
    data = datetime.now().strftime("%d/%m/%Y")
    values = [[data, 'Cobrança automatizada', len(df), exec_time]]  # Valores para serem salvos no relatório.
    salvar_relatorio(values)