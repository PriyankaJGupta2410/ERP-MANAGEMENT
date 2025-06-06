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
        password = data.get('password')

        if not email or not password:
            message = "Email and password are required."
            code = 400

        else:
            query = "SELECT _id, role, username, email, contact, password FROM user_master WHERE email=%s"
            db.execute(query, (email,))
            user = db.fetchone()

            if user and check_password_hash(user[5], password):
                otp = str(random.randint(100000, 999999))
                session['otp'] = otp
                session['email'] = email
                session['user_id'] = user[0]

                success, error = send_otp_email(email, otp)

                if success:
                    status = "success"
                    code = 200
                    message = "OTP sent to your email for verification."
                    res_data = {
                        "user_id": user[0],
                        "email": user[3],
                        "role": user[1],
                        "username": user[2],
                        "contact": user[4]
                    }
                else:
                    message = f"Failed to send OTP: {error}"
                    code = 500
            else:
                message = "Invalid email or password."
                code = 401

    except Exception as ex:
        message = f"Error: {str(ex)}"
        code = 500

    return jsonify({"status": status,"code": code,"message": message,"res_data": res_data})

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
                user_id = user[0]
                role = user[1]

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
        data = request.json
        username = data.get("username")
        email = data.get("email")
        role = data.get("role")
        contact = data.get("contact")
        password = data.get("password")

        if not all([username, email, role, contact, password]):
            message = "All fields (username, email, role, contact, password) are required."
            return jsonify({"status": status, "code": 400, "message": message, "res_data": res_data})

        hashed_password = generate_password_hash(password)
        superadmin_id = str(uuid.uuid4())
        created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        query = """INSERT INTO user_master 
                   (_id, username, email, password, role, contact, created_date) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        values = (superadmin_id, username, email, hashed_password, role, contact, created_date)

        db.execute(query, values)
        conn.commit()

        message = "Superadmin registration done successfully"
        code = 200
        status = "success"
        res_data = {
            "_id": superadmin_id,
            "username": username,
            "email": email,
            "role": role,
            "contact": contact,
            "created_date": created_date
        }
    except Exception as ex:
        message = f"RegisterSuperadmin: {ex}"

    return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})


@auth_bp.route('/RegisterSchool', methods=['POST'])
def RegisterSchool():
    message = ""
    code = 500
    status = "fail"
    res_data = {}
    try:
        data = request.json
        superadmin_id = data.get("superadmin_id")
        about = data.get("about")
        infrastructure = data.get("infrastructure")
        news = data.get("news")
        gallery = data.get("gallery")
        contact = data.get("contact")

        if not all([superadmin_id, about, infrastructure, news, gallery, contact]):
            message = "All fields (superadmin_id, about, infrastructure, news, gallery, contact) are required."
            return jsonify({"status": status, "code": 400, "message": message, "res_data": res_data})

        school_id = str(uuid.uuid4())
        created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        query = """
            INSERT INTO school_master (_id, superadmin_id, about_us, infrastructure, latest_news, gallery, contact_us, created_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (school_id, superadmin_id, about, infrastructure, news, gallery, contact, created_date)
        db.execute(query, values)
        conn.commit()
        message = "School details register successfully"
        code =200
        status = "success"
        res_data = {
            "school_id": school_id,
            "superadmin_id": superadmin_id,
            "about_us": about,
            "infrastructure": infrastructure,
            "latest_news": news,
            "gallery": gallery,
            "contact_us": contact,
            "created_date": created_date
        }
    except Exception as ex:
        message = f"RegisterSchool:{ex}"
    return jsonify({"status": status,"code": code,"message": message,"res_data": res_data})

