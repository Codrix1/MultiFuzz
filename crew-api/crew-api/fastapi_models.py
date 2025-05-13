from pydantic import BaseModel

class FuzzerRequestModel(BaseModel):
    question: str
    
class FuzzerResponseModel(BaseModel):
    response: str