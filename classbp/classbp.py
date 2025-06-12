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

class_bp = Blueprint('class_bp',__name__)

################################### CLASS API ###############################
@class_bp.route('/POSTclass', methods=['POST'])
@authentication
def POSTclass(current_user_id=None):
    message = ""
    res_data = {}
    status = "fail"
    code = 500

    try:
        data = request.json
        class_id = str(uuid.uuid4())
        class_name = data.get('class_name')
        section = data.get('section')
        academic_year = data.get('academic_year')

        if not class_name or not section or not academic_year:
            message = "class_name, section, and academic_year are required."
            code = 400
            return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

        created_date = datetime.now()

        query = """
            INSERT INTO class_master (
                _id, class_name, section, academic_year, is_active, created_by, created_date
            ) VALUES (%s, %s, %s, %s, TRUE, %s, %s)
        """
        values = (class_id, class_name, section, academic_year, current_user_id, created_date)
        db.execute(query, values)
        conn.commit()

        status = "success"
        code = 200
        message = "Class created successfully."
        res_data = {"_id": class_id, "class_name": class_name, "section": section, "academic_year": academic_year}

    except Exception as ex:
        message = f"Error in POSTclass: {str(ex)}"
        code = 500

    return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

@class_bp.route('/GETALLclass', methods=['GET'])
@authentication
def GETALLclass(current_user_id = None):
    message = ""
    code = 500
    status =  "fail"
    res_data = []
    try:
        db.execute("SELECT school_id FROM user_master WHERE _id = %s", (current_user_id,))
        user = db.fetchone()

        if not user:
            message = "Unauthorized user"
            code = 403
            return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

        db.execute("""
            SELECT 
                cm._id, cm.class_name, cm.section, cm.academic_year, 
                cm.is_active, cm.created_date, created_by
            FROM class_master cm
                WHERE cm.is_active = TRUE
        """)
        classes = db.fetchall()

        if classes:
            res_data = classes
            status = "success"
            code = 200
            message = "Classes fetched successfully."
        else:
            message = "No classes found."
            code = 404
    except Exception as ex:
        message = f"Error in GETALLclass: {str(ex)}"
        code = 500
    return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

@class_bp.route('/UPDATEclass', methods=['POST'])
@authentication
def UPDATEclass(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        data = request.json
        class_id = data.get("_id") 
        class_name = data.get("class_name")
        section = data.get("section")
        academic_year = data.get("academic_year")

        if not all([class_id, class_name, section, academic_year]):
            message = "Missing required fields"
            code = 400
            return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})
        
        db.execute("SELECT school_id FROM user_master WHERE _id = %s", (current_user_id,))
        user = db.fetchone()
        school_id = user.get("school_id") if user else None

        if not school_id:
            message = "Invalid user or school"
            code = 403
            return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

        db.execute("""
            SELECT _id FROM class_master 
            WHERE _id = %s AND created_by = %s
        """, (class_id, current_user_id))
        existing_class = db.fetchone()

        if not existing_class:
            message = "Class not found or permission denied"
            code = 404
            return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

        # Update the class
        db.execute("""
            UPDATE class_master 
            SET class_name = %s,
                section = %s,
                academic_year = %s,
                modified_date = NOW()
            WHERE _id = %s
        """, (class_name, section, academic_year, class_id))
        conn.commit()

        status = "success"
        code = 200
        message = "Class updated successfully"
        res_data = {
            "_id": class_id,
            "class_name": class_name,
            "section": section,
            "academic_year": academic_year
        }

    except Exception as ex:
        message = f"UPDATEclass: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@class_bp.route('/TOGGLEclassStatus', methods=['POST'])
@authentication
def TOGGLEclassStatus(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        data = request.json
        class_id = data.get("_id")
        is_active = data.get("is_active")

        if class_id is None or is_active is None:
            message = "Missing class_id or is_active field"
            code = 400
            return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

        db.execute("SELECT school_id FROM user_master WHERE _id = %s", (current_user_id,))
        user = db.fetchone()
        school_id = user.get("school_id") if user else None

        if not school_id:
            message = "Unauthorized or invalid user"
            code = 403
            return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

        db.execute("SELECT _id FROM class_master WHERE _id = %s AND created_by = %s", (class_id, current_user_id))
        class_row = db.fetchone()

        if not class_row:
            message = "Class not found or permission denied"
            code = 404
            return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

        # Update is_active status
        db.execute("""
            UPDATE class_master
            SET is_active = %s,
                modified_date = NOW()
            WHERE _id = %s
        """, (is_active, class_id))
        conn.commit()

        status = "success"
        code = 200
        message = f"Class {'activated' if is_active else 'deactivated'} successfully"
        res_data = {"class_id": class_id, "is_active": is_active}

    except Exception as ex:
        message = f"TOGGLEclassStatus: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })
