from PyPDF2 import PdfReader
from typing import List
import pandas as pd
import os


def vr_suporte_de_locacao(path: str) -> None:
    with open(path, 'rb') as file_bin:
        pdf = PdfReader(file_bin)
        rows: List[List[str]] = []
        for page in pdf.pages:
            new_rows: List[str] = page.extract_text().split('\n')
            rows.append(new_rows)

    for page in rows:
        for i, row in enumerate(page):
            print([i, row])


if __name__ == '__main__':
    try:
        paths = [path for path in os.listdir() if '.pdf' in path.lower()]
        for path in paths:
            vr_suporte_de_locacao(path)
    except Exception as e:
        print(e)
