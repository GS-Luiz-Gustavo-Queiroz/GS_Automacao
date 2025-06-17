from modelos.BB_CONDO_PREST.app import bb_condoprest
from modelos.BRADESCO_HISYSTEM.app import bradesco_hisystem
import pandas as pd

#df = bb_condoprest('modelos/BB_CONDO_PREST/BB - CONDO PREST - 00.pdf')
df = bradesco_hisystem('modelos/BRADESCO_HISYSTEM/Bradesco_HISYSTEM 09062025_101125.CSV')

df.to_excel('planilha_formatada.xlsx', index=False)
