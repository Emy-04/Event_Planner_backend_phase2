from flask import Blueprint, request, jsonify
from app.services.user_service import register_user, login_user

user_bp = Blueprint('user', __name__)

@user_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    response, status = register_user(data)
    return jsonify(response), status

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    response, status = login_user(data)
    return jsonify(response), status
