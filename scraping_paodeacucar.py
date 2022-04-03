#Extracao de dados e download de imagens de um site

#Biblioteca Uteis
import requests
import  json
from bs4 import BeautifulSoup
import os
import time

#variveis gerais
iLISTA_DEPARTAMENTOS = []
iURL_BASE = "https://www.paodeacucar.com/"
iBASEAPI = "https://api.gpa.digital/pa/categoria/ecom"

################# CAPTURA DOS DEPARTAMENTOS INICIO
def captaDEPARTAMENTOS(iJSON,iLISTA_DEPARTAMENTOS):
    for itens in iJSON['props']['initialProps']['layoutProps']['categories']:
        for depto_secao in itens['subCategory']:
            iLISTA_DEPARTAMENTOS.append(depto_secao['uiLink'])

def acessaSITE(iURLBASE,iLISTA_DEPARTAMENTOS):
    response = requests.request("GET", iURLBASE)
    soup = BeautifulSoup(response.text, 'html.parser')
    iJSON = str(soup.find_all('script',id='__NEXT_DATA__')).replace('[<script id="__NEXT_DATA__" type="application/json">','').replace('</script>]','')
    captaDEPARTAMENTOS(json.loads(iJSON),iLISTA_DEPARTAMENTOS)
################# CAPTURA DOS DEPARTAMENTOS FIM

################ GRAVAO DE ARQUIVO TEXTO
def gera_TXT(iTEXTOLOG): 
    iPASTA_ARQ = "C:/Users/pinhe/Documents/Python/TMP/" #informe o caminho da sua pasta
    arquivo = open(iPASTA_ARQ + "extracao.txt", 'a', encoding="utf-8")  
    arquivo.writelines(str(iTEXTOLOG) + "\n")
    arquivo.close()


############GRAVACAO DOS ARQUIVOS DE IMAGENS
def baixaARQIMAGEM(iURL,IEAN):
    iPASTA_DOWN = "C:/Users/pinhe/Documents/Python/TMP" + "/" #informe o caminho da sua pasta
    iNOMEARQ =  iPASTA_DOWN + str(IEAN) + ".webp" 
    if os.path.isfile(iNOMEARQ) == False:
        response = requests.get(iURL)
        file = open(iNOMEARQ, "wb")
        file.write(response.content)
        file.close()

################# CAPTURA DAS INDORMAÇÕES DE ITENS - INICIO
def buscaITENS_PAGINA(departamento,numPAGINATOTAL):
    print("iniciando captura dos itens departamento: " + str(departamento) + " total de paginas: " + str(numPAGINATOTAL))
    iCONTADOR = 0
    while iCONTADOR <= numPAGINATOTAL:
        response = requests.request("GET", str(iBASEAPI) + str(departamento) + "?storeId=461&qt=36&s=&ftr=&p=" + str(iCONTADOR)  + "&rm=&gt=grid&isClienteMais=true")
        iTOTAL_ITENS_PAGINA = 0
        if response.status_code == 200:
            for itens in json.loads(response.text)['content']['products']:
                
                #JSON COMPLETO
                iPROD_JSON = json.dumps(itens, indent=4, sort_keys=True)
                
                #BASE
                iPROD_NOME = ""
                iSKU_PROD = 0
                iPRECO_PROD = 0
                iPRECO_OFERTA = 0
                iURL_PROD = ""

                iPROD_NOME = itens['name']
                iSKU_PROD = itens['sku']
                iURL_PROD = str(iURL_BASE) + str(itens['urlDetails'])
                iPRECO_PROD = itens['currentPrice']
                
                if "productPromotions" in itens: 
                    iPRECO_OFERTA = itens['productPromotion']['unitPrice']

                #IMAGEM
                iIMG_PRINCIPAL_PROD = ""
                iIMGBASE64 = ""
                try:
                    if str(iSKU_PROD) != "0"  :
                        iIMG_PRINCIPAL_PROD = itens['mapOfImages']['0']['BIG']
                        baixaARQIMAGEM(str(iURL_BASE) + str(iIMG_PRINCIPAL_PROD),iSKU_PROD)
                except:
                    pass

                print(str(iPROD_NOME) + " " + str(iPRECO_PROD)  + " " + str(iURL_PROD))
                gera_TXT(str(iPROD_NOME) + "|" + str(iSKU_PROD) + "|" + str(iPRECO_PROD) + "|"    + str(iPRECO_OFERTA)  + "|" + str(iURL_PROD))
                time.sleep(2)
                
                
                iTOTAL_ITENS_PAGINA += 1

        print("pagina: " + str(iCONTADOR) + " de: " + str(numPAGINATOTAL) + " total de itens na pagina: " + str(iTOTAL_ITENS_PAGINA))
        if iTOTAL_ITENS_PAGINA == 0 : break #acabou os itens da selecao
        iCONTADOR += 1 

def varreTOTALITENS(departamento,iJSON_PROD):
    iTOTALPAGINAS = iJSON_PROD['props']['initialProps']['componentProps']['categoryContent']['totalPages']
    buscaITENS_PAGINA(departamento,iTOTALPAGINAS)

def captaITENS_DEPTOS(iLISTA_DEPARTAMENTOS):
    for departamento in iLISTA_DEPARTAMENTOS:
        print("iniciando captura dos itens departamento: " + str(departamento))
        response = requests.request("GET", str(iURL_BASE) + "/categoria" + str(departamento) + "?qt=12&p=0&gt=grid")
        soup = BeautifulSoup(response.text, 'html.parser')
        iJSON_PROD = str(soup.find_all('script',id='__NEXT_DATA__')).replace('[<script id="__NEXT_DATA__" type="application/json">','').replace('</script>]','')
        varreTOTALITENS(departamento,json.loads(iJSON_PROD))
################# CAPTURA DAS INDORMAÇÕES DE ITENS - FIM

acessaSITE(iURL_BASE,iLISTA_DEPARTAMENTOS) #FAZ A CAPTURA DOS DEPARTAMENTOS
captaITENS_DEPTOS(iLISTA_DEPARTAMENTOS) #PERCORRE OS DEPARTAMENTOS EM BUSCA DOS ITENS