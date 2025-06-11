from flask import request, Blueprint , jsonify , json
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash,check_password_hash
from connector import db,conn
from decorator import authentication
import json
import random
import string
import uuid
import base64


load_dotenv()
teacher_bp = Blueprint('teacher',__name__)

#################################### TEACHER API ###########################################

@teacher_bp.route('/AssignTeacher',methods=['POST'])
@authentication
def AssignTeacher(current_user_id = None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        data = request.json
        class_id = data.get('class_id')
        teacher_id = data.get('teacher_id')

        if not class_id or not teacher_id:
            message = "class_id and teacher_id are required."
            code = 400
            return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})
        
        # Check if the class already has a teacher assigned
        db.execute("SELECT * FROM class_teacher WHERE class_id = %s", (class_id,))
        existing_assignment = db.fetchone()
        if existing_assignment:
            message = "This class already has a teacher assigned."
            code = 400
            return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

        query = """
            INSERT INTO class_teacher (class_id, teacher_id, created_by, created_date)
            VALUES (%s, %s, %s, NOW())
        """
        values = (class_id, teacher_id, current_user_id)
        db.execute(query, values)
        conn.commit()
        status = "success"
        code = 200
        message = "Teacher assigned to class successfully."
    
    except Exception as ex:
        message = f"Error in AssignTeacher: {str(ex)}"
        code = 500
    return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})
