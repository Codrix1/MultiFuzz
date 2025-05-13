import os, copy, pytz
from datetime import datetime
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai import Agent, Task, Crew
from drag_agent import retrieval_agent, retrieval_task
from tools import PacketParsingTool
from llm_utils import deepseek, llama31, llama3, knowledge_source
from pydantic_models import CoveragePlateauSurpassingNetworkPacket
from prompts import coverage_plateau_prompt
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "logs")

rag_agent = retrieval_agent.copy()
rag_task = copy.copy(retrieval_task)

cov_plateau_agent = Agent(
    role="RTSP protocol professional Context Analysis Agent, and Proffesional Fuzz Testing Coverage Plateau Surpasser",
    goal="Analyze the fuzzer's question and the context provided, to generate a network packet that would surpass the fuzzer's coverage plateau. Strictly use the tool provided to parse and provide the final answer of the agent.",
    backstory="\n".join([
        "You are an expert AI analysis agent, who have context awareness of the {protocol} protocol's state machine/model,",
        "and it's different states. You also have great capabilities of generating a network packet,",
        "that would surpass the coverage plateau of the protocol fuzzer, triggering new state transitions,",
        "leading to better code coverage across the protocol implementation.",
        "You need to analyze the fuzzers question, and review the context provided",
        "from the retrieval_agent, to generate the network packet that would surpass the fuzzer's coverage plateau.",
        "Strictly use the 'Packet Parsing Tool' to parse and provide your final answer.",
    ]),
    llm=llama3,
    tools=[PacketParsingTool(result_as_answer=True)],
    verbose=True,
)

cov_plateau_task = Task(
    description="\n".join([
        "The task is analyze the context provided from the retrieval_agent, and also analyze the fuzzer's request/question,"
        "to generate a network packet that would surpass the fuzzer's coverage plateau and trigger new state transitions or vulnerbilities in the server under test.",
        "Don't include any direction before the packet, like C->S: or S->C:",
        "It is required strictly to use the 'Packet Parsing Tool', to parse and provide the final result network packet only.",
        "The input passed to the 'Packet Parsing Tool' should be the json object of type: CoveragePlateauSurpassingNetworkPacket which is a pydantic model",
        f"structured in that way: {CoveragePlateauSurpassingNetworkPacket.model_json_schema()}.",
        "Ensure the pydantic object is passed to the tool is wrapped under the key pydantic_output_object, not directly,",
        "it must contain the 'packet' key which is a str representing the value of the network packet surpassing the coverage plateau,",
        "and also must contain the key 'explanation' which is your explanation why did you provide this packet typically.",
        "The object passed to tool is expected to be like this: {{'pydantic_output_object': {{'packet': '<packet>', 'explanation': '<explanation>'}}}}",
        "After obtaining the tool's output which is the packet only, the task is completed, return only the network packet string, don't include your thinking process in the final answer and dont suround the packet arround backticks.",
        "The fuzzer's question/request: \n\n <fuzzer_question>{question}</fuzzer_question>",
    ]),
    expected_output="The 'Packet Parsing Tool' output, which is the network packet that would surpass the coverage plateau.",
    context=[rag_task],
    output_file=os.path.join(output_dir, f"cov_plateau_packet_{datetime.now(pytz.timezone('Africa/Cairo')).strftime('%d-%I-%M-%S')}.txt"),
    agent=cov_plateau_agent,
)


def assemble_coverage_plateau_crew():
    """Assemble the coverage plateau crew."""
    
    knowledge = StringKnowledgeSource(content=knowledge_source)

    coverage_plateau_crew = Crew(
        agents=[rag_agent, cov_plateau_agent],
        tasks=[rag_task, cov_plateau_task],
        knowledge_sources=[knowledge],
        output_log_file=os.path.join(output_dir, f"coverage_plateau_crew_{datetime.now(pytz.timezone('Africa/Cairo')).strftime('%d-%I-%M-%S')}.txt"),
        verbose=False
    )
    
    return coverage_plateau_crew


if __name__ == "__main__":
    load_dotenv()
    coverage_plateau_crew = assemble_coverage_plateau_crew()

    coverage_plateau_results = coverage_plateau_crew.kickoff(
        inputs = {
            "protocol": "RTSP",
            "question": coverage_plateau_prompt
        }
    )