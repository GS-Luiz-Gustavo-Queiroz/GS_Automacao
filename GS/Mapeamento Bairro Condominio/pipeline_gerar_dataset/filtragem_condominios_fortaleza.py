# %%
"""
Para captar os condominios da cidade de fortaleza, a ideia consiste em:
 - Pegar os dados dos cnpj das empresas disponíveis no site da receita federal
 - A partir desses dados, filtrar pelo código da cidade de fortaleza e CNAE relativo a atitividade de condominio.

<u>código da cidade de fortaleza: 1389</u><br/>
<u>cnae da atividade de condominio: 8112500</u>
"""

# %%
import os
import numpy as np
import pandas as pd

# %%
"""
Tratamento dos datasets Estabelecimentos para obtenção dos condomínios de fortaleza (filtragem do dataset pelo codigo CNAE e códi)
"""

# %%
def unificacao_cnpj(dataset): #funcao para chamar depois de filtrar os condominios de fortaleza
    cnpj_completo = dataset["cnpj_base"] +"/"+ dataset["cnpj_ordem"] +"-"+ dataset["cnpj_dig_ver"]
    dataset.insert(0, 'cnpj', cnpj_completo)
    dataset = dataset.drop(["cnpj_ordem", "cnpj_dig_ver"], axis=1)
    # dataset.to_csv("condominios_total.csv", index=False, encoding='latin1')
    return dataset

# %%
def tratamento_data_sit_cadast(dataset):
    data_sit_cadast = dataset["data_sit_cadast"]
    data_sit_cadast_novo = data_sit_cadast.str[6:8] +"/"+ data_sit_cadast.str[4:6] +"/"+ data_sit_cadast.str[:4]
    dataset["data_sit_cadast"] = data_sit_cadast_novo

    dataset.to_csv("condominios_total.csv", index=False, encoding='latin1')

    return dataset

# %%
def tratamento_data_inicio(dataset):
    data_inicio = dataset["data_inicio"]
    data_inicio_novo = data_inicio.str[6:8] +"/"+ data_inicio.str[4:6] +"/"+ data_inicio.str[:4]
    dataset["data_inicio"] = data_inicio_novo

    dataset.to_csv("condominios_total.csv", index=False, encoding='latin1')

    return dataset

# %%
def filtrar_por_cnae_e_cidade(nome_do_arquivo): #obs.: o nome do aquivo tem que ser
    nomes_colunas = ["cnpj_base", "cnpj_ordem", "cnpj_dig_ver", "matriz_filial", "nome_fantasia", "sit_cadast", "data_sit_cadast", "motivo_sit_cadast", "nome_cidade_exterior", "pais", "data_inicio", "cnae_principal", "cnae_secundaria", "logradouro", "rua", "numero", "complemento", "bairro", "cep", "uf", "municipio", "ddd1", "telefone1", "ddd2", "telefone2", "ddd_fax", "fax", "email", "unamed1", "unamed2"]

    df_est = pd.read_csv(nome_do_arquivo, sep=';', dtype=str, encoding='latin1', names=nomes_colunas)

    df_est = df_est.drop(["unamed1", "unamed2"], axis=1) #dropando colunas vazias dos arquivos da receita federal
    
    df_cnae = df_est[df_est["cnae_principal"] == '8112500'] #filtrando o cnae de condominio

    df_munic_cnae = df_cnae[df_cnae["municipio"] == '1389'] #filtrando pelo codigo do municipio

    # df_munic_cnae.to_csv(f"condominios{numero_arquivo}.csv", index=False) #se quiser exportar o arquivo, mas vamos manter em memória
    df_munic_cnae = unificacao_cnpj(df_munic_cnae)
    df_munic_cnae = tratamento_data_sit_cadast(df_munic_cnae)
    df_munic_cnae = tratamento_data_inicio(df_munic_cnae)

    return df_munic_cnae

# %%
def filtrar_cond_fortaleza():

    pasta_atual = os.getcwd()

    pasta_arquivos = os.path.join(pasta_atual, '..', "estabelecimentos")
    pasta_arquivos = os.path.abspath(pasta_arquivos)
    os.makedirs(pasta_arquivos, exist_ok=True)

    pasta_destino = os.path.join(pasta_atual, '..', "condominios_fortaleza")
    pasta_destino = os.path.join(pasta_destino)
    os.makedirs(pasta_destino, exist_ok=True)

    #capturando nome dos arquivos de estabelecimentos
    arquivos_extraidos = os.listdir(pasta_arquivos)

    #loop para cada arquivo ser tratado e apos cada tratamento ser adicionado na lista para depois concatenar
    arquivos_tratados_e_filtrados = []
    for arquivo in arquivos_extraidos:
        arquivo_atual = os.path.join(pasta_arquivos, arquivo)
        arquivo_atual = os.path.abspath(arquivo_atual)

        arquivos_tratados_e_filtrados.append( filtrar_por_cnae_e_cidade(arquivo_atual) )
    
    #concatenção dos arquivos de estabelecimentos tratados, ou seja, condominios de fortaleza
    df_cond_final = pd.concat(arquivos_tratados_e_filtrados)

    arquivo_destino = os.path.join(pasta_destino, "condominios_fortaleza.csv")
    arquivo_destino = os.path.abspath(arquivo_destino)

    df_cond_final.to_csv(arquivo_destino, index=False, encoding='latin1')

# %%
"""
### Chamada da função principal de filtrar os condomínios de Fortaleza.
"""

# %%
filtrar_cond_fortaleza()