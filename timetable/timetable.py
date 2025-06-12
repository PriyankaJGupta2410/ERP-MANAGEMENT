from flask import Blueprint, request, jsonify
from connector import db, conn
from decorator import authentication
import uuid
from datetime import datetime

timetable_bp = Blueprint('timetable', __name__)

################################### TIMETABLE API #####################################

@timetable_bp.route('/POSTtimetable', methods=['POST'])
@authentication
def POSTtimetable(current_user_id):
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        data = request.json
        class_id = data.get("class_id")
        day_of_week = data.get("day_of_week")
        subject = data.get("subject")
        time_slot = data.get("time_slot")
        teacher_name = data.get("teacher_name")

        if not all([class_id, day_of_week, subject, time_slot, teacher_name]):
            return jsonify({
                "status": status,
                "code": 400,
                "message": "class_id, day_of_week, subject, time_slot, and teacher_name are required.",
                "res_data": res_data
            })

        timetable_id = str(uuid.uuid4())
        query = """
            INSERT INTO timetable_master (_id, class_id, day_of_week, subject, time_slot, teacher_name, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (timetable_id, class_id, day_of_week, subject, time_slot, teacher_name, current_user_id)
        db.execute(query, values)
        conn.commit()

        status = "success"
        code = 200
        message = "Timetable entry added successfully."
        res_data = {
            "timetable_id": timetable_id,
            "class_id": class_id,
            "day_of_week": day_of_week,
            "subject": subject,
            "time_slot": time_slot,
            "teacher_name": teacher_name
        }

    except Exception as ex:
        message = f"Error in POSTtimetable: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })



######################################

@timetable_bp.route('/GETallTimetable', methods=['GET'])
@authentication
def GETallTimetable(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        query = """
            SELECT _id, class_id, day_of_week, subject, time_slot, teacher_name
            FROM timetable_master
            WHERE created_by = %s
        """
        db.execute(query, (current_user_id,))
        rows = db.fetchall()

        timetable = []
        for r in rows:
            timetable.append({
                "timetable_id": r.get("_id"),
                "class_id": r.get("class_id"),
                "day_of_week": r.get("day_of_week"),
                "subject": r.get("subject"),
                "time_slot": r.get("time_slot"),
                "teacher_name": r.get("teacher_name")
            })

        return jsonify({
            "status": "success",
            "code": 200,
            "message": "Timetable retrieved successfully.",
            "res_data": {"timetable": timetable}
        })

    except Exception as ex:
        message = f"GETallTimetable: {ex}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })


