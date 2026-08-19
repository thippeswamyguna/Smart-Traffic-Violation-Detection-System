from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='viewer')  # admin, officer, viewer
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def set_password(self, password):
        # Generate salt and hash the password
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
    def check_password(self, password):
        # Verify the password hash
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "email": self.email
        }


class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    owner_name = db.Column(db.String(100), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)  # car, motorcycle, truck, bus
    is_flagged = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "plate_number": self.plate_number,
            "owner_name": self.owner_name,
            "vehicle_type": self.vehicle_type,
            "is_flagged": self.is_flagged
        }


class Violation(db.Model):
    __tablename__ = 'violations'
    
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), nullable=False, index=True)
    violation_type = db.Column(db.String(50), nullable=False)  # no_helmet, no_seatbelt, red_light, wrong_way, illegal_parking
    location = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, confirmed, dismissed
    fine_amount = db.Column(db.Float, nullable=False)
    officer_notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "plate_number": self.plate_number,
            "violation_type": self.violation_type,
            "location": self.location,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "confidence_score": self.confidence_score,
            "image_path": self.image_path,
            "status": self.status,
            "fine_amount": self.fine_amount,
            "officer_notes": self.officer_notes
        }
