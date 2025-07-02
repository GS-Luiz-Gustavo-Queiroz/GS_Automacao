import pymssql
import pandas as pd

def get_data(server, user, password, database):
    try:
        # Cria a conexão.
        conn = pymssql.connect(server=server, user=user,
                                password=password, database=database, tds_version="7.0")
        # Cria o cursor.
        cursor = conn.cursor()
        # Realiza a consulta da tabela da pedidos.
        cursor.execute("""
            SELECT 
            SYS.M0_CGC AS  EMPRESA, 
            SYS.M0_FILIAL  AS NOME_EMPRESA, 
            SE1.E1_NUM AS NUM_TITULO, 
            SE1.E1_TIPO AS TIPO, 
            SA1.A1_CGC AS CNPJ_CLI, 
            SE1.E1_NOMCLI AS DESC_CLI,
            SA1.A1_EMAIL AS EMAIL_CLI,
            SE1.E1_BAIXA AS DT_BAIXA,
            SE1.E1_EMISSAO AS DT_EMISSAO, -- usar como principal para DRE
            SE1.E1_VENCTO AS DT_VENCIMENTO
            --SF2010.F2_VALBRUT AS VALOR_BRUTO, --valor bruto, não utilizar
            --SE1.E1_VALOR AS VALOR_TITULO, --valor bruto, utilizar para DRE
            --SE1.E1_VALOR - (SE1.E1_VRETIRF + SE1.E1_VRETISS + SE1.E1_INSS + SE1.E1_PIS + SE1.E1_COFINS + SE1.E1_CSLL) AS VALOR_LIQUIDO
            FROM C7FTHA_136941_PR_PD.dbo.SE1010 SE1
            LEFT JOIN C7FTHA_136941_PR_PD.dbo.SA1010 SA1 ON SA1.A1_COD = SE1.E1_CLIENTE  AND SA1.A1_LOJA = SE1.E1_LOJA AND SA1.D_E_L_E_T_ = ''
            LEFT JOIN C7FTHA_136941_PR_PD.dbo.SED010 ED ON ED.ED_CODIGO = SE1.E1_NATUREZ AND  ED.D_E_L_E_T_ = ''
            LEFT JOIN C7FTHA_136941_PR_PD.dbo.SC5010 (NOLOCK)
            ON SC5010.C5_NOTA = SE1.E1_NUM AND SC5010.C5_CLIENTE = SE1.E1_CLIENTE AND SC5010.C5_LOJACLI = SE1.E1_LOJA AND SC5010.C5_FILIAL = SE1.E1_FILORIG AND SC5010.D_E_L_E_T_ <> '*'
            LEFT JOIN C7FTHA_136941_PR_PD.dbo.SA1010 (NOLOCK)
            ON SA1010.A1_COD = SE1.E1_CLIENTE AND SA1010.A1_LOJA = SE1.E1_LOJA AND SA1010.D_E_L_E_T_ <> '*'
            LEFT JOIN C7FTHA_136941_PR_PD.dbo.SF2010 (NOLOCK)
            ON SF2010.F2_DOC = SE1.E1_NUM AND SF2010.F2_CLIENTE = SE1.E1_CLIENTE AND SF2010.F2_LOJA = SE1.E1_LOJA AND SF2010.F2_FILIAL = SE1.E1_FILORIG AND SF2010.D_E_L_E_T_ <> '*'
            LEFT JOIN C7FTHA_136941_PR_PD.dbo.SYS_COMPANY SYS (nolock) ON SYS.M0_CODFIL = SE1.E1_FILIAL AND SYS.D_E_L_E_T_ = ''
            WHERE SE1.E1_TIPO IN ('NF') 
            AND SE1.D_E_L_E_T_ = ''
            AND SE1.E1_FILIAL NOT IN ('020101', '030101','050101','060101')
            AND SE1.E1_VENCTO BETWEEN GETDATE()-5 AND GETDATE()-4
            AND SE1.E1_BAIXA = ''
            AND LEFT(SE1.E1_FILIAL,2) = '01'
            """)
        columns = ['cnpj', 'empresa', 'num_titulo', 'tipo', 'cnpj_cli', 'desc_cli', 'email_cli', 'dt_baixa', 'dt_emissao', 'dt_vencimento']
        df = pd.DataFrame(cursor.fetchall(), columns=columns)
        
        # Encerrando a conexão
        conn.close()
        cursor.close()

        return df
    except Exception as e:
        print(f"Erro ao capturar dados: {e}")