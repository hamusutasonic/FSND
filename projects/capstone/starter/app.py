import os
from datetime import datetime

from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from models import setup_db, User, Organisation, Event

app = Flask(__name__)
db = setup_db(app)
CORS(app) 


#----------------------------------------------------------------------------#
# Api Endpoints - Events
#----------------------------------------------------------------------------#
"""
Get all events
    - public
"""
@app.route('/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    return jsonify({
        'success': True, 
        'data': [e.format() for e in events]
    })

"""
Get specific event
    - public
"""
@app.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.query.get_or_404(event_id)
    return jsonify({
        'success': True, 
        'data': event.format()
    })

"""
Create an event
    - permitted to organisation
"""
@app.route('/events/create', methods=['POST'])
def create_event():
    body = request.get_json()
    try:
        event = Event(**body)
        event.insert()
        return jsonify({
            'success': True,
            'data': {
                'created': event.id
            }
        })
    except Exception as e:
        print(e)
        abort(422)


"""
Update an event
    - permitted to organisation
"""
@app.route('/events/<int:event_id>', methods=['PATCH'])
def update_event(event_id):
    pass


"""
Delete an event
    - permitted to organisation
"""
@app.route('/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    try: 
        event = Event.query.get_or_404(event_id)
        event.delete()

        return jsonify({
            'success': True,
            'data': {
                'deleted': event_id
            }
        })
    except Exception as e:
        print(e)
        abort(422)


#----------------------------------------------------------------------------#
# Api Endpoints - Organisations
#----------------------------------------------------------------------------#
"""
Get all organisations
    - public
"""
def f(organisation, return_events=False):
    data = organisation.format()
    past_events = []
    upcoming_events = []
    for event in organisation.events:
        if event.start_time <= datetime.now():
            past_events.append(event.format())
        else:
            upcoming_events.append(event.format())

    data[past_events] = past_events
    data[upcoming_events] = upcoming_events




@app.route('/organisations', methods=['GET'])
def get_organisations():
    organisations = Organisation.query.all()
    return jsonify({
        'success': True,
        'data': [org.format() for org in organisations]
    })


"""
Get specific organisation
    - public
"""
@app.route('/organisations/<int:organisation_id>', methods=['GET'])
def get_organisation(organisation_id):
    organisation = Organisation.query.get_or_404(organisation_id)

    data = organisation.format()
    past_events = []
    upcoming_events = []
    for event in organisation.events:
        if event.end_datetime <= datetime.now():
            past_events.append(event.format())
        else:
            upcoming_events.append(event.format())
    data['past_events'] = past_events
    data['upcoming_events'] = upcoming_events
    
    return jsonify({
        'success': True, 
        'data': data 
    })

#---------------------------------------
# Custom error handlers
#---------------------------------------
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized access"
    }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "access is forbidden"
    }), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)