from crewai import LLM
from dotenv import load_dotenv

load_dotenv()

llama33 = LLM(model="groq/llama-3.3-70b-versatile", temperature=0) # RAG Agent
qwen_qwq = LLM(model="groq/qwen-qwq-32b", temperature=0) # Tools Agent
llama4 = LLM(model="groq/meta-llama/llama-4-scout-17b-16e-instruct", temperature=0) # Task Agent
deepseek = LLM(model="groq/deepseek-r1-distill-llama-70b", temperature=0) # Task Agent
llama31 = LLM(model="groq/llama-3.1-8b-instant", temperature=0) # Task Agent
llama3 = LLM(model="groq/llama3-70b-8192", temperature=0) # Task Agent
# gemma2 = LLM(model="groq/gemma2-9b-it", temperature=0) # Task Agent

knowledge_source = "A coverage plateau is defined as a stage during protocol fuzzing where no new code or states are being covered, despite continued input generation. It's essentially a point where progress in exploring the protocol implementation stalls."