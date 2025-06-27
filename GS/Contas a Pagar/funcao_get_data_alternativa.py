def get_data(self) -> pd.DataFrame:
        try:
            # Cria a conexão.
            conn = pymssql.connect(server=self.creds['s'], user=self.creds['u'],
                                   password=self.creds['p'], database=self.creds['d'])
            # Cria o cursor.
            cursor = conn.cursor()
            # Realiza a consulta da tabela da pedidos.
            cursor.execute("""
                SELECT
                    EMP.Nome,
                    PED.EST_Codigo,
                    EST.Nome AS EST_Nome,
                    VCP.[Data] AS DT_VENCIMENTO,
                    DPE.[Path] AS CAMINHO_ARQUIVO,
                    PED.CODIGO AS CODIGO_PEDIDO,
                    CPG.Codigo AS CODIGO_CONTAS_PAGAR,
                    VCP.Sequencial AS SEQUENCIAL_CONTAS_PAGAR,
                    PED.CampoExtra1 AS CONTAS_AVULSAS,
                    PED.CampoExtra2 AS FORMA_PAGAMENTO,
                    PED.CampoExtra3 AS NOTA,
                    PED.CampoExtra4 AS SETOR,
                    PED.CAMPOEXTRA6 AS TIPO
                FROM PED
                LEFT JOIN DPE
                    ON DPE.EMP_Codigo = PED.EMP_CODIGO AND DPE.PED_Codigo = PED.CODIGO
                LEFT JOIN CPG
                    ON CPG.EMP_Codigo = PED.EMP_CODIGO AND CPG.Codigo = PED.CPG_CODIGO
                LEFT JOIN VCP
                    ON VCP.EMP_Codigo = CPG.EMP_Codigo AND VCP.CPG_Codigo = CPG.Codigo
                LEFT JOIN EST
                    ON EST.EMP_Codigo = PED.EMP_Codigo AND EST.Codigo = PED.EST_Codigo
                LEFT JOIN EMP
                    ON EST.EMP_Codigo = EMP.Codigo;
                """)
            """
                Criação de uma lista que irá guardar os resultados da consulta, onde cada item do dicionário será
            um dicionário, com as chaves 'ped_codigo', que é o código do pedido, e 'path' que é o caminho até o arquivo
            referente ao pedido.
            """
            columns = ['Grupo', 'EST_Codigo', 'EST_nome', 'dt_vencimento', 'path', 'cod_ped', 'COD_cpg', 'sequencial', 'contas_avulsas', 'forma_pag', 'nota', 'setor', 'tipo']
            df = pd.DataFrame(cursor.fetchall(), columns=columns)
            #apagar dps
            df.to_excel("teste.xlsx", index=False)
            # Remove valores nulos.
            df.dropna( inplace=True)
            # Remove valores do df com datas acima da data mínima.
            df = self.filtra_data(df)
            # Corrige a coluna dt_vencimento.
            df['dt_vencimento'] = df['dt_vencimento'].dt.strftime('%d-%m-%Y')
            # Encerrando a conexão
            conn.close()
            cursor.close()

            return df
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")