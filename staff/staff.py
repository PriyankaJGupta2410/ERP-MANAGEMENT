from flask import request, Blueprint , jsonify , json,request, session,render_template
from dotenv import load_dotenv
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
        join_date = data.get('join_date')  # Expected: YYYY-MM-DD
        status_text = 'Active'
        created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if not all([username, email, password, contact, salary, join_date]):
            return jsonify({
                "status": status,
                "code": 400,
                "message": "All fields are required.",
                "res_data": res_data
            })

        with conn.cursor() as cursor:
            cursor.execute("SELECT _id FROM user_master WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({
                    "status": status,
                    "code": 400,
                    "message": "Email already exists",
                    "res_data": res_data
                })

            user_id = str(uuid.uuid4())
            staff_id = str(uuid.uuid4())
            hashed_password = generate_password_hash(password)

            cursor.execute("""
                INSERT INTO user_master (_id, username, email, contact, password, role, created_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, username, email, contact, hashed_password, role, created_date))

            cursor.execute("""
                INSERT INTO staff_master (_id, user_id, salary, join_date, status, created_date, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (staff_id, user_id, salary, join_date, status_text, created_date, current_user_id))

            conn.commit()

            message = "Staff successfully registered"
            code = 200
            status = "success"
            res_data = {
                "staff_id": staff_id,
                "user_id": user_id,
                "username": username,
                "email": email,
                "created_by": current_user_id
            }

    except Exception as ex:
        message = f"POSTstaff: {ex}"

    return jsonify({"status": status,"code": code,"message": message,"res_data": res_data})

@staff_bp.route('/GETstaff', methods=['GET'])
@authentication
def GETstaff(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = []

    try:
        with conn.cursor() as cursor:  # Use conn, not db
            query = """
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
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            columns = [col[0] for col in cursor.description]
            staff_list = [dict(zip(columns, row)) for row in rows]

            message = "Staff data fetched successfully"
            code = 200
            status = "success"
            res_data = staff_list

    except Exception as ex:
        message = f"GETstaff: {str(ex)}"

    return jsonify({"status": status,"code": code,"message": message,"res_data": res_data})
