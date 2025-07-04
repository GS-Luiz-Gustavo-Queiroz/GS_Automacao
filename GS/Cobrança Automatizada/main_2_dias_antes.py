import pandas as pd
import smtplib
from ler_credenciais import ler_credenciais_remet, ler_credenciais_db
from get_data import get_data_2_dias_antes
from enviar_email import enviar_email_2_dias_antes
from data_venc import data_venc
from tqdm import tqdm
from tratar_email import tratar_email

def cobranca_automatizada():
    creds_db = ler_credenciais_db()
    df = get_data_2_dias_antes(creds_db['server'], creds_db['username'], creds_db['password'], creds_db['database'])

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

            enviar_email_2_dias_antes(servidor_email, creds_remet, emails_dest, num_nota, data)
    
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
    finally:
        servidor_email.quit()

cobranca_automatizada()