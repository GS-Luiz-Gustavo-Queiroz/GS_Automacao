import pandas as pd
import re
import random
import time

CAMINHO_PLANILHA = 'C:\\Users\\user244\\Documents\\CONTROLE_DE_ENVIOS_DET_(18.06).xlsx'
DOMINIO_EMAIL = 'outlook.com'

def gerar_email(primeiro_nome, segundo_nome):
    numero_aleatorio = random.randint(100, 999)  
    nome1 = re.sub(r'[^a-z0-9]', '', primeiro_nome.lower())
    nome2 = re.sub(r'[^a-z0-9]', '', segundo_nome.lower()) if segundo_nome else ''
    return f"{nome1}.{nome2}{numero_aleatorio}@{DOMINIO_EMAIL}"

def gerar_senha(primeiro_nome):
    numero_aleatorio = random.randint(100, 999)  
    return f"309263@{primeiro_nome}{numero_aleatorio}"

def atualizar_planilha_com_emails(caminho_arquivo):
    try:
        df = pd.read_excel(caminho_arquivo)

        for col in ['RAZÃO SOCIAL', 'E-MAIL', 'SENHA']:
            if col not in df.columns:
                df[col] = ''

        for i, row in df[df['E-MAIL'].isna() | df['E-MAIL'].eq('')].iterrows():
            empresa = str(row['RAZÃO SOCIAL']).strip()
            partes = empresa.split()

            if not partes:
                continue  

            primeiro_nome = partes[0]
            segundo_nome = partes[1] if len(partes) > 1 else 'RAZÃO SOCIAL'

            email = gerar_email(primeiro_nome, segundo_nome)
            df.at[i, 'E-MAIL'] = email
            df.at[i, 'SENHA'] = gerar_senha(primeiro_nome)

        df.to_excel(caminho_arquivo, index=False)
        print("Planilha atualizada com emails e senhas.")
        time.sleep(3)

    except Exception as e:
        print(f"[ERRO] Ocorreu um problema: {e}")

atualizar_planilha_com_emails(CAMINHO_PLANILHA)