import smtplib
from email.mime.text import MIMEText
from data_venc import data_venc

def enviar_email_5_dias_atraso(servidor_email, remetente, email_dest, num_nota, data):
    
    #DEFININDO O CORPO DO E-MAIL
    conteudo = f"""Prezado(a), boa tarde!

A Singular Facilities informa que, conforme nosso sistema, consta em aberto o seguinte título:
	•	Nota Fiscal nº {num_nota}
	•	Vencimento: {data}

Em caso de confirmação da seguinte pendência, podemos contar com a regularização ainda hoje?

Caso o pagamento já tenha sido realizado, pedimos a gentileza de desconsiderar esta mensagem.

Agradecemos pela atenção, parceria e compromisso de sempre. Permanecemos à disposição para quaisquer esclarecimentos.

Atenciosamente,
Departamento Financeiro
Singular Facilities
Em caso de dúvidas, entre em contato conosco (85) 98998-3984"""
    conteudo = MIMEText(conteudo, "plain")
    conteudo["Subject"] = f"Pendência Financeira - Nota Fiscal nº {num_nota}"
    conteudo["From"] = remetente

    servidor_email.sendmail(remetente, email_dest, conteudo.as_string())



def enviar_email_2_dias_antes(servidor_email, remetente, email_dest, num_nota, data):

    #DEFININDO O CORPO DO E-MAIL
    conteudo = f"""Prezado(a), Boa tarde!

Esperamos que esteja tudo bem com você!

Estamos passando para lembrar que a Nota Fiscal nº {num_nota} tem vencimento próximo, com data prevista para {data}.

Caso o pagamento já tenha sido realizado, por favor, desconsidere este aviso.
Se precisar de qualquer apoio ou tiver dúvidas, nossa equipe está à disposição.

Agradecemos pela parceria e confiança!

Atenciosamente,
Departamento Financeiro
Singular Facilities
Em caso de dúvidas, entre em contato conosco (85) 98998-3984"""
       
    conteudo = MIMEText(conteudo, "plain")
    conteudo["Subject"] = f"Sua nota fiscal de nº {num_nota} vence em 2 dias"
    conteudo["From"] = remetente

    servidor_email.sendmail(remetente, email_dest, conteudo.as_string())