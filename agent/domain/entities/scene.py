from pydantic import BaseModel

from agent.domain.entities.prompt import Prompt
from agent.domain.values.output_format import OutputFormat


class Scene(BaseModel):
    name: str
    description: str
    
    role: str | None
    task: str | None
    examples: list = []
    
    references: list = []
    
    skills: list = []
    constraint: str | None    
    
    output_format: OutputFormat | None
    
    models: list = []
    
    
    