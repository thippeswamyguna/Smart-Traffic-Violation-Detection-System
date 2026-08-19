import os
import base64
import uuid
import cv2
import numpy as np
from flask import Blueprint, request, jsonify, current_app
from models import db, Violation, Vehicle
from routes.auth import token_required
from services.detector import detect_objects
from services.ocr import extract_license_plate
from services.classifier import classify_violation

detect_bp = Blueprint('detect', __name__)

@detect_bp.route('/image', methods=['POST'])
@token_required
def detect_image(current_user):
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected for uploading.'}), 400

    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)

    # Save uploaded file
    base_name = os.path.splitext(file.filename)[0]
    filename = f"{uuid.uuid4().hex[:10]}_{base_name}.jpg"
    input_path = os.path.join(upload_folder, filename)

    # If uploaded file is webp or non-standard format, decode via cv2
    try:
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img_decoded = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if img_decoded is not None:
            cv2.imwrite(input_path, img_decoded)
        else:
            file.seek(0)
            file.save(input_path)
    except Exception:
        file.seek(0)
        file.save(input_path)

    # 1. Run Detector
    out_filename = f"annotated_{uuid.uuid4().hex[:10]}.jpg"
    output_path = os.path.join(upload_folder, out_filename)
    detections, annotated_web_path = detect_objects(input_path, output_path)

    # 2. Run OCR
    bbox = detections[0]['bbox'] if detections else None
    plate_number, ocr_confidence = extract_license_plate(input_path, bbox)

    # 3. Run Violation Classifier
    classification = classify_violation(detections, plate_number)

    # Calculate overall confidence
    det_conf = detections[0]['confidence'] if detections else 0.88
    final_conf = round((det_conf + ocr_confidence) / 2.0, 2)

    # Save to Violation Database
    new_violation = Violation(
        plate_number=plate_number,
        violation_type=classification['violation_type'],
        location=classification['location'],
        confidence_score=final_conf,
        image_path=annotated_web_path,
        status='pending',
        fine_amount=classification['fine_amount'],
        officer_notes=classification['officer_notes']
    )
    db.session.add(new_violation)
    db.session.commit()

    return jsonify({
        'message': 'Analysis completed successfully!',
        'violation_id': new_violation.id,
        'detections': detections,
        'plate_number': plate_number,
        'ocr_confidence': ocr_confidence,
        'violation_type': classification['violation_type'],
        'violation_title': classification['violation_title'],
        'fine_amount': classification['fine_amount'],
        'officer_notes': classification['officer_notes'],
        'location': classification['location'],
        'vehicle_info': classification['vehicle_info'],
        'annotated_image_path': annotated_web_path
    }), 200


@detect_bp.route('/live', methods=['POST'])
@token_required
def detect_live(current_user):
    data = request.get_json() or {}
    image_b64 = data.get('image')

    if not image_b64:
        return jsonify({'message': 'Base64 image parameter is missing'}), 400

    try:
        if ',' in image_b64:
            header, encoded = image_b64.split(',', 1)
        else:
            encoded = image_b64

        img_bytes = base64.b64decode(encoded)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({'detected': False, 'message': 'Invalid frame data'}), 400

        # Save temporary frame file for analyzer
        tmp_folder = current_app.config['UPLOAD_FOLDER']
        tmp_path = os.path.join(tmp_folder, "live_frame_tmp.jpg")
        cv2.imwrite(tmp_path, frame)

        # Run quick detection and OCR
        detections, _ = detect_objects(tmp_path)
        bbox = detections[0]['bbox'] if detections else None
        plate_number, _ = extract_license_plate(tmp_path, bbox)
        classification = classify_violation(detections, plate_number)

        # Remove tmp file
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass

        return jsonify({
            'detected': True,
            'detections': detections,
            'plate_number': plate_number,
            'violation_type': classification['violation_type'],
            'violation_title': classification['violation_title'],
            'fine_amount': classification['fine_amount'],
            'location': classification['location']
        }), 200

    except Exception as e:
        return jsonify({'detected': False, 'error': str(e)}), 500
