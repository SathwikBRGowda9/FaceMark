import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Enable CORS for face recognition API calls
CORS(app)

# configure the database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///attendance.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Admin credentials (hardcoded as per requirements)
app.config["ADMIN_USERNAME"] = "admin"
app.config["ADMIN_PASSWORD"] = "admin123"

# initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    from models import User, Attendance
    
    # Import routes
    from routes import *
    
    db.create_all()
    
    # Create a sample user for testing if none exist
    if not User.query.first():
        from werkzeug.security import generate_password_hash
        sample_user = User()
        sample_user.name = "John Doe"
        sample_user.password = generate_password_hash("password123")
        sample_user.face_encoding = "[]"  # Empty encoding for now
        sample_user.photo_url = "https://via.placeholder.com/150"
        
        db.session.add(sample_user)
        db.session.commit()
        logging.info("Sample user created: username=John Doe, password=password123")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
