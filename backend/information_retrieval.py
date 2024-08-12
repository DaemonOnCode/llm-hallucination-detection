import requests

from utils import FileReader

class InformationRetrieval:
    def __init__(self):
        self.elasticsearch_url = "http://localhost:9200"
        self.wikidata_url = "https://www.wikidata.org/w/api.php"
        self.dbpedia_url = "https://dbpedia.org/sparql"

    def retrieve_from_elasticsearch(self, index, query):
        url = f"{self.elasticsearch_url}/{index}/_search"
        response = requests.get(url, params={"q": query})
        if response.status_code == 200:
            return response.json()
        else:
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
            return response.json()
        else:
            return None

    def retrieve_from_dbpedia(self, query):
        sparql_query = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?subject ?label WHERE {{
                ?subject rdfs:label ?label .
                FILTER (lang(?label) = 'en' && contains(?label, "{query}"))
            }}
            LIMIT 10
        """
        params = {
            "query": sparql_query,
            "format": "json"
        }
        response = requests.get(self.dbpedia_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None
        

    def add_to_elasticsearch(self, index, data):
        url = f"{self.elasticsearch_url}/{index}/_doc"
        response = requests.post(url, json=data)
        if response.status_code == 201:
            return response.json()
        else:
            return None
        
    def add_file_to_elasticsearch(self, index, file_path):
        fileReader = FileReader(file_path)
        data = fileReader.read()
        url = f"{self.elasticsearch_url}/{index}/_doc"
        response = requests.post(url, json=data)
        if response.status_code == 201:
            return response.json()
        else:
            return None
        
    def retrieve(self, source, query):
        if source == "elasticsearch":
            return self.retrieve_from_elasticsearch("index", query)
        elif source == "wikidata":
            return self.retrieve_from_wikidata(query)
        elif source == "dbpedia":
            return self.retrieve_from_dbpedia(query)
        else:
            return None