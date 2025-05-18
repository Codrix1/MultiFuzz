import time, os, json, pytz
from datetime import datetime
from crewai.tools import BaseTool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from pydantic import BaseModel, Field
from typing import Type, Union
from rich import print
from pydantic_models import RTSPGrammarTemplates, EnrichedNetworkPacketSeeds, CoveragePlateauSurpassingNetworkPacket
import requests
from dotenv import load_dotenv

class CustomRagToolInput(BaseModel):
    search_query: str = Field(..., description="The query to search for in the vector store")

class CustomRagTool(BaseTool):
    name: str = "RAG Tool"
    description: str = "Retrieves relevant data from the vector store to help answer a question."
    args_schema: Type[BaseModel] = CustomRagToolInput

    def load_vstore(self, persist_directory, collection_name):
        vectorstore = Chroma(
            persist_directory=persist_directory,
            collection_name=collection_name,
            embedding_function=OpenAIEmbeddings(model='text-embedding-ada-002'),
        )
        print("Loaded Chroma Vector Store Successfully.")
        return vectorstore

    def get_custom_retriever(self, vstore, search_kwargs: dict):
        retriever = vstore.as_retriever(search_kwargs=search_kwargs)
        return retriever


    def _run(self, search_query: str) -> str:
        """This tool Retrieves context from the vector store."""
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        persist_directory = os.path.join(script_dir, "chroma_db_agentic_chunks_unique")
        collection_name = "agentic_chunks"

        vstore = self.load_vstore(persist_directory, collection_name)
        retriever = self.get_custom_retriever(vstore, {"k": 10})

        documents = retriever.invoke(search_query)
        context = "\n\n".join([doc.page_content for doc in documents])

        print("DEBUG SEARCH QUERY:  ", search_query)
        # print("DEBUG CONTEXT: \n\n", context)

        time.sleep(3)
        return context
    
    
class GrammarExtractionFormattingToolInput(BaseModel):
    pydantic_output_object: RTSPGrammarTemplates

class GrammarExtractionFormattingTool(BaseTool):
    name: str = "Grammar Extraction Formatting Tool"
    description: str = "Formats a JSON object into a nicely structured string."
    args_schema: Type[BaseModel] = GrammarExtractionFormattingToolInput

    def _run(self, pydantic_output_object: Union[RTSPGrammarTemplates, dict]) -> str:
        """Formats the given JSON object into a structured string."""

        if isinstance(pydantic_output_object, dict):
            pydantic_output_object = RTSPGrammarTemplates(**pydantic_output_object)

        print("DEBUG TYPE:", type(pydantic_output_object))
        print("DEBUG CONTENT:", pydantic_output_object)

        i = 1
        final_output = "For the RTSP protocol, the client request templates are:\n\n"

        for template in pydantic_output_object.templates:
          for req_name, lines in template.root.items():
            final_output += f"""{i}. {req_name}: {str(lines)}\n\n"""
            i += 1

        return final_output
    
class SeedEnrichmentParsingToolInput(BaseModel):
    pydantic_output_object: EnrichedNetworkPacketSeeds

class SeedEnrichmentParsingTool(BaseTool):
    name: str = "Seeds Parsing Tool"
    description: str = "Parses a JSON object and returns the enriched network packet seeds"
    args_schema: Type[BaseModel] = SeedEnrichmentParsingToolInput

    def _run(self, pydantic_output_object: Union[EnrichedNetworkPacketSeeds, dict]) -> str:
        """This tool is useful for parsing and returns the enriched seeds"""

        if isinstance(pydantic_output_object, dict):
            pydantic_output_object = EnrichedNetworkPacketSeeds(**pydantic_output_object)
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(script_dir, "logs")            
            file_path = os.path.join(output_dir, f"enriched_seeds_{datetime.now(pytz.timezone('Africa/Cairo')).strftime('%d-%I-%M-%S')}.json")
            
            with open(file_path, "w", encoding="utf-8") as f:
                json_obj = json.dumps(pydantic_output_object.model_dump(), indent=4)
                f.write(json_obj)

        print("DEBUG TYPE:", type(pydantic_output_object))
        print("DEBUG CONTENT:", pydantic_output_object)

        enriched_seeds = pydantic_output_object.enriched_seeds
        return enriched_seeds        
    

class PacketParsingToolInput(BaseModel):
    pydantic_output_object: CoveragePlateauSurpassingNetworkPacket

class PacketParsingTool(BaseTool):
    name: str = "Packet Parsing Tool"
    description: str = "Parses a JSON object and returns the network packet that would surpass the coverage plateau"
    args_schema: Type[BaseModel] = PacketParsingToolInput

    def _run(self, pydantic_output_object: Union[CoveragePlateauSurpassingNetworkPacket, dict]) -> str:
        """This tool is useful for parsing and returns the network packet that would surpass the coverage plateau"""

        if isinstance(pydantic_output_object, dict):
            pydantic_output_object = CoveragePlateauSurpassingNetworkPacket(**pydantic_output_object)
        
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "logs")
        file_path  = os.path.join(output_dir, f"cov_plateau_packet_{datetime.now(pytz.timezone('Africa/Cairo')).strftime('%d-%I-%M-%S')}.json")
        
        with open(file_path, "w", encoding="utf-8") as f:
            json_obj = json.dumps(pydantic_output_object.model_dump(), indent=4)
            f.write(json_obj)

        print("DEBUG TYPE:", type(pydantic_output_object))
        print("DEBUG CONTENT:", pydantic_output_object)

        packet = pydantic_output_object.packet

        print("DEBUG COVERAGE PLATEAU PACKET: \n", packet)

        time.sleep(5)

        return packet

class CVEsRetrievalToolInput(BaseModel):
    url: str = Field(..., description="The URL of the CVEs list")

class CVEsRetrievalTool(BaseTool):
    name: str = "CVEs Retrieval Tool"
    description: str = "Fetches CVEs, and vulnerbilities for a specific protocol given a url for the CVE list."
    args_schema: Type[BaseModel] = CVEsRetrievalToolInput

    def _run(self, url: str) -> str:
        """
        This tool is useful for fetching CVEs, and vulnerbilities for a specific protocol given a url for the CVE list.
        The tool returns a structured JSON object containing the CVE ID, severity, and description.
        """
        response = requests.get(url)
        cves_json = response.json()

        parsed_output = []

        for vuln in cves_json["vulnerabilities"]:
            cve = vuln["cve"]
            cve_id = cve.get("id")

            severity = ""
            if "metrics" in cve and "cvssMetricV2" in cve["metrics"]:
                severity = cve["metrics"]["cvssMetricV2"][0].get("cvssData", {}).get("baseSeverity", "")

            description = next(
                (desc["value"] for desc in cve.get("descriptions", []) if desc["lang"] == "en"),
                ""
            )

            parsed_output.append({
                "cve_id": cve_id,
                "severity": severity,
                "description": description,
            })

        final_json_list = str(json.dumps(parsed_output, indent=2))

        time.sleep(10)

        return final_json_list

if __name__ == "__main__":
    load_dotenv()
    custom_rag_tool = CustomRagTool(result_as_answer=True)
    print("RAG Tool output: \n", custom_rag_tool._run("RTSP client request methods, and header fields"))
    
    