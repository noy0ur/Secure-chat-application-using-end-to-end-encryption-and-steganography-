from flask import Blueprint, render_template, request, redirect, session
from database.db import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def login_page():
    return render_template('login.html')

@auth_bp.route('/register_page')
def register_page():
    return render_template('register.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    conn = get_db()
    conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()

    return redirect('/')

@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()

    if user:
        session['user_id'] = user['id']
        return redirect('/dashboard')

    return "Invalid Credentials"

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
