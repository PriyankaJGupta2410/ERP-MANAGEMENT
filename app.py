from flask import Flask,render_template
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