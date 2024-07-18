import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

def get_content(url):    
    try:
        resp = requests.get(url, headers=headers)
        print(f"URL: {url} | Status Code: {resp.status_code}")
        return resp
    except requests.RequestException as e:
        print(f"Erro ao tentar acessar {url}: {e}")
        return None

def get_basic_infos(soup):
    div_page = soup.find("div", class_="td-page-content")
    if div_page:
        try:
            paragrafo = div_page.find_all("p")[1]
            print("Parágrafo encontrado: ", paragrafo.text)
            ems = paragrafo.find_all("em")
            data = {}
            for i in ems:
                if ":" in i.text:
                    chave, valor = i.text.split(":", 1)
                    chave = chave.strip(" ")
                    data[chave] = valor.strip(" ")
            return data
        except IndexError as e:
            print(f"Erro ao tentar acessar parágrafo: {e}")
            return {}
    else:
        print("Div 'td-page-content' não encontrada.")
        return {}

def get_aparicoes(soup):
    div_page = soup.find("div", class_="td-page-content")
    if div_page:
        h4_tag = div_page.find("h4")
        if h4_tag:
            ul_tag = h4_tag.find_next("ul")
            if ul_tag:
                lis = ul_tag.find_all("li")
                aparicoes = [i.text for i in lis]
                return aparicoes
            else:
                print("Tag 'ul' não encontrada após 'h4'.")
                return []
        else:
            print("Tag 'h4' não encontrada.")
            return []
    else:
        print("Div 'td-page-content' não encontrada.")
        return []

def get_personagem_infos(url):
    resp = get_content(url)
    if resp is None or resp.status_code != 200:
        print("Não foi possível obter os dados")
        return {}
    else:
        soup = BeautifulSoup(resp.text, 'html.parser')
        data = get_basic_infos(soup)
        data["Aparicoes"] = get_aparicoes(soup)
        return data

def get_links():
    url = "https://www.residentevildatabase.com/personagens/"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        soup_personagens = BeautifulSoup(resp.text, 'html.parser')
        ancoras = (soup_personagens.find("div", class_="td-page-content")
                                   .find_all("a", href=True))
        links = [i["href"] for i in ancoras if i["href"].startswith("http")]
        return links
    else:
        print(f"Falha ao obter links. Status code: {resp.status_code}")
        return []

# %%
links = get_links()
data = []
for i in tqdm(links):
    d = get_personagem_infos(i)
    if d:
        d["Link"] = i
        nome = i.strip("/").split("/")[-1].replace("-", " ").title()
        d["Nome"] = nome
        data.append(d)


df = pd.DataFrame(data)
df
