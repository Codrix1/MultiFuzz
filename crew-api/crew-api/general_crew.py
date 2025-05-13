import os, copy, pytz
from datetime import datetime
from crewai import Agent, Task, Crew
from drag_agent import retrieval_agent, retrieval_task
from llm_utils import llama4
from prompts import general_prompt
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "logs")

rag_agent = retrieval_agent.copy()
rag_task = copy.copy(retrieval_task)

general_agent = Agent(
    role="RTSP protocol Finite State Machine Expert.",
    goal="Analyze the fuzzer's question, and then generate an appropriate answer.",
    backstory="\n".join([
        "You are an expert AI agent, who have context awareness of the {protocol} protocol's finite state machine/model,",
        "and it's different states. You need to analyze the fuzzers question, and review the context provided",
        "from the retrieval_agent, to generate an appropriate answer to the fuzzer's question.",
    ]),
    llm=llama4,
    verbose=True,
)

general_task = Task(
    description="\n".join([
        "The task is analyze the context provided from the retrieval_agent, and also analyze the fuzzer's request/question,"
        "to generate an appropriate answer to the fuzzer's question.",
        "Don't include any direction before any generated packets, like C->S: or S->C:",
        "The fuzzer's question/request: <fuzzer_question>{question}</fuzzer_question>",
    ]),
    expected_output="An appropriate answer to the fuzzer's request/question.",
    context=[rag_task],
    output_file=os.path.join(output_dir, f"general_response_{datetime.now(pytz.timezone('Africa/Cairo')).strftime('%d-%I-%M-%S')}.txt"),
    agent=general_agent,
)


def assemble_general_fsm_crew():
    """Assemble the state machine general crew."""
    
    general_crew = Crew(
        agents=[rag_agent, general_agent],
        tasks=[rag_task, general_task],
        output_log_file=os.path.join(output_dir, f"general_state_machine_crew_{datetime.now(pytz.timezone('Africa/Cairo')).strftime('%d-%I-%M-%S')}.txt"),
        verbose=False
    )
    
    return general_crew


if __name__ == "__main__":
    load_dotenv()
    general_crew = assemble_general_fsm_crew()

    general_crew_results = general_crew.kickoff(
        inputs = {
            "protocol": "RTSP",
            "question": general_prompt
        }
    )