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

	def get_latest_diagnosis(self) -> tuple[dict, dict]:
		"""
		Get the latest computed diagnosis. If no diagnosis has been computed, it will raise an error.
		"""
		if self.results is None:
			raise ValueError("No diagnosis computed yet")

		return self.results.output, self.results.attribution

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

		self.dh = DataHandler(self.data)
		self.codec = BasicPromptCodec(system=self.config.system_instruction)
		self.llm_interface = OpenAIInterface(model_name="gpt-4o-mini")
		self.shapley = ShapleyAttribution(
			data_handler=self.dh,
			prompt_codec=self.codec,
			model=self.llm_interface,
			use_cache=True,
			num_threads=2
		)
		self.results = self.shapley.attribution()	
		return self.results.output, self.results.attribution

if __name__ == "__main__":
	config = LLMShapConfig(
		system_instruction="You are a helpful assistant for debugging machine learning models. You will be given a prediction and the input features that led to that prediction. Your task is to identify which features were most influential in the model's decision and provide insights into why the model made that prediction.",
		permanent_keys=[],
		exclude_permanent_keys=False
	)
	service = LLMShapService(config)
	data = {
		"question1": "What is the capital of France? answer: Paris",
		"question2": "What is the largest mammal? answer: squirrel",
	}
	service.compute_diagnosis(data)
	print(service.get_latest_diagnosis())