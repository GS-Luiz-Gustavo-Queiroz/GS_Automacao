from typing import List, Dict, Optional
import pandas as pd
import unicodedata
import os
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font

def normalizar_texto(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return ''.join(c for c in texto if c.isalnum() or c.isspace()).strip().lower()

def formatar_contabil(valor) -> str:
    if pd.isna(valor):
        return ""
    try:
        valor = float(valor)
        return f"{valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return str(valor)

def identificar_linha_cabecalho(df: pd.DataFrame, variacoes: Dict[str, List[str]]) -> Optional[int]:
    for idx, linha in df.iterrows():
        linha_normalizada = [normalizar_texto(str(cell)) for cell in linha.values]
        encontrados = {key: False for key in variacoes}
        for col in linha_normalizada:
            for key, alias in variacoes.items():
                if any(v in col for v in alias):
                    encontrados[key] = True
        if all(encontrados.values()):
            return idx
    return None

def extrair_saldo_por_dia(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    variacoes_cabecalhos = {
        'data': ['data', 'dataocorrencia', 'data_ocorrencia', 'data_da_ocorrencia', 'dataocorrência', 'data ocorrência'],
        'saldo': ['saldo', 'saldos', 'sld']
    }

    linha_cabecalho = identificar_linha_cabecalho(df, variacoes_cabecalhos)
    if linha_cabecalho is None:
        return None

    df.columns = df.iloc[linha_cabecalho]
    df = df.drop(index=range(0, linha_cabecalho + 1)).dropna(how='all')

    col_data = next((col for col in df.columns if 'data' in normalizar_texto(str(col))), None)
    col_saldo = next((col for col in df.columns if 'saldo' in normalizar_texto(str(col))), None)

    if not all([col_data, col_saldo]):
        return None

    df = df[[col_data, col_saldo]].rename(columns={col_data: 'Data', col_saldo: 'Saldo'})
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
    df['Saldo'] = df['Saldo'].apply(lambda x: float(str(x).replace('.', '').replace(',', '.')) if pd.notna(x) else 0.0)
    df = df.dropna(subset=['Data'])

    df_filtrado = df.sort_values('Data').groupby(df['Data'].dt.date, as_index=False).last()
    df_filtrado['Data'] = pd.to_datetime(df_filtrado['Data']).dt.strftime('%d/%m/%Y')
    df_filtrado['Saldo'] = df_filtrado['Saldo'].apply(formatar_contabil)
    return df_filtrado

def salvar_em_excel(df: pd.DataFrame, caminho: str, nome_aba: str) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = nome_aba

    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)

    for row in ws.iter_rows(min_row=2, min_col=2, max_col=2):
        for cell in row:
            cell.number_format = '#.##0,00_-'
            cell.font = Font(bold=True)

    wb.save(caminho)

def AIRBI(path: str) -> Optional[pd.DataFrame]:
    if not (os.path.isfile(path) and path.lower().endswith('.xlsx')):
        return None

    dataframes_processados = []
    xls = pd.ExcelFile(path)

    for nome_aba in xls.sheet_names:
        df_raw = pd.read_excel(path, sheet_name=nome_aba, header=None)
        df_processado = extrair_saldo_por_dia(df_raw)
        if df_processado is not None:
            caminho_saida = f"saida_{normalizar_texto(nome_aba)}.xlsx"
            salvar_em_excel(df_processado, caminho_saida, 'Saldo por Dia')
            
            df_processado['Origem'] = nome_aba
            dataframes_processados.append(df_processado)

    if not dataframes_processados:
        return None

    return pd.concat(dataframes_processados, ignore_index=True)
