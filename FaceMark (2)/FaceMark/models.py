from app import db
from datetime import datetime
import uuid

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)  # Add email for notifications
    password = db.Column(db.String(256), nullable=False)
    face_encoding = db.Column(db.Text)  # JSON string of face encoding
    photo_url = db.Column(db.String(500))
    provider = db.Column(db.String(50), default='local')  # 'local', 'google', 'github'
    provider_id = db.Column(db.String(100))  # ID from social provider
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))  # Link to user
    date = db.Column(db.String(20), nullable=False)  # YYYY-MM-DD format
    time = db.Column(db.String(20), nullable=False)  # HH:MM:SS format
    email_sent = db.Column(db.Boolean, default=False)  # Track if confirmation email was sent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('attendances', lazy=True))

class NotificationSettings(db.Model):
    __tablename__ = 'notification_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    attendance_confirmations = db.Column(db.Boolean, default=True)
    absence_alerts = db.Column(db.Boolean, default=True)
    cutoff_time = db.Column(db.String(10), default="10:00")  # Format: "HH:MM"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
