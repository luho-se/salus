from flask import Blueprint, jsonify, request, Response

from ..services.diagnosis_service import create_diagnosis
from ..services.diagnosis_service import get_diagnosis_items
from ..services.diagnosis_service import DiagnosisItem


bp = Blueprint("diagnostic", url_prefix="/diagnosis")


@bp.route("/diagnosis/<int:project_id>", methods=["POST"])
def generate_diagnosis(project_id: int):
	try: 
		diagnosis_id: int = create_diagnosis(project_id)
		if diagnosis_id is None:
			return jsonify({"error": "Failed to create diagnosis"}), 500
		return jsonify({"diagnosis_id": diagnosis_id}), 201
	except Exception as e:
		return jsonify({"error": str(e)}), 500


@bp.route("/diagnosis/<int:diagnosis_id>/items", methods=["GET"])
def get_diagnoses(diagnosis_id: int):
	"""
	Returns the all diagnosis items for the given diagnosis_id
	Parameters:
		diagnosis_id (int)
	Returns:
	"""
	try: 
		diagnosis_items: list[DiagnosisItem] = get_diagnosis_items(diagnosis_id)
		if diagnosis_items is None:
			return jsonify({"error": "Diagnosis items not found"}), 404
		return jsonify(diagnosis_items)
	except Exception as e:
		return jsonify({"error": str(e)}), 500