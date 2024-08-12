from sentence_transformers import SentenceTransformer
import spacy
import torch
from transformers import AutoTokenizer, XLMRobertaForSequenceClassification

class FactChecker:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def verify_facts(self, claims, documents):
        print("Checking contradictions", claims, documents)

        results = []

        for claim in claims:
            for document in documents:
                claim = " ".join(claim)
                print(self.textual_similarity_check(claim, document))
                print(self.contradiction_check(claim, document))
                results.append({
                    "claim": claim,
                    "document": document,
                    "textual_similarity": self.textual_similarity_check(claim, document),
                    "contradiction": self.contradiction_check(claim, document)
                })

        return results

        
    
    def textual_similarity_check(self, claim, document):
        model = SentenceTransformer("all-mpnet-base-v2")
        # model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings_claim = model.encode(claim)
        embeddings_doc = model.encode(document)
        similarities = model.similarity(embeddings_claim, embeddings_doc)
        # if similarities.item() > 0.7:
        #     return "Similar"
        # return "Not similar"
        return str(similarities.item())
    
    @staticmethod
    def preprocess(data, tokenizer):
        kwargs = { 
            'truncation': True,
            'max_length': 256,
            'padding': 'max_length',
            'return_attention_mask': True, 
            'return_token_type_ids': True     
        }
        data = list(zip(data['premise'], data['hypothesis']))
        tokenized = tokenizer.batch_encode_plus(data,**kwargs)
        input_ids = torch.LongTensor(tokenized.input_ids)
        attention_masks = torch.LongTensor(tokenized.attention_mask)
        token_type_ids = torch.LongTensor(tokenized.token_type_ids)
        return input_ids, attention_masks, token_type_ids

    def contradiction_check(self, premise, hypothesis):

        device = "cpu"

        model_name = "./fine_tuned_model"

        model = XLMRobertaForSequenceClassification.from_pretrained(model_name, num_labels=3)
        model.to(device)

        tokenizer = AutoTokenizer.from_pretrained(model_name)

        print("Premise and hypothesis", premise, hypothesis)

        input_ids_, token_type_ids_, attention_masks_ = self.preprocess(
            {
                "premise":[premise],
                "hypothesis":[hypothesis]
            }
        ,tokenizer)

        # print(input_ids_.shape, token_type_ids_.shape, attention_masks_.shape)

        model.eval()
        with torch.no_grad():
            outputs = model(input_ids_.to(device), attention_mask=attention_masks_.to(device))
            logits = outputs.logits

        # Get predictions
        print(logits)
        predictions = torch.argmax(logits, dim=-1)
        predicted_labels = predictions.cpu().numpy().tolist()

        labels = {
            0: "entailment",
            1: "neutral",
            2: "contradiction"
        }

        return labels[predicted_labels[0]]