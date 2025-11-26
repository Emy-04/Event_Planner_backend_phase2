# app/services/event_service.py
from app.database import get_connection

# Create a new event
def create_event(user_id, data):
    title = data.get('title')
    date = data.get('date')
    time = data.get('time')
    location = data.get('location')
    description = data.get('description')

    if not title or not date or not time:
        return {"error": "Title, date, and time are required"}, 400

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO events (title, date, time, location, description, organizer_id)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """, (title, date, time, location, description, user_id))
        event_id = cur.fetchone()[0]

        # Add organizer as attendee
        cur.execute("""
            INSERT INTO event_attendees (event_id, user_id, role, status)
            VALUES (%s, %s, %s, %s)
        """, (event_id, user_id, 'organizer', 'Going'))

        conn.commit()
        cur.close()
        conn.close()
        return {"message": "Event created", "event_id": event_id}, 201
    except Exception as e:
        print("Error:", e)
        return {"error": "Database error"}, 500

# List events organized by user
def list_organized_events(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, date, time, location, description
        FROM events WHERE organizer_id=%s ORDER BY date, time
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    events = [{"id": r[0], "title": r[1], "date": str(r[2]), "time": str(r[3]),
               "location": r[4], "description": r[5]} for r in rows]
    return {"events": events}, 200

# List events the user is invited to
def list_invited_events(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT e.id, e.title, e.date, e.time, e.location, e.description, ea.role, ea.status
        FROM events e
        JOIN event_attendees ea ON e.id=ea.event_id
        WHERE ea.user_id=%s ORDER BY e.date, e.time
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    events = [{"id": r[0], "title": r[1], "date": str(r[2]), "time": str(r[3]),
               "location": r[4], "description": r[5], "role": r[6], "status": r[7]} for r in rows]
    return {"events": events}, 200

# Invite a user to an event
def invite_user(event_id, inviter_id, invitee_email):
    conn = get_connection()
    cur = conn.cursor()
    # check organizer
    cur.execute("SELECT organizer_id FROM events WHERE id=%s", (event_id,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close(); return {"error": "Event not found"}, 404
    if row[0] != inviter_id:
        cur.close(); conn.close(); return {"error": "Only organizer can invite"}, 403

    cur.execute("SELECT id FROM users WHERE email=%s", (invitee_email,))
    user = cur.fetchone()
    if not user:
        cur.close(); conn.close(); return {"error": "Invitee not found"}, 404
    invitee_id = user[0]

    try:
        cur.execute("""
            INSERT INTO event_attendees (event_id, user_id, role, status)
            VALUES (%s, %s, %s, %s)
        """, (event_id, invitee_id, 'attendee', 'Pending'))
        conn.commit()
        cur.close(); conn.close()
        return {"message": "User invited"}, 200
    except Exception as e:
        print("Error:", e)
        cur.close(); conn.close()
        return {"error": "Database error"}, 500

# Respond to an event (Going / Maybe / Not Going)
def respond_to_event(event_id, user_id, status):
    if status not in ['Going', 'Maybe', 'Not Going']:
        return {"error": "Invalid status"}, 400
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE event_attendees SET status=%s
        WHERE event_id=%s AND user_id=%s
    """, (status, event_id, user_id))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Response recorded"}, 200

# Get attendees for an event (organizer only)
def get_attendees(event_id, organizer_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT organizer_id FROM events WHERE id=%s", (event_id,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close(); return {"error": "Event not found"}, 404
    if row[0] != organizer_id:
        cur.close(); conn.close(); return {"error": "Only organizer can view attendees"}, 403

    cur.execute("""
        SELECT u.id, u.email, ea.role, ea.status
        FROM event_attendees ea
        JOIN users u ON ea.user_id=u.id
        WHERE ea.event_id=%s
    """, (event_id,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    attendees = [{"id": r[0], "email": r[1], "role": r[2], "status": r[3]} for r in rows]
    return {"attendees": attendees}, 200

# Delete event
def delete_event(event_id, organizer_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT organizer_id FROM events WHERE id=%s", (event_id,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close(); return {"error": "Event not found"}, 404
    if row[0] != organizer_id:
        cur.close(); conn.close(); return {"error": "Only organizer can delete"}, 403
    cur.execute("DELETE FROM events WHERE id=%s", (event_id,))
    conn.commit()
    cur.close(); conn.close()
    return {"message": "Event deleted"}, 200

# Search events
def search_events(user_id=None, keyword=None, date=None, role=None):
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT e.id, e.title, e.date, e.time, e.location, e.description FROM events e"
    clauses = []
    params = []

    if role and user_id:
        query += " JOIN event_attendees ea ON e.id=ea.event_id"
        clauses.append("ea.user_id=%s")
        params.append(user_id)
        if role.lower() == "organizer":
            clauses.append("ea.role='organizer'")
        elif role.lower() == "attendee":
            clauses.append("ea.role='attendee'")

    if keyword:
        clauses.append("(e.title ILIKE %s OR e.description ILIKE %s)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    if date:
        clauses.append("e.date=%s")
        params.append(date)

    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY e.date, e.time"

    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    cur.close(); conn.close()
    events = [{"id": r[0], "title": r[1], "date": str(r[2]), "time": str(r[3]),
               "location": r[4], "description": r[5]} for r in rows]
    return {"events": events}, 200
