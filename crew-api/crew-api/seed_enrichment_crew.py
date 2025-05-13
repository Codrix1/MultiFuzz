import os, copy, pytz
from datetime import datetime
from crewai import Agent, Task, Crew
from drag_agent import retrieval_agent, retrieval_task
from tools import SeedEnrichmentParsingTool
from llm_utils import qwen_qwq, llama31, llama4, deepseek, llama3
from prompts import seed_enrichment_prompt
from dotenv import load_dotenv
from rich import print

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "logs")

rag_agent = retrieval_agent.copy()
rag_task = copy.copy(retrieval_task)

seed_enrichment_agent = Agent(
    role="{protocol} Protocol State Machine Expert, and Network Packets Enricher",
    goal="\n".join([
                "Use the retrieved context from the seed_enrichment_retreival_agent.",
                "The retrieved context will help you enrich some network packets",
                "and add new packets in proper places, according the protocol state machine/model",
            ]),
    backstory="\n".join([
        "You are an expert AI agent who excels great knowledge in the {protocol} protocol finite state machine.",
        "You also have great capabilities of using the retrieved knowledge, to help you enrich a set of network packets",
        "with new desired ones, according the the {protocol} protocol's finite state machine."
        "You should use the tool provided to parse and provide the final answer."
    ]),
    tools=[SeedEnrichmentParsingTool(result_as_answer=True)],
    llm=llama31,
    verbose=True,
)

seed_enrichment_task = Task(
    description="\n".join([
        "The task is to enrich some network packets and add new packets in proper places, according the protocol state machine/model.",
        "The enriched seeds shouldn't contain server responses in between, it should contain the old seeds provided in the fuzzer's question,"
        " enriched with the new 2 new seeds desired and given in the fuzzer's question.",
        "analyze the retrieved context from the retreival_agent to help complete your task.",
        "You are required to use the 'Seeds Parsing Tool', to parse and provide the full enriched network packet seeds.",
        "The input passed to the tool should be the json object of type EnrichedNetworkPacketSeeds.",
        "Ensure the pydantic object is passed to the tool is wrapped under the key pydantic_output_object, not directly,",
        "it must contain the 'enriched_seeds' key which is a str representing enriched network packets with the 2 new desired ones to be placed,",
        " and also must contain the key 'explanation' which is your explanation for the enriched seeds.",
        " The object passed to tool is expected to be like this: {{'pydantic_output_object': {{'enriched_seeds': '<enriched_seeds>', 'explanation': '<explanation>'}}}}",
        " After obtaining the tool's output which is the enriched seeds, the task is completed.",
        "The fuzzer's question/request: <fuzzer_question>{question}</fuzzer_question>",
    ]),
    expected_output="The 'Seeds Parsing Tool' output, which is the enriched network packets.",
    context=[rag_task],
    output_file=os.path.join(output_dir, f"enriched_seeds_{datetime.now(pytz.timezone('Africa/Cairo')).strftime('%d-%I-%M-%S')}.txt"),
    agent=seed_enrichment_agent,
)

def assemble_seed_enrichment_crew():
    """Assemble the seed enrichment crew."""
    return Crew(
        agents=[rag_agent, seed_enrichment_agent],
        tasks=[rag_task, seed_enrichment_task],
        output_log_file=os.path.join(output_dir, f"seed_enrichment_crew_{datetime.now(pytz.timezone('Africa/Cairo')).strftime('%d-%I-%M-%S')}.txt"),
        verbose=False
    )

if __name__ == "__main__":
    load_dotenv()
    seed_enrichment_crew = assemble_seed_enrichment_crew()
    
    seed_enrichment_results = seed_enrichment_crew.kickoff(
        inputs={
            "protocol": "RTSP",
            "question": seed_enrichment_prompt
        }
    )