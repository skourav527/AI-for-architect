from pydantic import BaseModel
from pydantic import Field
from pydantic import ValidationError


# age: int = Field(..., gt=0, description="Age must be a positive integer")

# class ChatRequest(BaseModel):
#     provider: str
#     model: str
#     prompt: str
#     max_tokens: int = Field(gt=1, le=4096)

# try:    chat_request = ChatRequest(
#         provider="OpenAI",
#         model="gpt-3.5-turbo",
#         prompt="Hello, how are you?",
#         max_tokens=2
#     )
# except ValidationError as e:
#     print(e)
# else:
#     print(chat_request)

# from pydantic import BaseModel 
# from typing import Optional

# class ChatRequest(BaseModel): 
#     provider: str
#     model: str
#     prompt: str
#     max_tokens: int = 1024 # default value
#     temperature: float = 0.7
#     system: Optional[str] = None # nullable

# # --- create an instance ---
# req = ChatRequest(
#     provider="anthropic",
#     model="claude-sonnet-4-20250514",
#     prompt="Summarise pydantic in 2 lines."
# )
# print(req.provider) # anthropic
# print(req.max_tokens) # 1024 (default)
# print(req.system) # None
# print(req) # full repr

# # type coercion: str "512" → int 512
# req2 = ChatRequest(
#     provider="openai",
#     model="gpt-4o",
#     prompt="Hello",
#     max_tokens="512"
# )
# print(type(req2.max_tokens)) # <class 'int'>

##-----Nested model ----------------------------------------------------------------

from pydantic import BaseModel, Field 
from typing import List, Optional 

##--------------child model --- 
class Usage(BaseModel): 
    prompt_tokens: int = Field(ge=0) 
    completion_tokens: int = Field(ge=0) 
    total_tokens: int = Field(ge=0) 

##--------------parent model --- 
class ChatResponse(BaseModel): 
    id: str 
    model: str 
    content: str 
    usage: Usage 

# pass a plain dict — pydantic converts it 
resp = ChatResponse(
    id="resp_001",
    model="claude-sonnet-4-20250514",
    content="Pydantic validates your data.",
    usage={  # dict ✓
        "prompt_tokens": 14,
        "completion_tokens": 6,
        "total_tokens": 20
    }
)
print(resp.usage.total_tokens)  # 20
print(type(resp.usage))  # <class 'Usage'>, not dict

# nested validation error — wrong type inside usage
from pydantic import ValidationError
try:
    ChatResponse(
        id="x",
        model="y",
        content="z",
        usage={"prompt_tokens": 1, "completion_tokens": "eee", "total_tokens": 1}
    )
except ValidationError as e:
    print(e.errors()[0]["loc"])  # ('usage', 'completion_tokens')

## ------------------------Pro Tips -----------------------------------

#1. strict mode
#ChatRequest.model_validate( data, strict=True )
#No coercion — "512" won't become 512. Good for internal service-to-service calls where types must be exact.

#2. model_json_schema()
#ChatRequest .model_json_schema()
#Auto-generates an OpenAPI-compatible JSON Schema from your model. Free documentation with no extra work.

#3. @model_validator
#@model_validator(mode="after") def check(self): ...
#Cross-field validation — e.g. ensure total_tokens == prompt + completion. Runs after all field validators pass.

#4. @field_validator
#@field_validator("model") def clean(cls, v): ...
#Custom logic for a single field — strip whitespace, normalise casing, call an external lookup, etc.

#5. model_config
#model_config = ConfigDict( str_strip_whitespace=True )
#Class-level settings: strip strings, freeze the model (immutable), populate by alias, extra='forbid', etc.

#6. extra='forbid'
#model_config = ConfigDict( extra="forbid" )
#Raises ValidationError if the payload contains any key not defined in the model. Prevents silent field injection.