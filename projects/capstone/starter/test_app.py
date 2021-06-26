
import os
import json
import unittest
from unittest.mock import patch


from flask_sqlalchemy import SQLAlchemy
from flask import Flask

from app import app
from models import setup_db, User, Organisation, Event
from fixtures import reset_db_with_fixtures
# import auth

DB_HOST = os.getenv('DB_HOST', '0.0.0.0:5433')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')  
DB_NAME = os.getenv('DB_NAME', 'volunteer_app')  
DB_PATH = 'postgresql+psycopg2://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

db = setup_db(app,  database_path=DB_PATH)
client = app.test_client


class VolunteerAppTest(unittest.TestCase):
    def setUp(self):
        """reset test db with fixtures before each run"""
        reset_db_with_fixtures(db=db)

    def tearDown(self):
        """Executed after each test"""
        db.session.close()

    def test_get_events(self):
        res = client().get('/events')
        data = json.loads(res.data)

        events = Event.query.all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['data']), len(events))

    def test_get_event_success(self):
        res = client().get('/events/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['data']['id'], 1)

    def test_get_event_not_found(self):
        res = client().get('/events/100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_create_event_success(self, mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'auth0|60c58135612d820070a5f049',
            'permissions': ['create:event']
        }

        count_before = Event.query.count()
        res = client().post('/events', json={
            'name': 'new event',
            'organisation_id': 1
        })
        data = json.loads(res.data)
        event_id = data['created']['id']
        event = Event.query.get(event_id)
        count_after = Event.query.count()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(count_before+1, count_after)
        self.assertEqual(event.name, data['created']['name'])

    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_create_event_not_permitted_role(self, mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'auth0|60c58135612d820070a5f049',
            'permissions': ['update:event']
        }
        
        res = client().post('/events', json={
            'name': 'new event',
            'organisation_id': 1
        })
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['message'], 'unauthorized')

    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_create_event_not_permitted_wrong_id(self, mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'auth0|60c58135612d820070a5f049',
            'permissions': ['create:event']
        }
        
        res = client().post('/events', json={
            'name': 'new event',
            'organisation_id': 2
        })
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['message'], 'access is forbidden')


    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_create_event_org_not_found(self, mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'auth0|60c58135612d820070a5f049',
            'permissions': ['create:event']
        }
        res = client().post('/events', json={
            'name': 'new event',
            'organisation_id': 100
        })
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'unprocessable')

    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_update_event_success(self, mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'auth0|60c58135612d820070a5f049',
            'permissions': ['update:event']
        }
        
        #update name field
        event_id = 1
        res = client().patch(f'/events/{event_id}', json={
            'name': 'new name'
        })
        data = json.loads(res.data)
        event = Event.query.get(event_id)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(event.name, data['updated']['name'])
  
    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_update_event_not_found(self, mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'auth0|60c58135612d820070a5f049',
            'permissions': ['update:event']
        }

        event_id = 1000
        res = client().patch(f'/events/{event_id}', json={
            'name': 'new name'
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_update_event_not_permitted_role(self,  mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'auth0|60c58135612d820070a5f049',
            'permissions': []
        }

        event_id = 1
        res = client().patch(f'/events/{event_id}', json={
            'name': 'new name'
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unauthorized')
        

    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_update_event_not_permitted_wrong_id(self,  mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'ranomd_string',
            'permissions': ['update:event']
        }

        event_id = 1
        res = client().patch(f'/events/{event_id}', json={
            'name': 'new name'
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'access is forbidden')

    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_delete_event_success(self,  mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'auth0|60c58135612d820070a5f049',
            'permissions': ['delete:event']
        }

        event_id = 1
        res = client().delete(f'/events/{event_id}')
        data = json.loads(res.data)

        event = Event.query.get(event_id)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], event_id)
        self.assertEqual(event, None)       

    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_delete_event_not_found(self,  mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'auth0|60c58135612d820070a5f049',
            'permissions': ['delete:event']
        }

        event_id = 1000
        res = client().delete(f'/events/{event_id}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_delete_event_not_permitted_role(self,  mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'auth0|60c58135612d820070a5f049',
            'permissions': []
        }
        
        event_id = 1
        res = client().delete(f'/events/{event_id}')
        data = json.loads(res.data)

        event = Event.query.get(event_id)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unauthorized')
        self.assertTrue(event) #check event is not deleted    

    
    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_delete_event_not_permitted_wrong_id(self,  mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'some_id',
            'permissions': ['delete:event']
        }
        
        event_id = 1
        res = client().delete(f'/events/{event_id}')
        data = json.loads(res.data)

        event = Event.query.get(event_id)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'access is forbidden')
        self.assertTrue(event) #check event is not deleted    

    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_add_event_participant_success(self,  mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'auth0|60c58174612d820070a5f057',
            'permissions': ['add:event-participant']
        }
        
        user_id = 1
        event_id = 1

        event = Event.query.get(event_id)
        event.participants = []
        event.update()

        res = client().post(f'/events/{event_id}/participants', json={
            'user_id': user_id
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        event = Event.query.get(event_id)
        self.assertIn(user_id, [u.id for u in event.participants]) #check db
        self.assertIn(user_id, data['updated']['event_participants']) #check output


    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_add_event_participant_event_not_found(self,  mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'auth0|60c58174612d820070a5f057',
            'permissions': ['add:event-participant']
        }

        user_id = 1
        event_id = 1000
        res = client().post(f'/events/{event_id}/participants', json={
            'user_id': user_id
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_add_event_participant_not_permitted_role(self,  mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'auth0|60c58174612d820070a5f057',
            'permissions': []
        }
        
        user_id = 1
        event_id = 1

        event = Event.query.get(event_id)
        event.participants = []
        event.update()

        res = client().post(f'/events/{event_id}/participants', json={
            'user_id': user_id
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unauthorized')
        
        event = Event.query.get(event_id)
        self.assertEqual(event.participants, [])

    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_add_event_participant_not_permitted_role(self,  mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'some value',
            'permissions': ['add:event-participant']
        }
        
        user_id = 1
        event_id = 1

        event = Event.query.get(event_id)
        event.participants = []
        event.update()

        res = client().post(f'/events/{event_id}/participants', json={
            'user_id': user_id
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'access is forbidden')
        
        event = Event.query.get(event_id)
        self.assertEqual(event.participants, [])


    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_remove_event_participant_success(self,  mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'auth0|60c58174612d820070a5f057',
            'permissions': ['remove:event-participant']
        }
        
        user_id = 1
        event_id = 1

        user = User.query.get(user_id)
        event = Event.query.get(event_id)
        event.participants = [user]
        event.update()

        res = client().delete(f'/events/{event_id}/participants', json={
            'user_id': user_id
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        event = Event.query.get(event_id)
        self.assertEqual(event.participants, [])

    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_remove_event_participant_event_not_found(self,  mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'auth0|60c58174612d820070a5f057',
            'permissions': ['remove:event-participant']
        }

        user_id = 1
        event_id = 1000
        res = client().delete(f'/events/{event_id}/participants', json={
            'user_id': user_id
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_remove_event_participant_not_permitted_role(self,  mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'auth0|60c58174612d820070a5f057',
            'permissions': []
        }

        user_id = 1
        event_id = 1

        user = User.query.get(user_id)
        event = Event.query.get(event_id)
        event.participants = [user]
        event.update()

        res = client().delete(f'/events/{event_id}/participants', json={
            'user_id': user_id
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unauthorized')

        event = Event.query.get(event_id)
        self.assertEqual(len(event.participants), 1)
        

    @patch('auth.get_token_auth_header')
    @patch('auth.verify_decode_jwt')
    def test_remove_event_participant_not_permitted_wrong_id(self,  mock_verify_decode_jwt, mock_get_auth_header):
        mock_get_auth_header.return_value = 'some_token'
        mock_verify_decode_jwt.return_value = {
            'sub': 'wrong id',
            'permissions': ['remove:event-participant']
        }

        user_id = 1
        event_id = 1

        user = User.query.get(user_id)
        event = Event.query.get(event_id)
        event.participants = [user]
        event.update()

        res = client().delete(f'/events/{event_id}/participants', json={
            'user_id': user_id
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'access is forbidden')

        event = Event.query.get(event_id)
        self.assertEqual(len(event.participants), 1)


    def test_get_all_organisations(self):
        res = client().get('/organisations')
        data = json.loads(res.data)
        
        organisations = Organisation.query.all()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['data']), len(organisations))


    def test_get_organisation_success(self):
        org_id = 1
        res = client().get(f'/organisations/{org_id}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['data']['id'], org_id)
        self.assertIn('past_events', data['data'].keys())
        self.assertIn('upcoming_events', data['data'].keys())

    def test_get_organisation_not_found(self):
        org_id = 100
        res = client().get(f'/organisations/{org_id}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
      

if __name__ == "__main__":
    unittest.main()