# save this as app.py
from turtle import pos
from flask import Flask, redirect, render_template, request, session, url_for, flash
import re
from db import db_connection
from services.funtion import *

app = Flask(__name__)
app.secret_key = '1'


@app.route("/")
def index():
    forum = getAllPosts()
    return render_template('index.html', forum=forum)


@app.route('/forum/')
def title():
    conn = db_connection()
    return render_template('forum.html')


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        conn = db_connection()
        cur = conn.cursor()
        sql = """
            SELECT id, email, name, age, user_password
            FROM users
            WHERE name = '%s' AND user_password = '%s'
        """ % (username, password)
        cur.execute(sql)
        user = cur.fetchone()
        error = ''
        if user is None:
            error = 'Invalid email address or password!!'
        else:
            session.clear()
            # Ini sebenernya nge return data session, jadi tinggal di ambil make session.get('')
            session['id'] = user[0]
            session['name'] = user[2]
            return redirect(url_for('index'))

        flash(error)
        cur.close()
        conn.close()

    return render_template('login.html')


@app.route('/logout')
def logout():
    """ function to do logout """
    session.clear()  # clear all sessions
    return redirect(url_for('index'))


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        age = request.form['age']
        conn = db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE name = %s', (username))
        account = cur.fetchall()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cur.execute('INSERT INTO users (name,user_password,email, age) VALUES ( %s, %s,%s, %s)',
                        (username, password, email, age))
            conn.commit()
            cur.close()
            conn.close()
            msg = 'You have successfully registered!'
            flash(msg)
            return redirect(url_for('login'))
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('signup.html', msg=msg)


@app.route('/CreateThread', methods=['POST', 'GET'])
def create():
    if not session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        id = session.get('id')
        username = session.get('name')
        conn = db_connection()
        cur = conn.cursor()

        sql = "INSERT INTO posts (title,body,users_id,username) VALUES ('%s', '%s','%s','%s') " % (
            title, body, id, username)

        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('create.html')


@app.route('/signup/TermOfService')
def tos():
    msg = ''
    db = db_connection()
    cursor = db.cursor()
    sql = "SELECT tos FROM tos"
    cursor.execute(sql)
    text = cursor.fetchone()
    if text is None:
        msg1 = 'Term of Service not yet made'
        return msg1
    else:
        msg1 = 'Hello'
        return render_template('TermOfService.html', msg1=msg1, text=text)
    return render_template('signup.html', msg1=msg1, text=text)


@app.route('/forum/<int:id>/', methods=['GET'])
def read(id):  # id is post_id
    conn = db_connection()
    cur = conn.cursor()
    cur1 = conn.cursor()
    sql = """ 
        SELECT p.title, p.body, usr.name
        FROM posts p
        JOIN users usr 
        ON usr.id = p.users_id
        WHERE p.id = %s
        """ % id
    comment = """ 
        SELECT c.username, c.body
        FROM comments c
        LEFT JOIN posts p
        ON p.id = c.FK_post_id
        WHERE p.id = %s
        """ % id
    cur.execute(sql)
    post = cur.fetchone()
    cur1.execute(comment)
    comments = cur1.fetchall()
    cur.close()
    conn.close()
    # dont forget to pass id lol
    return render_template('detail.html', id=id, post=post, comments=comments)


@app.route('/forum/<int:id>/comment/', methods=['POST','GET'])
def comment(id): # id is post_id
    if not session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        body = request.form['body']
        user_id = session.get('id')
        username = session.get('name')
        conn = db_connection()
        cur = conn.cursor()
        sql = "INSERT INTO comments (body,FK_post_id,FK_user_id,username) VALUES ('%s', '%s','%s','%s') " % (body,id,user_id,username)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('read', id=id))
    return render_template('comment.html', id=id)


@app.route('/forum/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    if not session:
        return redirect(url_for('login'))
    conn = db_connection()
    cur = conn.cursor()
    sql = 'DELETE FROM posts WHERE id = %s' % id
    cur.execute(sql)
    cur.close()
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


# # # # # # #  CATEGORY SECTION # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@app.route('/category')
def category():
    return render_template('category/index.html')


@app.route('/category/introduction')
def intro():
    conn = db_connection()
    cur = conn.cursor()
    sql = "SELECT users_id, title, body, id FROM introduction"
    cur.execute(sql)
    intro = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('category/introduction/introduction.html', intro=intro)


@app.route('/category/introduction/create', methods=['POST', 'GET'])
def create_intro():
    if not session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        id = session.get('id')
        username = session.get('name')
        conn = db_connection()
        cur = conn.cursor()

        sql = "INSERT INTO introduction (title,body,users_id) VALUES ('%s', '%s','%s') " % (
            title, body, id)

        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('intro'))
    return render_template('category/introduction/create.html')


@app.route('/category/introduction/<title>/<int:id>')
def view_intro(title, id):
    conn = db_connection()
    cur = conn.cursor()
    sql = """SELECT p.body, p.title FROM introduction p 
        WHERE p.id = '%s' AND p.title = '%s' """ % (id, title)
    cur.execute(sql)
    post = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('category/introduction/view.html', post=post)


@app.route('/category/gtc')
def gtc():
    return render_template('category/gtc.html')

########################### EDIT PROFILE ####################################################################################


@app.route('/profile')
def profile():
    id = session.get('id')
    db = db_connection()
    if not session.get('id'):
        return print('no id lol')
    cur = db.cursor()
    sql = "SELECT `id`, `name`, `user_password`, `age`, `email` FROM `users` WHERE id =  %d " % (int(id)) 
    cur.execute(sql)
    profile = cur.fetchone()
    cur.close()
    db.close()
    return render_template('profile/profile_view.html', profile=profile, id=id)

@app.route('/profile/edit', methods=['POST','GET'])
def profile_edit():
    id = session.get('id')
    db = db_connection()
    if not session.get('id'):
        return print('no id lol')
    cur = db.cursor()
    sql = "SELECT `id`, `name`, `user_password`, `age`, `email` FROM `users` WHERE id =  %d " % (int(id)) 
    cur.execute(sql)
    profile = cur.fetchone()
    cur.close()
    db.close()
    if request.method == 'POST':
        id = session.get('id')
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        age = request.form['age']
        params = (username,password,age,email,id)
        db = db_connection()
        cur = db.cursor()
        sql = "UPDATE users SET name = '%s', user_password = '%s', age = '%s', email = '%s' WHERE id = %s " % params
        cur.execute(sql)
        db.commit()
        cur.close()
        db.close()
        return redirect(url_for('profile'))
    return render_template('profile/edit.html', profile=profile)
    