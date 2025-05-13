from crewai import LLM

llama3_70b_8192 = LLM(
    model="groq/llama3-70b-8192",
    temperature=0.6,  
)

llama3_70b_versatile = LLM(
    model="groq/llama-3.3-70b-versatile",
    temperature=0.6,  
)

deepseek_r1_distill_llama_70B = LLM(
    model="groq/deepseek-r1-distill-llama-70b",
    temperature=0.0,  
)


