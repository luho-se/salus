from dataclasses import dataclass

@dataclass
class LLMShapConfig:

	system_instruction: str
	permanent_keys: list[str]
	exclude_permanent_keys: bool
