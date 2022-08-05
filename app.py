from flask import Flask, jsonify, request
from datetime import datetime
from flask_mysqldb import MySQL
import smtplib
import ssl
from email.message import EmailMessage

# python -m flask run -h localhost -p 3000

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'leave_request'
app.config['MYSQL_HOST'] = 'localhost'

#Example call API: http://127.0.0.1:5000/api/uc10/get-leave-request/

mysql.init_app(app)

# Get leave requests

@app.route('/home', methods=['POST', 'GET'])
def helloworld():
    return jsonify({'message': 'Hello World!'})

@app.route('/api/uc10/get-leave-request', methods=['POST', 'GET'])
def get_leave_request():
    """
    Example req body
    {
       "limit":"1", //optional
       "page":"1", //optional
       "employee_id":"1",
       "status":[], 
       "leave_from":"2020-01-01", //optional
       "leave_to":"2020-01-01", //optional
       "leave_type":"Annual Leave", //optional
    }
    """
    body_request = request.get_json()
    leave_typeid=""
    leave_typeid = body_request["leave_typeid"].lower()
    print(leave_typeid)
    switcher={
                'annual leave':'1',
                'personal leave':'2',
                'compensation leave':'3',
                'sick leave':'4',
                'non-paid leave':'5',
                'maternity leave':'6',
                'engagement ceremony':'7',
                'wedding leave':'8',
                'relative funeral leave':'9'
             }
    leave_typeid = switcher.get(leave_typeid,"Invalid leave type id")
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM request_leave")
    rv = cur.fetchall()
    return jsonify(leave_typeid)

@app.route('/api/uc10/delete-a-request', methods=['POST', 'DELETE'])
def delete_leavereq():
    """
    Example req body
    {
       "rleave_id":"4"
    }
    """
    conn = mysql.connection
    cursor = conn.cursor()

    body_request = request.get_json()

    rleave_id = ""
    try:
        rleave_id = body_request["rleave_id"]
    except:
        return "Leave request ID not found. Please enter the Leave request ID", 400

    if(type(rleave_id).__name__ != 'str'):
        return "Leave request ID is not a string", 400

    if(len(rleave_id) != 0):
        try:
            cursor.execute('DELETE FROM request_leave_detail WHERE RLEAVE_ID = %s',
                           (rleave_id))

            cursor.execute('DELETE FROM request_leave WHERE RLEAVE_ID = %s',
                           (rleave_id))

            conn.commit()
            return "OK", 200
        except:
            return "System has error", 500
    else:
            return "System has error when deleting leave request", 500