import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import unicodedata
import os
import re
from decimal import Decimal, InvalidOperation
from dateutil import parser
import xlrd
from openpyxl import Workbook
from datetime import datetime

class ExtratorDadosFinanceiros:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

    # ======================
    # FUNÇÕES DE PROCESSAMENTO DE VALORES
    # ======================
    
    @staticmethod
    def extrair_valor_numerico(texto):
        """
        Extrai valores numéricos de texto com precisão absoluta
        Versão 4.0 - Totalmente otimizada para dados financeiros brasileiros
        """
        if pd.isna(texto) or not str(texto).strip():
            return None

        texto = str(texto).strip()
        
        # Padrão completo para valores financeiros brasileiros
        padrao_dinheiro = r"""
            (?:R\$\s*)?                  # R$ opcional
            ([-+]?)                       # Sinal (+/-)
            \s*                           # Espaços
            (                             # Parte inteira:
            \d{1,3}(?:\.\d{3})*         # Com separador de milhar
            |\d+                         # Ou sem separador
            )
            (?:                           # Parte decimal:
            ([.,])                       # Separador decimal
            (\d{1,2})                   # 1-2 dígitos decimais
            )?                           # Parte decimal opcional
        """
        
        # Encontra todos os valores no texto
        matches = re.finditer(padrao_dinheiro, texto, re.VERBOSE)
        valores = []
        
        for match in matches:
            sinal, parte_inteira, sep_decimal, parte_decimal = match.groups()
            
            # Limpeza da parte inteira
            if '.' in parte_inteira:
                # Verifica se o ponto é separador de milhar (formato brasileiro)
                if sep_decimal == ',' or (sep_decimal is None and ',' not in texto):
                    parte_inteira = parte_inteira.replace('.', '')
            
            # Construção do número
            numero_str = parte_inteira
            if sep_decimal and parte_decimal:
                # Completa com zeros se necessário
                parte_decimal = parte_decimal.ljust(2, '0')[:2]
                numero_str += '.' + parte_decimal
            
            try:
                valor = Decimal(numero_str)
                if sinal == '-':
                    valor = -valor
                valores.append(float(valor))
            except InvalidOperation:
                continue
        
        # Lógica para selecionar o valor correto
        if not valores:
            return None
        elif len(valores) == 1:
            return valores[0]
        else:
            # Prioriza o maior valor absoluto (mais provável de ser o principal)
            return max(valores, key=abs)

    @staticmethod
    def formatar_moeda_brasileira(valor):
        """Formata valores no padrão brasileiro com precisão"""
        if valor is None or pd.isna(valor):
            return ""
        
        try:
            valor = float(valor)
            # Formata com separadores
            formatado = "{:,.2f}".format(abs(valor))
            
            # Aplica formato brasileiro
            if valor < 0:
                return "-" + formatado.replace(",", "X").replace(".", ",").replace("X", ".")
            return formatado.replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, TypeError):
            return str(valor)

    # ======================
    # FUNÇÕES DE PROCESSAMENTO DE DATAS
    # ======================
    
    @staticmethod
    def parse_data(data_str):
        """Converte datas em vários formatos para DD/MM/YYYY"""
        try:
            if isinstance(data_str, datetime):
                return data_str.strftime('%d/%m/%Y')
            
            data_str = str(data_str).strip()
            
            # Padrões de data suportados
            padroes_data = [
                r'\b\d{2}/\d{2}/\d{4}\b',  # DD/MM/YYYY
                r'\b\d{2}-\d{2}-\d{4}\b',   # DD-MM-YYYY
                r'\b\d{4}-\d{2}-\d{2}\b',   # YYYY-MM-DD
                r'\b\d{8}\b',               # DDMMYYYY
                r'\b\d{1,2}/\d{1,2}/\d{2}\b' # DD/MM/YY
            ]
            
            # Tenta encontrar um padrão correspondente
            for padrao in padroes_data:
                match = re.search(padrao, data_str)
                if match:
                    data_str = match.group()
                    # Padroniza separadores
                    data_str = data_str.replace('-', '/')
                    break
            
            return parser.parse(data_str, dayfirst=True).strftime('%d/%m/%Y')
        except Exception:
            return None

    # ======================
    # FUNÇÕES DE ARQUIVO
    # ======================
    
    def selecionar_arquivo(self):
        """Abre diálogo para seleção de arquivo"""
        return filedialog.askopenfilename(
            title="Selecione o arquivo",
            filetypes=[("Arquivos Excel/CSV", "*.xlsx *.xls *.csv"), ("Todos os arquivos", "*.*")]
        )

    def criar_nome_saida(self, arquivo_original, sufixo="extraido"):
        """Cria nome único para arquivo de saída"""
        base, ext = os.path.splitext(arquivo_original)
        contador = 1
        while True:
            novo_nome = f"{base}_{sufixo}_{contador}.xlsx"
            if not os.path.exists(novo_nome):
                return novo_nome
            contador += 1

    # ======================
    # FUNÇÕES DE PROCESSAMENTO DE ARQUIVOS
    # ======================
    
    def ler_como_html(self, caminho_arquivo):
        """Tenta ler arquivos .xls antigos como HTML"""
        try:
            dfs = pd.read_html(caminho_arquivo, header=0)
            if dfs:
                print("Arquivo .xls lido com sucesso como HTML")
                return dfs[0]
        except Exception as e:
            print(f"Erro ao ler como HTML: {e}")
        return None

    def converter_xls_para_xlsx(self, caminho_arquivo):
        """Converte arquivos .xls antigos para .xlsx"""
        print("Convertendo .xls para .xlsx...")
        try:
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
            print(f"Arquivo convertido: {novo_arquivo}")
            return novo_arquivo
        except Exception as e:
            print(f"Falha na conversão: {e}")
            return None

    # ======================
    # FUNÇÕES DE PROCESSAMENTO DE DADOS
    # ======================
    
    def encontrar_linha_saldo_inicial(self, df):
        """Encontra linha com 'saldo inicial'"""
        for idx, linha in df.iterrows():
            if any('saldo inicial' in str(cell).lower() for cell in linha.values):
                return idx
        return None

    def normalizar_texto(self, texto):
        """Normaliza texto removendo acentos e caracteres especiais"""
        if not isinstance(texto, str):
            return ""
        texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
        return ''.join(c for c in texto if c.isalnum() or c.isspace()).strip().lower()

    def extrair_de_texto_nao_estruturado(self, texto):
        """Extrai dados financeiros de texto não estruturado"""
        # Extrai datas
        datas = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', texto)
        
        # Extrai valores
        valores = []
        for parte in re.split(r'\s+', texto):
            valor = self.extrair_valor_numerico(parte)
            if valor is not None:
                valores.append(valor)
        
        if len(datas) >= 1 and len(valores) >= 2:
            return {
                'Data': datas[0],
                'Valor': valores[0],
                'Saldo': valores[-1]
            }
        return None

    def processar_dataframe(self, df):
        """Processa DataFrame para extrair colunas financeiras"""
        if df.empty or len(df.columns) < 2:
            print("DataFrame vazio ou inválido")
            return None

        # Remove linha de saldo inicial
        linha_saldo = self.encontrar_linha_saldo_inicial(df)
        if linha_saldo is not None:
            print(f"Removendo 'saldo inicial' na linha {linha_saldo + 1}")
            df = df.iloc[linha_saldo + 1:]

        # Tenta normalizar cabeçalhos
        try:
            if df.shape[0] > 1:
                df.columns = [self.normalizar_texto(str(col)) for col in df.iloc[0]]
                df = df.iloc[1:]
        except Exception as e:
            print(f"Erro ao normalizar colunas: {e}")
            df.columns = [f"Coluna_{i}" for i in range(len(df.columns))]

        # Mapeamento de colunas
        mapeamento_colunas = {
            'data': ['data', 'datareferencia', 'dataemissao', 'dt'],
            'valor': ['valor', 'valores', 'vlr', 'montante'],
            'saldo': ['saldo', 'saldos', 'sld']
        }

        # Identifica colunas relevantes
        colunas_encontradas = {}
        for col in df.columns:
            col_normalizada = self.normalizar_texto(str(col))
            for tipo, possiveis in mapeamento_colunas.items():
                if any(p in col_normalizada for p in possiveis):
                    colunas_encontradas[tipo] = col
                    break

        # Se encontrou todas colunas necessárias
        if all(k in colunas_encontradas for k in ['data', 'valor', 'saldo']):
            df_final = df[[colunas_encontradas['data'], 
                         colunas_encontradas['valor'], 
                         colunas_encontradas['saldo']]].copy()
            df_final.columns = ['Data', 'Valor', 'Saldo']
        else:
            print("Colunas padrão não encontradas. Extraindo de texto não estruturado...")
            dados_extraidos = []
            
            for _, linha in df.iterrows():
                linha_texto = ' '.join(str(cell) for cell in linha.values)
                dados = self.extrair_de_texto_nao_estruturado(linha_texto)
                if dados:
                    dados_extraidos.append(dados)
            
            if dados_extraidos:
                df_final = pd.DataFrame(dados_extraidos)
            else:
                print("Não foi possível extrair dados válidos")
                print("Colunas disponíveis:", df.columns.tolist())
                return None

        # Processamento final
        df_final['Data'] = df_final['Data'].apply(self.parse_data)
        df_final['Valor'] = df_final['Valor'].apply(self.extrair_valor_numerico)
        df_final['Saldo'] = df_final['Saldo'].apply(self.extrair_valor_numerico)
        
        # Formatação
        df_final['Valor'] = df_final['Valor'].apply(self.formatar_moeda_brasileira)
        df_final['Saldo'] = df_final['Saldo'].apply(self.formatar_moeda_brasileira)
        
        # Limpeza
        df_final = df_final.dropna(subset=['Data', 'Valor', 'Saldo'], how='all')
        df_final = df_final[(df_final['Valor'].notna()) | (df_final['Saldo'].notna())]
        
        # Remove últimas linhas (totais/rodapé)
        if len(df_final) > 4:
            df_final = df_final.iloc[:-4]

        return df_final

    def processar_arquivo(self, caminho_arquivo):
        """Processa o arquivo de acordo com seu formato"""
        if caminho_arquivo.lower().endswith('.xls'):
            df = self.ler_como_html(caminho_arquivo)
            if df is not None:
                return {"Planilha_HTML": df}, "HTML"
            else:
                novo_arquivo = self.converter_xls_para_xlsx(caminho_arquivo)
                if novo_arquivo:
                    caminho_arquivo = novo_arquivo
                else:
                    return None, None
        
        try:
            if caminho_arquivo.lower().endswith(('.xlsx', '.xls')):
                xls = pd.ExcelFile(caminho_arquivo)
                planilhas = {}
                for nome in xls.sheet_names:
                    print(f"\nProcessando planilha: {nome}")
                    df = pd.read_excel(xls, sheet_name=nome, header=None)
                    planilhas[nome] = df
                return planilhas, "Excel"
            elif caminho_arquivo.lower().endswith('.csv'):
                codificacoes = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
                separadores = [',', ';', '\t']
                for codificacao in codificacoes:
                    for sep in separadores:
                        try:
                            df = pd.read_csv(caminho_arquivo, header=None, encoding=codificacao, sep=sep)
                            print(f"CSV lido com encoding {codificacao} e separador '{sep}'")
                            return {"CSV": df}, "CSV"
                        except:
                            continue
                print("Falha ao ler arquivo CSV")
                return None, None
            else:
                print("Formato não suportado")
                return None, None
        except Exception as e:
            print(f"Erro ao processar arquivo: {e}")
            return None, None

    def executar(self):
        """Método principal de execução"""
        caminho_arquivo = self.selecionar_arquivo()
        if not caminho_arquivo:
            print("Nenhum arquivo selecionado")
            return
        
        print(f"\nProcessando arquivo: {caminho_arquivo}")
        
        dados, tipo = self.processar_arquivo(caminho_arquivo)
        if dados is None:
            messagebox.showerror("Erro", "Falha ao processar o arquivo")
            return
        
        resultados = []
        for nome_planilha, df in dados.items():
            print(f"\nProcessando: {nome_planilha}")
            
            df_processado = self.processar_dataframe(df)
            if df_processado is None:
                print(f"Não foi possível extrair dados de {nome_planilha}")
                continue
            
            nome_saida = self.criar_nome_saida(caminho_arquivo, f"extraido_{nome_planilha}")
            df_processado.to_excel(nome_saida, index=False)
            
            print(f"\nDados salvos em: {nome_saida}")
            print(f"Total de linhas: {len(df_processado)}")
            print("Primeiras linhas:")
            print(df_processado.head())
            
            resultados.append({
                'planilha': nome_planilha,
                'arquivo': nome_saida,
                'linhas': len(df_processado)
            })
        
        if resultados:
            resumo = "\n".join(
                f"- {res['planilha']}: {res['linhas']} linhas → {res['arquivo']}"
                for res in resultados
            )
            messagebox.showinfo(
                "Processamento Concluído",
                f"Dados extraídos com sucesso:\n\n{resumo}"
            )
        else:
            messagebox.showwarning(
                "Aviso",
                "Nenhum dado financeiro válido foi encontrado"
            )

if __name__ == "__main__":
    extrator = ExtratorDadosFinanceiros()
    extrator.executar()