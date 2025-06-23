
# from modelos.SPX_VISON.main import spx_vision
# from modelos.CAIXA.app import CAIXA
# from modelos.AIRBI.app import AIRBI
# from modelos.BANESTES_RPL.app import BANESTES_RPL
from modelos.GRAFENO.app import GRAFENO
# from modelos.GRAFENO_HITEC.app import GRAFENO_HITEC
# from modelos.HITEC.app import HITEC
# from modelos.ITAU.app import ITAU
# from modelos.ITAU_VISION.app import ITAU_VISION
# from modelos.SANTANDER.app import SANTANDER
# from modelos.SANTANDER_SING.app import SANTANDER_SING
# from modelos.CEF_FOLK.app import CEF_FOLK
# from modelos.CORA_GS_FACILITIES.app import CORA_GS_FACILITIES
# from modelos.SICOOB_JS_ADM.app import sicoob_js_adm



# df = AIRBI('modelos/AIRBI/AIRBI SOLUCAOextrato_0003740223_de_02-06-2025_ate_09-06-2025.xlsx')
# df.to_excel('planilha_teste.xlsx', index=False)

# df = BANESTES_RPL('modelos/BANESTES_RPL/BANESTES RPL.xlsx')
# df.to_excel('BANESTES_RPL_FORMATADO.xlsx', index=False)

# # path = 'modelos/CAIXA/HITEC 37 - ABRIL (EXTRATO CAIXA).txt' 
# # path = 'modelos/CAIXA/HITEC 37 - MAIO (EXTRATO CAIXA).txt'
# # CAIXA(path)

# path = 'modelos/CEF_FOLK/CEF FOLK 2025-06-09-08-47-14-006681292000578216851.xls'
# CEF_FOLK(path)

# path = 'modelos/CORA_GS_FACILITIES/CORA gs-facilites-for_01052025_a_31052025_f8711ab6 (1).pdf'
# CORA_GS_FACILITIES(path)

df = GRAFENO('modelos/GRAFENO/HITEC 37 - ABRIL (EXTRATO GRAFENO).xlsx')
df.to_excel('GRAFENO_FORMATADO.xlsx', index=False)



# path = 'modelos/GRAFENO_HITEC/GRAFENO HITEC Relatorio_-_Extrato 05.2025.xlsx'
# GRAFENO_HITEC(path)

# path = 'modelos/HITEC/HITEC Relatorio_-_Extrato 05.2025.xlsx'
# HITEC(path)

# path = 'modelos/ITAU/HITEC 37 - ABRIL (EXTRATO ITAU).xls'
# ITAU(path)

# path = 'modelos/ITAU_VISION/ITAU VISON Extrato_0546-145699-09-06-2025.xls'
# ITAU_VISION(path)

# path = 'modelos/SANTANDER/HITEC 37 - MAIO (EXTRATO SANTANDER).xls'
# SANTANDER(path)

# path = 'modelos/SANTANDER_SING/SANTANDER sing 95 EXTRATO.xls'
# SANTANDER_SING(path)

# path = 'modelos/SPX_VISON/SPX VISON.pdf'
# spx_vision(path)

# df  = sicoob_js_adm('modelos/SICOOB_JS_ADM/SICOOB - JS ADM  EXTRATO BANCARIO -.pdf')
# df.to_excel('SICOOB_FORMATADO.xlsx', index=False)

