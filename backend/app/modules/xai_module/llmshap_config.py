from dataclasses import dataclass, field

@dataclass
class LLMShapConfig:
    system_instruction: str
    permanent_keys: list[str] = field(default_factory=list)
    exclude_permanent_keys: bool = False
