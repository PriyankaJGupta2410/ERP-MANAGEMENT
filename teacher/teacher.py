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

@teacher_bp.route('/POSTSyllabus', methods=['POST'])
@authentication
def POSTSyllabus(current_user_id):
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        metadata = json.loads(request.form.get('metadata', '{}'))

        syllabus_id = str(uuid.uuid4())
        class_name = metadata.get('class')

        syllabus_file = request.files.get('syllabus_file')

        if not all([class_name, syllabus_file]):
            return jsonify({
                "status": status,
                "code": 400,
                "message": "_id, class name, and syllabus file are required.",
                "res_data": res_data
            })

        syllabus_data = syllabus_file.read()

        query = '''
            INSERT INTO syllabus_master (_id, class, subject_syllabus, uploaded_by, created_date)
            VALUES (%s, %s, %s, %s, NOW())
        '''
        db.execute(query, (syllabus_id, class_name, syllabus_data, current_user_id))
        conn.commit()

        status = "success"
        code = 200
        message = "Subject syllabus added successfully."
        res_data = {
            "syllabus_id": syllabus_id,
            "class": class_name
        }

    except Exception as ex:
        message = f"POSTSyllabus: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })


# Get all syllabi, decode blobs as base64 strings
@teacher_bp.route('/GETallSyllabus', methods=['GET'])
@authentication
def GETallSyllabus(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}
    try:
        query = "SELECT _id, class,subject_syllabus FROM syllabus_master WHERE uploaded_by = %s" 
        db.execute(query, (current_user_id))
        rows = db.fetchall()

        syllabi = []
        for r in rows:
            syllabus_data = r.get("subject_syllabus")
            if isinstance(syllabus_data,bytes):
                syllabus_data = base64.b64encode(syllabus_data).decode('utf-8')

            syllabi.append({
                "class": r.get("class"),
                "subject_syllabus_base64": syllabus_data
            })
        
        return jsonify({
            "status": "success",
            "code": 200,
            "message": "Syllabi retrieved successfully.",
            "res_data": {"syllabi": syllabi}
        })

    except Exception as ex:
        message = f"GETallSyllabus:{ex}"
    return jsonify({
    "status": status,
    "code": code,
    "message": message,
    "res_data": res_data
})

# Add weekly schedule (unchanged, JSON only)
@teacher_bp.route('/POSTSchedule', methods=['POST'])
@authentication
def POSTSchedule(current_user_id):
    status = "fail"
    code = 500
    res_data = {}
    try:
        metadata = json.loads(request.form.get('metadata', '{}'))

        day_of_week = metadata.get('day_of_week')
        subject = metadata.get('subject')
        time_slot = metadata.get('time_slot')

        schedule_file = request.files.get('schedule_file')

        if not all([day_of_week, subject, time_slot, schedule_file]):
            return jsonify({
                "status": status,
                "code": 400,
                "message": "_id, day_of_week, subject, time_slot are required.",
                "res_data": res_data
            })

        schedule_data = schedule_file.read()

        query = '''
            INSERT INTO schedule_master (_id, uploaded_by, day_of_week, subject, time_slot, schedule_file, created_date)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        '''

        db.execute(query, (str(uuid.uuid4()), current_user_id, day_of_week, subject, time_slot, schedule_data))
        conn.commit()

        status = "success"
        code = 200
        message = "Weekly schedule added successfully."
        res_data = {
            "day_of_week": day_of_week,
            "subject": subject,
            "time_slot": time_slot,
        }

    except Exception as ex:
        message = f"PostSchedule: {str(ex)}"

    return jsonify({
            "status": status,
            "code": 500,
            "message": message,
            "res_data": res_data
    })
    
# Get weekly schedule
@teacher_bp.route('/GETSchedule', methods=['GET'])
@authentication
def GETSchedule(current_user_id=None):
    status = "fail"
    code = 500
    message = ""
    res_data = {}
    try:
        query = "SELECT _id, day_of_week, subject, time_slot, schedule_file FROM schedule_master WHERE uploaded_by = %s"
        db.execute(query, (current_user_id,))
        rows = db.fetchall()

        schedule = []
        for r in rows:
            schedule_data = r.get("schedule_file")
            if isinstance(schedule_data, bytes):
                schedule_data = base64.b64encode(schedule_data).decode('utf-8')

            schedule.append({
                "_id": r.get("_id"),
                "day_of_week": r.get("day_of_week"),
                "subject": r.get("subject"),
                "time_slot": r.get("time_slot"),
                "schedule_image_base64": schedule_data 
            })

        return jsonify({
            "status": "success",
            "code": 200,
            "message": "Syllabi retrieved successfully.",
            "res_data": {"schedule":schedule}
    })

    except Exception as ex:
        message = f"GETSchedule:{ex}"
    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })


# Add notice (unchanged)
@teacher_bp.route('/PostNotice', methods=['POST'])
@authentication
def PostNotice(current_user_id):
    status = "fail"
    code = 500
    res_data = {}
    try:
        metadata = json.loads(request.form.get('metadata', '{}'))

        notice_text = metadata.get('notice')

        notice_file = request.files.get('notice_file')

        if not all([notice_text, notice_file]):
            return jsonify({
                "status": status,
                "code": 400,
                "message": "_id and notice text are required.",
                "res_data": res_data
            })

        notice_data = notice_file.read()

        query = '''
            INSERT INTO notice_master (_id, notice_text, uploaded_by, notice_file, created_at)
            VALUES (%s, %s, %s, NOW())
        '''
        db.execute(query, (notice_text, current_user_id, notice_data))
        conn.commit()

        status = "success"
        code = 200
        message = "Notice added successfully."
        res_data = {
            "notice_text": notice_text,
        }    

    except Exception as ex:
        message = f"PostNotice: {str(ex)}"

    return jsonify({
            "status": status,
            "code": 500,
            "message": message,
            "res_data": res_data
        })


# Get notices
@teacher_bp.route('/GetNotice', methods=['GET'])
@authentication
def GetNotice(current_user_id=None):
    status = "fail"
    code = 500
    message = ""
    res_data = {}
    try:
        query = "SELECT _id, notice_text, notice_file FROM notice_master WHERE uploaded_by = %s"
        db.execute(query, (current_user_id,))
        rows = db.fetchall()

        notice = []
        for r in rows:
            notice_data = r.get("notice_file")
            if isinstance(notice_data, bytes):
                notice_data = base64.b64encode(notice_data).decode('utf-8')

            notice.append({
                "_id": r.get("_id"),
                "notice_text": r.get("notice_text"),
                "notice_image_base64": notice_data
            })

        return jsonify({
            "status": "success",
            "code": 200,
            "message": "Notices retrieved successfully.",
            "res_data": {"notice": notice}
        })

    except Exception as ex:
        message = f"GetNotice: {ex}"
    
    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })


# Mark attendance 
@teacher_bp.route('/PostAttendance', methods=['POST'])
@authentication
def PostAttendance(current_user_id):
    status = "fail"
    code = 500
    res_data = {}

    try:
        metadata = json.loads(request.form.get('metadata', '{}'))

        date = metadata.get('date')
        attendance_status = metadata.get('status')

        if not all([date, attendance_status]):
            return jsonify({
                "status": status,
                "code": 400,
                "message": "Date and status are required.",
                "res_data": res_data
            })

        query = '''
            INSERT INTO attendance_master (date, status, uploaded_by)
            VALUES (%s, %s, %s)
        '''
        db.execute(query, (date, attendance_status, current_user_id))
        conn.commit()

        status = "success"
        code = 200
        message = "Attendance recorded successfully."
        res_data = {
            "date": date,
            "status": attendance_status
        }

    except Exception as ex:
        message = f"PostAttendance: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })


# Get attendance
@teacher_bp.route('/GetAttendance', methods=['GET'])
@authentication
def GetAttendance(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}
    try:
        query = "SELECT date, status FROM attendance_master WHERE uploaded_by = %s"
        db.execute(query, (current_user_id,))
        rows = db.fetchall()

        attendance_records = []
        for r in rows:
            attendance_records.append({
                "date": r.get("date").isoformat() if r.get("date") else None,
                "status": r.get("status")
            })

        return jsonify({
            "status": "success",
            "code": 200,
            "message": "Attendance records retrieved successfully.",
            "res_data": {"attendance": attendance_records}
        })

    except Exception as ex:
        message = f"GetAttendance: {ex}"
    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

