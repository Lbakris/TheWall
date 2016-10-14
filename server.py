from flask import Flask, render_template, redirect, request,session,flash
from mySQLconnection import MySQLConnector
import re
#import random
app = Flask(__name__)
app.secret_key = "The coding dojo 101316"
mysql = MySQLConnector(app, 'mydb')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
@app.route('/')
def main():
    if 'current_user' in session:
        return redirect('/wall')
    return render_template('/index.html')

@app.route('/registration',methods=["post"])
def registration():
    form = request.form
    if validate_input(form):
        # add the user to the DB
        query = "INSERT INTO users (email, first_name, last_name, password) VALUES (:email, :first_name, :last_name, :password)"

        data = { 'email': form['email'],
        'first_name': form['first_name'],
        'last_name': form['last_name'],
        'password': form['password'] }
        session['current_user'] = mysql.query_db(query, data)
        flash('Registration Complete & Successful')
        return redirect('/wall')
    else:
        flash('There are errors with your registration, please fix')
        return redirect('/')

@app.route('/login',methods=["post"])
def login():
    password = request.form['password']
    query = "SELECT * FROM users WHERE email = :email"
    data = { 'email': request.form['email'] }
    result = mysql.query_db(query, data)
    if result:
        if password == result[0]['password']:
            session['current_user'] = result[0]['id']
            return redirect('/wall')
        else:
            flash('Passwords do not match!')
    else:
        flash('User does not exist!')
        return redirect('/')
    return render_template('index.html')



def validate_input(form):
    isValid = True
    # TODO: RESOLVE ISSUE WITH validate login

    if form['password'] != form['confirmpassword']:
        flash('Passwords do not match!')
        isValid = False

    if len(form['password']) < 8:
        flash('Password is not long enough!')
        isValid = False

    if not EMAIL_REGEX.match(form['email']):
        flash('Email is not valid!')
        isValid = False

    if len(form['first_name']) < 2:
        flash('First name must be longer than 2 characters')
        isValid = False

    if any(char.isdigit() for char in form['first_name']):
        flash('First name may not contain any numbers')
        isValid = False

    if len(form['last_name']) < 2:
        flash('Last name must be longer than 2 characters')
        isValid = False

    if any(char.isdigit() for char in form['last_name']):
        flash('Last name may not contain any numbers')
        isValid = False

    return isValid




@app.route('/wall')
def wall():
    query = "SELECT * FROM MESSAGES"
    messages = mysql.query_db(query)

    query = "SELECT * FROM COMMENTS"
    comments = mysql.query_db(query)

    return render_template('wall.html', messages = messages, comments = comments)


@app.route('/wall', methods=['POST'])
def createpost():
    form = request.form
    query = "INSERT INTO MESSAGES SET MESSAGE = :msg, USER_ID = 1"
    data = {'msg': form['message']}
    mysql.query_db(query, data)
    return redirect('/wall')

@app.route('/comment',methods= ['POST'])
def createComment():
    form = request.form
    query = "INSERT INTO COMMENTS SET COMMENT = :cmnt, USER_ID = :userID, messagesID = :msgID"
    data = {'cmnt': form['comment'], 'userID' : form ['user_id'], 'msgID' : form ['message_id']}
    mysql.query_db(query, data)
    return redirect('/wall')

@app.route('/logoff')
def logoff():
    del session['current_user']
    return redirect('/')

app.run(debug=True)
