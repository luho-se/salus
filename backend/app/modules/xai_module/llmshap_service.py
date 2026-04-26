from llmSHAP import DataHandler
from llmSHAP import BasicPromptCodec
from llmSHAP import ShapleyAttribution
from llmSHAP.llm import OpenAIInterface
from .llmshap_config import LLMShapConfig

class LLMShapService:

	def __init__(self, config: LLMShapConfig):
		self.config = config
		self.data = None
		self.dh = None
		self.codec = None
		self.llm_interface = None
		self.shapley = None
		self.results = None

	def set_data(self, data: dict):
		"""
		Set the data for which to compute the diagnosis.
		"""
		self.data = data

	def compute_diagnosis(self, data: dict = None) -> tuple[dict, dict]:
		"""
		Compute the diagnosis for the given data. If data is not provided
		it will use the data set in the service.

		If no data is provided and no data is set in the service, it will raise an error.
		"""
		if data is not None:
			self.set_data(data)

		if self.data is None:
			raise ValueError("No data provided for diagnosis")

		self.dh = DataHandler(data=self.data)
		self.codec = BasicPromptCodec(system=self.config.system_instruction)
		self.llm_interface = OpenAIInterface(model_name="gpt-4o-mini")
		self.shapley = ShapleyAttribution(
			data_handler=self.dh,
			prompt_codec=self.codec,
			model=self.llm_interface,
			use_cache=True,
			num_threads=8
		)
		self.results = self.shapley.attribution()	
		return self.results.output, self.results.attribution

