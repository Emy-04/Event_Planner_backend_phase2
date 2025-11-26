from flask import Blueprint, request, jsonify
from app.services.event_service import (
    create_event, list_organized_events, list_invited_events,
    invite_user, respond_to_event, get_attendees, delete_event, search_events
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import get_connection

event_bp = Blueprint('event', __name__)

# Create event
@event_bp.route('/create', methods=['POST'])
@jwt_required()
def create():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    response, status = create_event(user_id, data)
    return jsonify(response), status

# Get organized events
@event_bp.route('/organized', methods=['GET'])
@jwt_required()
def organized():
    user_id = int(get_jwt_identity())
    response, status = list_organized_events(user_id)
    return jsonify(response['events']), status  # return array directly

# Get invited events
@event_bp.route('/invited', methods=['GET'])
@jwt_required()
def invited():
    user_id = int(get_jwt_identity())
    response, status = list_invited_events(user_id)
    return jsonify(response['events']), status  # return array directly

# Invite a user
@event_bp.route('/invite', methods=['POST'])
@jwt_required()
def invite():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    response, status = invite_user(data['event_id'], user_id, data['email'])
    return jsonify(response), status

# Respond to an event
@event_bp.route('/respond', methods=['POST'])
@jwt_required()
def respond():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    response, status = respond_to_event(data['event_id'], user_id, data['status'])
    return jsonify(response), status

# Get attendees of an event
@event_bp.route('/attendees/<int:event_id>', methods=['GET'])
@jwt_required()
def attendees(event_id):
    user_id = int(get_jwt_identity())
    response, status = get_attendees(event_id, user_id)
    return jsonify(response['attendees']), status  # return array directly

# Delete an event
@event_bp.route('/delete/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete(event_id):
    user_id = int(get_jwt_identity())
    response, status = delete_event(event_id, user_id)
    return jsonify(response), status

# Search events
@event_bp.route('/search', methods=['GET'])
@jwt_required()
def search():
    user_id = int(get_jwt_identity())
    keyword = request.args.get('keyword')
    date = request.args.get('date')
    role = request.args.get('role')
    response, status = search_events(user_id, keyword, date, role)
    return jsonify(response['events']), status  # return array directly

# Get all events
@event_bp.route('/all', methods=['GET'])
@jwt_required()
def all_events():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, date, time, location, description FROM events ORDER BY date, time")
    rows = cur.fetchall()
    cur.close(); conn.close()
    events = [{"id": r[0], "title": r[1], "date": str(r[2]), "time": str(r[3]), "location": r[4], "description": r[5]} for r in rows]
    return jsonify(events), 200  # return array

# Get event by ID
@event_bp.route('/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event(event_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, date, time, location, description FROM events WHERE id=%s", (event_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if not row:
        return jsonify({"error": "Event not found"}), 404
    event = {"id": row[0], "title": row[1], "date": str(row[2]), "time": str(row[3]), "location": row[4], "description": row[5]}
    return jsonify(event), 200
