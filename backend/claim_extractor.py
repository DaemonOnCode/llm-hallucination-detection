import json
import spacy

from llm import LLMRunner

class ClaimExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
    
    def extract_claims_spacy(self, text):
        doc = self.preprocess_statement(text)
        return self.extract_triplets(doc)

    def extract_entity_claims(self, statement):
        doc = self.nlp(statement)
        entities = [(ent.text, ent.label_) for ent in doc.ents]

        tokens = [(token.text, token.dep_, token.head.text) for token in doc]

        claims = []
    
        def get_span_text(token):
            return ' '.join([t.text for t in token.subtree if t.dep_ not in ['punct', 'cc']]).strip()
        
        for sent in doc.sents:
            root = [token for token in sent if token.dep_ == "ROOT"][0]

            subject = None
            for child in root.children:
                if child.dep_ in ["nsubj", "nsubjpass"]:
                    subject = child
                    break
                    
            if subject:
                main_claim = f"{get_span_text(subject)} {get_span_text(root)}".strip()
                claims.append(main_claim)

            for token in sent:
                if token.dep_ == "conj" and token.pos_ == "VERB":
                    conj_subject = None
                    for child in token.children:
                        if child.dep_ in ["nsubj", "nsubjpass"]:
                            conj_subject = child
                            break
                    
                    if conj_subject is None:
                        conj_subject = subject
                    
                    if conj_subject:
                        conj_claim = f"{get_span_text(conj_subject)} {get_span_text(token)}".strip()
                        claims.append(conj_claim)

            for token in sent:
                if token.dep_ == "advcl":
                    advcl_subject = None
                    for child in token.children:
                        if child.dep_ in ["nsubj", "nsubjpass"]:
                            advcl_subject = child
                            break
                    
                    if advcl_subject:
                        advcl_claim = f"{get_span_text(advcl_subject)} {get_span_text(token)}".strip()
                    else:
                        advcl_claim = f"{get_span_text(subject)} {get_span_text(token)}".strip()
                    claims.append(advcl_claim)
        print(claims)
        return claims

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
        result = LLMRunner("ollama", model_name="mistral:7b-instruct").run("Extract only the different claims that exist from the given input in the given format {claims:[<claim1>,<claim2>,<claim3>]} \n"+text, format="json", max_tokens=-1)
        return json.loads(result)["claims"]
    

