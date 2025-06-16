import pandas as pd
import tkinter as tk
from tkinter import filedialog
import unicodedata
import os
import platform
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font

def converter_xls_para_xlsx(caminho_arquivo):
    import xlrd
    from openpyxl import Workbook

    if not caminho_arquivo.lower().endswith('.xls'):
        return caminho_arquivo 

    print("Convertendo .xls para .xlsx...")
    wb_xls = xlrd.open_workbook(caminho_arquivo)
    pasta = os.path.dirname(caminho_arquivo)
    nome = os.path.splitext(os.path.basename(caminho_arquivo))[0]
    novo_arquivo = os.path.join(pasta, nome + '.xlsx')

    wb_xlsx = Workbook()
    ws_xlsx = wb_xlsx.active
    sheet = wb_xls.sheet_by_index(0)

    for row in range(sheet.nrows):
        ws_xlsx.append(sheet.row_values(row))

    wb_xlsx.save(novo_arquivo)
    print(f"Arquivo convertido para: {novo_arquivo}")
    return novo_arquivo

def selecionar_arquivo():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="Selecione o arquivo",
        filetypes=[("Arquivos Excel/CSV", "*.xlsx *.xls *.csv"), ("Todos os arquivos", "*.*")]
    )

def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return ''.join(c for c in texto if c.isalnum() or c.isspace()).strip().lower()

def criar_nome_arquivo_saida(arquivo_original, nome_planilha):
    base, ext = os.path.splitext(arquivo_original)
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

def extrair_dados(arquivo):
    if arquivo.lower().endswith('.xls'):
        arquivo = converter_xls_para_xlsx(arquivo)

    try:
        if arquivo.lower().endswith(('.xlsx', '.xls')):
            xls = pd.ExcelFile(arquivo)
            processar_excel(xls, arquivo)
        elif arquivo.lower().endswith('.csv'):
            processar_csv(arquivo)
        else:
            print("Formato de arquivo não suportado.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

def processar_excel(xls, arquivo):
    for sheet_name in xls.sheet_names:
        print(f"\nProcessando planilha: {sheet_name}")
        try:
            df = pd.read_excel(arquivo, sheet_name=sheet_name, header=None)
            processar_dataframe(df, arquivo, sheet_name)
        except Exception as e:
            print(f"Erro ao processar planilha {sheet_name}: {e}")

def processar_csv(arquivo):
    print("\nProcessando arquivo CSV")
    encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    separadores = [',', ';', '\t']
    for encoding in encodings:
        for sep in separadores:
            try:
                df = pd.read_csv(arquivo, header=None, encoding=encoding, sep=sep)
                print(f"Arquivo lido com encoding {encoding} e separador '{sep}'")
                processar_dataframe(df, arquivo, "CSV")
                return
            except:
                continue
    print("Não foi possível ler o arquivo CSV")

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

def main():
    arquivo = selecionar_arquivo()
    if arquivo:
        print(f"\nArquivo selecionado: {arquivo}")
        extrair_dados(arquivo)
    else:
        print("Nenhum arquivo selecionado.")

if __name__ == "__main__":
    main()
