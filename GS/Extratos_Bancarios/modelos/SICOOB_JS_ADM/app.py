from typing import Dict
import pandas as pd
import sys
import os
# Adiciona a raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from configs.utils import dict_to_df, get_text_from_pdf


def sicoob_js_adm(path: str) -> pd.DataFrame:
    pages = get_text_from_pdf(path)
    for page in pages:
        for i, row in enumerate(page):
            print([i, row])