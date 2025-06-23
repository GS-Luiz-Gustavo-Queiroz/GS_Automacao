# %%
"""
Para captar os novos condominios da cidade de fortaleza, a ideia consiste em:
 - Capturar os dados dos condomínios com o [programa gerar_dataset_cond_fortaleza](../pipeline_gerar_dataset/gerar_dataset_cond_fortaleza.py) disponibilizados no mês atual no site da receita.
 - A partir desses dados, realizar uma diferenciação entre o dataset antigo e o novo.
 - A partir dessa diferenciação gerar dois datasets: 1 apenas com os novos condomínios, e o outro geral, com os antigos mais os novos, no qual é o próprio dataset gerado.
"""

# %%
import os
import sys
import pandas as pd
import importlib

# %%
pasta_atual = os.getcwd()
gerar_dataset = os.path.join(pasta_atual, '..', 'pipeline_gerar_dataset')
gerar_dataset = os.path.abspath(gerar_dataset)
sys.path.append(gerar_dataset)

# %%
from gerar_dataset_cond_fortaleza import gerar_dataset

# %%
"""
#### Gerando o dataset do mês atual
"""

# %%
#captura o dataset dos condominios no mes atual e guarda o dataset
#compara com o dataset antigo e gera um dataset a mais informando os condominios acrescentados
def gerar_novo_dataset():
    #capturando o dataset de condominios de fortaleza com o programa gerar_dataset()
    dataset = gerar_dataset("condominios_fortaleza_com_razao_social_atualizado.csv")

    #capturando o diretorio dos datasets dos condominios novo e antigo
    pasta_atual = os.getcwd()

    pasta_arquivos = os.path.join(pasta_atual, '..', "condominios_fortaleza")
    pasta_arquivos = os.path.abspath(pasta_arquivos)
    os.makedirs(pasta_arquivos, exist_ok=True)

    pasta_destino = os.path.join(pasta_atual, '..', "condominios_fortaleza")
    pasta_destino = os.path.join(pasta_destino)
    os.makedirs(pasta_destino, exist_ok=True)

    condominios_fortaleza_antigo = os.path.join(pasta_arquivos, "condominios_fortaleza.csv")
    condominios_fortaleza_antigo = os.path.abspath(condominios_fortaleza_antigo)

    condominios_fortaleza_novo = os.path.join(pasta_arquivos, "condominios_fortaleza_com_razao_social_atualizado.csv")
    condominios_fortaleza_novo = os.path.abspath(condominios_fortaleza_novo)

    #importando os datasets novo e antigo
    condominios_novo = pd.read_csv(condominios_fortaleza_novo, dtype=str, encoding='latin1')
    condominios_antigo = pd.read_csv(condominios_fortaleza_antigo, dtype=str, encoding='latin1')

    #comparando os datasets novo e antigo para capturar os condominios acrescentados
    condominios_adicionados = condominios_novo[~condominios_novo['cnpj_base'].isin(condominios_antigo['cnpj_base'])]
    condominios_adicionados

    #exportando o dataset adicional apenas com os condominios que foram acrescentados em relação ao dataset antigo
    arquivo_destino = os.path.join(pasta_destino, 'condominios_novos_do_mes.csv')
    arquivo_destino = os.path.abspath(arquivo_destino)
    condominios_adicionados.to_csv(arquivo_destino, index=False, encoding='latin1')

    return dataset, condominios_adicionados

# %%
gerar_dataset("condominios_fortaleza_com_razao_social_atualizado.csv")

# %%
"""
#### Gerando verificação do dataset antigo com o dataset atual
"""

# %%
pasta_atual = os.getcwd()

pasta_arquivos = os.path.join(pasta_atual, '..', "condominios_fortaleza")
pasta_arquivos = os.path.abspath(pasta_arquivos)
os.makedirs(pasta_arquivos, exist_ok=True)

pasta_destino = os.path.join(pasta_atual, '..', "condominios_fortaleza")
pasta_destino = os.path.join(pasta_destino)
os.makedirs(pasta_destino, exist_ok=True)

condominios_fortaleza_antigo = os.path.join(pasta_arquivos, "condominios_fortaleza.csv")
condominios_fortaleza_antigo = os.path.abspath(condominios_fortaleza_antigo)

condominios_fortaleza_novo = os.path.join(pasta_arquivos, "condominios_fortaleza_com_razao_social_atualizado.csv")
condominios_fortaleza_novo = os.path.abspath(condominios_fortaleza_novo)

# %%
condominios_novo = pd.read_csv(condominios_fortaleza_novo, dtype=str, encoding='latin1')
condominios_antigo = pd.read_csv(condominios_fortaleza_antigo, dtype=str, encoding='latin1')

# %%
condominios_adicionados = condominios_novo[~condominios_novo['cnpj_base'].isin(condominios_antigo['cnpj_base'])]
condominios_adicionados

# %%
arquivo_destino = os.path.join(pasta_destino, 'condominios_novos_do_mes.csv')
arquivo_destino = os.path.abspath(arquivo_destino)
condominios_adicionados.to_csv(arquivo_destino, index=False, encoding='latin1')