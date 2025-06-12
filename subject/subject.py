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
subject_bp = Blueprint('subject',__name__)

################################### SUBJECT API #####################################

@subject_bp.route('/POSTsubject', methods=['POST'])
@authentication
def POSTsubject(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = []

    try:
        data = request.json
        class_id = data.get('class_id')
        subjects = data.get('subjects', [])

        if not class_id:
            message = "class_id is required."
            code = 400
            return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

        if not subjects or not isinstance(subjects, list):
            message = "subjects must be a non-empty list."
            code = 400
            return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

        for subject in subjects:
            subject_name = subject.get('subject_name')
            subject_code = subject.get('subject_code')
            description = subject.get('description', '')

            if not subject_name or not subject_code:
                continue  

            db.execute("SELECT _id FROM subject_master WHERE subject_code = %s AND class_id = %s", (subject_code, class_id))
            if db.fetchone():
                continue  # Skip already existing subject_code for that class

            _id = str(uuid.uuid4())

            db.execute("""
                INSERT INTO subject_master (
                    _id, subject_name, subject_code, description,
                    class_id, created_by, created_date
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (
                _id,
                subject_name.strip(),
                subject_code.strip(),
                description.strip(),
                class_id,
                current_user_id
            ))

            res_data.append({
                "_id": _id,
                "subject_name": subject_name.strip(),
                "subject_code": subject_code.strip()
            })

        conn.commit()

        if res_data:
            status = "success"
            code = 200
            message = "Subjects added successfully."
        else:
            code = 400
            message = "No new subjects were added. Possibly all subject_codes already exist."

    except Exception as ex:
        message = f"Error in POSTsubject: {str(ex)}"
        code = 500
        conn.rollback()

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@subject_bp.route('/GETsubjectsbyclass',methods=['GET'])
@authentication
def GETsubjectbyclass(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = []

    try:
        class_id = request.args.get('class_id')

        if not class_id:
            message = "class_id is required."
            code = 400
            return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

        db.execute("SELECT * FROM subject_master WHERE class_id = %s", (class_id,))
        subjects = db.fetchall()

        if not subjects:
            message = "No subjects found for the given class."
            code = 404
        else:
            status = "success"
            code = 200
            res_data = [{
                "_id": subject['_id'],
                "subject_name": subject['subject_name'],
                "subject_code": subject['subject_code'],
                "description": subject['description']
            } for subject in subjects]

    except Exception as ex:
        message = f"Error in GETsubjectsbyclass: {str(ex)}"
        code = 500

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@subject_bp.route("/GETallsubjects", methods=['GET'])
@authentication
def GETallsubjects(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = []

    try:
        db.execute("SELECT * FROM subject_master ORDER BY class_id, subject_name")
        subjects = db.fetchall()

        if not subjects:
            message = "No subjects found."
            code = 404
        else:
            class_subject_map = {}

            # Group subject names by class_id
            for subject in subjects:
                class_id = subject.get('class_id')
                subject_name = subject.get('subject_name')

                if class_id not in class_subject_map:
                    class_subject_map[class_id] = []

                class_subject_map[class_id].append(subject_name)

            # Convert to list format
            res_data = [{"class_id": class_id, "subject_names": names}
                        for class_id, names in class_subject_map.items()]

            status = "success"
            code = 200
            message = "Subjects fetched successfully."

    except Exception as ex:
        message = f"Error in GETallsubjects: {str(ex)}"
        code = 500

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })
