from flask import render_template, request, jsonify, session, redirect, url_for, flash, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db
from models import User, Attendance, NotificationSettings
from face_recognition_utils import recognize_face_from_image
from email_service import email_service
from datetime import datetime, date, time
import json
import csv
import io
import base64
import logging
import threading

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        
        if not name or not password:
            flash('Please enter both name and password', 'error')
            return render_template('student_login.html')
        
        user = User.query.filter_by(name=name).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_type'] = 'student'
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('student_login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['user_type'] = 'admin'
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'error')
    
    return render_template('admin_login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        photo_url = request.form.get('photo_url', 'https://via.placeholder.com/150')
        
        if not name or not password:
            flash('Please enter both name and password', 'error')
            return render_template('register.html')
        
        # Get email if provided
        email = request.form.get('email', '').strip()
        
        # Check if user already exists
        existing_user = User.query.filter_by(name=name).first()
        if existing_user:
            flash('User already exists', 'error')
            return render_template('register.html')
        
        # Create new user
        new_user = User()
        new_user.name = name
        new_user.email = email if email else None
        new_user.password = generate_password_hash(password)
        new_user.face_encoding = "[]"  # Will be updated when face is captured
        new_user.photo_url = photo_url
        new_user.provider = 'local'
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('student_login'))
    
    return render_template('register.html')

@app.route('/student_dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'student':
        return redirect(url_for('student_login'))
    
    user = User.query.get(session['user_id'])
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get today's attendance for this user
    today_attendance = Attendance.query.filter_by(name=user.name, date=today).all()
    
    # Get stats for today (all users)
    all_today_attendance = Attendance.query.filter_by(date=today).all()
    unique_present_today = len(set(att.name for att in all_today_attendance))
    total_users = User.query.count()
    absent_today = total_users - unique_present_today
    
    return render_template('student_dashboard.html', 
                         user=user, 
                         today_attendance=today_attendance,
                         present_today=unique_present_today,
                         absent_today=absent_today)

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    return render_template('admin_dashboard.html')

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not logged in'}), 401
        
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'success': False, 'message': 'No image provided'}), 400
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        today = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # Check if attendance already marked today
        existing_attendance = Attendance.query.filter_by(name=user.name, date=today).first()
        if existing_attendance:
            return jsonify({
                'success': False, 
                'message': 'Attendance already marked for today',
                'name': user.name,
                'date': today,
                'time': existing_attendance.time
            })
        
        # For now, we'll mark attendance without face recognition
        # In a production system, you would implement proper face recognition here
        new_attendance = Attendance()
        new_attendance.name = user.name
        new_attendance.user_id = user.id
        new_attendance.date = today
        new_attendance.time = current_time
        new_attendance.email_sent = False
        
        db.session.add(new_attendance)
        db.session.commit()
        
        # Send email notification in background if enabled and user has email
        def send_email_async():
            try:
                settings = NotificationSettings.query.first()
                if settings and settings.attendance_confirmations and user.email:
                    timestamp = datetime.now()
                    success, message = email_service.send_attendance_confirmation(
                        user.email, user.name, timestamp
                    )
                    if success:
                        new_attendance.email_sent = True
                        db.session.commit()
                        logging.info(f"Attendance confirmation sent to {user.email}")
                    else:
                        logging.error(f"Failed to send email: {message}")
            except Exception as e:
                logging.error(f"Email sending error: {e}")
        
        # Send email in background thread
        email_thread = threading.Thread(target=send_email_async)
        email_thread.daemon = True
        email_thread.start()
        
        # Get updated stats
        all_today_attendance = Attendance.query.filter_by(date=today).all()
        unique_present_today = len(set(att.name for att in all_today_attendance))
        total_users = User.query.count()
        absent_today = total_users - unique_present_today
        
        return jsonify({
            'success': True,
            'message': 'Attendance marked successfully',
            'name': user.name,
            'date': today,
            'time': current_time,
            'photo_url': user.photo_url,
            'present_today': unique_present_today,
            'absent_today': absent_today
        })
        
    except Exception as e:
        logging.error(f"Error marking attendance: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/get_attendance_today')
def get_attendance_today():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    user = User.query.get(session['user_id'])
    today = datetime.now().strftime('%Y-%m-%d')
    
    attendance_records = Attendance.query.filter_by(name=user.name, date=today).all()
    
    records = []
    for record in attendance_records:
        records.append({
            'id': record.id,
            'name': record.name,
            'date': record.date,
            'time': record.time
        })
    
    return jsonify({'success': True, 'records': records})

@app.route('/get_all_attendance')
def get_all_attendance():
    if not session.get('admin'):
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    date_filter = request.args.get('date')
    name_filter = request.args.get('name')
    
    query = Attendance.query
    
    if date_filter:
        query = query.filter_by(date=date_filter)
    
    if name_filter:
        query = query.filter_by(name=name_filter)
    
    attendance_records = query.order_by(Attendance.created_at.desc()).all()
    
    records = []
    for record in attendance_records:
        records.append({
            'id': record.id,
            'name': record.name,
            'date': record.date,
            'time': record.time
        })
    
    return jsonify({'success': True, 'records': records})

@app.route('/get_stats')
def get_stats():
    if not session.get('admin'):
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # Get attendance for the specific date
    attendance_records = Attendance.query.filter_by(date=date).all()
    unique_present = len(set(att.name for att in attendance_records))
    total_users = User.query.count()
    absent = total_users - unique_present
    
    return jsonify({
        'success': True,
        'date': date,
        'present': unique_present,
        'absent': absent,
        'total': total_users
    })

@app.route('/export_attendance')
def export_attendance():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    date_filter = request.args.get('date')
    
    query = Attendance.query
    if date_filter:
        query = query.filter_by(date=date_filter)
    
    attendance_records = query.order_by(Attendance.created_at.desc()).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Name', 'Date', 'Time'])
    
    # Write data
    for record in attendance_records:
        writer.writerow([record.name, record.date, record.time])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=attendance_export.csv'
    
    return response

# Notification Settings Routes
@app.route('/notification_settings', methods=['GET', 'POST'])
def notification_settings():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        data = request.json
        
        settings = NotificationSettings.query.first()
        if not settings:
            settings = NotificationSettings()
        
        settings.attendance_confirmations = data.get('attendance_confirmations', True)
        settings.absence_alerts = data.get('absence_alerts', True)
        settings.cutoff_time = data.get('cutoff_time', '10:00')
        
        if not settings.id:
            db.session.add(settings)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Settings updated successfully'})
    
    # GET request
    settings = NotificationSettings.query.first()
    if not settings:
        settings = NotificationSettings(
            attendance_confirmations=True,
            absence_alerts=True,
            cutoff_time='10:00'
        )
        db.session.add(settings)
        db.session.commit()
    
    return jsonify({
        'success': True,
        'settings': {
            'attendance_confirmations': settings.attendance_confirmations,
            'absence_alerts': settings.absence_alerts,
            'cutoff_time': settings.cutoff_time
        }
    })

# Social Login Routes (Placeholder for Supabase integration)
@app.route('/auth/google')
def auth_google():
    # This would redirect to Google OAuth
    # For now, just redirect back with a message
    flash('Social login with Google will be available soon', 'info')
    return redirect(url_for('student_login'))

@app.route('/auth/github')
def auth_github():
    # This would redirect to GitHub OAuth
    # For now, just redirect back with a message
    flash('Social login with GitHub will be available soon', 'info')
    return redirect(url_for('student_login'))

@app.route('/auth/callback')
def auth_callback():
    # This would handle OAuth callbacks
    # For now, just redirect to login
    return redirect(url_for('student_login'))

# Check Absences and Send Notifications (Background task)
@app.route('/check_absences', methods=['POST'])
def check_absences():
    if not session.get('admin'):
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        settings = NotificationSettings.query.first()
        if not settings or not settings.absence_alerts:
            return jsonify({'success': False, 'message': 'Absence alerts are disabled'})
        
        today = date.today()
        cutoff_time_str = settings.cutoff_time
        
        # Get all users with email
        users_with_email = User.query.filter(User.email.isnot(None), User.email != '').all()
        absent_count = 0
        
        for user in users_with_email:
            # Check if user has attendance today
            attendance_today = Attendance.query.filter_by(
                user_id=user.id, 
                date=today.strftime('%Y-%m-%d')
            ).first()
            
            if not attendance_today:
                # Send absence notification
                try:
                    success, message = email_service.send_absence_notification(
                        user.email, user.name, today, cutoff_time_str
                    )
                    if success:
                        absent_count += 1
                        logging.info(f"Absence notification sent to {user.email}")
                    else:
                        logging.error(f"Failed to send absence notification to {user.email}: {message}")
                except Exception as e:
                    logging.error(f"Error sending absence notification to {user.email}: {e}")
        
        return jsonify({
            'success': True,
            'message': f'Absence notifications sent to {absent_count} students'
        })
        
    except Exception as e:
        logging.error(f"Error checking absences: {e}")
        return jsonify({'success': False, 'message': 'Error checking absences'}), 500

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))
    session.clear()
    return redirect(url_for('index'))

@app.route('/get_users')
def get_users():
    if not session.get('admin'):
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'name': user.name,
            'photo_url': user.photo_url
        })
    
    return jsonify({'success': True, 'users': user_list})
