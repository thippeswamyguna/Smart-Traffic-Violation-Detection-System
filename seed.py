import os
import cv2
import numpy as np
from datetime import datetime, timedelta
import random
from app import create_app
from models import db, User, Vehicle, Violation

def create_seed_image(path, label, plate):
    """
    Generates a dark-themed visual placeholder image for seeded violations.
    Draws vehicle boxes, license plates, and status text.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Create canvas
    img = np.zeros((360, 640, 3), dtype=np.uint8)
    
    # Dark blue-gray background (#0A0F1E -> RGB 10, 15, 30 -> BGR 30, 15, 10)
    img[:] = (30, 15, 10)
    
    # Draw grid patterns
    for i in range(0, 640, 40):
        cv2.line(img, (i, 0), (i, 360), (40, 25, 20), 1)
    for j in range(0, 360, 40):
        cv2.line(img, (0, j), (640, j), (40, 25, 20), 1)
        
    # Draw radar concentric circles
    cv2.circle(img, (320, 180), 100, (80, 50, 30), 1)
    cv2.circle(img, (320, 180), 150, (80, 50, 30), 1)
    
    # Draw vehicle bbox (Cyan #00D4FF)
    cv2.rectangle(img, (160, 80), (480, 280), (255, 212, 0), 2)
    cv2.putText(img, "VEHICLE DETECTED", (170, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 212, 0), 1)
    
    # Draw license plate bbox (Yellow)
    cv2.rectangle(img, (260, 220), (380, 260), (0, 255, 255), 2)
    cv2.putText(img, plate, (270, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
    cv2.putText(img, "LP AREA", (280, 245), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
    
    # Violation details block
    color_map = {
        "no_helmet": (0, 165, 255),      # Orange
        "no_seatbelt": (0, 165, 255),    # Orange
        "red_light": (0, 0, 255),         # Red
        "wrong_way": (0, 0, 255),         # Red
        "illegal_parking": (0, 255, 255)  # Yellow
    }
    color = color_map.get(label, (255, 255, 255))
    
    # Add a top header bar for violation
    cv2.rectangle(img, (0, 0), (640, 45), color, -1)
    cv2.putText(img, f"TRAFFIC VIOLATION: {label.upper().replace('_', ' ')}", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Overlay glassmorphic card for details
    cv2.rectangle(img, (20, 290), (620, 350), (45, 30, 25), -1)
    cv2.putText(img, f"Plate: {plate} | Loc: C1 Intersection Sector 4", (35, 315),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
    cv2.putText(img, f"Confidence: {random.uniform(85, 98):.2f}% | Fine: ${random.randint(50, 250)}", (35, 338),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
                
    cv2.imwrite(path, img)


def run_seeder():
    app = create_app()
    with app.app_context():
        print("Recreating database tables...")
        db.drop_all()
        db.create_all()
        
        # 1. Seed Users
        print("Seeding users...")
        users = [
            ("admin", "adminpassword", "admin", "admin@traffic.gov"),
            ("officer", "officerpassword", "officer", "officer@traffic.gov"),
            ("viewer", "viewerpassword", "viewer", "viewer@traffic.gov")
        ]
        for username, password, role, email in users:
            user = User(username=username, role=role, email=email)
            user.set_password(password)
            db.session.add(user)
            
        # 2. Seed Vehicles
        print("Seeding vehicles...")
        vehicles_data = [
            ("DL-01-CA-1234", "Rajesh Kumar", "car", False),
            ("KA-03-MM-5678", "Amit Patel", "motorcycle", True),
            ("MH-12-RS-9012", "Vikram Singh", "car", False),
            ("HR-26-AB-3456", "Priya Sharma", "car", False),
            ("UP-16-CD-7890", "Rahul Verma", "truck", True),
            ("GJ-01-EF-2345", "Sunita Mehta", "car", False),
            ("KL-07-GH-6789", "George Joseph", "motorcycle", False),
            ("TN-02-JK-1230", "Karthik R", "bus", False),
            ("AP-09-LM-4567", "Lakshmi Prasad", "car", False),
            ("TS-10-NP-8901", "Venkatesh Rao", "motorcycle", True)
        ]
        for plate, owner, v_type, flagged in vehicles_data:
            vehicle = Vehicle(plate_number=plate, owner_name=owner, vehicle_type=v_type, is_flagged=flagged)
            db.session.add(vehicle)
            
        # Commit users and vehicles
        db.session.commit()
        
        # 3. Seed Violations
        print("Seeding violations...")
        violation_types = [
            ("no_helmet", 100.0, ["KA-03-MM-5678", "KL-07-GH-6789", "TS-10-NP-8901"]),
            ("no_seatbelt", 150.0, ["DL-01-CA-1234", "MH-12-RS-9012", "HR-26-AB-3456"]),
            ("red_light", 200.0, ["GJ-01-EF-2345", "UP-16-CD-7890", "DL-01-CA-1234"]),
            ("wrong_way", 250.0, ["TN-02-JK-1230", "AP-09-LM-4567"]),
            ("illegal_parking", 50.0, ["MH-12-RS-9012", "HR-26-AB-3456"])
        ]
        
        locations = [
            "Intersection Sector 4", "Main St & 5th Ave", "Highway Km 12",
            "Central Expressway", "No Parking Zone B", "Downtown Crossing"
        ]
        
        statuses = ["pending", "confirmed", "dismissed"]
        
        # We need 20 violations distributed over the past 14 days
        upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)
            
        for i in range(20):
            # Select random type
            v_type, fine, plates_pool = random.choice(violation_types)
            plate = random.choice(plates_pool)
            location = random.choice(locations)
            
            # Timestamp distributed in last 10 days
            days_ago = random.randint(0, 9)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            timestamp = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            # Status: slightly weighted towards pending and confirmed
            status = random.choices(statuses, weights=[0.5, 0.4, 0.1])[0]
            
            confidence = round(random.uniform(0.82, 0.98), 2)
            
            # Generate visual image
            image_name = f"seed_{i+1}.jpg"
            image_file_path = os.path.join(upload_folder, image_name)
            create_seed_image(image_file_path, v_type, plate)
            
            web_image_path = f"/static/uploads/{image_name}"
            
            notes_templates = {
                "no_helmet": "Rider detected on motorcycle without safety helmet.",
                "no_seatbelt": "Driver cabin analysis shows shoulder seatbelt unbuckled.",
                "red_light": "Vehicle passed pedestrian lane while traffic signal was RED.",
                "wrong_way": "Vehicle moving in opposite direction on one-way traffic path.",
                "illegal_parking": "Vehicle parked in designated tow-away lane zone."
            }
            
            violation = Violation(
                plate_number=plate,
                violation_type=v_type,
                location=location,
                timestamp=timestamp,
                confidence_score=confidence,
                image_path=web_image_path,
                status=status,
                fine_amount=fine,
                officer_notes=notes_templates[v_type]
            )
            db.session.add(violation)
            
        db.session.commit()
        print("Database seeding completed successfully!")

if __name__ == "__main__":
    run_seeder()
