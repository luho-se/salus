from dataclasses import dataclass

@dataclass
class LLMShapConfig:

	system_instruction: str
	ignored_tokens: list[str]
