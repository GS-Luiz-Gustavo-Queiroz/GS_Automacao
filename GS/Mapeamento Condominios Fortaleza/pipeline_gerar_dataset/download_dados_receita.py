# %%
"""
Códigos para obtenção de dados da receita </br>
Após esses códigos, usaremos os códigos feitos anteriormente para tratar os dados e também iremos cruzar esses dados com o anterior para excluir cpnjs que já não existem com novos cnpjs.
"""

# %%
"""
link [https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/2025-06/] </br>
obs.: como iremos rodar mensalmente, essa data iremos passar como parametro </br>
então o link será do tipo [https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/{ano}-{mes}/]

obs.: link para o mapeamento desse dataset [https://www.gov.br/receitafederal/dados/cnpj-metadados.pdf] </br>
      link para obtenção dos dados [https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/]
"""

# %%
import os
import requests
import datetime
import zipfile
from tqdm import tqdm

# %%
"""
OBS.: Faremos o código para capturar os dados das Empresas, para incrementar com a razão social nosso dataset dos estabelecimento de condominios residenciais em Fortaleza.
"""

# %%
"""
**Função download, descompactação e renomeação dos arquivos das Empresas:**
"""
def remover_arquivos(diretorio):
    arquivos = os.listdir(diretorio)

    for arquivo in arquivos:
        para_excluir = os.path.join(diretorio, arquivo)
        para_excluir = os.path.abspath(para_excluir)
        os.remove(para_excluir)

# %%
def download_empresas(): #função para download dos arquivos Empresas, descompactação e renomeação
    print("Parte 1.1/3")
    pbar = tqdm(total = 100)

    #criando uma pasta irmã para ser o destino dos arquivos baixados
    pasta_atual = os.getcwd()
    pasta_irma = os.path.join(pasta_atual, '..', "empresas")
    pasta_irma = os.path.abspath(pasta_irma)
    os.makedirs(pasta_irma, exist_ok=True)

    remover_arquivos(pasta_irma)

    #obtencao do mes e ano
    ano = datetime.datetime.now().year
    mes = datetime.datetime.now().month
    if mes < 10:
        mes = "0"+str(mes)
    data = str(ano)+"-"+mes
    
    #condicao do while e iterador dos arquivos no site
    #condicao e: se jogar um erro no try (o iterador passar da qtdd de arquivo) o except torna a condition False
    condition = True
    iter = 0

    #captura, baixa todos os arquivos com nome do tipo "Empresas_.zip"
    while(condition):
        
        try:
            url = f"https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/{data}/Empresas{str(iter)}.zip"

            caminho_arquivo = os.path.join(pasta_irma, f"Empresas{iter}.zip") #pasta de dados baixados

            #codigo para baixar arquivo da vez no loop while
            with requests.get(url, stream=True) as resposta:
                resposta.raise_for_status()
                with open(caminho_arquivo, "wb") as arquivo:
                    for chunk in resposta.iter_content(chunk_size=8192):
                        arquivo.write(chunk)

            #extracao do zip baixado no loop atual
            with zipfile.ZipFile(caminho_arquivo, 'r') as zip_ref:
                zip_ref.extractall(pasta_irma)

            print(f"Download Empresas{iter} concluído! Arquivo salvo em: {caminho_arquivo}")
            pbar.update(10)
        
            #depois do arquivo extraido, remove o .zip
            os.remove(caminho_arquivo)
            
            iter = iter + 1
        except:
            condition = False

    
    #agora irei renomear o nome dos arquivos
    arquivos_extraidos = os.listdir(pasta_irma)
    arquivos_extraidos

    indice = 0
    for arquivo in arquivos_extraidos:
        nome_antigo = os.path.join(pasta_irma, arquivo)
        nome_novo = os.path.join(pasta_irma, f"Empresas{indice}.csv")

        try:
            os.rename(nome_antigo, nome_novo)
        except:
            os.remove(nome_novo)
            os.rename(nome_antigo, nome_novo)

        indice = indice + 1
    

# %%
def download_estabelecimentos(): #função para download dos arquivos Estabelecimentos, descompactação e renomeação

    print("Parte 1.2/3")
    pbar = tqdm(total = 100)
    #criando uma pasta irmã para ser o destino dos arquivos baixados
    pasta_atual = os.getcwd()
    pasta_irma = os.path.join(pasta_atual, '..', "estabelecimentos")
    pasta_irma = os.path.abspath(pasta_irma)
    os.makedirs(pasta_irma, exist_ok=True)

    remover_arquivos(pasta_irma)

    #obtencao do mes e ano
    ano = datetime.datetime.now().year
    mes = datetime.datetime.now().month
    if mes < 10:
        mes = "0"+str(mes)
    data = str(ano)+"-"+mes
    
    #condicao do while e iterador dos arquivos no site
    #condicao e: se jogar um erro no try (o iterador passar da qtdd de arquivo) o except torna a condition False
    condition = True
    iter = 0

    while(condition):
        
        try:
            url = f"https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/{data}/Estabelecimentos{str(iter)}.zip"

            caminho_arquivo = os.path.join(pasta_irma, f"Estabelecimentos{iter}.zip") #pasta de dados baixados

            #codigo para baixar arquivo da vez no loop while
            with requests.get(url, stream=True) as resposta:
                resposta.raise_for_status()
                with open(caminho_arquivo, "wb") as arquivo:
                    for chunk in resposta.iter_content(chunk_size=8192):
                        arquivo.write(chunk)
            
            #extracao do zip baixado no loop atual
            with zipfile.ZipFile(caminho_arquivo, 'r') as zip_ref:
                zip_ref.extractall(pasta_irma)

            print(f"Download Estabelecimentos{iter} concluído! Arquivo salvo em: {caminho_arquivo}")
            pbar.update(10)

            #depois do arquivo extraido, remove o .zip
            os.remove(caminho_arquivo)
        
            iter = iter + 1
        except:
            condition = False

    #agora irei renomear o nome dos arquivos
    arquivos_extraidos = os.listdir(pasta_irma)
    arquivos_extraidos

    indice = 0
    for arquivo in arquivos_extraidos:
        nome_antigo = os.path.join(pasta_irma, arquivo)
        nome_novo = os.path.join(pasta_irma, f"Estabelecimentos{indice}.csv")

        try:
            os.rename(nome_antigo, nome_novo)
        except:
            os.remove(nome_novo)
            os.rename(nome_antigo, nome_novo)

        indice = indice + 1


# %%
def download_dados_estabelecimentos_empresas():
    print("Executando download dos dados da Receita")
    print("Parte 1/3")
    download_empresas()
    download_estabelecimentos()

# %%
# download_dados_estabelecimentos_empresas()