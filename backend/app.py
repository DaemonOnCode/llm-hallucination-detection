from typing import Any, Dict
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from multiprocessing import Pool

from claim_extractor import ClaimExtractor
from explanation_generator import ExplanationGenerator
from information_retrieval import InformationRetrieval
from llm import LLMRunner
from verification import FactChecker
from utils import max_occuring_value

import sys
print(sys.executable)

app = Flask(__name__)
# cors = CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/', methods=['GET'])
def hello():
    return 'Hello, World!'

# Example API data format
# {
#     "input": "",
#     "output": "",
#     "ground_truth": "",
#     "model": "",
#     "api_key": "",
# }, files

@app.route('/api/process', methods=['POST'])
def process_text():
    print("Request received")
    data = request.form.to_dict(flat=True)

    print(data)

    files = request.files

    print(files, files.values())

    input_text = data['prompt']

    llm_output = data.get('answer')

    if llm_output is None or llm_output == "":
        model_type = data["model"].lower().strip().split("_")[0]
        model_name = data["model"].replace(f"{model_type}_", "")
        if model_type.startswith("ollama"):
            llm_output = LLMRunner(model_type=model_type, model_name=model_name).run(input_text)
        elif model_type.startswith("hf"):
            llm_output = LLMRunner(model_type=model_type, model_name=model_name).run(input_text)
        elif model_type.startswith("openai"):
            llm_output = LLMRunner(model_type=model_type, model_name="gpt-4o", api_key=data["api_key"]).run(input_text)
        else:
            llm_output = ""

    # Extract claims from the LLM output
    claim_extractor = ClaimExtractor()
    claims = claim_extractor.extract_claims_spacy(llm_output)

    print(claims)
    
    # Retrieve information from external sources
    information_retrieval = InformationRetrieval()
    if data.get("ground_truth")=="":
        information_retrieval.add_to_elasticsearch("index", {"claim": input_text, "result": data["answer"]})

    if data.get("ground_truth"):
        results = [data["ground_truth"]]
    else:
        if request.files:
            for file in files.values():
                information_retrieval.add_file_to_elasticsearch("index", file)

        with Pool(3) as p:
            results = p.starmap(information_retrieval.retrieve, [(method, claims) for method in ["elasticsearch", "wikidata", "dbpedia"]])
        
    print(results, claims)

    # Fact verification
    fact_verification = FactChecker()
    verification_result = fact_verification.verify_facts(claims, results)

    ground_truth_similarity = fact_verification.textual_similarity_check(llm_output, results[0])


    set2 = set(results[0].lower().split(" "))
    sum_counts = []
    incorrect_count = 0
    correct_count = 0

    for word in llm_output.split(" "):
        if word.lower() in set2:
            sum_counts.append({
                "token": word,
                "status": True
            })
            correct_count += 1
        else:
            sum_counts.append({
                "token": word,
                "status": False
            })
            incorrect_count += 1

    print(sum_counts, incorrect_count, correct_count, correct_count/(correct_count+incorrect_count))
    

    # Explanation generation
    explanation_generation = ExplanationGenerator()
    explanation = explanation_generation.generate_explanation(llm_output, results, verification_result)

    print(explanation)



    return jsonify({
            "explanation": explanation,
            "ground_truth_similarity": ground_truth_similarity,
            "contradiction": str(max_occuring_value(list(map(lambda x: x["contradiction"], verification_result))) == "contradiction"),
            "token_comparison": sum_counts,
            "token_correct_percentage": correct_count/(correct_count+incorrect_count),
        }), 200

if __name__ == '__main__':
    app.run(debug=True)