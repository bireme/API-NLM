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
import time
from pymongo import MongoClient

# URL utilizada para recolher total de registros
URL_t = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=publisher[sb]&retmax=1&retmode=json'

# Executado consulta
r_t = requests.get(URL_t)

# Armazenando conteudo em 'data_t'
data_t = r_t.json()

print data_t

# Lendo conteudo 'count' em total_ids
# total_ids = data_t['esearchresult']['count']


# Forçando apenas para teste
total_ids = 10

print ' Total de registros: ', total_ids

# exit()

nome_arq_id = 'ids.id'



### Abrindo novo arquivo para gravacao
id_file = open(nome_arq_id, 'w')

COUNT = 0
while (COUNT <= total_ids ):
    print '+ ', COUNT


    # Montando URL para coleta do ID
    fixo_1 = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=publisher[sb]&retstart='
    fixo_2 = '&retmax=1&retmode=json'
    URL = '%s%s%s' % (fixo_1,COUNT,fixo_2)

    print URL

    # Executando consulta
    r_range = requests.get(URL)

    # Armazenando conteudo em 'data_d'
    data_d = r_range.json()

    # Lendo conteudo da chave 'esearchresult[idlist]' e guardando em lista
    lista = data_d['esearchresult']['idlist']

    # Lendo todos os ID´s e gravando em arquivo
    for valor in lista:
        print valor
        id_file.write(str(valor)+'\n')

    COUNT = COUNT + 1

# Fechando arquivo
id_file.close()

# URL do servidor MongoDB
mongoserver_uri = 'mongodb://localhost:27017'

# Conexão com o banco
connection = MongoClient(host=mongoserver_uri)

# Banco de Dados
db = connection['db_pubmed_aheadofprint']

# Coleção
# collection = db['col_id']

# Abrindo arquivo de ids para leitura
file_read = open(nome_arq_id, 'r')

for line in file_read:

    line = line.replace('\n','')
    print line
    db.col_id.insert_one({'_id':line})


# Fechando arquivo
file_read.close()


# Finaliza a execução do script
sys.exit(0)


