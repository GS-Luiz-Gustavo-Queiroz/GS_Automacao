class Arquivo:
    def __init__(self, path: str):
        path_split = path.split('\\')
        self.path: str = path
        self.instituicao_financeira = path_split[-2]
        self.estabelecimento = path_split[-3]
        self.grupo = path_split[-4]