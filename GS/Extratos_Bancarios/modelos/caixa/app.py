import pandas as pd
import unicodedata
import os

def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return ''.join(c for c in texto if c.isalnum() or c.isspace()).strip().lower()

def criar_nome_arquivo_saida(arquivo, sufixo=""):
    base, ext = os.path.splitext(arquivo)
    novo_nome = f"{base}_{sufixo}.xlsx" if sufixo else f"{base}.xlsx"
    contador = 1
    while os.path.exists(novo_nome):
        novo_nome = f"{base}_{sufixo}_{contador}.xlsx" if sufixo else f"{base}_{contador}.xlsx"
        contador += 1
    return novo_nome

def detectar_delimitador(arquivo):
    with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
        linha = f.readline()
        for sep in [',',';','\t','|']:
            if sep in linha:
                return sep
    return None

def carregar_dados(arquivo):
    ext = arquivo.lower().split('.')[-1]
    if ext in ['xls', 'xlsx']:
        df = pd.read_excel(arquivo)
    elif ext == 'csv':
        sep = detectar_delimitador(arquivo) or ','
        df = pd.read_csv(arquivo, sep=sep, encoding='utf-8', on_bad_lines='skip')
    elif ext == 'txt':
        sep = detectar_delimitador(arquivo) or '\t'
        df = pd.read_csv(arquivo, sep=sep, encoding='utf-8', on_bad_lines='skip')
    else:
        raise ValueError("Formato de arquivo não suportado")
    return df

def encontrar_colunas(df):
    variacoes_data = ['data', 'data_mov', 'dataocorrencia', 'data_ocorrencia', 'data movimentacao', 'data_movimentacao']
    variacoes_valor = ['valor', 'valores', 'vlr', 'val', 'montante']
    variacoes_debcred = ['deb_cred', 'debito_credito', 'debcre', 'credito_debito', 'tipo']

    col_data = col_valor = col_debcred = None

    for col in df.columns:
        col_norm = normalizar_texto(str(col))
        if any(v in col_norm for v in variacoes_data) and col_data is None:
            col_data = col
        if any(v in col_norm for v in variacoes_valor) and col_valor is None:
            col_valor = col
        if any(v in col_norm for v in variacoes_debcred) and col_debcred is None:
            col_debcred = col

    if col_data is None or col_valor is None or col_debcred is None:
        raise ValueError("Não foi possível encontrar as colunas 'Data_Mov', 'Valor' e 'Deb_Cred'")

    return col_data, col_valor, col_debcred

def processar_saldos_por_dia(df, col_data, col_valor, col_debcred):
    # Converter data
    df[col_data] = pd.to_datetime(df[col_data], format='%Y%m%d', errors='coerce')
    df = df.dropna(subset=[col_data, col_valor, col_debcred])

    # Normalizar coluna Deb_Cred
    df[col_debcred] = df[col_debcred].astype(str).str.strip().str.upper()

    # Converter valor para float
    df[col_valor] = pd.to_numeric(df[col_valor], errors='coerce')
    df = df.dropna(subset=[col_valor])

    # Aplicar sinal negativo aos débitos
    df['Valor_Ajustado'] = df.apply(
        lambda row: -row[col_valor] if row[col_debcred] == 'D' else row[col_valor],
        axis=1
    )

    # Agrupar por data e somar
    resultado = df.groupby(df[col_data].dt.strftime('%d/%m/%Y'))['Valor_Ajustado'].sum().reset_index()
    resultado.columns = ['Data', 'Saldo']

    return resultado

def salvar_resultado(resultado, arquivo_origem):
    nome_saida = criar_nome_arquivo_saida(arquivo_origem, "saldo_por_dia")
    resultado.to_excel(nome_saida, index=False)
    print(f"\nArquivo com saldo diário salvo em:\n{os.path.abspath(nome_saida)}")

def CAIXA(path: str):
    try:
        df = carregar_dados(path)
        col_data, col_valor, col_debcred = encontrar_colunas(df)
        resultado = processar_saldos_por_dia(df, col_data, col_valor, col_debcred)
        salvar_resultado(resultado, path)
    except Exception as e:
        print(f"Erro ao processar '{path}': {e}")
