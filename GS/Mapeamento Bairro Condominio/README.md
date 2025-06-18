#### Ordem de execução dos scripts:

1 - No arquivo [(download_dados_receita)](./scraping_download_dados_receita/download_dados_receita.ipynb), execute a função 'download_dados_estabelecimentos_empresas()'.
2 - No arquivo [(filtragem_condominios_fortaleza)](./tratamento_arquivos_receita/filtragem_condominios_fortaleza.ipynb), execute a função 'filtrar_cond_fortaleza()'.
3 - No arquivo [(cruzamento_cond_fortaleza_razao_social)](./tratamento_arquivos_receita/cruzamento_cond_fortaleza_razao_social.ipynb), execute a função 'cruzar_dados_cond_fort_razao_social()'.

A lógica é a seguinte:
1 - Na execução de **_download dos dados_**, os arquivos das empresas e estebelecimentos serão baixados, descompactados, nomeados e organizados em suas respectivas pastas (pasta essa que é irmã da pasta da execução do código).
2 - Na execução de **_filtragem de condomínios de fortaleza_** os dados de estabelecimentos serão filtrados pelo CNAE de condomínios prediais e pelo código da cidade de fortaleza, e então o dataset dos condomínios de fortaleza será gerado.
3 - Na execução da função de **_cruzamento de dados_**, nosso dataset dos condomínios de fortaleza terá seus dados cruzados com os dados das empresas para atribução da razão social.