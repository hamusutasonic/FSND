import React, { Component } from 'react';

import '../stylesheets/App.css';
import Question from './Question';
import Search from './Search';
import $ from 'jquery';

class QuestionView extends Component {
  constructor(){
    super();
    this.state = {
      questions: [],
      page: 1,
      totalQuestions: 0,
      categories: {},
      currentCategory: null,
    }
  }

  componentDidMount() {
    this.getCategories();
    this.getQuestions();
  }

  getCategories = () => {
    $.ajax({
      url: `/categories`, //TODO: update request URL
      type: "GET",
      success: (result) => {
        this.setState({
          categories: result.categories
        })
        return;
      },
      error: (error) => {
        alert('Unable to load questions. Please try your request again')
        return;
      }
    })
  }

  getQuestions = () => {
    let category_id = this.state.currentCategory;
    let page = this.state.page;
    $.ajax({
      url: `/questions?page=${page}&category=${category_id}`, //TODO: update request URL
      type: "GET",
      success: (result) => {
        this.setState({
          questions: result.questions,
          totalQuestions: result.total_questions, 
        })
        return;
      },
      error: (error) => {
        alert('Unable to load questions. Please try your request again')
        return;
      }
    })
  }

  selectPage(num) {
    this.setState({page: num}, () => this.getQuestions());
  }

  selectCategory(id) {
    this.setState({
      currentCategory: id, 
      page: 1  //reset page when new category is seleted
    }, () => this.getQuestions());
  }

  createPagination(){
    let pageNumbers = [];
    let maxPage = Math.ceil(this.state.totalQuestions / 10)
    for (let i = 1; i <= maxPage; i++) {
      pageNumbers.push(
        <span
          key={i}
          className={`page-num ${i === this.state.page ? 'active' : ''} clickable`}
          onClick={() => {this.selectPage(i)}}>{i}
        </span>)
    }
    return pageNumbers;
  }

  // getByCategory= (id) => {
  //   $.ajax({
  //     // url: `/categories/${id}/questions`, //TODO: update request URL
  //     url: `/questions?category=${id}&page=${this.state.page}`, //TODO: update request URL
  //     type: "GET",
  //     success: (result) => {
  //       this.setState({
  //         questions: result.questions,
  //         totalQuestions: result.total_questions,
  //         currentCategory: result.current_category })
  //       return;
  //     },
  //     error: (error) => {
  //       alert('Unable to load questions. Please try your request again')
  //       return;
  //     }
  //   })
  // }

  submitSearch = (searchTerm) => {
    $.ajax({
      url: `/questions/search`, //TODO: update request URL
      type: "POST",
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify({search: searchTerm}),
      xhrFields: {
        withCredentials: true
      },
      crossDomain: true,
      success: (result) => {
        this.setState({
          questions: result.questions,
          totalQuestions: result.total_questions,
          currentCategory: result.current_category })
        return;
      },
      error: (error) => {
        alert('Unable to load questions. Please try your request again')
        return;
      }
    })
  }

  questionAction = (id) => (action) => {
    if(action === 'DELETE') {
      if(window.confirm('are you sure you want to delete the question?')) {
        $.ajax({
          url: `/questions/${id}`, //TODO: update request URL
          type: "DELETE",
          success: (result) => {
            this.getQuestions();
          },
          error: (error) => {
            alert('Unable to load questions. Please try your request again')
            return;
          }
        })
      }
    }
  }

  render() {
    return (
      <div className="question-view">
        <div className="categories-list">
          <h2 className='clickable' onClick={() => {this.selectCategory(null)}}>Categories</h2>
          <ul>
            {Object.keys(this.state.categories).map((id, ) => (
              <li className={`${id == this.state.currentCategory ? 'highlight' : ''} clickable`}
                  key={id} 
                  onClick={() => {this.selectCategory(id)}}>
                <img className="category" src={`${this.state.categories[id].toString().toLowerCase()}.svg`}/>
                {this.state.categories[id]}
                
              </li>
            ))}
          </ul>
          <Search submitSearch={this.submitSearch}/>
        </div>
        <div className="questions-list">
          <h2>Questions</h2>
          {this.state.questions.map((q, ind) => (
            <Question
              key={q.id}
              question={q.question}
              answer={q.answer}
              category={this.state.categories[q.category]} 
              difficulty={q.difficulty}
              questionAction={this.questionAction(q.id)}
            />
          ))}
          <div className="pagination-menu">
            {this.createPagination()}
          </div>
        </div>

      </div>
    );
  }
}

export default QuestionView;
