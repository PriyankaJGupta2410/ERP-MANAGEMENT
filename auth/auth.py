from flask import request, Blueprint , jsonify , json,request, session,render_template
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash,check_password_hash
from connector import db,conn
from functools import wraps
from decorator import authentication
import jwt
import os
from datetime import datetime,timedelta
import smtplib
from email.mime.text import MIMEText
import random
import uuid
from werkzeug.utils import secure_filename


load_dotenv()
auth_bp = Blueprint('auth',__name__)
##########################################
EMAIL = os.environ.get("EMAIL")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

######################################## AUTHENTICATION CODE #####################################
def generate_token(ID, email=None):
    token = jwt.encode({
        '_id': str(ID),
        "email": email,
        "iat": datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=365)
    }, os.environ.get("JWT_SECRET_KEY"), algorithm='HS256')
    return token

def send_otp_email(email, otp):
    try:
        msg = MIMEText(f"Hello Welcome To The Sam's School ERP.\nYour OTP is {otp}. \nIt will expire in 5 minutes.")
        msg['Subject'] = "Your OTP for Sam's School Login"
        msg['From'] = "ERP_School"
        msg['To'] = email

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL, EMAIL_PASSWORD)
        server.sendmail(EMAIL, email, msg.as_string())
        server.quit()

        return True, None
    except Exception as e:
        return False, str(e)

@auth_bp.route('/login', methods=['POST'])
def login():
    message = ""
    res_data = {}
    status = "fail"
    code = 500

    try:
        data = request.json
        email = data.get('email')
        input_password = data.get('password')  # Don't overwrite this later

        if not email or not input_password:
            message = "Email and password are required."
            code = 400

        else:
            query = "SELECT _id, role, username, email, contact, password FROM user_master WHERE email=%s"
            db.execute(query, (email,))
            user = db.fetchone()

            if user and check_password_hash(user.get("password"), input_password):
                otp = "123456"  # Static OTP for testing
                session['otp'] = otp
                session['email'] = email
                session['user_id'] = user.get("_id")

                status = "success"
                code = 200
                message = "OTP generated and stored in session for verification (email not sent)."
                res_data = {
                    "user_id": user.get("_id"),
                    "email": user.get("email"),
                    "role": user.get("role"),
                    "username": user.get("username"),
                    "contact": user.get("contact")
                }
            else:
                message = "Invalid email or password."
                code = 401

    except Exception as ex:
        message = f"Error: {str(ex)}"
        code = 500

    return jsonify({
        "status": status,
        "code": code,
        "message": message,"res_data": res_data})

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    message = ""
    res_data = {}
    status = "fail"
    code = 500

    try:
        data = request.json
        entered_otp = data.get('otp')

        saved_otp = session.get('otp')
        email = session.get('email')

        if not entered_otp:
            message = "OTP is required."
            code = 400

        elif entered_otp == saved_otp:
            query = "SELECT _id, role FROM user_master WHERE email=%s"
            db.execute(query, (email,))
            user = db.fetchone()

            if user:
                user_id = user.get("_id")
                role = user.get("role")

                token = generate_token(user_id, email)

                status = "success"
                code = 200
                message = "OTP verified successfully."
                res_data = {
                    "user_id": user_id,
                    "email": email,
                    "role": role,
                    "token": token
                }

                if session.get('forgot_password'):
                    # Forgot password flow: mark OTP verified, keep email for reset
                    session['otp_verified'] = True
                    session.pop('otp', None)
                else:
                    # Normal login flow: clear sensitive session data
                    session.pop('otp', None)
                    session.pop('email', None)
            else:
                message = "User not found."
                code = 404
        else:
            message = "Invalid OTP. Please try again."
            code = 401

    except Exception as ex:
        message = f"Error: {str(ex)}"
        code = 500

    return jsonify({"status": status,"code": code,"message": message,"res_data": res_data})

@auth_bp.route('/send-forgot-otp', methods=['POST'])
def send_forgot_otp():
    message = ""
    status = "fail"
    code = 500

    try:
        data = request.json
        email = data.get('email')

        if not email:
            message = "Email is required."
            code = 400
        else:
            query = "SELECT _id FROM user_master WHERE email=%s"
            db.execute(query, (email,))
            user = db.fetchone()

            if user:
                otp = "123456"  # For production, use random OTP
                session['otp'] = otp
                session['email'] = email
                session['forgot_password'] = True 
        
                message = "OTP sent successfully to your email."
                code = 200
                status = "success"
            else:
                message = "Email not registered."
                code = 404

    except Exception as ex:
        message = f"Error: {str(ex)}"
        code = 500

    return jsonify({"status": status, "code": code, "message": message})

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    message = ""
    status = "fail"
    code = 500

    try:
        data = request.json
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        email = session.get('email')

        if not new_password or not confirm_password:
            message = "Both password fields are required."
            code = 400
        elif new_password != confirm_password:
            message = "Passwords do not match."
            code = 400
        elif not email:
            message = "OTP not verified or session expired."
            code = 403
        else:
            hashed_password = generate_password_hash(new_password)
            query = "UPDATE user_master SET password=%s WHERE email=%s"
            db.execute(query, (hashed_password, email))
            conn.commit()  # Commit on connection, NOT on cursor

            # Clear session
            session.pop('email', None)

            message = "Password reset successfully."
            status = "success"
            code = 200

    except Exception as ex:
        message = f"Error: {str(ex)}"
        code = 500

    return jsonify({"status": status, "code": code, "message": message})

@auth_bp.route('/logout', methods=['POST'])
def logout():
    message = ""
    res_data = {}
    status = "fail"
    code = 500

    try:
        # Clear session data
        session_keys = ['user_id', 'email', 'otp']
        for key in session_keys:
            session.pop(key, None)

        status = "success"
        code = 200
        message = "User successfully logged out."
        res_data = {}

    except Exception as ex:
        message = f"Error during logout: {str(ex)}"
        code = 500

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })


@auth_bp.route('/RegisterSuperadmin', methods=['POST'])
def RegisterSuperadmin():
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        username = request.form.get("username")
        email = request.form.get("email")
        role = request.form.get("role")
        contact = request.form.get("contact")
        password = request.form.get("password")
        profilepic_file = request.files.get("profilepic")

        if not all([username, email, role, contact, password]):
            message = "All Fields are required"
            code = 400
            return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

        hashed_password = generate_password_hash(password)
        superadmin_id = str(uuid.uuid4())
        created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        profilepic_data = profilepic_file.read() if profilepic_file else None

        query = """INSERT INTO user_master 
                   (_id, username, email, password, role, contact, profile_image, created_date) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (superadmin_id, username, email, hashed_password, role, contact, profilepic_data, created_date)

        db.execute(query, values)
        conn.commit()

        return jsonify({
            "status": "success",
            "code": 200,
            "message": "Superadmin registered successfully",
            "res_data": {
                "_id": superadmin_id,
                "username": username,
                "email": email,
                "role": role,
                "contact": contact,
                "created_date": created_date
            }
        })
    except Exception as ex:
        message = f"RegisterSuperadmin : {ex}"
    return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

@auth_bp.route('/RegisterSchool', methods=['POST'])
def RegisterSchool():
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        superadmin_id = request.form.get("superadmin_id")
        about = request.form.get("about")
        infrastructure = request.form.get("infrastructure")
        news = request.form.get("news")
        contact = request.form.get("contact")
        gallery_file = request.files.get("gallery")

        if not all([superadmin_id, about, infrastructure, news, contact, gallery_file]):
            return jsonify({"status": status, "code": 400, "message": "All fields are required", "res_data": {}})

        school_id = str(uuid.uuid4())
        created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        gallery_data = gallery_file.read()

        insert_query = """
            INSERT INTO school_master (_id, superadmin_id, about_us, infrastructure, latest_news, gallery, contact_us, created_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        db.execute(insert_query, (school_id, superadmin_id, about, infrastructure, news, gallery_data, contact, created_date))

        db.execute("UPDATE user_master SET school_id = %s WHERE _id = %s", (school_id, superadmin_id))
        conn.commit()

        res_data = {
            "school_id": school_id,
            "superadmin_id": superadmin_id,
            "about_us": about,
            "infrastructure": infrastructure,
            "latest_news": news,
            "contact_us": contact,
            "created_date": created_date
        }
        status = "success"
        code = 200
        message = "School registered successfully"
    except Exception as ex:
        message = f"RegisterSchool: {ex}"

    return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

####################### Student Registration API #############################
@auth_bp.route('/register_student', methods=['POST'])
@authentication
def register_student(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        data = request.json
        student_id = str(uuid.uuid4())
        admission_id = data.get("admission_id")
        class_id = data.get("class_id")
        roll_number = data.get("roll_number")
        academic_year = data.get("academic_year")
        email = data.get("email")
        contact = data.get("contact")
        username = data.get("username")
        password = data.get("password")  # ✅ Take password from input

        if not all([username, email, contact, password]):
            raise Exception("Missing required user fields")

        user_id = str(uuid.uuid4())
        hashed_password = generate_password_hash(password)

        # Insert into user_master
        db.execute("""
            INSERT INTO user_master (
                _id, username, email, contact, password, role, created_by, created_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """, (user_id, username, email, contact, hashed_password, "student", current_user_id))

        # Insert into student_master
        db.execute("""
            INSERT INTO student_master (
                student_id, admission_id, user_id, class_id, roll_number,
                academic_year, is_active, created_by, created_date
            ) VALUES (%s, %s, %s, %s, %s, %s, TRUE, %s, NOW())
        """, (student_id, admission_id, user_id, class_id, roll_number, academic_year, current_user_id))

        status = "success"
        code = 201
        message = "Student registered successfully"
        res_data = {"student_id": student_id, "user_id": user_id}

    except Exception as ex:
        message = f"register_student: {str(ex)}"

    return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

#################### Parent Registration API #############################
@auth_bp.route('/register_parent', methods=['POST'])
@authentication
def register_parent(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        data = request.json
        parent_id = str(uuid.uuid4())
        occupation = data.get("occupation")
        relation = data.get("relation")
        address = data.get("address")
        email = data.get("email")
        contact = data.get("contact")
        username = data.get("username")
        password = data.get("password") 

        if not all([username, email, contact, password]):
            raise Exception("Missing required user fields")

        user_id = str(uuid.uuid4())
        hashed_password = generate_password_hash(password)

        db.execute("""
            INSERT INTO user_master (
                _id, username, email, contact, password, role, created_by, created_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """, (user_id, username, email, contact, hashed_password, "parent", current_user_id))

        db.execute("""
            INSERT INTO parent_master (
                parent_id, user_id, occupation, relation, address,
                is_active, created_by, created_date
            ) VALUES (%s, %s, %s, %s, %s, TRUE, %s, NOW())
        """, (parent_id, user_id, occupation, relation, address, current_user_id))

        status = "success"
        code = 201
        message = "Parent registered successfully"
        res_data = {"parent_id": parent_id, "user_id": user_id}

    except Exception as ex:
        message = f"register_parent: {str(ex)}"

    return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})




