from flask import Blueprint, jsonify, request, Response

bp = Blueprint("diagnostic", url_prefix="/diagnostic")

@bp.route("/diagnosis/<int:project_id>", methods=["get"])
def get_diagnosis(project_id: int):
	# Get the given project, questions and answers from the database
    
    
	# Compute the diagnosis for the project using the LLMShapService
    
	# Store the diagnosis in the database

	# Return the diagnosis and attribution as JSON response
    pass
