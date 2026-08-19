import io
import csv
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, Response, current_app
from sqlalchemy import func
from models import db, Violation, Vehicle
from routes.auth import token_required, role_required

violations_bp = Blueprint('violations', __name__)

@violations_bp.route('/stats', methods=['GET'])
@token_required
def get_stats(current_user):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    total_today = Violation.query.filter(Violation.timestamp >= today_start).count()
    pending_count = Violation.query.filter_by(status='pending').count()
    total_fines = db.session.query(func.sum(Violation.fine_amount)).filter_by(status='confirmed').scalar() or 0.0
    active_cameras = 8  # Simulated active CCTV nodes

    # 7-day trend line data
    trend_labels = []
    trend_counts = []
    for i in range(6, -1, -1):
        day_date = datetime.utcnow().date() - timedelta(days=i)
        day_start = datetime.combine(day_date, datetime.min.time())
        day_end = datetime.combine(day_date, datetime.max.time())
        cnt = Violation.query.filter(Violation.timestamp >= day_start, Violation.timestamp <= day_end).count()
        trend_labels.append(day_date.strftime("%b %d"))
        trend_counts.append(cnt)

    # Violation types breakdown
    type_counts = db.session.query(Violation.violation_type, func.count(Violation.id)).group_by(Violation.violation_type).all()
    categories = {t: c for t, c in type_counts}

    # 5 most recent pending violations
    recent = Violation.query.order_by(Violation.timestamp.desc()).limit(5).all()

    return jsonify({
        'total_today': total_today,
        'pending_count': pending_count,
        'total_fines': round(total_fines, 2),
        'active_cameras': active_cameras,
        'trend': {
            'labels': trend_labels,
            'counts': trend_counts
        },
        'categories': categories,
        'recent': [v.to_dict() for v in recent]
    }), 200


@violations_bp.route('', methods=['GET'])
@token_required
def list_violations(current_user):
    search = request.args.get('search', '').strip()
    violation_type = request.args.get('type', '').strip()
    status = request.args.get('status', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Violation.query

    if search:
        query = query.filter((Violation.plate_number.ilike(f"%{search}%")) | (Violation.location.ilike(f"%{search}%")))
    if violation_type and violation_type != 'all':
        query = query.filter_by(violation_type=violation_type)
    if status and status != 'all':
        query = query.filter_by(status=status)
    if start_date:
        try:
            s_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Violation.timestamp >= s_dt)
        except ValueError:
            pass
    if end_date:
        try:
            e_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Violation.timestamp < e_dt)
        except ValueError:
            pass

    pagination = query.order_by(Violation.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'violations': [v.to_dict() for v in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': per_page
    }), 200


@violations_bp.route('/<int:violation_id>', methods=['GET'])
@token_required
def get_violation(current_user, violation_id):
    v = Violation.query.get_or_404(violation_id)
    v_dict = v.to_dict()
    vehicle = Vehicle.query.filter_by(plate_number=v.plate_number).first()
    if vehicle:
        v_dict['vehicle_info'] = vehicle.to_dict()
    return jsonify(v_dict), 200


@violations_bp.route('/<int:violation_id>', methods=['PUT'])
@token_required
@role_required(['admin', 'officer'])
def update_violation(current_user, violation_id):
    v = Violation.query.get_or_404(violation_id)
    data = request.get_json() or {}

    if 'status' in data:
        v.status = data['status']
    if 'officer_notes' in data:
        v.officer_notes = data['officer_notes']
    if 'fine_amount' in data:
        try:
            v.fine_amount = float(data['fine_amount'])
        except (ValueError, TypeError):
            pass

    db.session.commit()
    return jsonify({
        'message': 'Violation updated successfully!',
        'violation': v.to_dict()
    }), 200


@violations_bp.route('/<int:violation_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_violation(current_user, violation_id):
    v = Violation.query.get_or_404(violation_id)
    db.session.delete(v)
    db.session.commit()
    return jsonify({'message': f'Violation #{violation_id} deleted successfully.'}), 200


@violations_bp.route('/export', methods=['GET'])
@token_required
def export_violations_csv(current_user):
    search = request.args.get('search', '').strip()
    violation_type = request.args.get('type', '').strip()
    status = request.args.get('status', '').strip()

    query = Violation.query
    if search:
        query = query.filter((Violation.plate_number.ilike(f"%{search}%")) | (Violation.location.ilike(f"%{search}%")))
    if violation_type and violation_type != 'all':
        query = query.filter_by(violation_type=violation_type)
    if status and status != 'all':
        query = query.filter_by(status=status)

    items = query.order_by(Violation.timestamp.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Plate Number', 'Violation Type', 'Location', 'Timestamp', 'Confidence', 'Status', 'Fine Amount', 'Notes'])

    for item in items:
        writer.writerow([
            item.id,
            item.plate_number,
            item.violation_type,
            item.location,
            item.timestamp.strftime("%Y-%m-%d %H:%M:%S") if item.timestamp else '',
            f"{item.confidence_score * 100:.1f}%",
            item.status,
            f"${item.fine_amount:.2f}",
            item.officer_notes or ''
        ])

    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=sentri_violations_export.csv'
    return response


@violations_bp.route('/report', methods=['GET'])
@token_required
def get_report_data(current_user):
    # 24-hour heatmap matrix calculation (00:00 to 23:00)
    hourly = [0] * 24
    all_violations = Violation.query.all()
    for v in all_violations:
        if v.timestamp:
            hourly[v.timestamp.hour] += 1

    total_scanned = len(all_violations) + 140  # Simulated compliance ratio base
    total_violations = len(all_violations)
    compliance_rate = round(((total_scanned - total_violations) / total_scanned) * 100, 1)

    peak_hour = hourly.index(max(hourly)) if hourly else 14

    return jsonify({
        'hourly_heatmap': hourly,
        'compliance_rate': compliance_rate,
        'total_scanned': total_scanned,
        'total_violations': total_violations,
        'peak_hour': f"{peak_hour:02d}:00 - {peak_hour+1:02d}:00"
    }), 200
