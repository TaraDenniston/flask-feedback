from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)   


class User(db.Model):
    """Model for a single user"""

    __tablename__ = 'users'

    username = db.Column(db.String(20), primary_key=True, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'< User {self.username}: {self.first_name} {self.last_name}, {self.email} >'


    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        """Register user with hashed password and return user instance"""

        # create hashed version of password to store
        pw_hash = bcrypt.generate_password_hash(pwd).decode('utf8')

        user = cls(username=username, password=pw_hash, email=email, \
                   first_name=first_name, last_name=last_name)
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct
		   Return user if valid; else return False"""
	
        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
			# return user instance
            return u
        else:
            return False