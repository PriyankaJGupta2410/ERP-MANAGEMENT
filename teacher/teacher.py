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
        classteacher_id = str(uuid.uuid4())

        if not class_id or not teacher_id:
            message = "class_id and teacher_id are required."
            code = 400
            return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})
        
        # Check if the class already has a teacher assigned
        db.execute("SELECT * FROM class_teacher_master WHERE class_id = %s", (class_id,))
        existing_assignment = db.fetchone()
        if existing_assignment:
            message = "This class already has a teacher assigned."
            code = 400
            return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

        query = """
            INSERT INTO class_teacher_master (_id,class_id, teacher_id, created_by, created_date)
            VALUES (%s,%s, %s, %s, NOW())
        """
        values = (classteacher_id,class_id, teacher_id, current_user_id)
        db.execute(query, values)
        conn.commit()
        status = "success"
        code = 200
        message = "Teacher assigned to class successfully."
        res_data = {
            "_id": classteacher_id,
            "class_id": class_id,
            "teacher_id": teacher_id,
            "created_by": current_user_id
        }
    except Exception as ex:
        message = f"Error in AssignTeacher: {str(ex)}"
        code = 500
    return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

@teacher_bp.route('/GETALLteachers', methods=['GET'])
@authentication
def GETALLteachers(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = []

    try:
        db.execute("SELECT * FROM user_master WHERE role = 'teacher' AND status = 'active'")
        teachers = db.fetchall()

        if not teachers:
            message = "No active teachers found."
            code = 404
        else:
            status = "success"
            code = 200
            for teacher in teachers:
                if teacher['profile_image']:
                    # Decode the base64 image data
                    try:
                        profile_image = base64.b64decode(teacher['profile_image'])
                        # Convert to base64 string for JSON response
                        teacher['profile_image'] = base64.b64encode(profile_image).decode('utf-8')
                    except Exception as e:
                        teacher['profile_image'] = None
                res_data.append({
                    "_id": teacher['_id'],
                    "username": teacher['username'],
                    "profile_image" : teacher['profile_image'],
                    "email": teacher['email'],
                    "contact": teacher['contact'],
                    "created_date": teacher['created_date']
                })
            message = "Teachers retrieved successfully."

    except Exception as ex:
        message = f"Error in GETALLteachers: {str(ex)}"
    
    return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

@teacher_bp.route('/ASSIGNsubjectToTeacher', methods=['POST'])
@authentication
def ASSIGNsubjectToTeacher(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = []

    try:
        data = request.json
        teacher_id = data.get("teacher_id")
        class_id = data.get("class_id")
        subject_ids = data.get("subject_ids", [])  # List of subject_master._id

        if not teacher_id or not class_id or not subject_ids:
            message = "teacher_id, class_id, and subject_ids are required."
            code = 400
            return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

        for subject_id in subject_ids:
            _id = str(uuid.uuid4())

            db.execute("""
                SELECT * FROM Subject_Assigned_Master 
                WHERE teacher_id=%s AND class_id=%s AND subject_id=%s
            """, (teacher_id, class_id, subject_id))
            if db.fetchone():
                continue  # Skip already existing mapping

            db.execute("""
                INSERT INTO Subject_Assigned_Master (_id, teacher_id, class_id, subject_id, created_by)
                VALUES (%s, %s, %s, %s, %s)
            """, (_id, teacher_id, class_id, subject_id, current_user_id))

            res_data.append({
                "_id": _id,
                "teacher_id": teacher_id,
                "class_id": class_id,
                "subject_id": subject_id
            })

        if res_data:
            conn.commit()
            status = "success"
            code = 200
            message = "Subjects assigned to teacher successfully."
        else:
            code = 400
            message = "No new assignments. Possibly all subjects already assigned."

    except Exception as ex:
        message = f"Error in ASSIGNsubjectToTeacher: {str(ex)}"
        code = 500
    return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})
