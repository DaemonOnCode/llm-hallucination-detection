import json
from openai import OpenAI
from transformers import AutoModelForCausalLM, AutoTokenizer
import requests

class LLMRunner:
    def __init__(self, model_type, api_key = "", model_name = "", max_tokens = 100):
        print("LLMRunner initialized", model_type, model_name)
        self.model_type = model_type
        self.model_name = model_name
        self.api_key = api_key
        self.max_tokens = max_tokens

    def run_ollama(self, prompt):
        print("Running OLLAMA", self.model_name, prompt)
        res = requests.post("http://localhost:11434/api/generate", 
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": self.max_tokens
            }
        }))        
        return res.json()["response"]

    def run_openai(self, prompt):
        openai = OpenAI(self.api_key)
        messages = [{"role": "user", "content": prompt}]
        response = openai.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=False
        )
        return response.choices[0].text.strip()
    
    def run_huggingface(self, prompt):
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForCausalLM.from_pretrained(self.model_name)

        inputs = tokenizer.encode(prompt, return_tensors="pt")
        outputs = model.generate(inputs, max_length=200)

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
    
    def run(self, prompt):
        print("Running LLM", self.model_type, self.model_name)
        if self.model_type == "ollama":
            return self.run_ollama(prompt)
        elif self.model_type == "openai":
            return self.run_openai(prompt)
        elif self.model_type == "hf":
            return self.run_huggingface(prompt)
        else:
            raise ValueError("Unsupported model type.")