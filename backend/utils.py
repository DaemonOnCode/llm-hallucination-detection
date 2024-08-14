from collections import Counter
import pypdf
import docx
import spacy

class FileReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        if self.file_path.endswith(".pdf"):
            return self.read_pdf()
        elif self.file_path.endswith(".docx"):
            return self.read_docs()
        else:
            return self.read_text()

    def read_text(self):
        with open(self.file_path, 'r') as file:
            return file.read()
        
    def read_pdf(file_path):
        reader = pypdf.PdfReader(file_path)
        text = ""
        for page in len(reader.pages):
            text += reader.pages[page].extract_text()
            text += "\n"
        return text
    
    def read_docs(file_path):
        doc = docx.Document(file_path)
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        return '\n'.join(fullText)

def max_occuring_value(s):
    counts = Counter(s)

    max_val = max(counts, key=counts.get)
    
    return max_val

def noun_extractor(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    nouns = []
    for token in doc:
        if token.pos_ == "NOUN":
            nouns.append(token.text)
    entities = [ent.text for ent in doc.ents]
    nsubj = [token.text for token in doc if token.dep_ == "nsubj"]
    return list(set(nouns+entities+nsubj))