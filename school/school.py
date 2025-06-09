from flask import request, Blueprint , jsonify , json,request, session,render_template
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash,check_password_hash
from connector import db,conn
from functools import wraps
from decorator import authentication
import uuid
import base64

load_dotenv()
school_bp = Blueprint('school',__name__)

####################################### School API ###############################

@school_bp.route('/GETschooldetails', methods=['GET'])
@authentication
def GETschooldetails(current_user_id=None):
    message = ""
    status = "fail"
    code = 500
    res_data = {}

    try:
        db.execute("SELECT school_id FROM user_master WHERE _id = %s", (current_user_id,))
        user_row = db.fetchone()

        if user_row and user_row.get("school_id"):
            school_id = user_row.get("school_id")
            
            db.execute("SELECT * FROM school_master WHERE _id = %s", (school_id,))
            school = db.fetchone()

            if school:
                gallery_data = school.get("gallery")
                if isinstance(gallery_data, bytes):
                    # Encode bytes to base64 string
                    gallery_data = base64.b64encode(gallery_data).decode('utf-8')

                # Optional: try parsing gallery as JSON if expected
                try:
                    gallery_data = json.loads(gallery_data)
                except Exception:
                    # If not JSON, keep as string
                    pass
                res_data = {
                    "_id": school.get("_id"),
                    "about_us": school.get("about_us"),
                    "infrastructure": school.get("infrastructure"),
                    "latest_news": school.get("latest_news"),
                    "gallery": gallery_data,
                    "contact_us": school.get("contact_us"),
                    "created_date": str(school.get("created_date")),
                    "superadmin_id": school.get("superadmin_id")
                }
                message = "School details fetched successfully."
                status = "success"
                code = 200
            else:
                message = f"No school found for school_id: {school_id}"
                code = 404
        else:
            message = "User not found or school_id not assigned."
            code = 403

    except Exception as ex:
        message = f"GETschooldetails error: {str(ex)}"
        code = 500

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })


