from flask import request, Blueprint , jsonify , json,request, session,render_template
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash,check_password_hash
from connector import db,conn
from functools import wraps
from decorator import authentication
import jwt
import os
from datetime import datetime,timedelta
import uuid
import base64


load_dotenv()
model_bp = Blueprint('model',__name__)

################################### MODEL API ########################################

@model_bp.route('/upload_file', methods=['POST'])
@authentication
def upload_file(current_user_id=None):
    message = ""
    status = "fail"
    code = 500
    res_data = {}

    try:
        file = request.files.get("file")

        if not file:
            return jsonify({
                "message": "No file uploaded",
                "status": status,
                "code": 400,
                "res_data": {}
            })

        file_name = file.filename
        file_type = file.content_type
        file_data = file.read()

        file_id = str(uuid.uuid4())
        created_date = datetime.now()

        insert_query = """
            INSERT INTO file_uploads (_id, file_name, file_type, file_data, uploaded_by, created_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        db.execute(insert_query, (
            file_id, file_name, file_type, file_data,current_user_id, created_date.strftime('%Y-%m-%d %H:%M:%S')
        ))
        conn.commit()

        encoded_file = base64.b64encode(file_data).decode("utf-8")

        res_data = {
            "_id": file_id,
            "file_name": file_name,
            "file_type": file_type,
            "file_base64": encoded_file
        }

        message = "File uploaded successfully"
        status = "success"
        code = 200

    except Exception as e:
        message = f"Unexpected error in upload_file: {str(e)}"

    return jsonify({
        "message": message,
        "status": status,
        "code": code,
        "res_data": res_data
    })


def GETuserdetails(current_user_id=None):
    message = ""
    status = "fail"
    code = 500
    res_data = {}

    try:
        # Fetch user data by ID
        db.execute("SELECT * FROM user_master WHERE _id = %s", (current_user_id,))
        user = db.fetchone()

        if not user:
            message = "User not found"
            code = 404
            return jsonify({
                "status": status,
                "code": code,
                "message": message,
                "res_data": res_data
            })

        # Build response with base64 encoded image
        for key, value in user.items():
            if isinstance(value, datetime):
                res_data[key] = str(value)
            elif key == "profile_image" and value is not None:
                res_data[key] = base64.b64encode(value).decode('utf-8')
            else:
                res_data[key] = value

        message = "User details retrieved successfully"
        status = "success"
        code = 200

    except Exception as e:
        message = f"Unexpected error in GETuserdetails: {str(e)}"
        code = 500

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })
