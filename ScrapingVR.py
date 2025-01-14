import streamlit as st
import locale
from babel.numbers import format_currency
import googlemaps
from datetime import datetime
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import folium
import streamlit as st
from streamlit_folium import folium_static
import plotly.express as px
from streamlit_card import card


# LINK COLAB: https://colab.research.google.com/drive/1WBLHOJAsWAXwqVZ5mBmqoA95i1DRq-Ji?usp=sharing
st.set_page_config(
		page_title="Scraping - Viva Real Imóveis",
		page_icon="🧊",
		layout="wide",
		initial_sidebar_state="expanded",
		menu_items={
			'Get Help': 'https://30days-tmp.streamlit.app/?ref=blog.streamlit.io',
			'Report a bug': "mailto:massaki.igarashi@gmail.com",
			'About': "# Scraping - Viva Real Imóveis (Desenvolvedor: Massaki de O. Igarashi)"
		}
	)

st.title(":blue[Scraping] - Viva Real :blue[Imóveis]")
st.subheader(":blue[Desenvolvido por: Massaki de O. Igarashi]")    
#FUNÇÕES

#!pip install babel

from babel.numbers import format_currency

def formatar_para_real(valor):
    return format_currency(valor, 'BRL', locale='pt_BR')

# Exemplo de uso
valor = 12345.67
#st.write(formatar_para_real(valor))  # Saída: R$ 12.345,67

import locale

def SepararEndereco(VETendereco):
  for i in range(len(VETendereco)):
    END = str(VETendereco[i]).split('-')
    if len(END)==3:
      RuaNum = str(END[0]).split(',')
      Rua = RuaNum[0]
      Num = RuaNum[1]
      BairroCidade = str(END[1]).split(',')
      Bairro = BairroCidade[0]
      Cidade = BairroCidade[1]
      Estado = END[2]
      return Rua, Num, Bairro, Cidade, Estado

#A função SepararEndereco2 é para WebScraping_imobiliariaVIVAREAL(7).ipynb
# D = Apartamento na Avenida Prefeito Luís Latorre, 4399, Vila das Hortências em Jundiaí, por R$ 528.000 - Viva Real
# E = Avenida Prefeito Luís Latorre, 4399 - Vila das Hortências, Jundiaí - SP
def SepararEndereco2(endereco):
  try:
    RuaBairroCidade = endereco.split(',')
    if len(RuaBairroCidade)==3:
      Rua = RuaBairroCidade[0]
      NumBairro = RuaBairroCidade[1].split('-')
      Num = NumBairro[0]
      Bairro = NumBairro[1]
      Cidade = RuaBairroCidade[2]
      return Rua, Num, Bairro, Cidade
    elif len(RuaBairroCidade)==2:
      Bairro = RuaBairroCidade[0]
      Cidade = RuaBairroCidade[1]
      return " ", " ", Bairro, Cidade
    elif len(RuaBairroCidade)==1:
      Cidade = RuaBairroCidade
      return " ", " ", " ", Cidade
  except Exception as e:
    st.write( f"Erro de processamento {e}")
    return " ", " ", " ", " "

def converter_preco(preco_str):
    # Remove 'R$', espaços extras e substitui ',' por '.'
    preco_str = preco_str.replace('R$', '').replace('.', '').replace(',', '.').replace('A partir de ', '').replace('Preço abaixo do mercado','').strip()
    return float(preco_str)

def calcular_media_intervalo(intervalo_str):
    # Divide a string pelo separador '-'
    valores = intervalo_str.split('-')
    s = 0
    for i in range(len(valores)):
      s = s + float(valores[i])
    media = s / len(valores)
    return media

def formatar_para_real(valor):
    # Try setting a supported locale
    # Check available locales with: locale -a
    # Choose one relevant to your system, e.g., 'pt_BR' or 'pt_BR.utf8'
    # Replace 'pt_BR.UTF-8' if it doesn't exist in the locale -a output
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        # Try fallback locales if 'pt_BR.UTF-8' is not available
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR') # Try without .UTF-8
        except locale.Error:
            locale.setlocale(locale.LC_ALL, '')  # Use system default

    return locale.currency(valor, grouping=True)

def CalcDist(rua, numero, bairro, cidade, pais = "Brazil", EndREF = "Rua Dr. Eloy Chaves, 178, Ponte São João, Jundiaí - SP, Brasil"):
  try:
    # TODO: Replace the API key below with a valid API key. Will not work otherwise.
    gmaps = googlemaps.Client(key='AIzaSyDaQ5PLjBiz1himo5glHszyQNiMlkqHNns') #criada em 11jan24 e-mail massaki.igarashi@gmail.com

    #rua = input("Rua: ")
    #numero = input("Nº: ")
    #bairro = input("Bairro: ")
    #cidade = input("Cidade: ")
    #pais = "Brazil"

    endereco = str(rua + ", " + numero + ", " + bairro + ", " + cidade + ", " + pais)
    #st.write(endereco)
    # Use Geocoding API to look up latitude, longitude for a place
    #address = 'Av. Brasil, 1220, Jardim Guanabara, Campinas, Brazil'
    address = endereco
    geocode_result = gmaps.geocode(address)

    #st.write("Endereço de PARTIDA: ", address)
    LatLon = str(geocode_result[0]["geometry"]["location"])
    #st.write(LatLon)
    lat1 = float(LatLon[7:17])  # Substring: https://www.freecodecamp.org/news/how-to-substring-a-string-in-python/
    #st.write("A Latitude é ", lat1)
    lon1 = float(LatLon[27:36])
    #st.write("A Longitude é ", lon1)
    #st.write("======================================================")
    #st.write("Geocoding address...")
    #st.write("Address:",address,"Coordinates:",geocode_result[0]["geometry"]["location"])

    # Look up an address with reverse geocoding (UBC Vancouver)
    #Coordenadas Torre do Castelo
    #lat = -22.890011259393248
    #lon = -47.07690080476346
    reverse_geocode_result = gmaps.reverse_geocode((lat1, lon1))

    #st.write("PROGRAMA PARA CALCULAR ROTA, DISTÂNCIA e TEMPO para o deslocamento entre dois endereços a serem fornecidos por você!")
    #st.write("Por favor, insira os dados do ENDEREÇO DE REFERÊNCIA para o cálculo de distância entre cada endereço:")

    #rua2 = input("Rua: ")
    #numero2 = input("Nº: ")
    #bairro2 = input("Bairro: ")
    #cidade2 = input("Cidade: ")
    #pais2 = "Brazil"
    #endereco2 = str(rua2 + ", " + numero2 + ", " + bairro2 + ", " + cidade2 + ", " + pais2)

    #st.write(endereco2)
    # Use Geocoding API to look up latitude, longitude for a place
    #address2 = 'Av. Brasil, 1220, Jardim Guanabara, Campinas, Brazil'
    #address2 = endereco2
    address2 = EndREF

    geocode_result2 = gmaps.geocode(address2)
    LatLon02 = address2.split('{')
    #st.write(LatLon02)
    #st.write("======================================================")
    #st.write("Para o Endereço: ", address2)
    LatLon2 = str(geocode_result2[0]["geometry"]["location"])
    #st.write(LatLon2)
    lat2 = float(LatLon2[7:19])  # Substring: https://www.freecodecamp.org/news/how-to-substring-a-string-in-python/
    #st.write("A Latitude é ", lat2)
    lon2 = float(LatLon2[27:37])
    #st.write("A Longitude é ", lon2)
    reverse_geocode_result = gmaps.reverse_geocode((lat2, lon2))
    #st.write("\nReverse geocoding...")
    #st.write("Coordinates: ",lat2,lon2,"Address:",reverse_geocode_result[0]["formatted_address"])

    # Request driving directions between UBC Okanagan and UBC Vancouver
    now = datetime.now()
    directions_result = gmaps.directions(address,
                                        reverse_geocode_result[0]["formatted_address"],
                                        mode="driving",
                                        departure_time=now)

    #st.write("\nDriving directions...")
    leg = directions_result[0]['legs'][0]

    #ROTINA DE SEPARAÇÃO DO CEP
    cep = str(leg['start_address']).split(',')

    #st.write("Endereço 1:",leg['start_address'],"\nEndereço 2:",leg['end_address'])

    if len(cep)<5:
      CEP = ""
    else:
      CEP = cep[3]
    #st.write("Distance:",leg['distance']['text'],"Time:",leg['duration']['text'])
    i = 1
    for step in leg['steps']:
        #st.write("Step",i,":",step['duration']['text'], step['html_instructions'])
        i=i+1

    #st.write("================================================================")
    #st.write("Distância entre os dois endereços:",leg['distance']['text'])
    return lat1, lon1, leg['distance']['text'], CEP
  except Exception as e:
    st.write( f"Erro de processamento {e}")
    return " ", " ", " ", " "

#========================================================================================
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd

def CustoM2(valor_str, area):
  try:
    VAL = str(valor_str).split(".")
    if len(VAL)==2:
      preco = VAL[0]
      Valor = float(preco)*1000
    else:
      Valor = float(valor_str)
    return round(Valor/float(area), 2)
  except Exception as e:
    return " "

# Link = https://www.vivareal.com.br/imovel/apartamento-3-quartos-vila-das-hortencias-bairros-jundiai-com-garagem-75m2-venda-RS528000-id-2770017239/
def ExtraiDadosDaDescricaoFromURL(url):
  try:
    scraper = cloudscraper.create_scraper()
    # Faz a requisição à página
    response = scraper.get(url)
    if response.status_code == 200:
      soup = BeautifulSoup(response.text, 'html.parser')

        # Salva o conteúdo do objeto soup em um arquivo HTML
      with open('pagina_raspada3.html', 'w', encoding='utf-8') as file:
        file.write(soup.prettify())


      # Localizar o dado específico
      titulo_tag = soup.find('title')
      # Extrair o texto do título
      titulo = titulo_tag.get_text(strip=True) if titulo_tag else 'Dado não encontrado'

      # Localizar o elemento que contém o endereço
      endereco_tag = soup.find('p', class_='l-text l-u-color-neutral-28 l-text--variant-body-regular l-text--weight-bold address-info-value')
      endereco = endereco_tag.get_text(strip=True) if endereco_tag else 'Endereço não encontrado'

      # Localizar o elemento que contém o valor
      valor_tag = soup.find('p', class_='l-text l-u-color-neutral-28 l-text--variant-display-regular l-text--weight-bold price-info-value', attrs={'data-testid': 'price-info-value'})
      valor = valor_tag.get_text(strip=True) if valor_tag else 'Valor não encontrado'
      preco = valor.split("R$")
      # Localizar o elemento que contém a área
      area_tag = soup.find('span', class_='amenities-item-text', attrs={'data-cy': 'ldp-propertyFeatures-txt'})
      area = area_tag.get_text(strip=True) if area_tag else 'Área não encontrada'
      ValorArea = area.split("m²")
      # Localizar todos os elementos com a classe e atributo específicos
      amenities_tags = soup.find_all('span', class_='amenities-item-text', attrs={'data-cy': 'ldp-propertyFeatures-txt'})

      # Encontrar o elemento <span> com a classe e id específicos
      elemento_condominio = soup.find('span', class_='l-text l-u-color-neutral-28 l-text--variant-body-regular l-text--weight-bold undefined', id='condo-fee-price')

      # Extrair o texto do elemento encontrado
      valor_condominio = elemento_condominio.get_text() if elemento_condominio else 'Dado não encontrado'

      return titulo, endereco, float(preco[1])*1000.0, int(ValorArea[0]), float(CustoM2(preco[1], ValorArea[0])), valor_condominio
  except Exception as e:
    st.write( f"Erro de processamento {e} na url = {url}")
    return " ", " ", " ", " ", " ", " "

#url = 'https://www.vivareal.com.br/venda/sp/jundiai/apartamento_residencial/3-quartos/#com=salao-de-festas,sacada&onde=Brasil,S%C3%A3o%20Paulo,Jundia%C3%AD,,,,,,BR%3ESao%20Paulo%3ENULL%3EJundiai,,,&ordenar-por=preco:ASC&quartos=3&vagas=2'
with st.container(border=True):
    coluna1, coluna2, coluna3 = st.columns(3)
    with coluna1:
        OPTcomodos = st.selectbox(
        "QTD de comodos",
        ("1-quarto", "2-quartos", "3-quartos", "4-quartos"),
        index=2,
        #placeholder="Selecione a quantidade de comodos...",
        )
    with coluna2:
        OPTvagas = st.selectbox(
        "QTD de Vagas na Garagem",
        ("1 vaga", "2 vagas", "3 vagas", "4 vagas"),
        index=1,
        #placeholder="Selecione a quantidade de comodos...",
        )

    with coluna3:
        OPTcidade = st.selectbox(
        "Cidade:",
        ("Jundiai", "Campinas", "São Paulo"),
        index=0,
        #placeholder="Selecione a quantidade de comodos...",
        )
    
    if OPTcomodos == "1-quarto":
        quartos = "quartos=1"
    elif OPTcomodos == "2-quartos":
        quartos = "quartos=2"
    elif OPTcomodos == "3-quartos":
        quartos = "quartos=3"
    elif OPTcomodos == "4-quartos":
        quartos = "quartos=4"  

    if OPTvagas == "1 vaga":
        vagas = "vagas=1"
    elif OPTvagas == "2 vagas":
        vagas = "vagas=2"
    elif OPTvagas == "3 vagas":
        vagas = "vagas=3"
    elif OPTvagas == "4 vagas":
        vagas = "vagas=4"     
    
   
    if OPTcidade == "São Paulo":
        Cidade = "São%20Paulo"
        cidade = "sao-paulo"
    else:
        Cidade = OPTcidade
        cidade = OPTcidade.lower()
      
    coluna11, coluna12 = st.columns(2)
    with coluna11:
        coluna111, coluna112 = st.columns(2)
        with coluna111:
            ValorMinimoBusca = st.number_input("Valor mínimo para busca:", value=400000, step = 10000)
        with coluna112:
            ValorMaximoBusca = st.number_input("Valor máximo para busca:", value=600000, step = 10000)
    with coluna12:
        st.write(" ")
        
    path = f"https://www.vivareal.com.br/venda/sp/{cidade}/apartamento_residencial/{OPTcomodos}/#com=salao-de-festas,sacada&onde=Brasil,S%C3%A3o%20Paulo,{Cidade}%C3%AD,,,,,,BR%3ESao%20Paulo%3ENULL%3E{Cidade},,,&ordenar-por=preco:ASC&{quartos}&{vagas}"
    txtURL = st.text_input("Raspar a URL:", path)
    if txtURL:
        url = txtURL  

scraper = cloudscraper.create_scraper()

# Faz a requisição à página
response = scraper.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

# Salva o conteúdo do objeto soup em um arquivo HTML
with open('pagina_raspada.html', 'w', encoding='utf-8') as file:
  file.write(soup.prettify())

linkUtil = []
j = 0
for a_href in soup.find_all("a", href=True):
    if str(a_href["href"]).startswith("/imovel/"):
      linkUtil.append(a_href["href"])
      #st.write(f"ID: {j}")
      #st.write(a_href["href"])
      j = j+1

#st.write(linkUtil)

linkUtil2 = []
for i in range(len(linkUtil)):
  link = "https://www.vivareal.com.br" + linkUtil[i]
  dados = linkUtil[i].split("/")
  #st.write(dados)
  dadosImovel = dados[2].split("-")
  comodos = dadosImovel[1]
  Val = dadosImovel[len(dadosImovel)-3]
  Valor = Val.split("RS")
  area = dadosImovel[len(dadosImovel)-5].split("m2")
  if int(Valor[1]) > int(ValorMinimoBusca) and int(Valor[1]) < int(ValorMaximoBusca):
    #st.write(f"i: {i}")
    #st.write(dadosImovel)
    #st.write(f"Comodos: {comodos}")
    #st.write(f"area: {area[0]}")
    #st.write(f"Valor: {Valor[1]}")
    linkUtil2.append(link)
    #st.write(link)
with st.expander("Auditoria dos Links obtidos na raspagem:"):
    st.write(linkUtil2)

#=====================================================================================
VETdesc = []
VETend = []
VETrua = []
VETnum = []
VETbairro = []
VETcidade = []
VETval = []
VETarea = []
VETm2 = []
VETcond = []
VETlat = []
VETlon = []
VETdist = []
VETcep = []
VETlink = []
for i in range(len(linkUtil2)):
  #link = "https://www.vivareal.com.br" + linkUtil[i]
  #link = linkUtil2[i]
  VETlink.append(linkUtil2[i])
  #st.write(f"Link = {link}")
  D, E, V, A, M2, VCND = ExtraiDadosDaDescricaoFromURL(linkUtil2[i])
  #st.write(f"D = {D}")
  #st.write(f"E = {E}")
  Rua, Num, Bairro, Cidade = SepararEndereco2(E)
  VETdesc.append(D)
  VETend.append(E)
  VETrua.append(Rua)
  VETnum.append(Num)
  VETbairro.append(Bairro)
  VETcidade.append(Cidade)
  lat, lon, dist, CEP = CalcDist(Rua, Num, Bairro, Cidade, pais = "Brazil", EndREF = "Rua Dr. Eloy Chaves, 178, Ponte São João, Jundiaí - SP, Brasil")
  VETlat.append(lat)
  VETlon.append(lon)
  VETdist.append(dist)
  VETcep.append(CEP)
  VETval.append(V)
  VETarea.append(A)
  VETm2.append(M2)
  VETcond.append(VCND)

dFPesqIMOVEIS = pd.DataFrame({'DESCRIÇÃO': VETdesc, 'LOGRADOURO': VETend, 'RUA':VETrua, 'NUM': VETnum, 'BAIRRO':  VETbairro, 'CIDADE': VETcidade, 'CEP': VETcep, 'VALOR': VETval, 'AREA': VETarea, 'R$/m2': VETm2, 'Val. Condominio': VETcond, 'LAT': VETlat, 'LON': VETlon, 'DIST': VETdist, 'link': VETlink})
#st.write(dFPesqIMOVEIS)

dFPesqIMOVEIS2 = dFPesqIMOVEIS.dropna()
# Convert columns with lists to tuples or strings before dropping duplicates
for column in dFPesqIMOVEIS2.select_dtypes(include=['object']).columns:
    # Check if the column contains any lists
    if any(isinstance(x, list) for x in dFPesqIMOVEIS2[column]):
        # If it does, convert lists to tuples
        dFPesqIMOVEIS2[column] = dFPesqIMOVEIS2[column].apply(lambda x: tuple(x) if isinstance(x, list) else x)

dFPesqIMOVEIS = dFPesqIMOVEIS2.drop_duplicates(subset=['LOGRADOURO'])
dFPesqIMOVEIS = dFPesqIMOVEIS.dropna()

indiceVazio = []
# Iterate through the DataFrame using .iterrows() or .index
# Use .index to get the actual index values for the rows
# for i in dFPesqIMOVEIS.index:
# or: for index, row in dFPesqIMOVEIS.iterrows():
for index, row in dFPesqIMOVEIS.iterrows():
  if row['DESCRIÇÃO'] == " ":
    indiceVazio.append(index)  # Append the index value of empty description
for i in indiceVazio:
  dFPesqIMOVEIS = dFPesqIMOVEIS.drop(i)

st.write(dFPesqIMOVEIS)  
st.divider()
#https://leonardovinci67.medium.com/visualizing-location-on-google-map-using-python-25b6bf7eee65

LAT = list(dFPesqIMOVEIS['LAT'])
LON = list(dFPesqIMOVEIS['LON'])
COORD2 = []
ROTULOS2 = []

for index, row in dFPesqIMOVEIS.iterrows():
    if row['LAT'] != " ":
        COORD2.append([row['LAT'], row['LON']])
        ROTULOS2.append(f"{index} - {row['DESCRIÇÃO']} (R${row['VALOR']})")

# Cálculo do ponto central
LAT = [float(x) for x in LAT if x != " "]
LON = [float(x) for x in LON if x != " "]
center_lat = sum(LAT) / len(LAT)
center_lon = sum(LON) / len(LON)

# Criação do mapa com Folium
mapa = folium.Map(location=[center_lat, center_lon], zoom_start=13)

# Adição dos marcadores ao mapa
for j, (lat, lon) in enumerate(COORD2):
    folium.Marker([lat, lon], popup=ROTULOS2[j]).add_to(mapa)

# Exibição do mapa no Streamlit
col1, col2 = st.columns(2)
with col1:
    st.title("Mapa de Imóveis desta raspagem")
    folium_static(mapa)
with col2:    
    VALORmedio = dFPesqIMOVEIS['VALOR'].mean()
    VALORmedio = int(VALORmedio)

    VALORmedioM2 = dFPesqIMOVEIS['R$/m2'].mean()
    VALORmedioM2 = int(VALORmedioM2)
    
    AREAmedia = dFPesqIMOVEIS['AREA'].mean()
    AREAmedia = int(AREAmedia)

    col2_1, col2_2, col2_3 = st.columns(3)
    with col2_1:
        res = card(
            title=f"R$ {VALORmedio}",
            text="Val. Venda Médio",
            image="https://placekitten.com/500/500",
            styles={
                "card": {
                    "width": "100%", # <- make the card use the width of its container, note that it will not resize the height of the card automatically
                    "height": "100px" # <- if you want to set the card height to 300px                    
                }
            }
        )
    with col2_2:
        res = card(
            title=f"R$ {VALORmedioM2}",
            text="Média R$/m²",
            image="https://placekitten.com/500/500",
            styles={
                "card": {
                    "width": "100%", # <- make the card use the width of its container, note that it will not resize the height of the card automatically
                    "height": "100px" # <- if you want to set the card height to 300px                    
                }
            }
        )
    with col2_3:
        res = card(
            title=F"{AREAmedia} m²",
            text="Área média",
            image="https://placekitten.com/500/500",
            styles={
                "card": {
                    "width": "100%", # <- make the card use the width of its container, note that it will not resize the height of the card automatically
                    "height": "100px" # <- if you want to set the card height to 300px                    
                }
            }
        )
    VALORminimo = min(dFPesqIMOVEIS['VALOR'])
    VALORmaximo = max(dFPesqIMOVEIS['VALOR'])
    st.write("Menor Valor: R$", VALORminimo)    
    resultadoMIN = dFPesqIMOVEIS.loc[dFPesqIMOVEIS['VALOR'] == VALORminimo]
    st.write(resultadoMIN)
    st.write("Maior Valor: R$", VALORmaximo)
    resultadoMAX = dFPesqIMOVEIS.loc[dFPesqIMOVEIS['VALOR'] == VALORmaximo]
    st.write(resultadoMAX)
# Contagem de valores por bairro
ListaBairros = dFPesqIMOVEIS["BAIRRO"].value_counts()
# Armazenar os bairros e suas contagens em um dicionário
bairros_dict = ListaBairros.to_dict()
dfListaBairros = pd.DataFrame({'BAIRRO': bairros_dict.keys(), 'IMOVEIS': bairros_dict.values()})
#st.title("Distribuição de imóveis por bairro:")
#st.write(dfListaBairros)# Contagem de valores por bairro

n = len(dfListaBairros["BAIRRO"])
VETcustom2 = []
if n==1:
  selecao0 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][0]
  df0 = dFPesqIMOVEIS[selecao0]
  #st.write(df0["R$/m2"].mean())
  VETcustom2.append(df0["R$/m2"].mean())
elif n==2:
  selecao0 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][0]
  df0 = dFPesqIMOVEIS[selecao0]
  #st.write(df0["R$/m2"].mean())
  VETcustom2.append(df0["R$/m2"].mean())

  selecao1 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][1]
  df1 = dFPesqIMOVEIS[selecao1]
  #st.write(df1["R$/m2"].mean())
  VETcustom2.append(df1["R$/m2"].mean())
elif n==3:
  selecao0 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][0]
  df0 = dFPesqIMOVEIS[selecao0]
  #st.write(df0["R$/m2"].mean())
  VETcustom2.append(df0["R$/m2"].mean())

  selecao1 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][1]
  df1 = dFPesqIMOVEIS[selecao1]
  #st.write(df1["R$/m2"].mean())
  VETcustom2.append(df1["R$/m2"].mean())

  selecao2 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][2]
  df2 = dFPesqIMOVEIS[selecao2]
  #st.write(df2["R$/m2"].mean())
  VETcustom2.append(df2["R$/m2"].mean())
elif n==4:
  selecao0 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][0]
  df0 = dFPesqIMOVEIS[selecao0]
  #st.write(df0["R$/m2"].mean())
  VETcustom2.append(df0["R$/m2"].mean())

  selecao1 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][1]
  df1 = dFPesqIMOVEIS[selecao1]
  #st.write(df1["R$/m2"].mean())
  VETcustom2.append(df1["R$/m2"].mean())

  selecao2 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][2]
  df2 = dFPesqIMOVEIS[selecao2]
  #st.write(df2["R$/m2"].mean())
  VETcustom2.append(df2["R$/m2"].mean())

  selecao3 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][3]
  df3 = dFPesqIMOVEIS[selecao3]
  #st.write(df3["R$/m2"].mean())
  VETcustom2.append(df3["R$/m2"].mean())
elif n==5:
  selecao0 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][0]
  df0 = dFPesqIMOVEIS[selecao0]
  #st.write(df0["R$/m2"].mean())
  VETcustom2.append(df0["R$/m2"].mean())

  selecao1 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][1]
  df1 = dFPesqIMOVEIS[selecao1]
  #st.write(df1["R$/m2"].mean())
  VETcustom2.append(df1["R$/m2"].mean())

  selecao2 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][2]
  df2 = dFPesqIMOVEIS[selecao2]
  #st.write(df2["R$/m2"].mean())
  VETcustom2.append(df2["R$/m2"].mean())

  selecao3 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][3]
  df3 = dFPesqIMOVEIS[selecao3]
  #st.write(df3["R$/m2"].mean())
  VETcustom2.append(df3["R$/m2"].mean())

  selecao4 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][4]
  df4 = dFPesqIMOVEIS[selecao4]
  #st.write(df4["R$/m2"].mean())
  VETcustom2.append(df4["R$/m2"].mean())
elif n==6:
  selecao0 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][0]
  df0 = dFPesqIMOVEIS[selecao0]
  #st.write(df0["R$/m2"].mean())
  VETcustom2.append(df0["R$/m2"].mean())

  selecao1 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][1]
  df1 = dFPesqIMOVEIS[selecao1]
  #st.write(df1["R$/m2"].mean())
  VETcustom2.append(df1["R$/m2"].mean())

  selecao2 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][2]
  df2 = dFPesqIMOVEIS[selecao2]
  #st.write(df2["R$/m2"].mean())
  VETcustom2.append(df2["R$/m2"].mean())

  selecao3 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][3]
  df3 = dFPesqIMOVEIS[selecao3]
  #st.write(df3["R$/m2"].mean())
  VETcustom2.append(df3["R$/m2"].mean())

  selecao4 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][4]
  df4 = dFPesqIMOVEIS[selecao4]
  #st.write(df4["R$/m2"].mean())
  VETcustom2.append(df4["R$/m2"].mean())

  selecao5 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][5]
  df5 = dFPesqIMOVEIS[selecao5]
  #st.write(df5["R$/m2"].mean())
  VETcustom2.append(df5["R$/m2"].mean())
elif n==7:
  selecao0 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][0]
  df0 = dFPesqIMOVEIS[selecao0]
  #st.write(df0["R$/m2"].mean())
  VETcustom2.append(df0["R$/m2"].mean())

  selecao1 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][1]
  df1 = dFPesqIMOVEIS[selecao1]
  #st.write(df1["R$/m2"].mean())
  VETcustom2.append(df1["R$/m2"].mean())

  selecao2 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][2]
  df2 = dFPesqIMOVEIS[selecao2]
  #st.write(df2["R$/m2"].mean())
  VETcustom2.append(df2["R$/m2"].mean())

  selecao3 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][3]
  df3 = dFPesqIMOVEIS[selecao3]
  #st.write(df3["R$/m2"].mean())
  VETcustom2.append(df3["R$/m2"].mean())

  selecao4 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][4]
  df4 = dFPesqIMOVEIS[selecao4]
  #st.write(df4["R$/m2"].mean())
  VETcustom2.append(df4["R$/m2"].mean())

  selecao5 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][5]
  df5 = dFPesqIMOVEIS[selecao5]
  #st.write(df5["R$/m2"].mean())
  VETcustom2.append(df5["R$/m2"].mean())

  selecao6 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][6]
  df6 = dFPesqIMOVEIS[selecao6]
  #st.write(df6["R$/m2"].mean())
  VETcustom2.append(df6["R$/m2"].mean())
elif n==8:
  selecao0 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][0]
  df0 = dFPesqIMOVEIS[selecao0]
  #st.write(df0["R$/m2"].mean())
  VETcustom2.append(df0["R$/m2"].mean())

  selecao1 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][1]
  df1 = dFPesqIMOVEIS[selecao1]
  #st.write(df1["R$/m2"].mean())
  VETcustom2.append(df1["R$/m2"].mean())

  selecao2 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][2]
  df2 = dFPesqIMOVEIS[selecao2]
  #st.write(df2["R$/m2"].mean())
  VETcustom2.append(df2["R$/m2"].mean())

  selecao3 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][3]
  df3 = dFPesqIMOVEIS[selecao3]
  #st.write(df3["R$/m2"].mean())
  VETcustom2.append(df3["R$/m2"].mean())

  selecao4 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][4]
  df4 = dFPesqIMOVEIS[selecao4]
  #st.write(df4["R$/m2"].mean())
  VETcustom2.append(df4["R$/m2"].mean())

  selecao5 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][5]
  df5 = dFPesqIMOVEIS[selecao5]
  #st.write(df5["R$/m2"].mean())
  VETcustom2.append(df5["R$/m2"].mean())

  selecao6 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][6]
  df6 = dFPesqIMOVEIS[selecao6]
  #st.write(df6["R$/m2"].mean())
  VETcustom2.append(df6["R$/m2"].mean())

  selecao7 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][7]
  df7 = dFPesqIMOVEIS[selecao7]
  #st.write(df7["R$/m2"].mean())
  VETcustom2.append(df7["R$/m2"].mean())
elif n==9:
  selecao0 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][0]
  df0 = dFPesqIMOVEIS[selecao0]
  #st.write(df0["R$/m2"].mean())
  VETcustom2.append(df0["R$/m2"].mean())

  selecao1 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][1]
  df1 = dFPesqIMOVEIS[selecao1]
  #st.write(df1["R$/m2"].mean())
  VETcustom2.append(df1["R$/m2"].mean())

  selecao2 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][2]
  df2 = dFPesqIMOVEIS[selecao2]
  #st.write(df2["R$/m2"].mean())
  VETcustom2.append(df2["R$/m2"].mean())

  selecao3 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][3]
  df3 = dFPesqIMOVEIS[selecao3]
  #st.write(df3["R$/m2"].mean())
  VETcustom2.append(df3["R$/m2"].mean())

  selecao4 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][4]
  df4 = dFPesqIMOVEIS[selecao4]
  #st.write(df4["R$/m2"].mean())
  VETcustom2.append(df4["R$/m2"].mean())

  selecao5 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][5]
  df5 = dFPesqIMOVEIS[selecao5]
  #st.write(df5["R$/m2"].mean())
  VETcustom2.append(df5["R$/m2"].mean())

  selecao6 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][6]
  df6 = dFPesqIMOVEIS[selecao6]
  #st.write(df6["R$/m2"].mean())
  VETcustom2.append(df6["R$/m2"].mean())

  selecao7 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][7]
  df7 = dFPesqIMOVEIS[selecao7]
  #st.write(df7["R$/m2"].mean())
  VETcustom2.append(df7["R$/m2"].mean())

  selecao8 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][8]
  df8 = dFPesqIMOVEIS[selecao8]
  #st.write(df8["R$/m2"].mean())
  VETcustom2.append(df8["R$/m2"].mean())
elif n==10:
  selecao0 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][0]
  df0 = dFPesqIMOVEIS[selecao0]
  #st.write(df0["R$/m2"].mean())
  VETcustom2.append(df0["R$/m2"].mean())

  selecao1 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][1]
  df1 = dFPesqIMOVEIS[selecao1]
  #st.write(df1["R$/m2"].mean())
  VETcustom2.append(df1["R$/m2"].mean())

  selecao2 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][2]
  df2 = dFPesqIMOVEIS[selecao2]
  #st.write(df2["R$/m2"].mean())
  VETcustom2.append(df2["R$/m2"].mean())

  selecao3 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][3]
  df3 = dFPesqIMOVEIS[selecao3]
  #st.write(df3["R$/m2"].mean())
  VETcustom2.append(df3["R$/m2"].mean())

  selecao4 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][4]
  df4 = dFPesqIMOVEIS[selecao4]
  #st.write(df4["R$/m2"].mean())
  VETcustom2.append(df4["R$/m2"].mean())

  selecao5 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][5]
  df5 = dFPesqIMOVEIS[selecao5]
  #st.write(df5["R$/m2"].mean())
  VETcustom2.append(df5["R$/m2"].mean())

  selecao6 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][6]
  df6 = dFPesqIMOVEIS[selecao6]
  #st.write(df6["R$/m2"].mean())
  VETcustom2.append(df6["R$/m2"].mean())

  selecao7 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][7]
  df7 = dFPesqIMOVEIS[selecao7]
  #st.write(df7["R$/m2"].mean())
  VETcustom2.append(df7["R$/m2"].mean())

  selecao8 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][8]
  df8 = dFPesqIMOVEIS[selecao8]
  #st.write(df8["R$/m2"].mean())
  VETcustom2.append(df8["R$/m2"].mean())

  selecao9 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][9]
  df9 = dFPesqIMOVEIS[selecao9]
  #st.write(df9["R$/m2"].mean())
  VETcustom2.append(df9["R$/m2"].mean())
elif n==11:
  selecao0 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][0]
  df0 = dFPesqIMOVEIS[selecao0]
  #st.write(df0["R$/m2"].mean())
  VETcustom2.append(df0["R$/m2"].mean())

  selecao1 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][1]
  df1 = dFPesqIMOVEIS[selecao1]
  #st.write(df1["R$/m2"].mean())
  VETcustom2.append(df1["R$/m2"].mean())

  selecao2 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][2]
  df2 = dFPesqIMOVEIS[selecao2]
  #st.write(df2["R$/m2"].mean())
  VETcustom2.append(df2["R$/m2"].mean())

  selecao3 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][3]
  df3 = dFPesqIMOVEIS[selecao3]
  #st.write(df3["R$/m2"].mean())
  VETcustom2.append(df3["R$/m2"].mean())

  selecao4 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][4]
  df4 = dFPesqIMOVEIS[selecao4]
  #st.write(df4["R$/m2"].mean())
  VETcustom2.append(df4["R$/m2"].mean())

  selecao5 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][5]
  df5 = dFPesqIMOVEIS[selecao5]
  #st.write(df5["R$/m2"].mean())
  VETcustom2.append(df5["R$/m2"].mean())

  selecao6 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][6]
  df6 = dFPesqIMOVEIS[selecao6]
  #st.write(df6["R$/m2"].mean())
  VETcustom2.append(df6["R$/m2"].mean())

  selecao7 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][7]
  df7 = dFPesqIMOVEIS[selecao7]
  #st.write(df7["R$/m2"].mean())
  VETcustom2.append(df7["R$/m2"].mean())

  selecao8 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][8]
  df8 = dFPesqIMOVEIS[selecao8]
  #st.write(df8["R$/m2"].mean())
  VETcustom2.append(df8["R$/m2"].mean())

  selecao9 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][9]
  df9 = dFPesqIMOVEIS[selecao9]
  #st.write(df9["R$/m2"].mean())
  VETcustom2.append(df9["R$/m2"].mean())

  selecao10 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][10]
  df10 = dFPesqIMOVEIS[selecao10]
  #st.write(df10["R$/m2"].mean())
  VETcustom2.append(df10["R$/m2"].mean())
elif n==12:
  selecao0 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][0]
  df0 = dFPesqIMOVEIS[selecao0]
  #st.write(df0["R$/m2"].mean())
  VETcustom2.append(df0["R$/m2"].mean())

  selecao1 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][1]
  df1 = dFPesqIMOVEIS[selecao1]
  #st.write(df1["R$/m2"].mean())
  VETcustom2.append(df1["R$/m2"].mean())

  selecao2 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][2]
  df2 = dFPesqIMOVEIS[selecao2]
  #st.write(df2["R$/m2"].mean())
  VETcustom2.append(df2["R$/m2"].mean())

  selecao3 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][3]
  df3 = dFPesqIMOVEIS[selecao3]
  #st.write(df3["R$/m2"].mean())
  VETcustom2.append(df3["R$/m2"].mean())

  selecao4 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][4]
  df4 = dFPesqIMOVEIS[selecao4]
  #st.write(df4["R$/m2"].mean())
  VETcustom2.append(df4["R$/m2"].mean())

  selecao5 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][5]
  df5 = dFPesqIMOVEIS[selecao5]
  #st.write(df5["R$/m2"].mean())
  VETcustom2.append(df5["R$/m2"].mean())

  selecao6 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][6]
  df6 = dFPesqIMOVEIS[selecao6]
  #st.write(df6["R$/m2"].mean())
  VETcustom2.append(df6["R$/m2"].mean())

  selecao7 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][7]
  df7 = dFPesqIMOVEIS[selecao7]
  #st.write(df7["R$/m2"].mean())
  VETcustom2.append(df7["R$/m2"].mean())

  selecao8 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][8]
  df8 = dFPesqIMOVEIS[selecao8]
  #st.write(df8["R$/m2"].mean())
  VETcustom2.append(df8["R$/m2"].mean())

  selecao9 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][9]
  df9 = dFPesqIMOVEIS[selecao9]
  #st.write(df9["R$/m2"].mean())
  VETcustom2.append(df9["R$/m2"].mean())

  selecao10 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][10]
  df10 = dFPesqIMOVEIS[selecao10]
  #st.write(df10["R$/m2"].mean())
  VETcustom2.append(df10["R$/m2"].mean())
  
  selecao11 = dFPesqIMOVEIS["BAIRRO"] == dfListaBairros["BAIRRO"][11]
  df11 = dFPesqIMOVEIS[selecao11]
  #st.write(df11["R$/m2"].mean())
  VETcustom2.append(df11["R$/m2"].mean())

dfResumoBairros = dfListaBairros.assign(VETcustom2=VETcustom2) # Assign VETcustom2 to a new column named 'VETcustom2'
dfResumoBairros.columns = ['BAIRRO', 'IMOVEIS', 'R$/m2'] # Rename columns

VetBAIRROS = dfResumoBairros['BAIRRO']
VetCustoM2 = dfResumoBairros['R$/m2']
   
dfResumoBairros["all"] = "all"  # Para ter um único nó raiz

# Construção do treemap com Plotly
fig = px.treemap(dfResumoBairros, path=['BAIRRO'], values='R$/m2')
fig.update_traces(root_color="lightgrey")
fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
# Criação do web app com Streamlit
st.divider()
colA, colB = st.columns(2)
with colA:
    st.header("Custo médio em R$/m² em cada Bairro:")
    st.write(dfResumoBairros)
with colB:
    st.title("Distribuição de Custo por Bairro")
    st.plotly_chart(fig) # Renderização do gráfico
