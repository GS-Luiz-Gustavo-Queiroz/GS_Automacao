import smtplib
from email.mime.text import MIMEText

def enviar_email(creds_remet, email_dest, num_nota, data):
    try:
        #configurando servidor de e-mail
        servidor_email = smtplib.SMTP('smtp.gmail.com', 587)
        #iniciando servidor de e-mail
        servidor_email.starttls()
        #logando e-mail
        servidor_email.login(creds_remet['usuario'], creds_remet['senha'])

        #OBS.: HAVERÁ UM FOR PARA ENVIAR PARA TODOS OS DEVEDORES CAPTURADOS NA CONSULTA SQL
        #criando o corpo do e-mail
        remetente = creds_remet['usuario']
        # destinatarios = ['ti.automacao01@gscsc.com.br']
        destinatarios = [email_dest]

        conteudo = """Prezado Cliente, boa tarde, tudo bem?


Me chamo Silvana Maia, trabalho no setor Financeiro.

Consta em nosso sistema uma pendência financeira e caso tenha efetuado o pagamento, solicito por gentileza que me envie o comprovante para verificarmos com o banco a inconsistência da baixa e solicito que desconsidere essa mensagem.

Caso não tenha pago podemos contar com esse pagamento para hoje?

Fico grata e conto sempre com sua prioridade, pontualidade e parceria. Qualquer dúvida estou a disposição.

--


Atenciosamente"""
        
        conteudo = MIMEText(conteudo, "plain")
        conteudo["Subject"] = f"Cobrança Referente a Nota Fiscal {num_nota} com Vencimento {data}"
        conteudo["From"] = creds_remet['usuario']

        servidor_email.sendmail(remetente, destinatarios, conteudo.as_string())
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
    finally:
        servidor_email.quit()