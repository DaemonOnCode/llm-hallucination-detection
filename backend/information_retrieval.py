import re
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse

from utils import FileReader

class InformationRetrieval:
    def __init__(self, llm_output= ""):
        self.elasticsearch_url = "http://localhost:9200"
        self.wikidata_url = "https://www.wikidata.org/w/api.php"
        self.wikimedia_url = "https://en.wikipedia.org/w/api.php"
        self.dbpedia_url = "https://dbpedia.org/sparql"
        self.llm_output = llm_output

    def retrieve_from_elasticsearch(self, index, query, custom_query=None):
        url = f"{self.elasticsearch_url}/{index}/_search"
        if custom_query:
            query = custom_query
        try:
            response = requests.get(url, params={"q": query})
            if response.status_code == 200:
                print(response.json())
                return [hit["_source"] for hit in response.json()['hits']['hits']]
            else:
                return None
        except Exception as e:
            return None

    def retrieve_from_wikidata(self, query):
        params = {
            "action": "wbsearchentities",
            "format": "json",
            "language": "en",
            "search": query
        }
        response = requests.get(self.wikidata_url, params=params)
        if response.status_code == 200:
            return response.json()["search"]
        else:
            return None
        
    def annotate_text(self, text):
        url = "http://api.dbpedia-spotlight.org/en/annotate"
        params = {
            'text': text,
            'confidence': 0.35,
            'support': 20
        }
        
        response = requests.post(url, data=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def extract_entities(self, annotated_data):
        entities = []
        if annotated_data and 'Resources' in annotated_data:
            for resource in annotated_data['Resources']:
                entities.append(resource['@id'])
        return entities

    def generate_sparql_query(self, entities):
        if not entities:
            print("No entities found for a meaningful query.")
            return ""
        select_clause = "SELECT ?property ?value WHERE {"
        for entity in entities:
            select_clause += f" <{entity}> ?property ?value ."
        select_clause += "}"
        
        return select_clause

    def retrieve_from_dbpedia(self, query):
        annotated_data = self.annotate_text(query)
        entities = self.extract_entities(annotated_data)
        sparql_query = self.generate_sparql_query(entities)
        params = {
            "query": sparql_query,
            "format": "json"
        }
        response = requests.get(self.dbpedia_url, params=params)
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()
        else:
            return None
        

    def add_to_elasticsearch(self, index, data):
        url = f"{self.elasticsearch_url}/{index}/_doc"
        try:
            response = requests.post(url, json=data)
            if response.status_code == 201:
                return response.json()
            else:
                return None
        except Exception as e:
            return None
        
    def add_file_to_elasticsearch(self, index, file_path):
        fileReader = FileReader(file_path)
        data = fileReader.read()
        url = f"{self.elasticsearch_url}/{index}/_doc"
        try:
            response = requests.post(url, json=data)
            if response.status_code == 201:
                return response.json()
            else:
                return None
        except Exception as e:
            return None
        
    def remove_html_tags(self, text):
        clean = re.sub(r'<.*?>', '', text) 
        return clean
        
    def search_wikimedia(self, query):
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "limit": 1
        }
        response = requests.get(self.wikimedia_url, params=params)
        if response.status_code >= 200 and response.status_code < 300:
            res = response.json()["query"]["search"]
            return [self.remove_html_tags(r["snippet"]) for r in res]
        else:
            return None
        
    def scrape_website(self, url):
        response = requests.get(url)

        if response.status_code >= 200 and response.status_code < 300:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        else:
            print(f"Error: {response.status_code}, {url}")
            return None
        
    def search_google(self, query):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        webdriver_service = Service()

        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

        driver.get(f"https://www.google.com/search?q={urllib.parse.quote(query)}")

        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#search")))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        
        results = []
        websites = []
        for g in soup.find_all('a', jsname ='UWckNb', href=True):
            websites.append(g["href"])
        for g in soup.find_all('span', class_='hgKElc'):
            results.append(g.text)
        for g in soup.find_all('div', class_='VwiC3b yXK7lf lVm3ye r025kc hJNv6b Hdw6tb'):
            results.append(g.text)
        errors = []
        for website in websites[:3]:
            soup = self.scrape_website(website)
            if soup is None:
                errors.append(website)
                continue
            soup_text = soup.get_text(strip=True)
            doc_exists = self.retrieve_from_elasticsearch("index", {"text":soup_text})
            if doc_exists:
                print("Already exists in elasticsearch")
            else:
                res = self.add_to_elasticsearch("index", {"text":soup_text})
            data = self.retrieve_from_elasticsearch("index", query, custom_query={
                "query": {
                    "match": {
                        "text": {
                            "query": query,
                            "fuzziness": "AUTO" 
                        }
                    }
                },
            })
            if data is not None and len(data)>0:
                results.extend([d["text"] for d in data])
        return results[:5]

    def retrieve(self, source, query):
        print("Retrieving", source, query)
        if source == "elasticsearch":
            res =  self.retrieve_from_elasticsearch("index", query)
            return res
        elif source == "wikidata":
            res = self.retrieve_from_wikidata(query)
            return res
        elif source == "dbpedia":
            res = self.retrieve_from_dbpedia(query)
            return res
        elif source == "wikimedia":
            res = self.search_wikimedia(query)
            return res
        elif source == "google":
            res = self.search_google(query)
            return res
        else:
            return None
        
    def retrieve_multiple(self, source, queries, input_text):
        results = []
        result = self.retrieve(source, input_text)
        results.append(result)
        return results