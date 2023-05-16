from flask import Flask, redirect, render_template, flash, session
from keys import SECRET_KEY
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm
from models import db, connect_db, User, Feedback

app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)
connect_db(app)

@app.route('/')
def redirect_reg():
    if 'username' not in session:
        return redirect('/register')
    username = session['username']
    return redirect(f'/users/{username}')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegisterForm()

    if form.validate_on_submit():
        # Use form data to register user
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = new_user.username

        return redirect(f'/users/{username}')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            return redirect(f'/users/{username}')
        else:
            form.username.errors = ['Inavlid username/password']

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('username')
    return redirect('/')

@app.route('/users/<username>')
def display_user(username):
    if 'username' not in session:
        flash('Please sign in first!')
        return redirect('/login')
    user = User.query.get(username)
    feedback = user.feedback
    return render_template('users.html', user=user, feedback=feedback)

@app.route('/users/<username>/delete')
def delete_user(username):
    if 'username' not in session:
        flash('Please sign in first!')
        return redirect('/login')
    user = User.query.get(username)
    session.pop('username')
    db.session.delete(user)
    db.session.commit()
    flash('Your account has been deleted.')
    return redirect('/')
