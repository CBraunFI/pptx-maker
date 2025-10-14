from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal, Any

class ModuleItem(BaseModel):
    title: str
    duration: Optional[str] = None
    outcomes: Optional[List[str]] = None

class TrainerItem(BaseModel):
    name: str
    role: str
    bio: Optional[str] = None
    photoRef: Optional[str] = None

SlideType = Literal[
    "title","agenda","context","need","understanding","vision",
    "approach","principles","architecture","modules_overview",
    "module_detail","transfer","digital","coaching","target_group",
    "impact","about_synk","team","references","expertise","partners",
    "investment","next_steps","contact"
]

class Slide(BaseModel):
    id: str
    type: SlideType
    title: str
    subtitle: Optional[str] = None
    content: Optional[Union[str, List[str]]] = None
    modules: Optional[List[ModuleItem]] = None
    trainers: Optional[List[TrainerItem]] = None
    visual: Optional[str] = None
    designHint: Optional[str] = None

class Style(BaseModel):
    font: str = "Arial Narrow"
    colors: dict
    logo: Optional[str] = None
    clientLogo: Optional[str] = None

class Meta(BaseModel):
    deckTitle: str
    deckSubtitle: Optional[str] = None
    author: str
    date: str
    customer: str
    useCase: Optional[str] = None
    style: Style

class Deck(BaseModel):
    meta: Meta
    slides: List[Slide]

class RenderRequest(BaseModel):
    deck: Deck

class RenderResponse(BaseModel):
    filename: str
    file: str  # base64
