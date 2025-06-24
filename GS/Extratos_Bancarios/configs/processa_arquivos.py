from tqdm import tqdm
from tqdm import tqdm
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from configs.arquivo import Arquivo
from configs.utils import list_all_files
from modelos.AIRBI.app import AIRBI  # Sem uso
from modelos.BANESTES_RPL.app import banestes
from modelos.BB_CONDO_PREST.app import bb_condoprest
from modelos.BRADESCO_HISYSTEM.app import bradesco_hisystem
from modelos.caixa.app import CAIXA
from modelos.CEF_FOLK.app import CEF_FOLK
from modelos.CORA_GS_FACILITIES.app import CORA_GS_FACILITIES
from modelos.ENTRIWAY.app import ENTRIWAY
from modelos.grafeno.app import GRAFENO
from modelos.GRAFENO_HITEC.app import GRAFENO_HITEC  # Redundante
from modelos.hitec_37_spx.app import hitec_37_spx  # Redundante
from modelos.INTER_SING.app import inter_sing
from modelos.itau.app import ITAU
from modelos.ITAU_VISION.app import ITAU_VISION  # Redundante
from modelos.santander.app import SANTANDER
from modelos.SANTANDER_SING.app import SANTANDER_SING  # Redundante
from modelos.SICOOB_JS_ADM.app import sicoob_js_adm
from modelos.SPX_VISON.app import spx
from modelos.VR_SUPORTE_DE_LOCACAO.app import vr



def processa_arquivos(path: str) -> pd.DataFrame:
    erros = []
    df = pd.DataFrame(columns=['Data', 'Saldo', 'grupo', 'estabelecimento', 'instituicao_financeira'])
    files = list_all_files([path])
    print('='*50)
    for file in tqdm(files):
        print(file)
        arq = Arquivo(file)
        instituicao_fin = arq.instituicao_financeira
        estabelecimento = arq.estabelecimento
        grupo = arq.grupo
        match instituicao_fin:
            case '0006 - CONDONAL SERVIÇO - BANESTES 7821' | '0020 - CONDONAL ADM RPJ - BANESTES' | '0016 - CONDAP 91 - BANESTES' | '0005 - CONDONAL SERVIÇO - BANESTES 2607' | '0024 - CONDONAL APOIO P&R - BANESTES' | '0037 - ESSENCIAL CONDOMINIOS - BANESTES' | '0012 - CONDLIMP 00 - BANESTES' | '0027 - CONDONAL LOCAÇÃO - BANESTES' | '0044 - ESSENCIAL APOIO - BANESTES' | '0089 - COMERCIO - BANESTES' | '0042 - ESSENCIAL GESTÃO - BANESTES':
                new_df = banestes(file)
            case '0028 - ABC ADM - BB' | '0029 - CONDONAL COMERCIO - BB' | '0002 - CONDONAL SERVIÇO - BB' | '0128 - ABC ADM - BB APLICAÇÃO' | '0013 - CONDAP 91 - BB' | '0154 - GARANTIDA CONDONAL COMERCIO - BB' | '0133 - CONDONAL COMERCIO - BB APLICAÇÃO' | '0009 - CONDLIMP 00 - BB':
                new_df = bb_condoprest(file)
            case '0022 - HISEG BA - BRADESCO CONTA CORRENTE' | '0158 - 08 - CONDONAL ADM RPJ - BRADESCO' | '0032 - HISYSTEM - BRADESCO CONTA CORRENTE' | '0055 - BRADESCO - MARGATRAN' | '0134 - BRADESCO - MARGATRAN APLICAÇÃO' | '0067 - NEOPORT - BRADESCO CONTA CORRENTE' | '0117 - NEOPORT - BRADESCO CONTA CORRENTE APL' | '0118 - HISEG BA - BRADESCO CONTA CORRENTE APL' | '0121 - HISYSTEM - BRADESCO CONTA CORRENTE APL' | '0157 - 09 - CONDONAL COMERCIO - BRADESCO' | '0054 - BRADESCO - VITORIAGATTI' | '0119 - MONITOR - BRADESCO CONTA CORRENTE APL' | '0013 - MONITOR - BRADESCO CONTA CORRENTE':
                new_df = bradesco_hisystem(file)
            case '0114 - HITEC - CAIXA CONTA GARANTIDA 1 APL' | '0066 - CAIXA APLICAÇÃO - GARANTIDA COMERCIO' | '0058 - KIENEN - CAIXA CONTA CORRENTE' | '0057 - FOLK - CAIXA CONTA POUPANÇA' | '0060 - FK PR - CAIXA CONTA CORRENTE' | '0055 - FOLK - CAIXA CONTA CORRENTE' | '0045 - 07 - CAIXA APLICAÇÃO - CONDO GROUP 07' | '0039 - TCM - CAIXA CONTA CORRENTE' | '0006 - HITEC - CAIXA APLICAÇÃO RENDA FIXA' | '0066 - NEOPORT - CAIXA CONTA CORRENTE' | '0024 - 48 - CAIXA 5068-4 - GESTCON 48' | '0037 - 80FL - CAIXA 5105-2 - CONDO FILIAL' | '0056 - FOLK - CAIXA CONTA GARANTIDA' | '0003 - HITEC - CAIXA CONTA CORRENTE' | '0082 - 09 CAIXA - CONDONAL COMERCIO' | '0046 - 07- CAIXA APLICAÇÃO GARANTIDA - CONDO 07' | '0044 - 07 - CAIXA 5170-2  CONDO GROUP GARANT' | '0005 - HITEC - CAIXA CONTA GARANTIDA 2' | '0030 - 07 - CAIXA 5090-0 - CONDO GROUP 07' | '0120 - HITEC - CAIXA CONTA GARANTIDA 2 APL' | '0031 - CONDONAL LOCAÇÃO - CAIXA' | '0004 - HITEC - CAIXA CONTA GARANTIDA 1' | '0002 - CAIXA INTERNO' | '0075 - 09 CAIXA - GARANTIDA CONDONAL COMERCIO' | '0064 - NEOPORT - CAIXA CONTA GARANTIDA':
                new_df = CAIXA(file)
            case '0011 - CEF GARANTIDA - G.A' | '0039 - ESSENCIAL CONDOMINIOS - CEF' | '0010 - CEF - G.A' | '0045 - ESSENCIAL ADM - CEF':
                new_df = CEF_FOLK(file)
            case '0060 - 06 - CORA - UNICA 01' | '0067 - 01 - CORA - PEGASUS 62' | '0066 - 02 - CORA - UNICA 42' | '0036 - HISYSTEM - CORA' | '0064 - 04 - CORA - UNICA 15' | '0137 - CORA - PORTARIA' | '0033 - CORA - PORTARIA' | '0025 - CORA - FACILITIES' | '0050 - 05 - CORA - UNICA 70' | '0069 - 10 - CORA - UNICA 30' | '0020 - MONITOR - CORA' | '0088 - CONDONAL LOCAÇÃO - CORA' | '0063 - 11 - CORA - UNICA 00' | '0029 - 07 - CORA 4575400-1 - CONDO GROUP' | '0068 - 07 - CORA - UNICA 59' | '0062 - 03 - CORA - UNICA 51' | '0032 - CORA - GOLD' | '0065 - 08 - CORA - UNICA 09' | '0061 - 09 - CORA - UNICA 61' | '0029 - HISEG BA - CORA' | '0124 - PRIMEE REMOTA - CORA' | '0036 - CORA - SELECT' | '0038 - 80FL - CORA 4634765-6 - CONDO FILIAL':
                new_df = CORA_GS_FACILITIES(file)
            case '0145 - ENTRIWAY - ITAU GARANTIDA' | '0134 - ENTRIWAY - ITAU' | '0142 - ENTRIWAY - SPX BANK' | '0135 - ENTRIWAY - SICREDI':
                new_df = ENTRIWAY(file)
            case '0012 - HITEC - GRAFENO':
                new_df = GRAFENO(file)
            case '0079 - GVP - INTER CONTA CORRETE':
                new_df = inter_sing(file)
            case '0046 - HIPAR - ITAU CERUS BANK' | '0143 - ENTRI ITAU GARANTIDA 36455' | '0145 - ENTRIWAY - ITAU GARANTIDA' | '0134 - ENTRIWAY - ITAU' | '0035 - 48 - ITAU 99820-5 - GESTCON 48' | '0042 - 80 - ITAU 98622-6 - CONDO FILIAL' | '0126 - ENTRI - ITAU' | '0140 - ENTRI ITAU GARANTIDA' | '0034 - 07 - ITAU 99827-0 - CONDO GROUP 07':
                new_df = ITAU(file)
            case '0023 - HISEG BA - SANTANDER CONTA CORRENTE' | '0003 - G A TERCEIRIZAÇÕES - SANTANDER' | '0015 - MONITOR - SANTANDER CONTA CORRENTE' | '0033 - HISYSTEM - SANTANDER CONTA CORRENTE' | '0122 - HITEC - SANTANDER APLICAÇÃO' | '0002 - HITEC - SANTANDER CONTA CORRENTE':
                new_df = SANTANDER(file)
            case '0034 - CONDOS - SICOOB' | '0027 - HISEG BA - SICOOB CONTA CAPITAL' | '0007 - CONDONAL SERVIÇO - SICOOB (MARKETING)' | '0008 - CONDONAL SERVIÇO - SICOOB 41' | '0026 - HISEG BA - SICOOB CONTA CORRENTE' | '0038 - ESSENCIAL CONDOMINIOS - SICOOB' | '0170 - 26 - CONDONAL TERCEIRIZAÇÃO - SICOOB 980' | '0057 - SICOOB - MARGATRAN' | '0051 - CONDLIMP (CONTROL PRIME) - SICOOB' | '0056 - SICOOB - VITORIAGATTI' | '0048 - CONDAP J2 - SICOOB':
                new_df = sicoob_js_adm(file)
            case '0140 - 03 - CONDAP J2 - SPX BANK' | '0152 - 17 - MARGATRAN - SPX BANK' | '0144 - 07 - CONDO APOIO P & R - SPX BANK' | '0155 - 20 - CONDONAL ADM 06 - SPX BANK' | '0046 - SPX BANK - FACILITIES' | '0147 - 12 - ESSENCIAL ADM - SPX BANK' | '0050 - SPX BANK - SELECT' | '0142 - 05 - CONDLIMP - SPX BANK' | '0145 - 10 - CONDONAL SERV - SPX BANK' | '0101 - 08 - SPX BANK - UNICA 09' | '0123 - MONITOR - SPX BANK' | '0129 - HITEC ES - SPX BANK' | '0048 - SPX BANK - TERCEIRIZAÇÕES' | '0148 - 13 - ESSENCIAL CONDOMINIO - SPX BANK' | '0131 - GVP - SPX BANK' | '0097 - 09 - SPX BANK - UNICA 61' | '0130 - HISEG BA - SPX BANK' | '0026 - SPX BANK - G.A' | '0058 - 07 - SPX BANK - CONDO GROUP' | '0131 - HIPAR - SPX BANK' | '0138 - 01 - ABC ADMINISTRADORA  - SPX BANK' | '0100 - 04 - SPX BANK - UNICA 15' | '0137 - 09 - CONDONAL COMERCIO - SPX BANK' | '0135 - 08 - CONDONAL ADM RPJ - SPX BANK' | '0099 - 11 - SPX BANK - UNICA 00' | '0130 - KIENEN - SPX BANK' | '0095 - 05 - SPX BANK - UNICA 70' | '0104 - 01 - SPX - PEGASUS 62' | '0126 - HISYSTEM - SPX BANK' | '0159 - 18 - RUBI - SPX BANK' | '0142 - ENTRIWAY - SPX BANK' | '0172 - 26 - CONDONAL TERCEIRIZAÇÃO - SPX BANK' | '0143 - 06 - CONDO LOCACAO - SPX BANK' | '0139 - PRIMEE PORTARIA - SPX BANK' | '0150 - 15 - ESSENCIAL APOIO ADM - SPX BANK' | '0149 - 14 - ESSENCIAL GEST E SER - SPX BANK' | '0141 - ENTRI - SPX BANK' | '0057 - 48 - SPX BANK - GESTCON' | '0133 - TCM - SPX BANK' | '0128 - NEOPORT - SPX BANK' | '0151 - 16 - VITORIAGATTI - SPX BANK' | '0173 - 29 - INTELLECTUS SERVIÇOS - SPX BANK' | '0094 - 06 - SPX BANK - UNICA 01' | '0146 - 11 - CONDOS ADM DE CONDOM - SPX BANK' | '0059 - 80FL - SPX BANK - CONDO FILIAL' | '0132 - HISEG ES - SPX BANK' | '0096 - 10 - SPX BANK - UNICA 30' | '0049 - SPX BANK - GOLD' | '0129 - FOLK - SPX BANK' | '0174 - 28 - NEXUS ADMINISTRAÇÃO - SPX BANK' | '0103 - 07 - SPX BANK - UNICA 59' | '0141 - 04 - CONDLIMP (CONTROL PRIME) - SPX' | '0001 - DAYO - SPX BANCK' | '0128 - HITEC BA - SPX BANK' | '0125 - LURAHSEG - SPX BANK' | '0132 - FK PR - SPX BANK' | '0102 - 02 - SPX BANK - UNICA 42' | '0127 - HITEC - SPX BANK' | '0139 - 02 - CONDAP - PREST - SPX BANK' | '0098 - 03 - SPX BANK - UNICA 51':
                new_df = spx(file)
            case '0028 - HISEG BA - VR CASHBACK' | '0019 - VR BENEFICIOS - UNICA 42' | '0007 - VR BENEFICIOS - UNICA 01' | '0042 - TCM - VR CASHBACK' | '0021 - MONITOR - VR CASHBACK' | '0004 - VR BENEFICIOS - UNICA 00' | '0032 - VR BENEFICIOS - UNICA 70' | '0026 - VR BENEFICIOS - UNICA 59' | '0037 - HISYSTEM - VR CASHBACK' | '0010 - HITEC - VR CASHBACK' | '0022 - VR BENEFICIOS - UNICA 51' | '0013 - VR BENEFICIOS - UNICA 15' | '0029 - VR BENEFICIOS - UNICA 61' | '0016 - VR BENEFICIOS - UNICA 30' | '0010 - VR BENEFICIOS - UNICA 09' | '0035 - VR BENEFICIOS - PEGASUS 62':
                new_df = vr(file)
            case _:
                erros.append(f'Não adaptada para a instituição financeira - {instituicao_fin} - {file}')
                continue
        print(instituicao_fin)
        new_df['grupo'] = grupo
        new_df['estabelecimento'] = estabelecimento
        new_df['instituicao_financeira'] = instituicao_fin
        df = pd.concat([df, new_df], ignore_index=True)

    for erro in erros:
        print(erro)
    df = df[['grupo', 'estabelecimento', 'instituicao_financeira', 'Data', 'Saldo']]
    return df
