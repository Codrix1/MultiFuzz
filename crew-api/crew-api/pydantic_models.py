from pydantic import BaseModel, Field
from typing import List, Dict

class Context(BaseModel):
    context: str = Field(..., description="The retrieved context from the vector store.")
    
class RTSPGrammarTemplates(BaseModel):
    templates: Dict[str, List[str]]
  
class EnrichedNetworkPacketSeeds(BaseModel):
    enriched_seeds: str = Field(..., description="The enriched sequence of network packets.")
    explanation: str = Field(..., description="The explanation for the enriched network packet seeds.")

class CoveragePlateauSurpassingNetworkPacket(BaseModel):
    packet: str = Field(..., description="The network packet that would surpass the coverage plateau.")
    explanation: str = Field(..., description="The explanation for the provided packet.")