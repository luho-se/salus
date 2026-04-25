from flask import Blueprint, current_app, jsonify, request, Response
from typing import Optional
import threading

from ..services.diagnosis_service import DiagnosisJobStatus, create_diagnosis
from ..services.diagnosis_service import get_diagnosis
from ..services.diagnosis_service import get_diagnosis_items
from ..services.diagnosis_service import get_diagnosis_list
from ..services.diagnosis_service import get_diagnosis_sentence_weights
from ..services.diagnosis_service import get_diagnosis_status as get_diagnosis_status_service
from ..services.diagnosis_service import save_diagnosis
from ..services.diagnosis_service import create_diagnosis_status
from ..services.diagnosis_service import DiagnosisItem
from ..services.diagnosis_service import Diagnosis
from ..services.diagnosis_service import DiagnosisReturn
from ..services.diagnosis_service import DiagnosisSentenceWeight


bp = Blueprint("diagnostic", __name__)


@bp.route("/diagnosis/<int:project_id>", methods=["POST"])
def generate_diagnosis(project_id: int):
	"""
	Generates a diagnosis for the given project_id and returns the diagnosis_id
	Parameters:
		project_id (int)
	Returns:
		diagnosis_id (int)
	"""
	try:

		diagnosis_id: int = save_diagnosis(project_id)
		if diagnosis_id is None:
			return jsonify({"error": "Failed during diagnosis initialization"}), 500
		create_diagnosis_status(project_id, diagnosis_id)
		app = current_app._get_current_object()
		def run_in_context():
			with app.app_context():
				create_diagnosis(project_id, diagnosis_id)
		thread = threading.Thread(target=run_in_context, daemon=True)
		thread.start()
		return jsonify({"diagnosis_id": diagnosis_id}), 200
	except Exception as e:
		return jsonify({"error": str(e)}), 500


@bp.route("/diagnosis/<int:diagnosis_id>/status", methods=["GET"])
def diagnosis_status_route(diagnosis_id: int):
	"""
	Returns the status of the diagnosis job for the given diagnosis_id
	Parameters:
		diagnosis_id (int)
	Returns:
		DiagnosisJobStatus or None if not found or on error
	"""
	try:
		status: Optional[DiagnosisJobStatus] = get_diagnosis_status_service(diagnosis_id)
		if status is None:
			return jsonify({"error": "Diagnosis status not found"}), 404
		return jsonify({"status": status}), 200
	except Exception as e:
		return jsonify({"error": str(e)}), 500


@bp.route("/diagnosis/list/<int:project_id>/slim", methods=["GET"])
def get_diagnosis_list_slim(project_id: int):
	"""
	Returns a slim list of diagnoses for the given project_id
	Parameters:
		project_id (int)
	Returns:
		List of diagnosis (id, project_id, created_at)
	"""
	try:
		diagnoses: list[Diagnosis] = get_diagnosis_list(project_id)

		if diagnoses is None:
			return jsonify({"error": "No diagnoses found for this project"}), 404
		
		return jsonify({"diagnoses": diagnoses}), 200
	except Exception as e:
		return jsonify({"error": str(e)}), 500

@bp.route("/diagnosis/<int:diagnosis_id>", methods=["GET"])
def get_diagnosis_route(diagnosis_id: int) -> DiagnosisReturn:
	"""
	Returns the diagnosis and its associated items and sentence weights for the given diagnosis_id
	Parameters:
		diagnosis_id (int)
	Returns:
		Diagnosis by ID, including its items and sentence weights.
	"""
	try:
		diagnosis: Diagnosis = get_diagnosis(diagnosis_id)
		items: list[DiagnosisItem] = get_diagnosis_items(diagnosis_id)
		weights: list[DiagnosisSentenceWeight] = get_diagnosis_sentence_weights(diagnosis_id)
		
		if diagnosis is None:
			return jsonify({"error": "Diagnosis not found"}), 404

		res: DiagnosisReturn = {
			"id": diagnosis["id"],
			"project_id": diagnosis["project_id"],
			"created_at": diagnosis["created_at"],
			"diagnosis_items": items,
			"diagnosis_weights": weights
		}
		return jsonify(res), 200
	except Exception as e:
		return jsonify({"error": str(e)}), 500
