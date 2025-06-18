import pandas as pd
import unicodedata
import os
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font

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

def extrair_dados(path):
    try:
        xls = pd.ExcelFile(path)
        for sheet_name in xls.sheet_names:
            print(f"\nProcessando planilha: {sheet_name}")
            try:
                df = pd.read_excel(path, sheet_name=sheet_name, header=None)
                processar_dataframe(df, path, sheet_name)
            except Exception as e:
                print(f"Erro ao processar planilha {sheet_name}: {e}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

def processar_dataframe(df, arquivo, nome_planilha):
    variacoes_cabecalhos = {
        'data': ['data', 'dataocorrencia', 'data_ocorrencia', 'data_da_ocorrencia', 'dataocorrência', 'data ocorrência'],
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
            break

    if linha_cabecalho is not None:
        print(f"Encontrados cabeçalhos na linha {linha_cabecalho + 1}")

        df.columns = df.iloc[linha_cabecalho]
        df = df.drop(index=range(0, linha_cabecalho + 1))
        df = df.dropna(how='all')

        col_data = next((col for col in df.columns if 'data' in normalizar_texto(str(col))), None)
        col_saldo = next((col for col in df.columns if 'saldo' in normalizar_texto(str(col))), None)

        if not all([col_data, col_saldo]):
            print("As colunas esperadas não foram encontradas")
            return

        df = df[[col_data, col_saldo]].rename(columns={col_data: 'Data', col_saldo: 'Saldo'})

        df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        df['Saldo'] = df['Saldo'].apply(lambda x: float(str(x).replace('.', '').replace(',', '.')) if pd.notna(x) else 0.0)
        df = df.dropna(subset=['Data'])

        df_filtrado = df.sort_values('Data').groupby(df['Data'].dt.date, as_index=False).last()
        df_filtrado['Data'] = pd.to_datetime(df_filtrado['Data']).dt.strftime('%d/%m/%Y')
        df_filtrado['Saldo'] = df_filtrado['Saldo'].apply(formatar_contabil)

        nome_saida = criar_nome_arquivo_saida(arquivo, nome_planilha)
        wb = Workbook()
        ws = wb.active
        ws.title = 'Saldo por Dia'

        for r in dataframe_to_rows(df_filtrado, index=False, header=True):
            ws.append(r)

        for row in ws.iter_rows(min_row=2, min_col=2, max_col=2):
            for cell in row:
                cell.number_format = '#.##0,00_-'
                cell.font = Font(bold=True)

        wb.save(nome_saida)
        print(f"\nNovo arquivo criado: {nome_saida}")
    else:
        print("Cabeçalhos não encontrados. Visualização das primeiras linhas:")
        print(df.head())

def AIRBI(path: str):
    if os.path.isfile(path) and path.lower().endswith('.xlsx'):
        print(f"\nArquivo recebido: {path}")
        extrair_dados(path)
    else:
        print(f"Arquivo inválido ou não encontrado: {path}")
