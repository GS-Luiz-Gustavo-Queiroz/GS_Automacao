#### O programa funciona da seguinte maneira:
1 - O arquivo principal é 'main_cobranca.py' no qual chama a função cobranca automatizada(num_dias) no qual o parâmetro num_dias é a quantidade de dias de vencimento sendo um valor positivo dias que faltam para vencer, e negativo dias que já passaram do vencimento.
2 - No arquivo 'cobranca_automatizada.py' é implementada a função cobranca_automatizada(), na qual:
    - lê os dados do banco de dados dos registros de pagamentos pendentes de acordo com os dias passados como parâmetro.
    - para cada registro de pagamento pendente envia um e-mail para o cliente realizando a cobrança.