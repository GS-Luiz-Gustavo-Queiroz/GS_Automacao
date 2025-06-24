import pandas as pd


df = pd.read_excel('instituicoes_financeiras.xlsx')
r = df[0][df[0].str.contains(' VR ')]
print(["' | '".join(r.values)])