from modelos.SPX_VISON.main import spx_vision
from modelos.CAIXA.app import CAIXA
from modelos.AIRBI.app import AIRBI
from modelos.BANESTES_RPL.app import BANESTES_RPL
from modelos.GRAFENO.app import GRAFENO
from modelos.GRAFENO_HITEC.app import GRAFENO_HITEC
from modelos.HITEC.app import HITEC
from modelos.ITAU.app import ITAU
from modelos.ITAU_VISION.app import ITAU_VISION
from modelos.SANTANDER.app import SANTANDER
from modelos.SANTANDER_SING.app import SANTANDER_SING
from modelos.CEF_FOLK.app import CEF_FOLK
from modelos.CORA_GS_FACILITIES.app import CORA_GS_FACILITIES




df = AIRBI('modelos/AIRBI/AIRBI SOLUCAOextrato_0003740223_de_02-06-2025_ate_09-06-2025.xlsx')
df.to_excel('planilha_teste.xlsx', index=False)