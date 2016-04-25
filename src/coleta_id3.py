#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------- #
# ?????.py - Coleta ID´s da API NLM e em seguida baixa os respectivos XMLs
# ------------------------------------------------------------------------- #
#      Entrada:
#        Saida: arquivos <database>.id
#     Corrente: /bases/NLM_api/apps/wrk
#      Chamada: python ../tpl/????.py
#      Exemplo: python ../tpl/????.py
#     Objetivo: criar arquivo contendo ID
#  Comentarios:
#  Observacoes:
#
# ------------------------------------------------------------------------- #
#   DATA    RESPONSAVEL                  COMENTARIO
# 20160418  Fabio Brito                  edicao original
# ------------------------------------------------------------------------- #


import requests
import sys
import os
import datetime
from MongoDb import MyMongo as Classe

from LoadUrl import LoadUrl as url

# conexao com o banco
job = Classe('nlm_api','tb_id')
# job = Classe('nlm_api','tb_id',host='mongodb.bireme.br')

# Apaga temporariamente a coleção
job.dropCollection()

# URL utilizada para recolher total de registros

retmax = '&retmax=1'
URL_base = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=pubstatusaheadofprint&retmode=json'

URL_xml = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id='


URL_count = '%s%s' % (URL_base,retmax) 


# Executado consulta
r_t = requests.get(URL_count)

# Armazenando conteudo em 'data_t'
data_t = r_t.json()

print (data_t)

# Lendo conteudo 'count' em total_ids
# total_ids = data_t['esearchresult']['count']


# Forçando apenas para teste
total_ids = 10

print (' Total de registros: ', total_ids)

# exit()

nome_arq_id = 'ids.id'



## Abrindo novo arquivo para gravacao
id_file = open(nome_arq_id, 'a')

COUNT = 0
while (COUNT <= total_ids ):
    print ('+ ', COUNT)


    # Montando URL para coleta do ID
    retmax = '&retmax=1'
    retstart= '&retstart='

    URL = '%s%s%s%s' % (URL_base,retmax,retstart,COUNT)

    print (URL)

    # Executando consulta
    r_range = requests.get(URL)

    # Armazenando conteudo em 'data_d'
    data_d = r_range.json()

    # Lendo conteudo da chave 'esearchresult[idlist]' e guardando em lista
    lista = data_d['esearchresult']['idlist']

    # Lendo todos os ID´s e gravando em arquivo
    for valor in lista:
        print (valor)
        id_file.write(str(valor)+'\n')

    COUNT = COUNT + 1

# Fechando arquivo
id_file.close()

# Abrindo arquivo de ids para leitura
file_read = open(nome_arq_id, 'r')

for line in file_read:
    line = line.replace('\n','')
    print (line)
    job.saveDoc({'_id':line,"last_modified": datetime.datetime.now()})

    URL_wrk = '%s%s' % (URL_xml,line)
    print (URL_wrk)

    print (url.loadUrl(URL_wrk))



# Fechando arquivo
file_read.close()


# Baixa o xml e guarda no mongo





# Finaliza a execução do script
sys.exit(0)


