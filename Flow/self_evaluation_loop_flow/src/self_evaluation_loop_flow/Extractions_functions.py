import re
from self_evaluation_loop_flow.main import RuleBook
from self_evaluation_loop_flow.Clean_n_divide import *
def extract_List(text: str) -> list[str]:
    # Find *all* bracketed contents
    matches = re.findall(r"\[([^\]]+)\]", text)
    if not matches:
        return []

    # Take the last match
    content = matches[-1]

    # Split and clean up quotes/whitespace
    return [item.strip().strip('"').strip("'") for item in content.split(',')]


def write_rulebook_to_txt(rulebook: RuleBook, filename: str = "rulebook_output.txt") -> None:

    with open(filename, "a") as file:
        file.write("------------------\n")
        file.write(f"\n{rulebook.chapter1}\n\n")
        file.write(f"\n{rulebook.chapter2}\n\n")
        file.write(f"\n{rulebook.chapter3}\n-----------------------------------------------------------------------------------------------------------\n\n")
    
    print(f"Successfully wrote RuleBook to {filename}")
