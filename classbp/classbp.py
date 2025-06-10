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