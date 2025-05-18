import os, pytz
from datetime import datetime
from crewai import Agent, Task, Crew
from tools import CustomRagTool
from prompts import coverage_plateau_prompt
from llm_utils import llama4
from dotenv import load_dotenv
from rich import print

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "logs")

retrieval_agent = Agent(
    role="Retrieval Agent",
    goal="Query the vectorstore using the RAG Tool to obtain context to be passed to the next agent.",
    backstory=(
    "You are an expert RAG assistant."
    " You are asked to query the vector store using the 'RAG Tool' to obtain context to be passed to the next agent."
    " The RAG Tool accepts a search_query parameter, which of type str."
    " The search_query you will generate should be detailed, and help retrieve all relevant information."
    ),
    max_iter=1,
    max_rpm=2,
    max_retry_limit=2,
    verbose=True,
    llm=llama4,
)

retrieval_task = Task(
    description="""Use the RAG Tool to retrieve related context from the vector store.
                   This context will be passed to the next agent to help answer the question: \n\n {question}""",
    expected_output=(
        "The 'RAG Tool' tool output, which is the retrieved context from the vector store."
        ),
    tools=[CustomRagTool(result_as_answer=True)],
    output_file=os.path.join(output_dir, f"retrieved_context_{datetime.now(pytz.timezone('Africa/Cairo')).strftime('%d-%I-%M-%S')}.txt"),
    agent=retrieval_agent,
)

if __name__ == "__main__":
    
    load_dotenv()
    
    crew = Crew(
        agents=[retrieval_agent],
        tasks=[retrieval_task],
        verbose=False
    )
    
    results = crew.kickoff(inputs={"question": coverage_plateau_prompt})
    print("RETRIEVAL RESULTS: \n", results)