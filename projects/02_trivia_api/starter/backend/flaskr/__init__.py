import os
import random

from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  return questions[start:end]

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  db = setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resoruces={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  # Question: what kind of headers should i set?
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization') #to modify
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS') #to modify
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = {c.id: c.type for c in Category.query.all()}

    return jsonify({
      'success': True, 
      'categories': categories
    })
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    category_id = request.args.get('category', None, type=int)
    
    if category_id:
      selection = Question.query.filter(Question.category == category_id).all()
    else:
      selection = Question.query.all()
      
    questions = paginate_questions(request, selection)
    
    if len(questions) == 0:
      abort(404)  #invalid page or no questions 

    return jsonify({
      'success': True,
      'total_questions': len(selection),
      'questions': questions
    })

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    try:
      new_question = body.get('question', None)
      new_answer = body.get('answer', None)
      new_difficulty = body.get('difficulty', None)
      new_category = body.get('category', None)
      
      if not all([new_question, new_category, new_answer, new_difficulty]):
        abort(422)

      question = Question(
            question=new_question, 
            answer=new_answer, 
            difficulty=new_difficulty, 
            category=new_category
      )        
      question.insert()

      return jsonify({
        'success': True, 
        'created': question.id
      })
    except Exception as e: 
        print(e)
        abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    body = request.get_json()

    search_term = body.get('search', None)
    if not search_term:
      abort(422)
  
    selection = Question.query.filter(Question.question.ilike(f"%{search_term}%")).all()
    questions = paginate_questions(request, selection)

    return jsonify({
      'success': True, 
      'total_questions': len(selection),
      'questions': questions,
    })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
          abort(404)

      question.delete()

      return jsonify({
          'success': True, 
          'deleted': question_id, 
      })
    except Exception as e:
      print(e)  
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quiz_question():
    body = request.get_json()

    previous_questions = body.get('previous_questions', [])
    quiz_category = body.get('quiz_category', None)
    if not quiz_category:
      abort(422)

    category_id = quiz_category['id'] 
    if category_id:
      questions = Question.query.filter(Question.category == category_id, Question.id.notin_(previous_questions)).all()
    else:
      questions = Question.query.filter(Question.id.notin_(previous_questions)).all()

    return jsonify({
      'success': True,
      'question': random.choice(questions).format() if len(questions) else None
    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  #---------------------------------------
  # Define custom error handlers
  #---------------------------------------
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

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
    }), 400

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "method not allowed"
    }), 405


  return app

    
