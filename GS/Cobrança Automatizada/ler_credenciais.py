from typing import Dict, Optional
import os

def ler_credenciais_remet(arquivo='configs/remet_cred.txt') -> Dict[str, Optional[str]]:
    credenciais = {'usuario': None, 'senha': None}

    try:
        with open(arquivo, 'r', encoding='utf-8') as file:
            for linha in file:
                linha = linha.strip()
                if not linha:
                    continue
                if linha.lower().startswith('usuario'):
                    credenciais['usuario'] = linha.split('=')[1].strip()
                elif linha.lower().startswith('senha'):
                    credenciais['senha'] = linha.split('=')[1].strip()
                if credenciais['usuario'] and credenciais['senha']:
                    break
    except FileNotFoundError:
        print(f"\nErro: Arquivo {arquivo} não encontrado!")
    except Exception as e:
        print(f"\nErro ao ler o arquivo de credenciais: {e}")

    return credenciais

def ler_credenciais_db(arquivo='configs/db_cred.txt') -> Dict[str, Optional[str]]:
    credenciais = {'server': None, 'database': None, 'username': None, 'password': None}

    try:
        with open(arquivo, 'r', encoding='utf-8') as file:
            for linha in file:
                linha = linha.strip()
                if not linha:
                    continue
                if linha.lower().startswith('server'):
                    credenciais['server'] = linha.split('=')[1].strip()
                elif linha.lower().startswith('database'):
                    credenciais['database'] = linha.split('=')[1].strip()
                elif linha.lower().startswith('username'):
                    credenciais['username'] = linha.split('=')[1].strip()
                elif linha.lower().startswith('password'):
                    credenciais['password'] = linha.split('=')[1].strip()
                if credenciais['server'] and credenciais['database'] and credenciais['username'] and credenciais['password']:
                    break
    except FileNotFoundError:
        print(f"\nErro: Arquivo {arquivo} não encontrado!")
    except Exception as e:
        print(f"\nErro ao ler o arquivo de credenciais: {e}")

    return credenciais