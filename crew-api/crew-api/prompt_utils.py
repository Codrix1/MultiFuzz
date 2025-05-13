from enum import Enum

class Techinque(Enum):
    grammar_extraction = 1
    seed_enrichment = 2
    coverage_plateau = 3
    general = 4 

def determine_prompt_type(prompt: str):
    """
      Determines the type of the prompt by identifying specific keywords or structures in the prompt.
    """
    
    if "client request/method templates" in prompt:
        return Techinque.grammar_extraction.value
    elif "sequence of client requests" in prompt and "add them" in prompt:
        return Techinque.seed_enrichment.value
    elif "communication history" in prompt and "next proper client request" in prompt:
        return Techinque.coverage_plateau.value
    
    return Techinque.general.value