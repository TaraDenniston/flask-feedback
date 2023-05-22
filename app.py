from flask import Flask, redirect, render_template, flash, session, request
from keys import SECRET_KEY
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm, FeedbackForm
from models import db, connect_db, User, Feedback
from sqlalchemy.exc import IntegrityError

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

        try:
            new_user = User.register(username, password, email, first_name, last_name)
            session['username'] = new_user.username
            return redirect(f'/users/{username}')
        except IntegrityError:
            form.username.errors.append('Username taken - please choose another.')

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
    flash('You are now logged out.', 'info')
    return redirect('/login')

@app.route('/users/<username>')
def display_user(username):
    if 'username' not in session:
        flash('Please sign in first!', 'danger')
        return redirect('/login')
    user = User.query.get(username)
    feedback = user.feedback
    return render_template('users.html', user=user, feedback=feedback)

@app.route('/users/<username>/delete')
def delete_user(username):
    if 'username' not in session:
        flash('Please sign in first!', 'danger')
        return redirect('/login')
    user = User.query.get(username)
    session.pop('username')
    db.session.delete(user)
    db.session.commit()
    flash('Your account has been deleted.', 'danger')
    return redirect('/')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    if 'username' not in session:
        flash('Please sign in first!', 'danger')
        return redirect('/login')
    
    form = FeedbackForm()

    if form.validate_on_submit():
        # Get info for feedback from form
        title = form.title.data
        content = form.content.data

        # Create Feedback instance
        feedback = Feedback(title=title, content=content, username=username)

        # Add feedback to database
        db.session.add(feedback)
        db.session.commit()

        flash('Your feedback has been added.', "success")
        return redirect(f'/users/{username}')
    
    return render_template('add_feedback.html', form=form)

@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    if 'username' not in session:
        flash('Please sign in first!', 'danger')
        return redirect('/login')
    
    feedback = Feedback.query.get_or_404(feedback_id)

    form = FeedbackForm()
    form.title.data = feedback.title
    form.content.data = feedback.content

    if form.validate_on_submit():
        # Get info for feedback from form
        title = request.form.get('title')
        content = request.form.get('content')
        # content = form.content.data

        # Update Feedback instance
        new_feedback = Feedback.query.get_or_404(feedback_id)
        new_feedback.title = title
        new_feedback.content = content

        # Add feedback to database
        db.session.add(new_feedback)
        db.session.commit()

        username = feedback.user.username

        flash('Your feedback has been updated.', "success")
        return redirect(f'/users/{username}')
    
    return render_template('edit_feedback.html', form=form, feedback=feedback)


