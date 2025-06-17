import pandas as pd
import os

def extrair_e_salvar_colunas(caminho_arquivo):
    extensao = os.path.splitext(caminho_arquivo)[1].lower()

    try:
        if extensao == '.csv':
            df = pd.read_csv(caminho_arquivo, header=1)
        elif extensao in ['.xls', '.xlsx']:
            df = pd.read_excel(caminho_arquivo, header=1)
        else:
            print("Formato de arquivo não suportado.")
            return

        if 'Data Lançamento' not in df.columns or 'Saldo' not in df.columns:
            print("As colunas 'Data Lançamento' e 'Saldo' devem estar presentes.")
            return

        df = df[['Data Lançamento', 'Saldo']].rename(columns={'Data Lançamento': 'Data'})

        df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Data'])

        # Criar coluna apenas com o dia (sem hora)
        df['Data_Dia'] = df['Data'].dt.date

        # Ordenar pela data completa (com hora se houver)
        df = df.sort_values('Data')

        # Pegar a última ocorrência de cada dia
        df_final = df.groupby('Data_Dia', as_index=False).tail(1).copy()

        # Formatar a data para dd/mm/yyyy
        df_final['Data'] = df_final['Data'].dt.strftime("%d/%m/%Y")

        df_final = df_final[['Data', 'Saldo']]

        # Salvar
        novo_caminho = os.path.join(os.path.dirname(caminho_arquivo), 'dados_extraidos.xlsx')
        df_final.to_excel(novo_caminho, index=False)

        print(f"Arquivo salvo com sucesso em: {novo_caminho}")

    except Exception as e:
        print("Erro ao processar o arquivo:", e)

def CEF_FOLK(path: str):
    if os.path.isfile(path):
        print(f"\nArquivo recebido: {path}")
        extrair_e_salvar_colunas(path)
    else:
        print("Arquivo não encontrado:", path)
