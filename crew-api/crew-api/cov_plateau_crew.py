import os, copy, pytz
from datetime import datetime
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai import Agent, Task, Crew
from drag_agent import retrieval_agent, retrieval_task
from tools import PacketParsingTool
from llm_utils import deepseek, llama31, llama33, knowledge_source
from pydantic_models import PacketGenerationPrompt
from tools import CVEsRetrievalTool
from prompts import coverage_plateau_prompt
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "logs")

rag_agent = retrieval_agent.copy()
rag_task = copy.copy(retrieval_task)

analysis_agent = Agent(
    role="RTSP protocol professional Context Analysis Agent",
    goal="Analyze the fuzzer's question, and the provided context to generate a detailed prompt.",
    backstory="\n".join([
        "You are an expert AI analyst agent, who have context awareness of the protocol's state machine/model,",
        "and it's different states. You need to analyze the fuzzers question, and review the context provided",
        "from the retrieval agent, to generate a detailed prompt, asking an AI agent to surpass a coverage plateau,",
        "by incorporating details about the packet that should be generated, including the state that should",
        "be explored, the method that should be sent and the headers necessary.",
    ]),
    llm=deepseek,
    verbose=True,
)

analysis_task = Task(
    description="\n".join([
        "The task is analyze the context provided from the retrieval agent, and also analyze the fuzzer's request,"
        "to generate a detailed prompt, asking an AI agent to surpass a coverage plateau,",
        "by incorporating details about the packet that should be generated, including the state that should",
        "be explored, the method that should be sent and the headers necessary.",
        "Make sure to to incorporate details about the packet to be generated, not generate a direct packet",
        "the fuzzer's question: \n\n <fuzzer_question>{question}</fuzzer_question>"
    ]),
    expected_output="A JSON object, containing a detailed prompt with the instructions for the next agent to generate a packet that surpasses a coverage plateau.",
    context=[rag_task],
    output_json=PacketGenerationPrompt,
    output_file=os.path.join(output_dir, f"analysis_agent_prompt_{datetime.now(pytz.timezone('Africa/Cairo')).strftime('%d-%I-%M-%S')}.json"),
    agent=analysis_agent,
)

vulnerbilities_agent = Agent(
    role="RTSP Protocol Vulnerbilities Aware Agent",
    goal="\n".join([
        "Use the provided tool, to fetch the CVE list for the {protocol} protocol's server: {server}.",
        "The goal is to re-review the analysis agent's generated prompt, and refine it only needed,",
        "otherwise pass it to the next agent as it is.",
    ]),
    backstory="\n".join([
        "You are an expert AI agent who have knowledge in the {protocol} protocol CVEs (Common Vulnerbilites and Exposure).",
        "and also have knowledge about the protocol's server vulneribilities, which is the server: {server}",
        "You should use the provided tool, providing it the url: {url} as a parameter,",
        "to retrieve the CVEs list in structure JSON. You need analyze and re-review the prompt generated from the previous agent,",
        "which requests an agent to generate a packet that surpasses a coverage plateau.",
        "if there is any chance to reproduce an existing vulnerbility, refine the prompt, otherwise if there is no chance,",
        "leave the agent's prompt as it is, and pass it to the next agent."
    ]),
    tools=[CVEsRetrievalTool()],
    llm=llama31,
    max_iter=2,
    max_rpm=2,
    max_retry_limit=2,
    verbose=True,
)

vulnerbilities_task = Task(
    description="\n".join([
        "The task is to firstly, use the 'CVEs Retrieval Tool' tool, to fetch a structured JSON object,",
        "containing necessary information about the CVEs. The tool returns a structured JSON object",
        "containing the CVEs ID, severity, and description. Use the url: {url} to pass it the tool an retrive",
        "the CVEs JSON. Secondly, analyze and re-review the prompt generated from the previous agent,",
        "which requests an agent to generate a packet that surpasses a coverage plateau.",
        "if there is any chance to reproduce an existing vulnerbility, refine the prompt,",
        "otherwise if there is no chance, leave the agent's prompt as it is, and pass it to the next agent.",
        "Make sure your final output is only the prompt according to the schema specified which is PacketGenerationPrompt, and don't include your thought process or even backtics around the final output"
    ]),
    expected_output="\n".join([
        "A JSON object, containing a detailed prompt with the instructions for the next agent to generate a packet that surpasses a coverage plateau.",
        "This prompt is either passed as it is from the previous agent (if not reproduction of any CVE applicable), or refined (if reproduction of a CVE is applicable)"
    ]),
    context=[analysis_task],
    output_json=PacketGenerationPrompt,
    output_file=os.path.join(output_dir, f"vulnerbilities_agent_prompt_{datetime.now(pytz.timezone('Africa/Cairo')).strftime('%d-%I-%M-%S')}.json"),
    agent=vulnerbilities_agent,
)

coverage_plateau_agent = Agent(
    role="Proffesional Fuzz Testing Coverage Plateau Surpasser",
    goal="Use the prompt of the previous agent to generate the network packet that would surpass the coverage plateau.",
    backstory="\n".join([
        "You are an expert AI agent who have great capabilities of generating a network packet,",
        "that would surpass the coverage plateau of the protocol fuzzer, triggering new state transitions,",
        "leading to better code coverage across the protocol. You should generate the network packet",
        "according to the prompt passed from the previous agent. Use the Packet Parsing Tool to parse and provide the final answer.",
    ]),
    tools=[PacketParsingTool(result_as_answer=True)],
    llm=llama33,
    verbose=True,
)

coverage_plateau_task = Task(
    description="\n".join([
        "The main task is to provide a {protocol} protocol network packet that would surpass the protocol",
        "fuzzer's coverage plateau and trigger new state transitions or vulnerbilities in the server under test.",
        "Generate the network packet accroding to the prompt passed from the previous agent, you should find all the",
        "neccessary instructions included in that prompt. Don't include any direction before the packet, like C->S: or S->C:",
        "It is required to use the 'Packet Parsing Tool', to parse and provide the result network packet.",
        "The input passed to the tool should be the json object of type CoveragePlateauSurpassingNetworkPacket.",
        "Ensure the pydantic object is passed to the tool is wrapped under the key pydantic_output_object, not directly,",
        "it must contain the 'packet' key which is a str representing the value of the network packet surpassing the coverage plateau,",
        "and also must contain the key 'explanation' which is your explanation why did you provide this packet typically.",
        "The object passed to tool is expected to be like this: {{'pydantic_output_object': {{'packet': '<packet>', 'explanation': '<explanation>'}}}}",
        "After obtaining the tool's output which is the packet only, the task is completed, return the packet string and strictly don't redo the task or any additional api-calls that cause rate limits."
    ]),
    expected_output="The 'Packet Parsing Tool' output, which is the network packet that would surpass the coverage plateau.",
    context=[vulnerbilities_task],
    output_file=os.path.join(output_dir, f"cov_plateau_packet_{datetime.now(pytz.timezone('Africa/Cairo')).strftime('%d-%I-%M-%S')}.txt"),
    agent=coverage_plateau_agent,
)


def assemble_coverage_plateau_crew():
    """Assemble the coverage plateau crew."""
    
    knowledge = StringKnowledgeSource(content=knowledge_source)

    coverage_plateau_crew = Crew(
                            agents=[rag_agent, analysis_agent, vulnerbilities_agent, coverage_plateau_agent],
                            tasks=[rag_task, analysis_task, vulnerbilities_task, coverage_plateau_task],
                            knowledge_sources=[knowledge],
                            output_log_file=os.path.join(output_dir, f"coverage_plateau_crew_{datetime.now(pytz.timezone('Africa/Cairo')).strftime('%d-%I-%M-%S')}.txt"),
                            verbose=False
                        )
    
    return coverage_plateau_crew


if __name__ == "__main__":
    load_dotenv()
    coverage_plateau_crew = assemble_coverage_plateau_crew()
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=Live555"
    server = "Live555"

    coverage_plateau_results = coverage_plateau_crew.kickoff(
        inputs = {
            "protocol": "RTSP",
            "server": server,
            "question": coverage_plateau_prompt,
            "url": url
        }
    )