from llm import LLMRunner


class ExplanationGenerator:
    def generate_explanation(self, llm_output, ground_truth, verification_result):

        llmrunner = LLMRunner("ollama", model_name="mistral:7b-instruct", max_tokens = -1)
        ground_truth = "\n".join(ground_truth)
        explanation = f"""Based on the information provided for the statement: {llm_output} and ground truth information: {ground_truth}, \n"""
        for res in verification_result:
            claim = res["claim"]
            contradiction = res["contradiction"]
            similiarity = res["textual_similarity"]
            explanation += """given the context of the claim: """ + claim + """, logic check result: """ + contradiction + """ and text similarity result: """ + similiarity + """\n"""
        explanation += """, generate possible explanations for the results only in the context of an Large Language model generating the response."""

        return llmrunner.run(explanation)