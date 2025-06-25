import pandas as pd
import os

#capturando o diretorio dos datasets dos condominios novo e antigo
pasta_atual = os.getcwd()

pasta_arquivos = os.path.join(pasta_atual, '..', "condominios_fortaleza")
pasta_arquivos = os.path.abspath(pasta_arquivos)
os.makedirs(pasta_arquivos, exist_ok=True)

pasta_destino = os.path.join(pasta_atual, '..', "condominios_fortaleza")
pasta_destino = os.path.join(pasta_destino)
os.makedirs(pasta_destino, exist_ok=True)

condominios_fortaleza_antigo = os.path.join(pasta_arquivos, "condominios_fortaleza_com_razao_social.csv")
condominios_fortaleza_antigo = os.path.abspath(condominios_fortaleza_antigo)

condominios_fortaleza_novo = os.path.join(pasta_arquivos, "condominios_fortaleza_com_razao_social_atualizado.csv")
condominios_fortaleza_novo = os.path.abspath(condominios_fortaleza_novo)

#importando os datasets novo e antigo
condominios_novo = pd.read_csv(condominios_fortaleza_novo, dtype=str, encoding='latin1')
try:
    condominios_antigo = pd.read_csv(condominios_fortaleza_antigo, dtype=str, encoding='latin1')

    #comparando os datasets novo e antigo para capturar os condominios acrescentados
    condominios_adicionados = condominios_novo[~condominios_novo['cnpj_base'].isin(condominios_antigo['cnpj_base'])]
    condominios_adicionados

    #exportando o dataset adicional apenas com os condominios que foram acrescentados em relação ao dataset antigo
    arquivo_destino = os.path.join(pasta_destino, 'condominios_novos_do_mes.csv')
    arquivo_destino = os.path.abspath(arquivo_destino)
    condominios_adicionados.to_csv(arquivo_destino, index=False, encoding='latin1')

    os.remove(condominios_fortaleza_antigo)
    os.rename(condominios_fortaleza_novo, condominios_fortaleza_antigo) #troca o nome novo pelo nome do antigo
    #ou seja troca "condominios_fortaleza_com_razao_social_atualizado.csv" por "condominios_fortaleza_com_razao_social.csv"
except:
    os.rename(condominios_fortaleza_novo, condominios_fortaleza_antigo)
    pass