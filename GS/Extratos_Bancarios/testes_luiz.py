from modelos.BB_CONDO_PREST.app import bb_condoprest

df = bb_condoprest('modelos/BB_CONDO_PREST/BB - CONDO PREST - 00.pdf')

df.to_excel('planilha_formatada.xlsx', index=False)
