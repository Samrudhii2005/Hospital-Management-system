from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import MySQLdb.cursors

app = Flask(__name__)
bcrypt = Bcrypt(app)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'samru'  
app.config['MYSQL_PASSWORD'] = 'samrudhi@2005'
app.config['MYSQL_DB'] = 'hospital'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
app.secret_key = 'HMS@2025'  

# Home Route
@app.route('/')
def home():
    return render_template('home.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['role'] = user['role']

            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            elif user['role'] == 'patient':
                return redirect(url_for('patient_dashboard'))
        else:
            return "Invalid credentials"
    return render_template('login.html')
#signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        role = request.form['role']
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                       (username, hashed_password, role))
        user_id = cursor.lastrowid

        if role == 'patient':
            if role == 'patient':
               gender = request.form.get('gender')
               phone = request.form.get('phone')
               address = request.form.get('address')
               medical_history = request.form.get('medical_history')
            query = "INSERT INTO patient (PatientID, FirstName, LastName, Gender, PhoneNumber, Address, MedicalHistory) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (user_id, first_name, last_name, gender, phone, address, medical_history)

        elif role == 'doctor':
            specialization = request.form['specialization']
            phone = request.form['phone']
            query = "INSERT INTO doctor (DoctorID, FirstName, LastName, Specialization, Phone) VALUES (%s, %s, %s, %s, %s)"
            values = (user_id, first_name, last_name, specialization, phone)

        elif role == 'admin':
            query = "INSERT INTO admin (AdminID, FirstName, LastName) VALUES (%s, %s, %s)"
            values = (user_id, first_name, last_name)

        cursor.execute(query, values)
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login')) 
    return render_template('signup.html')


#  Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

#  Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')
@app.route('/view_all_appointments')
def view_all_appointments():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
#view all appointments
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT a.AppointmentID, a.AppointmentDate, a.AppointmentTime, a.Status,
               p.FirstName AS PatientFirst, p.LastName AS PatientLast,
               d.FirstName AS DoctorFirst, d.LastName AS DoctorLast, d.Specialization
        FROM appointment a
        JOIN patient p ON a.PatientID = p.PatientID
        JOIN doctor d ON a.DoctorID = d.DoctorID
    """)
    appointments = cursor.fetchall()
    cursor.close()

    return render_template('view_all_appointments.html', appointments=appointments)

#manage_doctors 
@app.route('/manage_doctors')
def manage_doctors():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM doctor")
    doctors = cursor.fetchall()
    cursor.close()

    return render_template('manage_doctors.html', doctors=doctors)

#Edit doctors
@app.route('/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        specialization = request.form['specialization']

        cursor.execute("""
            UPDATE doctor 
            SET FirstName = %s, LastName = %s, Specialization = %s 
            WHERE DoctorID = %s
        """, (first_name, last_name, specialization, doctor_id))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('manage_doctors'))

    # GET request - fetch current doctor data
    cursor.execute("SELECT * FROM doctor WHERE DoctorID = %s", (doctor_id,))
    doctor = cursor.fetchone()
    cursor.close()

    return render_template('edit_doctor.html', doctor=doctor)

#delete doctors
@app.route('/delete_doctor/<int:doctor_id>')
def delete_doctor(doctor_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM doctor WHERE DoctorID = %s", (doctor_id,))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('manage_doctors'))

#add doctors
@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        specialization = request.form['specialization']

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO doctor (FirstName, LastName, Specialization)
            VALUES (%s, %s, %s)
        """, (first_name, last_name, specialization))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('manage_doctors'))

    return render_template('add_doctor.html')

#manage patients
@app.route('/manage_patients')
def manage_patients():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM patient")
    patients = cursor.fetchall()
    cursor.close()

    return render_template('manage_patients.html', patients=patients)

#edit patients
@app.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        address = request.form['address']
        medical_history = request.form['medical_history']

        cursor.execute("""
            UPDATE patient 
            SET FirstName = %s, LastName = %s, PhoneNumber = %s, Address = %s, MedicalHistory = %s
            WHERE PatientID = %s
        """, (first_name, last_name, phone, address, medical_history, patient_id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('manage_patients'))

    # GET request - fetch patient data
    cursor.execute("SELECT * FROM patient WHERE PatientID = %s", (patient_id,))
    patient = cursor.fetchone()
    cursor.close()

    return render_template('edit_patient.html', patient=patient)

#delete patient
@app.route('/delete_patient/<int:patient_id>')
def delete_patient(patient_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM patient WHERE PatientID = %s", (patient_id,))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('manage_patients'))

#add patients
@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        address = request.form['address']
        medical_history = request.form['medical_history']

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO patient (FirstName, LastName, PhoneNumber, Address, MedicalHistory)
            VALUES (%s, %s, %s, %s, %s)
        """, (first_name, last_name, phone, address, medical_history))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('manage_patients'))

    return render_template('add_patient.html')

#  Doctor Dashboard
@app.route('/doctor_dashboard')
def doctor_dashboard():
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM doctor WHERE DoctorID = %s", (session['user_id'],))
    doctor = cursor.fetchone()
    cursor.close()

    return render_template('doctor_dashboard.html', doctor=doctor)

#view doc appt
@app.route('/view_doctor_appointments', methods=['GET', 'POST'])
def view_doctor_appointments():
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        appointment_id = request.form['appointment_id']
        new_status = request.form['status']
        cursor.execute("UPDATE appointment SET Status = %s WHERE AppointmentID = %s", (new_status, appointment_id))
        mysql.connection.commit()

    # Fetch appointments
    cursor.execute("""
        SELECT a.AppointmentID, a.AppointmentDate, a.AppointmentTime, a.Status,
               p.FirstName, p.LastName, p.MedicalHistory
        FROM appointment a
        JOIN patient p ON a.PatientID = p.PatientID
        WHERE a.DoctorID = %s
        ORDER BY a.AppointmentDate DESC
    """, (session['user_id'],))
    
    appointments = cursor.fetchall()
    cursor.close()

    return render_template('view_doctor_appointments.html', appointments=appointments)

# Patient Dashboard
@app.route('/patient')
def patient_dashboard():
    if 'user_id' not in session or session['role'] != 'patient':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM patient WHERE PatientID = %s", (session['user_id'],))
    patient = cursor.fetchone()
    cursor.close()

    return render_template('patient_dashboard.html', patient=patient)

# BOOK APPOINTMENT ROUTE
@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'user_id' not in session or session['role'] != 'patient':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT DoctorID, FirstName, LastName, Specialization FROM doctor")
    raw_doctors = cursor.fetchall()
    cursor.close()

    # Prepare doctor display names
    doctors = []
    for doc in raw_doctors:
        doctors.append({
            'DoctorID': doc['DoctorID'],
            'DoctorName': f"Dr. {doc['FirstName']} {doc['LastName']} ({doc['Specialization']})"
        })

    success_message = None

    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        date = request.form['date']
        time = request.form['time']

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO appointment (PatientID, DoctorID, AppointmentDate, AppointmentTime, Status) 
            VALUES (%s, %s, %s, %s, %s)
        """, (session['user_id'], doctor_id, date, time, 'Pending'))
        mysql.connection.commit()
        cursor.close()

        return render_template('appointment_success.html')

    return render_template('book_appointment.html', doctors=doctors, success_message=success_message)

#View Appointment
@app.route('/view_appointment')
def view_appointment():
    if 'user_id' not in session or session['role'] != 'patient':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("""
        SELECT a.AppointmentID, a.AppointmentDate, a.AppointmentTime, a.Status,
               d.DoctorID, d.FirstName AS DocFirst, d.LastName AS DocLast, d.Specialization
        FROM appointment a
        JOIN doctor d ON a.DoctorID = d.DoctorID
        WHERE a.PatientID = %s
    """, (session['user_id'],))
    appointments = cursor.fetchall()
    cursor.close()

    return render_template('view_appointment.html', appointments=appointments)

#Cancel appointments
@app.route('/cancel_appointment', methods=['GET', 'POST'])
def cancel_appointment():
    if 'user_id' not in session or session['role'] != 'patient':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        appointment_id = request.form['appointment_id']
        cursor.execute("""
            UPDATE appointment 
            SET Status = 'Cancelled' 
            WHERE AppointmentID = %s AND PatientID = %s
        """, (appointment_id, session['user_id']))
        mysql.connection.commit()
        cursor.close()
        return render_template('cancel_success.html')  # ✅ Only after cancel

    cursor.execute("""
        SELECT a.AppointmentID, a.AppointmentDate, a.AppointmentTime, d.FirstName, d.LastName 
        FROM appointment a
        JOIN doctor d ON a.DoctorID = d.DoctorID
        WHERE a.PatientID = %s AND a.Status = 'Pending'
    """, (session['user_id'],))
    appointments = cursor.fetchall()
    cursor.close()
    return render_template('cancel_appointment.html', appointments=appointments)

if __name__ == '__main__':
    app.run(debug=True)
