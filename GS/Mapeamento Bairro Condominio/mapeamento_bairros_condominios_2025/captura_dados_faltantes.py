import requests
import pandas as pd
import numpy as np
import json
import time
import os

def captura_dados_faltantes_api(nome_do_arquivo):
    dataset = pd.read_csv((nome_do_arquivo), dtype=str, encoding='latin1') #carregando csv do dataset
    dataset.insert(2, 'razao_social', np.nan) #adicao de coluna razao_social

    cnpjs_para_consulta = dataset["cnpj"].str.replace('/', '').str.replace('-', '') #removendo / e - dos cnpj para consultar

    for i in range(0, dataset.shape[0]):

        

        cnpj = cnpjs_para_consulta[i] #cnpj do registro atual do loop
        dados_cnpj = requests.get(f"https://publica.cnpj.ws/cnpj/{cnpj}") #consulta na api
        empresa = dados_cnpj.json() #dados json da empresa relacionada ao cnpj

        razao_social = empresa["razao_social"]
        nome_fantasia = empresa["estabelecimento"]["nome_fantasia"]
        ddd1 = empresa["estabelecimento"]["ddd1"]
        telefone1 = empresa["estabelecimento"]["telefone1"]
        ddd2 = empresa["estabelecimento"]["ddd2"]
        telefone2 = empresa["estabelecimento"]["telefone2"]
        ddd_fax = empresa["estabelecimento"]["ddd_fax"]
        fax = empresa["estabelecimento"]["fax"]
        email = empresa["estabelecimento"]["email"]

        #a logica desses try catch é: se no dataset o dado é "vazio" NaN,
        # então verificamos se o dado vindo da consulta não é vazio, e então atribuimos o dado
        try:
            np.isnan(dataset["razao_social"][i])
            if(razao_social == None):
                pass
            else:
                dataset["razao_social"][i] = razao_social
        except:
            pass

        try:
            np.isnan(dataset["nome_fantasia"][i])
            if(nome_fantasia == None):
                pass
            else:
                dataset["nome_fantasia"][i] = nome_fantasia
        except:
            pass

        try:
            np.isnan(dataset["ddd1"][i])
            if(ddd1 == None):
                pass
            else:
                dataset["ddd1"][i] = ddd1
        except:
            pass

        try:
            np.isnan(dataset["telefone1"][i])
            if(telefone1 == None):
                pass
            else:
                dataset["telefone1"][i] = telefone1
        except:
            pass

        try:
            np.isnan(dataset["ddd2"][i])
            if(ddd2 == None):
                pass
            else:
                dataset["ddd2"][i] = ddd2
        except:
            pass

        try:
            np.isnan(dataset["telefone2"][i])
            if(telefone2 == None):
                pass
            else:
                dataset["telefone2"][i] = telefone2   
        except:
            pass

        try:
            np.isnan(dataset["ddd_fax"][i])
            if(ddd_fax == None):
                pass
            else:
                dataset["ddd_fax"][i] = ddd_fax
        except:
            pass

        try:
            np.isnan(dataset["fax"][i])
            if(fax == None):
                pass
            else:
                dataset["fax"][i] = fax
        except:
            pass

        try:
            np.isnan(dataset["email"][i])
            if(email == None):
                pass
            else:
                dataset["email"][i] = email
        except:
            pass

        os.system('cls' if os.name == 'nt' else 'clear') #limpar terminal

        
        print(f"{i+1} de {len(dataset)}")
        time.sleep(21)

    dataset.to_csv("incrementado_"+nome_do_arquivo, index=False, encoding='latin1')
    