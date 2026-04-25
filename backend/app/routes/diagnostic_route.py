from flask import Blueprint, jsonify, request, Response

bp = Blueprint("diagnostic", __name__)

@bp.route("/questions", methods=["get"])
def create_question():
    