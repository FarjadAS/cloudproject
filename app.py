from flask import Flask, render_template, redirect, url_for, request, flash
from extensions import db, login_manager
from flask_login import login_user, login_required, logout_user, UserMixin, current_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

from models import User, Task

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
        else:
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('User created!')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('todo'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/todo', methods=['GET', 'POST'])
@login_required
def todo():
    if request.method == 'POST':
        task = Task(content=request.form['task'], user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('todo.html', tasks=tasks)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    task = Task.query.get_or_404(id)
    if task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('todo'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
