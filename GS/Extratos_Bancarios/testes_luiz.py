from modelos.BB_CONDO_PREST.app import bb_condoprest
from modelos.BRADESCO_HISYSTEM.app import bradesco_hisystem
from modelos.INTER_SING.app import inter_sing
import pandas as pd

#df = bb_condoprest('modelos/BB_CONDO_PREST/BB - CONDO PREST - 00.pdf')
# df = bradesco_hisystem('modelos/BRADESCO_HISYSTEM/Bradesco_HISYSTEM 09062025_101125.CSV')
df = inter_sing('modelos/INTER_SING/INTER SING 08 Extrato-11-05-2025-a-09-06-2025.csv')
df.to_excel('planilha_formatada.xlsx', index=False)
