"""The one shared database object. Models import it from here to avoid circular imports."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
