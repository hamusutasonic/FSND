# Capstone Project - Volunteer App 

## About
This is a mock API for a Volunteer App services where Non-Profit / Charitable organisations 
can post volunteering events while users who are interested to volunteer for any of these events can sign up for the event. 

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Environment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virtual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by navigating to the directory where this repository is and run:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Use docker? 

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

## EndPoints

Endpoints are protected via OAuth2 Access Tokens. To access protected endpoints, pass in a valid token using the `Authorization: 'Bearer {ACCESS_TOKEN}'` header along with the API request. For public endpoints, no access token is required. 

#### GET /events
Get all events. 
- Permission: Public
- Request Body: None
- Response: 
    ```json
    {
        "success": true,
        "data": [{
            "name": "new event",
            "address": "London SW1A 0AA, UK",
            "description": "new volunteer event",
            "start_datetime": "2021-01-12T10:00:00",
            "end_datetime": "2021-01-12T12:00:00",
            "id": 1,
            "organisation": {
                "id": 1,
                "name": "my charity organisation"
            },
            "organisation_id": 1,
            "participants": [
                {
                    "id": 1,
                    "name": "Tom"
                },
                {
                    "id": 2,
                    "name": "Sally"
                }
            ],
        }, ...]
    }
    ```

#### GET /events/{event_id}
Get details of a specific event
- Permission: Public
- Request Body: None
- Response:
    ```json
    {
        "success": true,
        "data": {
            "name": "new event",
            "address": "London SW1A 0AA, UK",
            "description": "new volunteer event",
            "start_datetime": "2021-01-12T10:00:00",
            "end_datetime": "2021-01-12T12:00:00",
            "id": 1,
            "organisation": {
                "id": 1,
                "name": "my charity organisation"
            },
            "organisation_id": 1,
            "participants": [
                {
                    "id": 1,
                    "name": "Tom"
                },
                {
                    "id": 2,
                    "name": "Sally"
                }
            ],
        }
    }
    ```

#### POST /events 
Create a new event. 
- Permission: Organisation users only
- Request Body: 
    ```json
    {
        "name": "event name", //required
        "organisation_id": 1, //required
        "address": "event venue",
        "description": "event description",
        "start_datetime": "2021-01-12T10:00:00",
        "end_datetime": "2021-01-12T12:00:00",
    }
    ```
- Response:
    ```json
    {
        "success": true,
        "created": {
            "id": 7, //created event id
            "address": "event venue",
            "description": "event description",
            "start_datetime": "2021-01-12T10:00:00",
            "end_datetime": "2021-01-12T12:00:00",
            "name": "event name",
            "organisation": {
                "id": 1,
                "name": "my charity organisation"
            },
            "participants": []
        }
    }
    ```

#### PATCH /events/{event_id}
Update an existing event. Authenticated organisation users can only update their own events. 
- Permission: Organisation users only
- Request Body: 
    ```json
    {
        "organisation_id": 1, //required
        "name": "updated name",
        "address": "new venue",
        "description": "new description",
        "start_datetime": "2021-01-12T10:00:00",
        "end_datetime": "2021-01-12T12:00:00"
    }
    ```
- Response:
    ```json
    {
        "success": true,
        "updated": {
            "id": 1,
            "address": "new venue",
            "description": "new description",
            "start_datetime": "2021-01-12T10:00:00",
            "end_datetime": "2021-01-12T12:00:00",
            "name": "updated name",
            "organisation": {
                "id": 1,
                "name": "my charity organisation"
            },
            "participants": [
                {
                    "id": 1,
                    "name": "Tom"
                },
                {
                    "id": 2,
                    "name": "Sally"
                }
            ]
        }
    }
    ```

#### DELETE /events/{event_id}
Delete an event. Authenticated organisation users can only delete their own events. 
- Permission: Organisation users only
- Request Body: None
- Response:
    ```json
    {
        "success": true,
        "deleted": 7  //event_id of deleted event
    }
    ```


#### POST /events/{event_id}/participants
Add a new user to event participant list. Authenticated users can only add themselves to an event. 
- Permission: Volunteer users only
- Request Body: 
    ```json
    {
        "user_id": 1
    }
    ```
- Response:
    ```json
    {
        "success": true,
        "updated": {
            "event_id": 1, 
            "event_participants": [1, 2, 10] //updated event participant ids
        }
    }
    ```

#### DELETE /events/{event_id}/participants
Remove a user from event participant list. Authenticated users can only remove themselves from an event. 
- Permission: Volunteer users only
- Request Body: 
    ```json
    {
        "user_id": 1
    }
    ```
- Response:
    ```json
    {
        "success": true,
        "updated": {
            "event_id": 1, 
            "event_participants": [2, 10] //updated event participant ids
        }
    }
    ```

#### GET /organisations
Get general information for all organisations
- Permission: Public
- Request Body: None
- Response:
    ```json
    {
        "success": true,
        "data": [
            {
                "id": 1,
                "name": "my charity organisation",
                "description": "A new charity",
                "email_contact": "mycharity@test.com",
                "phone_contact": "1111111",
                "website": "http://mycharityorganisation.com"
            }, ...]
    }
    ```

#### GET /organisations/{organisation_id}
Get all information for a single organisation, included past and upcoming events.
- Permission: Public
- Request Body: None
- Response:
    ```json
    {
        "success": true,
        "data": {
            "id": 1,
            "name": "my charity organisation",
            "description": "A new charity",
            "email_contact": "mycharity@test.com",
            "phone_contact": "1111111",
            "website": "http://mycharityorganisation.com",
            "past_events": [{
                "id": 1,
                "name": "event name",
                "address": "event venue",
                "description": "event description",
                "start_datetime": "2020-01-12T10:00:00",
                "end_datetime": "2020-01-12T12:00:00",
                "participants": [
                    {
                        "id": 1,
                        "name": "Tom"
                    },
                    {
                        "id": 2,
                        "name": "Sally"
                    }
                ]
            }, ...],
            "upcoming_events": [{
                "id": 10,
                "name": "event name",
                "address": "event venue",
                "description": "event description",
                "start_datetime": "2022-01-12T10:00:00",
                "end_datetime": "2022-01-12T12:00:00",
                "participants": [
                    {
                        "id": 1,
                        "name": "Tom"
                    },
                    {
                        "id": 2,
                        "name": "Sally"
                    }
                ]
            }, ...],
        }
    }
    ```




## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```