
# from modelos.SPX_VISON.main import spx_vision
# from modelos.CAIXA.app import CAIXA
# from modelos.AIRBI.app import AIRBI
# from modelos.BANESTES_RPL.app import BANESTES_RPL
# from modelos.GRAFENO.app import GRAFENO
# from modelos.GRAFENO_HITEC.app import GRAFENO_HITEC
# from modelos.HITEC.app import HITEC
# from modelos.ITAU.app import ITAU
# from modelos.ITAU_VISION.app import ITAU_VISION
# from modelos.SANTANDER.app import SANTANDER
# from modelos.SANTANDER_SING.app import SANTANDER_SING
# from modelos.CEF_FOLK.app import CEF_FOLK
# from modelos.CORA_GS_FACILITIES.app import CORA_GS_FACILITIES
# from modelos.SICOOB_JS_ADM.app import sicoob_js_adm
from modelos.ENTRIWAY.app import ENTRIWAY



# df = AIRBI('modelos/AIRBI/AIRBI SOLUCAOextrato_0003740223_de_02-06-2025_ate_09-06-2025.xlsx')
# df.to_excel('planilha_teste.xlsx', index=False)

# df = BANESTES_RPL('modelos/BANESTES_RPL/BANESTES RPL.xlsx')
# df.to_excel('BANESTES_RPL_FORMATADO.xlsx', index=False)

# df = CAIXA('modelos/CAIXA/HITEC 37 - ABRIL (EXTRATO CAIXA).txt')
# df.to_excel('CAIXA_FORMATADO.xlsx', index=False)

# df = CEF_FOLK('modelos/CEF_FOLK/CEF FOLK 2025-06-09-08-47-14-006681292000578216851.xls')
# df.to_excel('CEF_FOLK_FORMATADO.xlsx', index=False)

# df = CORA_GS_FACILITIES('modelos/CORA_GS_FACILITIES/CORA gs-facilites-for_01052025_a_31052025_f8711ab6 (1).pdf')
# df.to_excel('CORA_GS_FACILITIES.xlsx', index=False)

# df = GRAFENO('modelos/GRAFENO/HITEC 37 - ABRIL (EXTRATO GRAFENO).xlsx')
# df.to_excel('GRAFENO_FORMATADO.xlsx', index=False)

# df = GRAFENO_HITEC('modelos/GRAFENO_HITEC/GRAFENO HITEC Relatorio_-_Extrato 05.2025.xlsx')
# df.to_excel('GRAFENO_HITEC_FORMATADO.xlsx', index=False)

# df = HITEC('modelos/HITEC/HITEC Relatorio_-_Extrato 05.2025.xlsx')
# df.to_excel('HITEC_FORMATADO.xlsx', index=False)

# df = ITAU('modelos/ITAU/HITEC 37 - ABRIL (EXTRATO ITAU).xls')
# df.to_excel('ITAU_FORMATADO.xlsx', index=False)

# df = ITAU_VISION('modelos/ITAU_VISION/ITAU VISON Extrato_0546-145699-09-06-2025.xls')
# df.to_excel('ITAU_VISION_FORMATADO.xlsx', index=False)

# df = SANTANDER('modelos/SANTANDER/HITEC 37 - MAIO (EXTRATO SANTANDER).xls')
# df.to_excel('SANTANDER_FORMATADO.xlsx', index=False)

# df = SANTANDER_SING('modelos/SANTANDER_SING/SANTANDER sing 95 EXTRATO.xls')
# df.to_excel('SANTANDER_SING_FORMATADO.xlsx', index=False)

# path = 'modelos/SPX_VISON/SPX VISON.pdf'
# spx_vision(path)

# df  = sicoob_js_adm('modelos/SICOOB_JS_ADM/SICOOB - JS ADM  EXTRATO BANCARIO -.pdf')
# df.to_excel('SICOOB_FORMATADO.xlsx', index=False)

df = ENTRIWAY('modelos/ENTRIWAY/ENTRIWAY Extrato 05.2025.xls')
df.to_excel('ENTRIWAY_FORMATADO.xlsx', index=False)
