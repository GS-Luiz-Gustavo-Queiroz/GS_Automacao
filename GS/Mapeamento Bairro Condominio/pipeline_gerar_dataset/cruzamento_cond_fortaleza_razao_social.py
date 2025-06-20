# %%
import os
import pandas as pd
import numpy as np

# %%
def capturar_dataset_empresas(nome_do_arquivo):
    pasta_atual = os.getcwd()
    pasta_empresas = os.path.join(pasta_atual, '..', 'empresas')
    pasta_empresas = os.path.abspath(pasta_empresas)

    empresas = os.path.join(pasta_empresas, nome_do_arquivo)
    empresas = os.path.abspath(empresas)

    nomes_colunas = ["cnpj_base", "razao_social", "nat_jurid", "qual_resp", "capit_soc", "porte", "ente_fed"]
    dataset_empresas = pd.read_csv(empresas, dtype=str, sep=";", encoding="latin1", names=nomes_colunas)
    dataset_empresas = dataset_empresas.drop(['nat_jurid', 'qual_resp', 'capit_soc', 'porte', 'ente_fed'], axis=1)

    return dataset_empresas
    

# %%
def cruzar_dados_cond_fort_razao_social():
    pasta_atual = os.getcwd()

    pasta_arquivos = os.path.join(pasta_atual, '..', "empresas")
    pasta_arquivos = os.path.abspath(pasta_arquivos)
    os.makedirs(pasta_arquivos, exist_ok=True)

    pasta_destino = os.path.join(pasta_atual, '..', "condominios_fortaleza")
    pasta_destino = os.path.join(pasta_destino)
    os.makedirs(pasta_destino, exist_ok=True)

    #capturando nome dos arquivos de estabelecimentos
    arquivos_extraidos = os.listdir(pasta_arquivos)

    condominios_fortaleza = os.path.join(pasta_destino, "condominios_fortaleza.csv")
    condominios_fortaleza = os.path.abspath(condominios_fortaleza)

    cond_fortaleza_com_razao_social = pd.read_csv(condominios_fortaleza, dtype=str, encoding='latin1')

    iter = 0
    for arquivo in arquivos_extraidos:
        empresa = capturar_dataset_empresas(arquivo)

        cond_fortaleza_com_razao_social = pd.merge(
            cond_fortaleza_com_razao_social,
            empresa,
            on='cnpj_base',
            how='left'
        )

        cond_fortaleza_com_razao_social = cond_fortaleza_com_razao_social.rename(columns={'razao_social': f"razao_social{iter}"})
        iter = iter + 1

    #combinando as colunas geradas de razão social
    cond_fortaleza_com_razao_social["razao_social"] = cond_fortaleza_com_razao_social["razao_social0"]
    for combinar_coluna in range(0, iter):
        cond_fortaleza_com_razao_social["razao_social"] = cond_fortaleza_com_razao_social["razao_social"].fillna(cond_fortaleza_com_razao_social[f"razao_social{combinar_coluna}"])

    # #organizando a posicao da coluna razao_social
    razao_social = cond_fortaleza_com_razao_social["razao_social"]
    cond_fortaleza_com_razao_social = cond_fortaleza_com_razao_social.drop(["razao_social"], axis=1)
    cond_fortaleza_com_razao_social.insert(3, "razao_social", razao_social)

    # #export do arquivo final
    nome_do_arquivo = os.path.join(pasta_destino, "condominios_fortaleza_com_razao_social.csv")
    nome_do_arquivo = os.path.abspath(nome_do_arquivo)
    cond_fortaleza_com_razao_social.to_csv(nome_do_arquivo, index=False, encoding='latin1')

    return cond_fortaleza_com_razao_social

# %%
# cruzar_dados_cond_fort_razao_social()