#### Ordem de execução dos scripts:

1 - Execute o arquivo [gerar_dataset_cond_fortaleza.py](./pipeline_gerar_dataset/gerar_dataset_cond_fortaleza.py)</br>
### OU </br>
1 - Execute o arquivo [download_dados_receita](./scraping_download_dados_receita/download_dados_receita.ipynb) (a função que executa é 'download_dados_estabelecimentos_empresas()').</br>
2 - Execute o arquivo [(filtragem_condominios_fortaleza)](./tratamento_arquivos_receita/filtragem_condominios_fortaleza.ipynb) (a função que executa é' filtrar_cond_fortaleza()').</br>
3 - Execute o arquivo [(cruzamento_cond_fortaleza_razao_social)](./tratamento_arquivos_receita/cruzamento_cond_fortaleza_razao_social.ipynb) (a função que executa é 'cruzar_dados_cond_fort_razao_social()').</br>

A lógica é a seguinte:</br>
1 - Na execução de **_download dos dados_**, os arquivos das empresas e estebelecimentos serão baixados, descompactados, nomeados e organizados em suas respectivas pastas (pasta essa que é irmã da pasta da execução do código).</br>
2 - Na execução de **_filtragem de condomínios de fortaleza_** os dados de estabelecimentos serão filtrados pelo CNAE de condomínios prediais e pelo código da cidade de fortaleza, e então o dataset dos condomínios de fortaleza será gerado.</br>
3 - Na execução da função de **_cruzamento de dados_**, nosso dataset dos condomínios de fortaleza terá seus dados cruzados com os dados das empresas para atribução da razão social.</br>


##### OBS.: Pela quantidade de dados baixados serem massivas, em uma rede de 100Mbps tomou 2 horas para finalizar a execução (download + tratamento + filtro + geração do dataset).