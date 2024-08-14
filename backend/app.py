from flask import Flask, request, jsonify
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
cors = CORS(app)

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
    try:
        print("Request received")
        data = request.form.to_dict(flat=True)

        files = request.files

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
        information_retrieval = InformationRetrieval(llm_output=llm_output)

        if data.get("ground_truth"):
            results = [data["ground_truth"]]
            claims = claim_extractor.extract_claims_spacy(llm_output)
        else:
            claims = claim_extractor.extract_claims_spacy(llm_output)
            if request.files:
                print("Files received", request.files)
                for file in files.values():
                    print(file)
                    information_retrieval.add_file_to_elasticsearch("index", file)

            with Pool() as p:
                results = p.starmap(information_retrieval.retrieve_multiple, [(method, claims, input_text) for method in ["wikidata", "dbpedia", "google"]])

            results = [
                item
                for sublist1 in results if sublist1 is not None and sublist1 != []
                for sublist2 in sublist1 if sublist2 is not None and sublist2 != []
                for item in sublist2 if item is not None
            ]
            results = list(filter(lambda x: x is not None and x != [], results))
            
        print(results, claims)

        # Fact verification
        if len(claims) == 0:
            return jsonify({
                "explanation": "No claims extracted from the LLM output.",
                "ground_truth_similarity": 0,
                "contradiction": "False",
                "token_comparison": [],
                "token_correct_percentage": 0,
            }), 200

        if len(results) == 0:
            return jsonify({
                "explanation": "No information retrieved from external sources.",
                "ground_truth_similarity": 0,
                "contradiction": "False",
                "token_comparison": [],
                "token_correct_percentage": 0,
            }), 200

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
                
        # Explanation generation
        explanation_generation = ExplanationGenerator()
        explanation = explanation_generation.generate_explanation(llm_output, results, verification_result)

        return jsonify({
                "explanation": explanation,
                "ground_truth_similarity": ground_truth_similarity,
                "contradiction": str(max_occuring_value(list(map(lambda x: x["contradiction"], verification_result))) == "contradiction"),
                "token_comparison": sum_counts,
                "token_correct_percentage": correct_count/(correct_count+incorrect_count),
            }), 200
    except Exception as e:
        print(e, e.__traceback__.tb_lasti, e.__traceback__.tb_lineno, e.__traceback__.tb_frame)
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)