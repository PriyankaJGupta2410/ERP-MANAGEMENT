from flask import request, Blueprint , jsonify , json,request, session,render_template
from dotenv import load_dotenv
import base64
from werkzeug.security import generate_password_hash,check_password_hash
from connector import db,conn
from functools import wraps
from decorator import authentication
import jwt
import os
from datetime import datetime,timedelta
import random
import uuid

load_dotenv()
staff_bp = Blueprint('staff',__name__)

############################### STAFF API ##############################
@staff_bp.route('/POSTstaff', methods=['POST'])
@authentication
def POSTstaff(current_user_id):
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        contact = data.get('contact')
        role = data.get('role', 'staff')
        salary = data.get('salary')
        join_date = data.get('join_date')
        profile_image_b64 = data.get('profile_image')  # optional base64 image
        status_text = 'Active'
        created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if not all([username, email, password, contact, salary, join_date]):
            return jsonify({
                "status": status,
                "code": 400,
                "message": "All required fields must be provided.",
                "res_data": res_data
            })

        # Decode base64 image
        profile_image_data = None
        if profile_image_b64:
            if ',' in profile_image_b64:
                profile_image_b64 = profile_image_b64.split(',')[1]
            try:
                profile_image_data = base64.b64decode(profile_image_b64)
            except Exception:
                return jsonify({
                    "status": status,
                    "code": 400,
                    "message": "Invalid base64 image data.",
                    "res_data": res_data
                })

        with conn.cursor() as cursor:
            cursor.execute("SELECT school_id FROM user_master WHERE _id = %s", (current_user_id,))
            school_result = cursor.fetchone()
            if not school_result or not school_result.get('school_id'):
                return jsonify({
                    "status": status,
                    "code": 403,
                    "message": "No associated school_id found for current user.",
                    "res_data": res_data
                })

            school_id = school_result.get('school_id')

            cursor.execute("SELECT _id FROM user_master WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({
                    "status": status,
                    "code": 400,
                    "message": "Email already exists.",
                    "res_data": res_data
                })

            user_id = str(uuid.uuid4())
            staff_id = str(uuid.uuid4())
            hashed_password = generate_password_hash(password)

            cursor.execute("""
                INSERT INTO user_master 
                (_id, username, email, contact, password, role, school_id, profile_image, created_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, username, email, contact, hashed_password, role, school_id, profile_image_data, created_date))

            cursor.execute("""
                INSERT INTO staff_master 
                (_id, user_id, school_id, salary, join_date, status, created_date, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (staff_id, user_id, school_id, salary, join_date, status_text, created_date, current_user_id))

            conn.commit()

            message = "Staff successfully registered"
            code = 200
            status = "success"
            res_data = {
                "staff_id": staff_id,
                "user_id": user_id,
                "school_id": school_id,
                "username": username,
                "email": email,
                "created_by": current_user_id
            }

    except Exception as ex:
        message = f"POSTstaff: {str(ex)}"

    return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})


@staff_bp.route('/GETstaff', methods=['GET'])
@authentication
def GETstaff(current_user_id=None):
    message = ""
    status = "fail"
    code = 500
    res_data = []

    try:
        db.execute("SELECT school_id FROM user_master WHERE _id = %s", (current_user_id,))
        user_row = db.fetchone()

        if user_row and user_row.get("school_id"):
            school_id = user_row.get("school_id")

            db.execute("""
                SELECT 
                    u._id AS user_id,
                    u.username,
                    u.email,
                    u.contact,
                    u.role,
                    s._id AS staff_id,
                    s.salary,
                    s.join_date,
                    s.status
                FROM user_master u
                JOIN staff_master s ON u._id = s.user_id
                WHERE s.school_id = %s
            """, (school_id,))
            staff_list = db.fetchall()

            message = "Staff data fetched successfully."
            status = "success"
            code = 200
            res_data = staff_list
        else:
            message = "User not found or school_id not assigned."
            code = 403

    except Exception as ex:
        message = f"GETstaff error: {str(ex)}"
        code = 500

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

