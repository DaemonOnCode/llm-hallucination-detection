import spacy

from llm import LLMRunner

class ClaimExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
    
    def extract_claims_spacy(self, text):
        doc = self.preprocess_statement(text)
        return self.extract_triplets(doc)

    def extract_entities(self, statement):
        doc = self.nlp(statement)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return entities

    def preprocess_statement(self, statement):
        doc = self.nlp(statement)
        # return " ".join([token.lemma_ for token in doc if not token.is_stop])
        return doc
    
    def extract_complex_claims(self, text):
        doc = self.nlp(text)
        claims = []
        
        for sent in doc.sents:
            root = [token for token in sent if token.dep_ == 'ROOT']
            if root:
                claims.append(sent.text)
                for token in root[0].conjuncts:
                    claims.append(f"{root[0].text} {token.text}")
        
        return claims
    
    def extract_triplets(self, text):
        doc = self.nlp(text)
        triplets = set()

        for sent in doc.sents:
            subject = None
            predicate = None
            objects = []
            for token in sent:
                if token.dep_ in ("nsubj", "nsubjpass"):
                    subject = token.text
                elif token.dep_ == "ROOT":
                    predicate = token.lemma_  

                elif token.dep_ == "dobj":
                    objects.append(token.text)

                elif token.dep_ == "prep":
                    phrase = token.text
                    for child in token.children:
                        if child.dep_ == "pobj":
                            phrase += " " + child.text
                    objects.append(phrase)

            noun_phrases = list(doc.noun_chunks)
            for chunk in noun_phrases:
                if subject and predicate and chunk.text not in objects:
                    objects.append(chunk.text)

            if subject and predicate:
                for obj in objects:
                    triplet = (subject, predicate, obj)
                    triplets.add(triplet) 

        return [list(triplet) for triplet in triplets]
    
    def extract_claims_llm(self, text):
        return LLMRunner("ollama", model_name="mistral:7b-instruct").run("Extract the different claims that exist from the given input: \n"+text)
    

