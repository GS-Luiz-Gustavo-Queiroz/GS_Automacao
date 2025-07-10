import pathlib
import os
from .f01 import f01
from .f02 import f02
from .f03 import f03
from .f04 import f04
from .f05 import f05
from .f06 import f06
from .f07 import f07

# Caminho do diretório onde este __init__.py está.
diretorio = pathlib.Path(__file__).parent
# Conta quantos arquivos de função existem no diretório.
N_FUNCTIONS = len([file for file in os.listdir(diretorio) if file.startswith('f') and file.endswith('.py')])
__all__ = [f'f{i:02}' for i in range(1, N_FUNCTIONS+1)]
# Nomeia cada função ao seu nome de arquivo.
NAMES = {
    1: 'Identificar Automaticamente (mais lento)',
    2: 'NFs Curitiba',
    3: 'NFs Salvador',
    4: 'NFs Sorocaba',
    5: 'NFs Vitória',
    6: 'NFs Vila Velha',
    7: 'Rendimentos Dirf'
}
