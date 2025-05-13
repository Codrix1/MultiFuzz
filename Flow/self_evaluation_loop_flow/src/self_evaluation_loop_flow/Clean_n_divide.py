import re
from typing import List, Optional
from pydantic import BaseModel , Field
from crewai import LLM
from dotenv import load_dotenv

load_dotenv()

# chunks=""

# llm = LLM(
#     model="groq/llama3-70b-8192",
#     temperature=0.6,  
# )

class Item(BaseModel):
    title: str
    score: int
    body: str
    subitems: List["Item"] = []
    path: str = ""

    def get_items_at_level(self, target_level: int, current_level: int = 1) -> List["Item"]:
        if target_level == current_level:
            return [self]
        items = []
        for subitem in self.subitems:
            items.extend(subitem.get_items_at_level(target_level, current_level + 1))
        return items

    @property
    def full_body(self) -> str:
        combined = [self.body]
        for sub in self.subitems:
            combined.append(sub.full_body)
        return "\n\n".join(part for part in combined if part.strip())

    def is_leaf(self) -> bool:
        """Check if this item is a leaf node (has no subitems)"""
        return not bool(self.subitems)

Item.model_rebuild()

class ItemList(BaseModel):
    items: List[Item] = Field(default_factory=list)

    def get_all_items_at_level(self, level: int) -> List[Item]:
        result = []
        for item in self.items:
            result.extend(item.get_items_at_level(level))
        return result

    def get_by_path(self, path: str) -> Optional[Item]:
        def search(items: List[Item]) -> Optional[Item]:
            for item in items:
                if item.path == path:
                    return item
                result = search(item.subitems)
                if result:
                    return result
            return None
        return search(self.items)
    

def collect_all_chunks(items: List[Item]) -> List[str]:
    chunks = []
    
    def collect_leaves(items: List[Item]):
        for item in items:
            if item.is_leaf() and item.body.strip():
                chunks.append(item.body.strip())
            collect_leaves(item.subitems)
    
    collect_leaves(items)
    return chunks

def parse_items(text: str, level: int = 1, parent_path: str = "") -> List[Item]:
    pattern = r'(?:^|\n)[ \t]*(?P<num>([A-Z]\.)?(\d+\.){%d}\d+)\.?\s+(?P<title>[^\n]+)' % (level - 1)
    matches = list(re.finditer(pattern, text))
    if not matches:
        return []

    items = []

    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        number = match.group("num").rstrip(".")
        title = f"{number} {match.group('title')}"
        section_text = text[start:end].strip()

        full_path = number if not parent_path else f"{parent_path}.{number.split('.')[-1]}"

        # Get subitems from the section_text
        subitems = parse_items(section_text, level + 1, parent_path=full_path)

        # Exclude subitem text from the body
        if subitems:
            # Use the position of the first subitem in the section_text
            sub_pattern = r'(?:^|\n)[ \t]*(\d+\.){%d}\d+\.?\s+' % level
            sub_match = re.search(sub_pattern, section_text)
            if sub_match:
                body = section_text[:sub_match.start()].strip()
            else:
                body = section_text.strip()
        else:
            body = section_text.strip()

        items.append(Item(title=title, score=0, body=body, subitems=subitems, path=full_path))

    return items

def parse_rfc(text: str) -> ItemList:

    text= clean_rfc_pages(text)

    top_level_pattern = r'\n(?P<num>\d+)\.?\s+(?P<title>[^\n]+)'
    matches = list(re.finditer(top_level_pattern, text))

    items = []

    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        number = match.group("num")
        title = f"{number} {match.group('title')}"
        section_text = text[start:end].strip()

        subitems = parse_items(section_text, level=2, parent_path=number)
        items.append(Item(title=title, score=0, body=section_text.strip(), subitems=subitems, path=number))

    return ItemList(items=items)


def clean_rfc_pages(text):
    
    pattern = re.compile(
        r'\n{3}'                                      # 3 newlines
        r'Schulzrinne, et\. al\..*\[Page \d+\]\n'      # Page info line
        r'\f\n'                                        # Form feed and newline
        r'RFC 2326.*?Real Time Streaming Protocol.*?\n' # RFC line
        r'\n{2}',                                      # 2 newlines
        re.MULTILINE
    )
    
    # Remove all such blocks
    cleaned_text = re.sub(pattern, '\n', text)
    return cleaned_text

def generate_appendix(items: List[Item]) -> str:
    lines = []

    def recurse(items: List[Item], level: int = 0):
        indent = "  " * level
        for item in items:
            lines.append(f"{indent}- {item.title}")
            recurse(item.subitems, level + 1)

    recurse(items)
    return "\n".join(lines)

with open("self_evaluation_loop_flow\\src\\self_evaluation_loop_flow\\Rfcs\\rfc2326.txt", "r", encoding="utf-8") as f:
    content = f.read()


# debugging code for the functions
#--------------------------------------
# parsed = parse_rfc(content)
# appendix = generate_appendix(parsed.items)
# chunks = collect_all_chunks(parsed.items)

# print(appendix)
# print(chunks)
# response = llm.call(
#             f"""
#                 using the following appendix, tell me which titles will contain the commmands or methods that it describles.
#                 it can be more that one title. i only want the commands. \n {appendix}
#             """
#         )


# print(response)

