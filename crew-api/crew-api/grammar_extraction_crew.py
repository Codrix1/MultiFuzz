import os, copy, pytz
from datetime import datetime
from crewai import Agent, Task, Crew
from drag_agent import retrieval_agent, retrieval_task
from tools import GrammarExtractionFormattingTool
from llm_utils import llama4, qwen_qwq, deepseek, llama31, llama3, gemma2, llama33
from pydantic_models import RTSPGrammarTemplates
from prompts import grammar_prompt
from dotenv import load_dotenv
from rich import print

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "logs")

rag_agent = retrieval_agent.copy()
rag_task = copy.copy(retrieval_task)

grammar_extraction_agent = Agent(
    role="{protocol} Protocol Grammar Extraction Agent",
    goal="\n".join([
                "Use the retrieved context from the retreival_agent.",
                "The retrieved context will help you provide a list of {protocol} grammar templates in structured JSON.",
            ]),
    backstory="This agent is designed to help in network protocols grammar extraction.",
    llm=copy.copy(llama33),
    verbose=True,
)

grammar_extraction_task = Task(
    description="\n".join([
        "For the {protocol} protocol, the task is to provide all the client request templates in a structured JSON.",
        "Use the retrieved context from the retrieval_agent to help completing your task."
        "For each client request template, the key is the request name, and the value is a list of all headers possible for the request.",
        "The rules are:",
        "1- You must use `<<VALUE>>` placeholders where appropriate",
        "2- Each header must end by: \\r\\n",
        "A simple example for the RTSP protocol's DESCRIBE request, the object is expected to be like this:",
        "{{'DESCRIBE': ['DESCRIBE <<VALUE>>\r\n','CSeq: <<VALUE>>\r\n','User-Agent: <<VALUE>>\r\n','Accept: <<VALUE>>\r\n']}}",
    ]),
    expected_output="A JSON object containing containing the request type as the key, and the value is a list of all the headers, according to the schema specified.",
    context=[rag_task],
    output_json=RTSPGrammarTemplates,
    output_file=os.path.join(output_dir, f"rtsp_grammar_templates_{datetime.now(pytz.timezone('Africa/Cairo')).strftime('%d-%I-%M-%S')}.json"),
    agent=grammar_extraction_agent
)


grammar_formating_agent = Agent(
    role="{protocol} Protocol Grammar Formatting Agent",
    goal="\n".join([
                "To use the specified tool to format a json object containing templates of the {protocol} protocol, to a nicely formatted string.",
            ]),
    backstory="This agent is designed to help in network protocols grammar templates formatting in a string by using the tool provided.",
    tools=[GrammarExtractionFormattingTool(result_as_answer=True)],
    llm=llama31,
    verbose=True,
)

grammar_formating_task = Task(
    description="\n".join([
        "The task is to use the 'Grammar Extraction Formatting Tool', to provide a nicely formatted string with the protocol templates."
        "The input passed to the tool should be the json obtained from the previous agent, it should not contain any additional metadata.",
        "Ensure the JSON object is passed to the 'Grammar Extraction Formatting Tool' wrapped under the key pydantic_output_object, not directly."
        "After obtaining the 'Grammar Extraction Formatting Tool' output, the task is completed, just return the tool's output."
    ]),
    expected_output="The 'Grammar Extraction Formatting Tool' output.",
    context=[grammar_extraction_task],
    output_file=os.path.join(output_dir, f"rtsp_grammar_templates_{datetime.now(pytz.timezone('Africa/Cairo')).strftime('%d-%I-%M-%S')}.txt"),
    agent=grammar_formating_agent,
)


def assemble_grammar_extraction_crew():
    """Assemble the grammar extraction crew."""
    return Crew(
        agents=[rag_agent, grammar_extraction_agent, grammar_formating_agent],
        tasks=[rag_task, grammar_extraction_task, grammar_formating_task],
        output_log_file=os.path.join(output_dir, f"grammar_extraction_crew_{datetime.now(pytz.timezone('Africa/Cairo')).strftime('%d-%I-%M-%S')}.txt"),
        verbose=False
    )


if __name__ == "__main__":
    load_dotenv()
    grammar_extraction_crew = assemble_grammar_extraction_crew()
    
    grammar_extraction_crew_results = grammar_extraction_crew.kickoff(
        inputs={
            "protocol": "RTSP",
            "question": grammar_prompt
        }
    )
    
    print("GRAMMAR EXTRACTION RESULTS: \n\n", grammar_extraction_crew_results.raw)