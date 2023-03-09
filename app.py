from flask import Flask, redirect, render_template
from keys import SECRET_KEY
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm
from models import db, connect_db, User

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
    return redirect('/register')


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

        return redirect('/secret')

    return render_template('register.html', form=form)

    
