from datetime import datetime
def data_venc(dt_vencimento):
    data = datetime.strptime(dt_vencimento, "%Y%m%d")
    dia = data.day
    mes = data.month
    ano = data.year

    if int(data.month) < 10:
        mes = f"0{data.month}"
    if int(data.day) < 10:
        dia = f"0{data.day}" 
    ano = data.year
    
    data = f"{dia}/{mes}/{ano}"
    return data
