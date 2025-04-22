from app import mysql

def get_patient_appointments(patient_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM appointments WHERE patient_id = %s", (patient_id,))
    appointments = cur.fetchall()
    cur.close()
    return appointments

def get_doctor_appointments(doctor_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM appointments WHERE doctor_id = %s", (doctor_id,))
    appointments = cur.fetchall()
    cur.close()
    return appointments

def get_all_appointments():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM appointments")
    appointments = cur.fetchall()
    cur.close()
    return appointments

def book_appointment(patient_id, doctor_id, appointment_date):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO appointments (patient_id, doctor_id, appointment_date, status) VALUES (%s, %s, %s, %s)", 
                (patient_id, doctor_id, appointment_date, 'scheduled'))
    mysql.connection.commit()
    cur.close()

def cancel_appointment(appointment_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE appointments SET status = %s WHERE id = %s", ('canceled', appointment_id))
    mysql.connection.commit()
    cur.close()
