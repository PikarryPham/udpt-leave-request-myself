from flask import Flask, jsonify, request
from datetime import datetime
from flask_mysqldb import MySQL

# python -m flask run -h localhost -p 3000

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'leave_request'
app.config['MYSQL_HOST'] = 'localhost'

# Example call API: http://127.0.0.1:3000/api/uc10/get-leave-request/

mysql.init_app(app)

# Get leave requests

'''
@app.route('/home', methods=['POST', 'GET'])
def helloworld():
    return jsonify({'message': 'Hello World!'})
'''


@app.route('/api/uc10/get-leave-requests', methods=['POST', 'GET'])
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
       "leave_type":"Annual Leave" //optional
    }
    """
    conn = mysql.connection
    cursor = conn.cursor()
    body_request = request.get_json()

    page = 0  # Trang 1: page 0, Trang 2: page 1....
    limit = 5  # Mac dinh moi trang co 5 bang ghi

    try:
        page = body_request["page"]
    except:
        print("page not found")

    try:
        limit = body_request["limit"]
    except:
        print("limit not found")

    offset = int(page)*int(limit)

    employee_id = ""
    try:
        employee_id = body_request["employee_id"]
    except:
        return "Employee id not found", 500

    leavefrom = "1970-01-01"
    try:
        leavefrom = body_request["leave_from"]
        leavefrom = str(leavefrom)
        leavefrom = f"'{leavefrom}'"
    except:
        print("Cannot find leave from of the leave request")

    leaveto = "1970-01-01"
    try:
        leaveto = body_request["leave_to"]
        leaveto = str(leaveto)
        leaveto = f"'{leaveto}'"
    except:
        print("Cannot find leave to of the leave request")

    leave_typeid = "" 
    try:
        leave_typeid = body_request["leave_type"].lower()
        switcher = {
            'annual leave': '1',
            'personal leave': '2',
            'compensation leave': '3',
            'sick leave': '4',
            'non-paid leave': '5',
            'maternity leave': '6',
            'engagement ceremony': '7',
            'wedding leave': '8',
            'relative funeral leave': '9'
        }
        leave_typeid = switcher.get(leave_typeid, "Invalid leave type id")
    except:
        print("Cannot find leave type of the leave request")
        
    if(leave_typeid == "Invalid leave type id" or leave_typeid == ""):
        leave_typeid = 0 #mac dinh la lay het leavetype
    print("Leave type id lan 2 la: " + str(leave_typeid))
    status = []
    try:
        status = body_request["status"]
    except:
        print("status not found")

    for i in range(0, len(status)):
        status[i] = f"'{status[i]}'"

    # Get the record
    query_string = "SELECT * FROM request_leave "+" WHERE STATUS IN (" + ",".join(
        status) + ")" + f" AND EMPLOYEE_ID = {employee_id}" + f" AND LEAVE_FROM >= {leavefrom}" + f" AND LEAVE_TO >= {leaveto}" + f" LIMIT {offset},{limit}"
    print("Do dai cua status" + str(len(status)))
    try:
        if(len(status) == 0 and leave_typeid != 0):
            query_string = "SELECT * FROM request_leave " + \
                f" WHERE EMPLOYEE_ID = {employee_id}" + f" AND LEAVE_FROM >= {leavefrom}" + \
                f" AND LEAVE_TO >= {leaveto}" + \
                f" AND LEAVE_TYPE = {leave_typeid}" + \
                f" LIMIT {offset},{limit}"
            print(query_string)
        elif(len(status) == 0 and (leave_typeid == 0 or leave_typeid == '0')):
            query_string = "SELECT * FROM request_leave " + \
                f" WHERE EMPLOYEE_ID = {employee_id}" + f" AND LEAVE_FROM >= {leavefrom}" + \
                f" AND LEAVE_TO >= {leaveto}" + \
                f" LIMIT {offset},{limit}"
            print(query_string)
    except:
        return "Status is not array", 500

    cursor.execute(query_string)

    row_headers = [x[0] for x in cursor.description]
    data = cursor.fetchall()
    json_data = []
    for result in data:
        json_data.append(dict(zip(row_headers, result)))

    # get the number of total record
    query_string = "SELECT COUNT(*) FROM request_leave "+" WHERE STATUS IN (" + ",".join(
        status) + ")" + f" AND EMPLOYEE_ID = {employee_id}" + f" AND LEAVE_FROM >= {leavefrom}" + f" AND LEAVE_TO >= {leaveto} "

    try:
        if(len(status) == 0 and leave_typeid != 0):
            query_string = "SELECT COUNT(*) FROM request_leave " + f" WHERE EMPLOYEE_ID = {employee_id}" + \
                f" AND LEAVE_FROM >= {leavefrom}" + \
                f" AND LEAVE_TO >= {leaveto}" + \
                f" AND LEAVE_TYPE = {leave_typeid}"
        elif(len(status) == 0 and leave_typeid == 0):
            query_string = "SELECT COUNT(*) FROM request_leave " + f" WHERE EMPLOYEE_ID = {employee_id}" + \
                f" AND LEAVE_FROM >= {leavefrom}" + \
                f" AND LEAVE_TO >= {leaveto}"
    except:
        return "System has error", 500

    cursor.execute(query_string)
    total = int(cursor.fetchall()[0][0])

    cursor.close()

    return jsonify({
        "total": total,
        "data": json_data,
    })


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
