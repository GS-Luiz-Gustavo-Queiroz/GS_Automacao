import pandas as pd
import unicodedata
import os
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return ''.join(c for c in texto if c.isalnum() or c.isspace()).strip().lower()

def criar_nome_arquivo_saida(arquivo_original, nome_planilha):
    base, _ = os.path.splitext(arquivo_original)
    contador = 1
    while True:
        novo_nome = f"{base}_extraido_{nome_planilha}_{contador}.xlsx"
        if not os.path.exists(novo_nome):
            return novo_nome
        contador += 1

def formatar_contabil(valor):
    if pd.isna(valor):
        return ""
    try:
        valor = float(valor)
        return f"{valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return str(valor)

def converter_xls_para_xlsx(arquivo):
    print(f"Convertendo arquivo .xls para .xlsx: {arquivo}")
    df_dict = pd.read_excel(arquivo, sheet_name=None, engine='xlrd')
    novo_arquivo = arquivo.replace('.xls', '_convertido.xlsx')
    with pd.ExcelWriter(novo_arquivo, engine='openpyxl') as writer:
        for nome, df in df_dict.items():
            df.to_excel(writer, sheet_name=nome, index=False)
    print(f"Arquivo convertido salvo como: {novo_arquivo}")
    return novo_arquivo

def extrair_dados(path):
    if not path.lower().endswith('.xls'):
        print("Formato inválido. Apenas arquivos .xls são suportados.")
        return

    try:
        path_convertido = converter_xls_para_xlsx(path)
        xls = pd.ExcelFile(path_convertido)
        processar_excel(xls, path_convertido, path)
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

def processar_excel(xls, arquivo_convertido, arquivo_original):
    for sheet_name in xls.sheet_names:
        print(f"\nProcessando planilha: {sheet_name}")
        try:
            df = pd.read_excel(arquivo_convertido, sheet_name=sheet_name, header=None)
            processar_dataframe(df, arquivo_original, sheet_name, arquivo_convertido)
        except Exception as e:
            print(f"Erro ao processar planilha {sheet_name}: {e}")

def processar_dataframe(df, arquivo_original, nome_planilha, arquivo_convertido):
    variacoes_cabecalhos = {
        'data': ['data', 'dataocorrencia', 'data_ocorrencia', 'Data_da_Ocorrencia', 'dataocorrência', 'data ocorrência'],
        'saldo': ['saldo', 'saldos', 'sld']
    }

    linha_cabecalho = None

    for idx, linha in df.iterrows():
        linha_normalizada = [normalizar_texto(str(cell)) for cell in linha.values]
        encontrados = {key: False for key in variacoes_cabecalhos}
        for col in linha_normalizada:
            for key, variacoes in variacoes_cabecalhos.items():
                if any(v in col for v in variacoes):
                    encontrados[key] = True
        if all(encontrados.values()):
            linha_cabecalho = idx
            print(f"Cabeçalhos encontrados na linha {linha_cabecalho + 1}")
            break

    if linha_cabecalho is None:
        print("Cabeçalhos não encontrados. Exibindo as primeiras linhas:")
        print(df.head())
        return

    df_final = pd.read_excel(arquivo_convertido, sheet_name=nome_planilha, header=linha_cabecalho)
    df_final = df_final.dropna(how='all')

    colunas_map = {col: normalizar_texto(col) for col in df_final.columns}
    df_final.rename(columns=colunas_map, inplace=True)

    col_data = next((col for col in df_final.columns if 'data' in col), None)
    col_saldo = next((col for col in df_final.columns if 'saldo' in col), None)

    if not col_data or not col_saldo:
        print("Colunas de data ou saldo não foram encontradas.")
        return

    df_final = df_final[[col_data, col_saldo]]
    df_final.columns = ['Data', 'Saldo']

    if linha_cabecalho == 0:
        df_final = df_final.iloc[1:]

    df_final['Saldo'] = df_final['Saldo'].apply(formatar_contabil)
    df_final = df_final[df_final['Saldo'] != '']

    df_final['Data'] = pd.to_datetime(df_final['Data'], errors='coerce', dayfirst=True)
    df_final = df_final.dropna(subset=['Data'])
    df_final = df_final.sort_values(by='Data')

    df_final['data_dia'] = df_final['Data'].dt.date
    df_final = df_final.groupby('data_dia').tail(1)
    df_final.drop(columns=['data_dia'], inplace=True)

    df_final['Data'] = df_final['Data'].dt.strftime('%d/%m/%Y')

    print("\nDados extraídos e filtrados (última data de cada dia):")
    print(df_final.head())

    nome_saida = criar_nome_arquivo_saida(arquivo_original, nome_planilha)

    wb = Workbook()
    ws = wb.active
    ws.title = 'Dados Extraídos'

    for r_idx, row in enumerate(dataframe_to_rows(df_final, index=False, header=True), 1):
        ws.append(row)
        if r_idx > 1:
            ws[f'B{r_idx}'].number_format = '#.##0,00_-'

    wb.save(nome_saida)
    print(f"\nNovo arquivo criado: {nome_saida}")

def SANTANDER_SING(path: str):
    if os.path.isfile(path) and path.lower().endswith('.xls'):
        print(f"\nArquivo recebido: {path}")
        extrair_dados(path)
    else:
        print("Arquivo inválido ou não encontrado. Apenas arquivos .xls são permitidos.")
