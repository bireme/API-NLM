#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------- #
# ?????.py - Coleta ID´s da API NLM e em seguida baixa os respectivos XMLs
# ------------------------------------------------------------------------- #
#      Entrada:
#        Saida: 
#     Corrente: 
#      Chamada: python3 ../tpl/????.py
#      Exemplo: python3 ../tpl/coleta_id3.py
#     Objetivo: 
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
from LoadUrl import loadUrl 

# conexao com o banco para id
job_id = Classe('db_pubmed_aheadofprint','col_id')

# conexao com o banco para id
job_xml = Classe('db_pubmed_aheadofprint','col_xml')




# Apaga temporariamente as coleções
job_id.dropCollection()
job_xml.dropCollection()

# URL utilizada para recolher total de registros
URL_esearch = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=pubstatusaheadofprint&retmode=json'

# retmax - essa variavel devera ser deixada com zero pois nesse momento o que é importante é o count
retmax = '&retmax=0'



# URL utilizada para trazer XMLs
URL_efetch = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id='

# Monsta a URL para trazer o JSON que contem "count"
URL_count = '%s%s' % (URL_esearch,retmax) 

# Executado consulta
r_t = requests.get(URL_count)

# Armazenando conteudo em 'data_t'
data_t = r_t.json()

# print (data_t)

# Lendo conteudo 'count' em total_ids
# total_ids = data_t['esearchresult']['count']


# Forçando apenas para teste
total_ids = 2

print (' Total de registros existentes na pesquisa: ', total_ids)

# exit()




nome_arq_id = 'ids.id'

## Abrindo novo arquivo para gravacao
id_file = open(nome_arq_id, 'w')


COUNT = 1
while (COUNT <= total_ids ):
    print ('+ ', COUNT)


    # Montando URL para coleta do ID
    retmax = '&retmax=1'
    retstart= '&retstart='

    URL = '%s%s%s%s' % (URL_esearch,retmax,retstart,COUNT)
    # print (URL)

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


## Tratamento para gravar o id e xml
# Abrindo arquivo de ids para leitura
file_read = open(nome_arq_id, 'r')

for line in file_read:

    # Insere id na colecao col_id
    #--------------------------------------------------------------------------
    line = line.replace('\n','')
    print ('Gravando id: ',line)
    job_id.saveDoc({'_id':line,"last_modified": datetime.datetime.now()})



    # Insere XML na colecao col_xml
    #--------------------------------------------------------------------------
    URL_wrk = '%s%s' % (URL_efetch,line)
    # print (URL_wrk)
    
    xml_content = loadUrl(URL_wrk)
    
    # pega 2 elemento da tupla ( [1] ) e codifica para utf-8. Codifica pois se nao o fizer
    # o tipo do dado sera gravado como BinData no MongoDB
    xml_content = xml_content[1].decode('utf-8')
    # print (loadUrl(URL_wrk))

    # print ('conteudo do XML: \n',xml_content)
    job_xml.saveDoc({'_id':line,"last_modified": datetime.datetime.now(),'xml_content':xml_content})
    



# Fechando arquivo
file_read.close()



# Finaliza a execução do script
sys.exit(0)


