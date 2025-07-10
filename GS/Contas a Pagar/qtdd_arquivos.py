import os

arquivos = []

pasta_atual = os.getcwd()
pasta_atual = os.path.abspath(pasta_atual)
# print(pasta_atual)

def qttd_arquivos(pasta, arquivos):

    for arquivo in os.listdir(pasta):
        arquivo = os.path.join(pasta, arquivo)
        arquivo = os.path.abspath(arquivo)

        if os.path.isfile(arquivo):
            arquivos.append(arquivo)

        if os.path.isdir(arquivo):
            nova_pasta = os.path.join(pasta, arquivo)
            nova_pasta = os.path.abspath(nova_pasta)
            qttd_arquivos(nova_pasta, arquivos)

qttd_arquivos(pasta_atual, arquivos)
print(len(arquivos))