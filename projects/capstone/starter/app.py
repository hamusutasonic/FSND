from auth import requires_auth
import os
from datetime import datetime

from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from models import setup_db, User, Organisation, Event
from auth import AuthError, requires_auth


app = Flask(__name__)
db = setup_db(app)
CORS(app) 


#----------------------------------------------------------------------------#
# Api Endpoints - Events
#----------------------------------------------------------------------------#
"""
Get all events
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
"""
@app.route('/events', methods=['POST'])
@requires_auth(permission='create:event')
def create_event(jwt_payload):
# def create_event():
    body = request.get_json()
    try:
        org_id = body.get('organisation_id', None)
        org = Organisation.query.get(org_id)
        if not org:
            abort(422)

        # nullable checking, foreign_id checking, datetime format 
        # checking all done at database layer
        event = Event(**body)
        event.insert()
        return jsonify({
            'success': True,
            'created': event.id
        })
    except Exception as e:
        print(e)
        abort(422)

"""
Update an event
"""
@app.route('/events/<int:event_id>', methods=['PATCH'])
@requires_auth(permission='update:event')
def update_event(jwt_payload, event_id):
    body = request.get_json()
    try:
        event = Event.query.get(event_id)
        if not event:
            raise
        
        # nullable checking, foreign_id checking, datetime format 
        # checking all done at database layer
        for key, value in body.items():
            setattr(event, key, value)

        event.update()
        return jsonify({
            'success': True,
            'data': event.format()
        })
    except Exception as e:
        print(e)
        abort(422)

"""
Delete an event
"""
@app.route('/events/<int:event_id>', methods=['DELETE'])
@requires_auth(permission='delete:event')
def delete_event(jwt_payload, event_id):
    try: 
        event = Event.query.get(event_id)
        if not event:
            raise 

        event.delete()

        return jsonify({
            'success': True,
            'deleted': event_id
        })
    except Exception as e:
        print(e)
        abort(422)

"""
Add user to event    
"""
@app.route('/events/<int:event_id>/participants', methods=['POST'])
@requires_auth(permission='add:event-participant')
def add_user_to_event(jwt_payload, event_id):
    body = request.get_json()

    try:
        user_id = body.get('user_id', None)
        user = User.query.get(user_id)
        if not user:
            abort(422) #should raise not permitted error?

        event = Event.query.get(event_id)
        if not event:
            raise 

        event.participants.append(user)
        event.update()

        return jsonify({
            'success': True,
            'data': [u.id for u in event.participants]
        })
    except Exception as e:
        print(e)
        abort(422)

"""
Remove user from event    
"""
@app.route('/events/<int:event_id>/participants', methods=['DELETE'])
@requires_auth(permission='remove:event-participant')
def remove_user_from_event(jwt_payload, event_id):
    body = request.get_json()

    try:
        user_id = body.get('user_id', None)
        user = User.query.get(user_id)
        if not user:
            abort(422) #should raise not permitted error?

        event = Event.query.get(event_id)
        if not event: 
            raise
        
        event.participants.remove(user)
        event.update()

        return jsonify({
            'success': True,
            'data': [u.id for u in event.participants]
        })
    except Exception as e:
        print(e)
        abort(422)

#----------------------------------------------------------------------------#
# Api Endpoints - Organisations
#----------------------------------------------------------------------------#
"""
Get all organisations
"""
@app.route('/organisations', methods=['GET'])
def get_organisations():
    organisations = Organisation.query.all()
    return jsonify({
        'success': True,
        'data': [org.format() for org in organisations]
    })


"""
Get specific organisation details
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

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['code']
    }), error.status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)