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
            return jsonify({"status": "fail", "code": 400, "message": "All fields are required", "res_data": {}})

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
                "created_date": created_date,
                "profile_image" : profilepic_data
            }
        })
    except Exception as ex:
        return jsonify({
            "status": "fail",
            "code": 500,
            "message": f"RegisterSuperadmin Error: {str(ex)}",
            "res_data": {}
        })

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



