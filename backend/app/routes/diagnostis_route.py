from flask import Blueprint, jsonify, request, Response

bp = Blueprint("diagnostis", url_prefix="/diagnostis")

@bp.route("/diagnosis/<int:project_id>", methods=["POST"])
def generate_diagnosis(project_id: int):
	# Get the given project, questions and answers from the database
    
	# Check if questions and answers are availbale and if they have changed if a diagnosis exists
    
	# Compute the diagnosis for the project using the LLMShapService
    
	# Store the diagnosis in the database

	# Return the diagnosis (or the id) and attribution as JSON response
    pass

@bp.route("/diagnosis/<int:project_id>", methods=["get"])
def get_diagnosis(project_id: int):
	# Get the latest diagnosis for the given project from the database

	# Return the diagnosis (or the id) and attribution as JSON response
	pass