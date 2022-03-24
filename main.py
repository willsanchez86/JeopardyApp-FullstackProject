from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, select, distinct
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import random
import os

# Generate secret key for Flask App configuration
# print(os.urandom(24))

##----------------------------AUTOMAP TO CREATE CLASSES FOR PREVIOUSLY CREATED TABLES ---------------------------##
# Base = automap_base()
#
# # engine, suppose it has two tables 'user' and 'address' set up
# engine = create_engine("sqlite:///jeopardy.db")
#
# # reflect the tables
# Base.prepare(engine, reflect=True)
#
# # mapped classes are now created with names by default
# # matching that of the table name.
# Questions = Base.classes.questions
# Categories = Base.classes.categories
#
# session = Session(engine)
#-------------------------------------------------------------------------------------------------------------------#
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///jeopardy.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app (app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String (100), unique=True, nullable=False)
    email = db.Column(db.String (100), unique=True, nullable=False)
    password = db.Column(db.String (100), nullable=False)
    games_won = db.Column(db.Integer, nullable=False)
    games_played = db.Column(db.Integer, nullable=False)
    total_winnings = db.Column(db.Integer, nullable=False)

# db.create_all()

## MUST ALSO CREATE MODELS FOR EXISTING TABLES WITHIN DB
class Category(db.Model):
    __tablename__ = "categories"
    category = db.Column(db.String (255), primary_key=True, nullable=False)
    num_questions = db.Column(db.Integer, nullable=False)


class Question(db.Model):
    __tablename__ = "questions"
    question_id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)



@app.route('/')
def home():
    return render_template('index.html')


def login():
    pass


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('/'))


@app.route('/new_game', methods=["GET", "POST"])
def new_game():
    # Join the tables to search for categories
    # cat_query = db.session.execute(
    #     select(Question.question, Question.answer, Category.category).
    #     join(Category, Question.category == Category.category).
    #     order_by(func.random()).
    #     group_by(Category.category).
    #     limit(6)
    # )
    # categories = [row.category for row in cat_query]
    #
    # game_dict = {item: [] for item in categories}
    #
    # # Search for questions/answers that match categories
    # for item in categories:
    #     question_query = db.session.execute(
    #         select(Question.question, Question.answer, Question.category).
    #         where(Question.category == item).
    #         limit(5)
    #     )
    #     game_dict[item] = [{'question': row.question, 'answer': row.answer} for row in question_query]

    return render_template('game.html')


#
#
@app.route('/start_game', methods=['GET', 'POST'])
def start_game():
    # Join the tables to search for categories
    cat_query = db.session.execute(
        select(Question.question, Question.answer, Category.category).
        join(Category, Question.category == Category.category).
        order_by(func.random()).
        group_by(Category.category).
        limit(6)
    )
    unique_categories = [row.category for row in cat_query]

    game_dict = {item: [] for item in unique_categories}

    # Search for questions/answers that match categories
    for item in unique_categories:
        question_query = db.session.execute(
            select(Question.question, Question.answer, Question.category).
            where(Question.category == item).
            limit(5)
        )
        game_dict[item] = [{'question': row.question, 'answer': row.answer} for row in question_query]

    # Creates a list containing 5 lists, each of 8 items, all set to 0
    w, h = 6, 6
    game_board = [[0 for x in range(w)] for y in range(h)]

    for i in range(len(unique_categories)):
        game_board[0][i] = unique_categories[i]

    # Add questions for each category
    for i in range(len(unique_categories)):
        question_query = db.session.execute(
            select(Question.question, Question.answer, Question.category).
            where(Question.category == unique_categories[i]).
            limit(5)
        )
        # Create separate list because returned query object is not iterable
        questions = [{'question': row.question, 'answer': row.answer} for row in question_query]
        for j in range(len(questions)):
            game_board[j+1][i] = questions[j]

    return jsonify(game_board)  # serialize and use JSON headers

if __name__ == "__main__":
    app.run (host='0.0.0.0', port=5000, debug=True)
