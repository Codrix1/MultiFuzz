#!/usr/bin/env python
from random import randint
from pydantic import BaseModel , Field
from crewai.flow import Flow, listen, start
from self_evaluation_loop_flow.crews.commands_extractor.commands_extractor import CommandsExtractor
from self_evaluation_loop_flow.Clean_n_divide import *
from self_evaluation_loop_flow.Extractions_functions import *
from self_evaluation_loop_flow.LLMs import *

import time
import json

with open("self_evaluation_loop_flow\\src\\self_evaluation_loop_flow\\Rfcs\\rfc959.txt", "r", encoding="utf-8") as f:
    content = f.read()

class CommandExtraction(BaseModel):
    updated_List: str = Field(..., description="The list of the extracted commands ")

class RuleBook(BaseModel):
    chapter1: str = Field(...,description="The content under Chapter 1")
    chapter2: str = Field(...,description="The content under Chapter 2")
    chapter3: str = Field(...,description="The content under Chapter 3")
    

class document(BaseModel):
    original_document: str = ""
    appendix: str = "" 
    CommandsExtractorResponse: str = ""
    parsed_items : ItemList = Field(default_factory=ItemList)
    chunks: list[str] = Field(default_factory=list)
    selected_titles: List[str] = Field(default_factory=list)
    Command_chunks:List[str] = Field(default_factory=list)
    Extracted_commands:List[str] = Field(default_factory=list)
    Rule_book:List[RuleBook] = Field(default_factory=list)

class RFC_extractor(Flow[document]):

    # @start()
    # def generate_title_list(self):
    #     self.state.parsed_items = parse_rfc(content)
    #     self.state.appendix = generate_appendix(self.state.parsed_items.items)
    #     self.state.chunks = collect_all_chunks(self.state.parsed_items.items)
    #     self.state.CommandsExtractorResponse= CommandsExtractor().crew().kickoff(inputs={"appendix":self.state.appendix}).raw
    #     print(self.state.appendix) 
    #     print("\n\n-------------------\n\n")
    #     print(self.state.CommandsExtractorResponse)
    #     print("\n\n-------------------\n\n")

    # @listen(generate_title_list)
    # def Extract_command_list(self):
    #     Titles = extract_List(self.state.CommandsExtractorResponse)
    #     for title in Titles:
    #         item = self.state.parsed_items.get_by_path(title)
    #         self.state.Command_chunks.append(f"{item.title} \n {item.body}")
    #     List=[]
    #     for chunk in self.state.Command_chunks:
    #         time.sleep(15)
    #         Prompt = f"""

    #                 This is a list that should contain all the command of the protocol each command written in capital letters.
    #                 List: {List}

    #                 Using the the context provides below add command to the command list using these rules.
    #                 only add the command if it satisfies all the rules

    #                 Rules:
    #                 1.Do not remove any command from the original List.
    #                 2.Any command mentioned in the document is written in captial letters so if something isnt entirely in capital letters it isnt a command.
    #                 3.Before you add the command check that it isnt in the list
    #                 4.Before you add the command check get its refrence, check that it isnt an obsolete command, check that its name is correct ,
    #                 5.check that it is explicitly mentioned and check that it is actual command.


    #                 Sometimes the context doesnt have any command that satisfies all the 5 rules if that happens dont update the list.
                    
    #                 Context:{chunk}





    #                 Expected Output: reasoning then the updated list of the extracted commands 
    #                 example -> the reason on the chosen commands
    #                 [COMMAND1 , COMMAND2 , ...]
    #         """
    #         response = deepseek_r1_distill_llama_70B.call(messages=Prompt)

    #         print(Prompt)
    #         print("\n\n-------------------\n\n")

    #         Prompt = f"""
    #                     extract the list of commands from the provided answer:

    #                     {response}
    #         """

    #         model = LLM(
    #                     model="groq/llama3-70b-8192",
    #                     temperature=0.0,
    #                     response_format = CommandExtraction  
    #                 )  
            
    #         format = model.call(messages=Prompt)
    #         List = extract_List(format);

    #         print(response)
    #         print("\n\n-------------------\n\n")
    #         print(format)
    #         print("\n\n----------_____---------\n\n")
    #     self.state.Extracted_commands=List
            

    @start()
    def Construct_Fuzzy_rule_book(self):
        self.state.parsed_items = parse_rfc(content)
        self.state.chunks = collect_all_chunks(self.state.parsed_items.items)
        list = ['USER', 'PASS', 'ACCT', 'CWD', 'CDUP', 'SMNT', 'QUIT', 'REIN', 'PORT', 'PASV', 'TYPE', 'STRU', 'MODE', 'RETR', 'STOR', 'STOU', 'APPE', 'ALLO', 'REST', 'RNFR', 'RNTO', 'ABOR', 'DELE', 'RMD', 'MKD', 'PWD', 'LIST', 'NLST', 'SITE', 'SYST', 'STAT', 'HELP', 'NOOP']

        # list = ["PAUSE"]
        # for command in self.state.Extracted_commands:
        for command in list:
            search_chunks = []
            search_chunks = [s for s in self.state.chunks if command in s]
            # for chunk in self.state.chunks:
            #     print(f"\n\n----------------------------\n\n{chunk}\n\n----------------------------\n\n")
            # time.sleep(9999999)
            chapter1=""
            chapter2=""
            chapter3=""
            print(f" starting with command {command}")
            for chunk in search_chunks:
                try:
                    prompt=f"""
                        You will carefully update the rule book for the {command} command based on the provided context, never answer in a table format, strictly following the all 6 rules below.
                        The rule book consists of three chapters—do not add, modify, or update anything that violates these rules..

                            Rules: 
                            1. Under the context and see if it includes useful information about the chapters or not. If it doesnt do not change anything.
                            2. If the reference does not contain new or conflicting information, leave the chapter unchanged.
                            3. Do not remove any existing information from any chapter; only add new details where necessary.
                            4. Do not add or modify anything unless explicitly supported by the reference. All updates must come directly from the context.
                            5. Do not add or infer any details beyond what is described in the reference.
                            6. Only include the commands that come from the client side not server side.

                            Chapter 1: Command Purpose & Outlines
                            Description: Explain the purpose of {command} in 1 sentence.and whether excuting {command} influnces the system state or not and can it be used anytime or not.

                            
                            Chapter 2: Valid direct Preceding Commands/Methods.

                            Description: A list of commands/methods that can or are required to directly precede {command} without intermediate commands between them.
                            Each entry must include on of the following: The exact preceding command. The state the system must be in for this sequence to be valid. Whether executing {command} after this command changes the system state.and what state it changes to

                            
                            Chapter 3: Valid direct Subsequent Commands/Methods

                            Description: A list of commands/methods that can directly follow {command} without intermediate commands between them.
                            Each entry must include: The exact subsequent command. The state the system must be in after {command} for this sequence to be valid. Whether the subsequent command changes the system state.and what state it changes to


                        chapter 1:
                        {chapter1}




                        chapter 2:
                        {chapter2}


                        

                        chapter 3:
                        {chapter3}


                        
                     

                        context:

                        {chunk}

                        
                         
                        Expected output:

                        chapter 1:
                        content of chapter 1
                        \n\n
                        chapter 2:
                        content of chapter 2 
                        \n\n
                        chapter 3:
                        content of chapter 3
                        \n\n

                        

                    """
                    response = deepseek_r1_distill_llama_70B.call(messages=prompt)
                    print("\n\n-------------------\n\n")
                    print(prompt)
                    print("\n\n-------------------\n\n\n\n")
                    print(response)
                    print("\n\n----------_____---------\n\n\n\n\n\n")
                    time.sleep(5)

                except:
                    print(f"\n\n\nerror processing chunk {chunk}\n\n\n\n\n")
                    pass

                try: 
                    cleaned_text = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)
                    extraction_prompt = f"""

                    Format the provided text into three separate strings without changing, modifying, rewording, or adding anything to the original content.
                    Input: text: {cleaned_text} 
                    Expected Output: 
                    string1 = "The content under Chapter 1" 
                    string2 = "The content under Chapter 2" 
                    string3 = "The content under Chapter 3" 
                    
                    Important Rules:
                     - Do not alter the text in any way (no rewording, no corrections, no additions). 
                     -maintain the white spaces dont squish everything together.
                    - Only separate the text into three strings according to the chapter divisions.

                    """
                    # llama = LLM(
                    #     model="groq/gemma2-9b-it",
                    #     temperature=0.0,
                    #     response_format = RuleBook  
                    # ) 
                    llama = LLM(
                        model="groq/llama-3.3-70b-versatile",
                        temperature=0.0,
                        response_format = RuleBook,  
                        
                    )  
                    Extraction_response = llama.call(messages=extraction_prompt)
                    print("\n\n----------extraction---------n\n")

                    print(Extraction_response)
                    print("\n\n----------extraction---------\n\n")

                    parsed = RuleBook.model_validate_json(Extraction_response)
                    chapter1 = parsed.chapter1
                    chapter2 = parsed.chapter2
                    chapter3 = parsed.chapter3  
                
                except:
                    print(f"\n\n\nerror formatting chunk {chunk}\n\n\n\n\n")
                    pass

                finally:
                    time.sleep(5)
            write_rulebook_to_txt(parsed, "my_rulebook.txt")
                
   


def kickoff():

    RFC_flow = RFC_extractor()
    RFC_flow.kickoff()


def plot():
    RFC_flow = RFC_extractor()
    RFC_flow.plot()


if __name__ == "__main__":
    kickoff()
    
