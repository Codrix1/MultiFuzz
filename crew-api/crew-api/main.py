import uvicorn
import time, pytz, os
import ujson
import agentops
from rich import print
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from grammar_extraction_crew import assemble_grammar_extraction_crew
from seed_enrichment_crew import assemble_seed_enrichment_crew
from cov_plateau_crew import assemble_coverage_plateau_crew
from general_crew import assemble_general_fsm_crew
from prompt_utils import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Context manager for the application's lifespan. """
    
    print("Lifespan: Setting up globals...")
    global grammar_crew, seeds_crew, coverage_crew, general_fsm_crew
    global log_file

    load_dotenv()
    
    grammar_crew = assemble_grammar_extraction_crew()
    seeds_crew = assemble_seed_enrichment_crew()
    coverage_crew = assemble_coverage_plateau_crew()
    general_fsm_crew = assemble_general_fsm_crew()
    
    os.makedirs("logs", exist_ok=True)
    agentops.init(api_key=os.getenv("AGENTOPS_API_KEY"), skip_auto_end_session=True)
    
    log_file = open("crew_api.log", "a+")
    log_file.write(f"MultiFuzz-API started at {datetime.now(pytz.timezone('Africa/Cairo')).strftime('%d-%I-%M-%S')}\n")
    
    # Yield control to the application
    yield

    print("Lifespan: Cleaning up resources...")
    grammar_crew, seeds_crew, coverage_crew, general_fsm_crew = None, None, None, None

app = FastAPI(title="MultiFuzz-API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def process_prompt(prompt: str):
    """
    Processes the prompt, determines the type, and runs a specialized crew.
    returns the response from the crew.
    """
    
    response = None
    prompt_type = determine_prompt_type(prompt)
    print(f"Prompt is of type: {prompt_type}")

    if prompt_type == Techinque.grammar_extraction.value:
        print("Prompt is of type: Grammar Extraction, chatting with the grammar extraction crew...")
        response = grammar_crew.kickoff(
            inputs={
                "protocol": "RTSP",
                "question": prompt
            }
        )
        
    elif prompt_type == Techinque.seed_enrichment.value:
        print("Prompt is of type: Seed Enrichment, chatting with the seed enrichment crew...")
        response = seeds_crew.kickoff(
            inputs={
                "protocol": "RTSP",
                "question": prompt
            }
        )
        
    elif prompt_type == Techinque.coverage_plateau.value:
        print("Prompt is of type: Coverage Plateau, chatting with the coverage plateau crew...")
        
        url = "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=Live555"
        server = "Live555"

        response = coverage_crew.kickoff(
            inputs = {
                "protocol": "RTSP",
                "server": server,
                "question": prompt,
                "url": url
            }
        )
        
    else:
        print("Prompt is of type: General FSM, chatting with the general FSM crew...")
        response = general_fsm_crew.kickoff(
            inputs={
                "protocol": "RTSP",
                "question": prompt
            }
        )
        
    return response.raw

def log_interaction(interaction: str):
    """
    Logs the interaction to the log file.
    """
    log_file.write(f"{datetime.now(pytz.timezone('Africa/Cairo')).strftime('%d-%I-%M-%S')}: {interaction}\n")

@app.get("/")
async def health_check():
    return {"status": "ok"}


@app.post("/chat-llm")
async def chat_with_crew(request: Request):
    print("Chatting with some crew...")

    raw_body = await request.body()
    try:
        prompt = ujson.loads(raw_body.decode('utf-8'))['question']
        print(f"Prompt in the coming request: {prompt}")

        response = process_prompt(prompt)
        log_interaction(f"------------------------------- \n Prompt: {prompt} \n\n Response: {response} \n ----------------------------------- \n\n")      
        print("*"*30)
        print(f"MultiFuzz Response: \n\n {response}")
        print("*"*30)

    except ValueError as ve:
        print(f"Value Error when decoding JSON: {ve}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    return {"response": response}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
