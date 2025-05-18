from pydantic import BaseModel, RootModel, Field
from typing import List, Dict

class Context(BaseModel):
    context: str = Field(..., description="The retrieved context from the vector store.")
    
class Template(RootModel[Dict[str, List[str]]]):
    pass

class RTSPGrammarTemplates(BaseModel):
    templates: List[Template]
  
class EnrichedNetworkPacketSeeds(BaseModel):
    enriched_seeds: str = Field(..., description="The enriched sequence of network packets.")
    explanation: str = Field(..., description="The explanation for the enriched network packet seeds.")

class PacketGenerationPrompt(BaseModel):
  prompt: str = Field(..., description="A detailed prompt for generating the coverage plateau surpassing packet, should be based on the guidance of the previous agents.")

class CoveragePlateauSurpassingNetworkPacket(BaseModel):
    packet: str = Field(..., description="The network packet that would surpass the coverage plateau.")
    explanation: str = Field(..., description="The explanation for the provided packet.")