import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app, QUESTIONS_PER_PAGE
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format(
            'winst@localhost:5432', self.database_name
        )
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'hello?',
            'answer': 'world',
            'difficulty': 100,
            'category': 4
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after each test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        categories = Category.query.all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['categories']), len(categories))


    def test_get_paginated_questions(self):

        res = self.client().get('/questions')
        data = json.loads(res.data)
        
        questions = Question.query.all()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(len(data['questions']) <= QUESTIONS_PER_PAGE)
        self.assertEqual(data['total_questions'], len(questions)) 


    def test_get_questions_by_category(self):
        category_id = 1
        res = self.client().get(f'/questions?category={category_id}')
        data = json.loads(res.data)
        
        questions = Question.query.filter(Question.category == category_id).all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(len(data['questions']) <= QUESTIONS_PER_PAGE)
        self.assertEqual(data['total_questions'], len(questions)) 

    def test_404_get_questions_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

        res = self.client().get('/questions?category=1&page=1000')
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_404_get_questions_beyond_valid_categories(self):
        res = self.client().get('/questions?category=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

        res = self.client().get('/questions?category=1000&page=1')
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_new_question(self):
        count_before = Question.query.count()
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        count_after = Question.query.count()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(count_before+1, count_after)

    def test_422_create_new_question_missing_fields(self):
        count_before = Question.query.count()
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)
        count_after = Question.query.count()

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
        self.assertEqual(count_before, count_after)

    def test_delete_question(self):
        question_id = 5
        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)
 
        question = Question.query.filter(Question.id == question_id).one_or_none() 
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None) 

    def test_get_question_search_with_results(self):
        search_term = 'Which'
        res = self.client().post('/questions/search', json={'search': search_term})
        data = json.loads(res.data)

        num_results = Question.query.filter(Question.question.ilike(f"%{search_term}%")).count()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions']) 
        self.assertEqual(len(data['questions']), num_results) 
 
    def test_get_question_search_without_results(self):
        search_term = 'bitcoin'
        res = self.client().post('/questions/search', json={'search': search_term})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0) # make sure list of books is empty
        self.assertEqual(len(data['questions']), 0)  # also make sure total books is 0

    def test_get_quiz_question(self):
        req_body = {
            'previous_questions': [], 
            'quiz_category': {
                'type': 'All',
                'id': 0
            }
        }
        res = self.client().post('/quizzes', json=req_body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

    def test_get_quiz_no_repeat_questions(self):
        req_body = {
            'previous_questions': [13, 15], 
            'quiz_category': {
                'type': 'Geography',
                'id': 3
            }
        }
        res = self.client().post('/quizzes', json=req_body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question']['id'], 14)

    
    def test_get_quiz_no_questions_left(self):
        req_body = {
            'previous_questions': [13, 14, 15], 
            'quiz_category': {
                'type': 'Geography',
                'id': 3
            }
        }
        res = self.client().post('/quizzes', json=req_body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question'], None)

    def test_422_get_quiz_no_category(self):
        req_body = {
            'previous_questions': [13, 14, 15], 
        }
        res = self.client().post('/quizzes', json=req_body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()