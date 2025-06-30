from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Create the instances of the extensions
db = SQLAlchemy()
bcrypt = Bcrypt()

# Import the models to make them accessible from the 'models' package
from .user import User
from .journey import Journey
from .step import Step