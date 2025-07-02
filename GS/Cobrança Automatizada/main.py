import pandas as pd
import smtplib
from ler_credenciais import ler_credenciais_remet, ler_credenciais_db
from get_data import get_data
from enviar_email import enviar_email
from data_venc import data_venc

def cobranca_automatizada():
    creds_db = ler_credenciais_db()
    df = get_data(creds_db['server'], creds_db['username'], creds_db['password'], creds_db['database'])

    creds_remet = ler_credenciais_remet()

    #BLOCO DE TESTES# APAGAR DEPOIS
    for _, i in df.iterrows():
        i['email_cli'] = 'controladoria.gestao@gscsc.com.br'
    #FIM DO BLOCO DE TESTES#

    for _, registro in df.iterrows():

        data = data_venc(registro['dt_vencimento']) #fazer função

        enviar_email(creds_remet, registro['email_cli'], registro['num_titulo'], data)

cobranca_automatizada()