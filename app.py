from flask import Flask,render_template,redirect,session, url_for
from connector import db
from dotenv import load_dotenv
import os

load_dotenv()
############################### Import Blueprints ########################
from auth.auth import auth_bp
from admission.admission import admission_bp
from staff.staff import staff_bp
from school.school import school_bp
from fee.fee import fee_bp
from classbp.classbp import class_bp
from store.store import store_bp 
from role.role import role_bp
from model.model import model_bp
from teacher.teacher import teacher_bp
from subject.subject import subject_bp
from library.library import library_bp
from leave.leave import leave_bp
from timetable.timetable import timetable_bp
#############################################
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

################################### Register Blueprint ##############################
app.register_blueprint(auth_bp, url_prefix = "/auth")
app.register_blueprint(admission_bp,url_prefix = "/admissions")
app.register_blueprint(staff_bp,url_prefix = '/staff')
app.register_blueprint(school_bp,url_prefix = '/school')
app.register_blueprint(fee_bp,url_prefix="/fee")
app.register_blueprint(class_bp,url_prefix="/class")
app.register_blueprint(store_bp, url_prefix="/store") 
app.register_blueprint(role_bp, url_prefix="/role")
app.register_blueprint(model_bp, url_prefix="/model")
app.register_blueprint(teacher_bp, url_prefix="/teacher")
app.register_blueprint(subject_bp, url_prefix="/subject")
app.register_blueprint(library_bp, url_prefix="/library")
app.register_blueprint(leave_bp, url_prefix="/leave")
app.register_blueprint(timetable_bp, url_prefix="/timetable")
####################################################################

@app.route("/")
def index():
    return "Hello World"

############################# DECLARE TEMPLATES ##############################
@app.route('/onboard')
def manual_onboard_form():
    return render_template('manual_onboard.html') 

@app.route('/login')
def login():
    return render_template('login.html') 

@app.route('/admission_form')
def admission_form():
    return render_template('add_admission.html') 

@app.route('/SendOtp')
def SendOtp():
    return render_template('send_otp.html')

@app.route('/VerifyOtp')
def VerifyOtp():
    return render_template('verify_otp.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/registerSuperadmin')
def registerSuperadmin():
    return render_template('register_superadmin.html')

@app.route('/registerSchool')
def registerSchool():
    return render_template('registerschool.html')

@app.route('/addSupervisor')
def addSupervisor():
    return render_template('add_supervisor.html')

@app.route('/Getstaff')
def Getstaff():
    return render_template('get_staff.html')

@app.route('/Superadmindashboard')
def Superadmindashboard():
    return render_template('superadmin_dashboard.html')

@app.route('/Supervisordashboard')
def Supervisordashboard():
    return render_template('supervisor_dashboard.html')

@app.route('/addStaff')
def addStaff():
    return render_template('add_staff.html')

@app.route('/AccountantDashboard')
def AccountantDashboard():
    return render_template('accountant_dashboard.html')

@app.route('/forgotpassword')
def forgotpassword():
    return render_template('forgot_password.html')

@app.route('/resetpassword')
def resetpassword():
    return render_template('reset_password.html')

@app.route('/forgotverifyotp')
def forgotverifyotp():
    return render_template('forgot_verify_otp.html')

if __name__ == '__main__':
    app.run(debug=True)
