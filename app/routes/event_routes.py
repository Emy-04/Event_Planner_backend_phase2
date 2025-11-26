from flask import Blueprint, request, jsonify
from app.services.event_service import (
    create_event, list_organized_events, list_invited_events,
    invite_user, respond_to_event, get_attendees, delete_event, search_events
)
from flask_jwt_extended import jwt_required, get_jwt_identity

event_bp = Blueprint('event', __name__)

@event_bp.route('/create', methods=['POST'])
@jwt_required()
def create():
    user_id = int(get_jwt_identity())  # ✅ fixed
    data = request.get_json()
    response, status = create_event(user_id, data)
    return jsonify(response), status

@event_bp.route('/organized', methods=['GET'])
@jwt_required()
def organized():
    user_id = int(get_jwt_identity())
    response, status = list_organized_events(user_id)
    return jsonify(response), status

@event_bp.route('/invited', methods=['GET'])
@jwt_required()
def invited():
    user_id = int(get_jwt_identity())
    response, status = list_invited_events(user_id)
    return jsonify(response), status

@event_bp.route('/invite', methods=['POST'])
@jwt_required()
def invite():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    response, status = invite_user(data['event_id'], user_id, data['email'])
    return jsonify(response), status

@event_bp.route('/respond', methods=['POST'])
@jwt_required()
def respond():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    response, status = respond_to_event(data['event_id'], user_id, data['status'])
    return jsonify(response), status

@event_bp.route('/attendees/<int:event_id>', methods=['GET'])
@jwt_required()
def attendees(event_id):
    user_id = int(get_jwt_identity())
    response, status = get_attendees(event_id, user_id)
    return jsonify(response), status

@event_bp.route('/delete/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete(event_id):
    user_id = int(get_jwt_identity())
    response, status = delete_event(event_id, user_id)
    return jsonify(response), status

@event_bp.route('/search', methods=['GET'])
@jwt_required()
def search():
    user_id = int(get_jwt_identity())
    keyword = request.args.get('keyword')
    date = request.args.get('date')
    role = request.args.get('role')
    response, status = search_events(user_id, keyword, date, role)
    return jsonify(response), status
