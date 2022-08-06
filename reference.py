from flask import Flask, jsonify, request
from datetime import datetime
from flaskext.mysql import MySQL

mysql = MySQL()
app = Flask(_name_)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'tutest'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/get-pa-goals', methods=['POST'])
def get_pa_goals():
    conn = mysql.connect()
    cursor = conn.cursor()

    body_request = request.get_json()

    page = 0  # trang 1
    limit = 5  # moi trang 5

    try:
        page = body_request["page"]
    except:
        print("page not found")

    try:
        limit = body_request["limit"]
    except:
        print("limit not found")

    offset = page*limit

    employee_id = ""
    try:
        employee_id = body_request["employee_id"]
    except:
        return "employee id not found", 500

    last_update = "'1970-01-01 00:00:00'"
    try:
        last_update = body_request["last_update"]
        last_update = str(last_update)
        last_update = f"'{last_update}'"
    except:
        print("last update not found")

    deadline = "'1970-01-01 00:00:00'"
    try:
        deadline = body_request["deadline"]
        deadline = str(deadline)
        deadline = f"'{deadline}'"
    except:
        print("deadline not found")

    status = []
    try:
        status = body_request["status"]
    except:
        print("status not found")

    for i in range(0, len(status)):
        status[i] = f"'{status[i]}'"

    # get the record
    query_string = "SELECT * FROM pa_goal "+" WHERE STATUS IN (" + ",".join(
        status) + ")" + f" AND EMPLOYEECREATE_ID = {employee_id}" + f" AND LASTUPDATE_DATE > {last_update}" + f" AND DEADLINE_PAGOAL > {deadline}" + f" LIMIT {offset},{limit}"

    try:
        if(len(status) == 0):
            query_string = "SELECT * FROM pa_goal " + \
                f" WHERE EMPLOYEECREATE_ID = {employee_id}" + f" AND LASTUPDATE_DATE > {last_update}" + \
                f" AND DEADLINE_PAGOAL > {deadline}" + \
                f" LIMIT {offset},{limit}"
    except:
        return "status is not array", 500

    cursor.execute(query_string)

    row_headers = [x[0] for x in cursor.description]
    data = cursor.fetchall()
    json_data = []
    for result in data:
        json_data.append(dict(zip(row_headers, result)))

    # get the number of total record
    query_string = "SELECT COUNT(*) FROM pa_goal "+" WHERE STATUS IN (" + ",".join(
        status) + ")" + f" AND EMPLOYEECREATE_ID = {employee_id}" + f" AND LASTUPDATE_DATE > {last_update}" + f" AND DEADLINE_PAGOAL > {deadline}"

    try:
        if(len(status) == 0):
            query_string = "SELECT COUNT(*) FROM pa_goal " + f" WHERE EMPLOYEECREATE_ID = {employee_id}" + \
                f" AND LASTUPDATE_DATE > {last_update}" + \
                f" AND DEADLINE_PAGOAL > {deadline}"
    except:
        return "System error", 500

    cursor.execute(query_string)
    total = int(cursor.fetchall()[0][0])

    cursor.close()

    return jsonify({
        "total": total,
        "data": json_data,
    })


@app.route('/unsubmit', methods=['POST'])
def unsubmit():
    conn = mysql.connect()
    cursor = conn.cursor()

    body_request = request.get_json()

    reason = ""
    pa_goal_id = ""
    date = datetime.now()

    try:
        reason = body_request["reason"]
    except:
        return "Reason not found", 400

    try:
        pa_goal_id = body_request["pa_goal_id"]
    except:
        return "pa goal id not found", 400

    try:
        cursor.execute('UPDATE pa_goal SET LASTUPDATE_DATE = %s, UNSUBMIT_REASON = %s, STATUS = %s  WHERE PAGOAL_ID = %s',
                       (date, reason, "Cancelled", pa_goal_id))
        conn.commit()
        return "OK", 200

    except:
        return "System error", 500


@app.route('/reject', methods=['POST'])
def reject():
    conn = mysql.connect()
    cursor = conn.cursor()

    body_request = request.get_json()

    comment = ""
    pa_goal_id = ""
    date = datetime.now()

    try:
        comment = body_request["comment"]
    except:
        return "Comment not found", 400

    try:
        pa_goal_id = body_request["pa_goal_id"]
    except:
        return "pa goal id not found", 400

    try:
        cursor.execute('UPDATE pa_goal SET LASTUPDATE_DATE = %s, MANAGER_COMMENT = %s, STATUS = %s  WHERE PAGOAL_ID = %s',
                       (date, comment, "Rejected", pa_goal_id))
        conn.commit()
        return "OK", 200

    except:
        return "System error", 500


@app.route('/change-status', methods=['POST'])
def change_status():
    conn = mysql.connect()
    cursor = conn.cursor()

    body_request = request.get_json()

    status = ""
    pa_goal_id = ""
    date = datetime.now()

    try:
        status = body_request["status"]
    except:
        return "Status not found", 400

    try:
        pa_goal_id = body_request["pa_goal_id"]
    except:
        return "pa goal id not found", 400

    try:
        cursor.execute('UPDATE pa_goal SET LASTUPDATE_DATE = %s, STATUS = %s WHERE PAGOAL_ID = %s',
                       (date, status, pa_goal_id))
        conn.commit()
        return "OK", 200

    except:
        return "System error", 500


@app.route('/get-pa-goal', methods=['POST'])
def get_pa_goal():

    conn = mysql.connect()
    cursor = conn.cursor()

    body_request = request.get_json()

    pa_goal_id = ""
    date = datetime.now()

    try:
        pa_goal_id = body_request["pa_goal_id"]
    except:
        return "pa goal id not found", 400

    cursor.execute('SELECT * from pa_goal_detail WHERE PAGOAL_ID = %s',
                   (pa_goal_id))

    row_headers = [x[0] for x in cursor.description]
    data = cursor.fetchall()
    json_data = []
    for result in data:
        json_data.append(dict(zip(row_headers, result)))

    return jsonify({
        "data": json_data,
    })


@app.route('/add-goal', methods=['POST'])
def add_goal():
    conn = mysql.connect()
    cursor = conn.cursor()

    body_request = request.get_json()

    pa_goal_id = ""
    try:
        pa_goal_id = body_request["pa_goal_id"]
    except:
        return "pa goal id not found", 400

    due_date = ""
    try:
        due_date = body_request["due_date"]
    except:
        return "dua date not found", 400

    complete_date = "1970-01-01 00:00:00"
    try:
        complete_date = body_request["complete_date"]
    except:
        print("complete date not found")

    status = "Processing"
    try:
        status = body_request["status"]
    except:
        print("status not found")

    name = ""
    action = ""
    comment = ""
    try:
        name = body_request["name"]
        action = body_request["action"]
        comment = body_request["comment"]
    except:
        return "name, action and comment is required", 400

    try:
        print("a")
        cursor.execute(
            "SELECT COUNT(*) FROM pa_goal_detail WHERE PAGOAL_ID = %s", (pa_goal_id))
        total = int(cursor.fetchall()[0][0])

        print("b")

        cursor.execute("INSERT INTO pa_goal_detail(PAGOAL_ID, GOAL_NAME,ACTION_STEP,DUE_DATE,COMPLETED_DATE,STATUS,COMMENT) VALUES (%s, %s,%s, %s,%s, %s,%s)",
                       (pa_goal_id, name, action, due_date, complete_date, status, comment))

        date = datetime.now()
        cursor.execute('UPDATE pa_goal SET LASTUPDATE_DATE = %s, TOTAL_GOALS = %s WHERE PAGOAL_ID = %s',
                       (date, total+1, pa_goal_id))

        conn.commit()
        return "OK", 200
    except:
        return "System error", 500


@app.route('/edit-goal', methods=['POST'])
def edit_goal():
    conn = mysql.connect()
    cursor = conn.cursor()

    body_request = request.get_json()

    pa_goal_detail_id = ""
    try:
        pa_goal_detail_id = body_request["pa_goal_detail_id"]
    except:
        return "pa goal detail id not found", 400

    pa_goal_id = ""
    try:
        pa_goal_id = body_request["pa_goal_id"]
    except:
        return "pa goal id not found", 400

    due_date = ""
    try:
        due_date = body_request["due_date"]
    except:
        return "dua date not found", 400

    complete_date = "1970-01-01 00:00:00"
    try:
        complete_date = body_request["complete_date"]
    except:
        print("complete date not found")

    status = "Processing"
    try:
        status = body_request["status"]
    except:
        print("status not found")

    name = ""
    action = ""
    comment = ""
    try:
        name = body_request["name"]
        action = body_request["action"]
        comment = body_request["comment"]
    except:
        return "name, action and comment is required", 400

    try:
        cursor.execute('UPDATE pa_goal_detail SET GOAL_NAME = %s,ACTION_STEP = %s, DUE_DATE = %s, COMPLETED_DATE = %s, STATUS = %s, COMMENT = %s  WHERE PAGOALDETAIL_ID = %s',
                       (name, action, due_date, complete_date, status, comment, pa_goal_detail_id))

        date = datetime.now()
        cursor.execute('UPDATE pa_goal SET LASTUPDATE_DATE = %s WHERE PAGOAL_ID = %s',
                       (date, pa_goal_id))

        conn.commit()
        return "OK", 200
    except:
        return "System error", 500


@app.route('/delete-goal', methods=['POST'])
def delete_goal():
    conn = mysql.connect()
    cursor = conn.cursor()

    body_request = request.get_json()

    pa_goal_detail_ids = []
    try:
        pa_goal_detail_ids = body_request["pa_goal_detail_ids"]
    except:
        return "pa goal detail ids not found", 400

    pa_goal_id = ""
    try:
        pa_goal_id = body_request["pa_goal_id"]
    except:
        return "pa goal id not found", 400

    if(type(pa_goal_detail_ids).__name__ != 'list'):
        return "pa goal detail ids is not array", 400

    if(len(pa_goal_detail_ids) == 0):
        try:
            cursor.execute('DELETE FROM pa_goal_detail WHERE PAGOAL_ID = %s',
                           (pa_goal_id))

            date = datetime.now()
            cursor.execute('UPDATE pa_goal SET LASTUPDATE_DATE = %s, TOTAL_GOALS = %s WHERE PAGOAL_ID = %s',
                           (date, "0", pa_goal_id))

            conn.commit()
            return "OK", 200
        except:
            return "System error", 500
    else:
        try:
            sql = "DELETE FROM pa_goal_detail WHERE PAGOALDETAIL_ID IN (" + ",".join(
                pa_goal_detail_ids) + ")"
            cursor.execute(sql)

            cursor.execute(
                "SELECT COUNT(*) FROM pa_goal_detail WHERE PAGOAL_ID = %s", (pa_goal_id))
            total = int(cursor.fetchall()[0][0])

            date = datetime.now()
            cursor.execute('UPDATE pa_goal SET LASTUPDATE_DATE = %s, TOTAL_GOALS = %s WHERE PAGOAL_ID = %s',
                           (date, total-len(pa_goal_detail_ids), pa_goal_id))

            conn.commit()
            return "OK", 200
        except:
            return "System error", 500


@app.route('/view-goal', methods=['POST'])
def view_goal():
    conn = mysql.connect()
    cursor = conn.cursor()

    body_request = request.get_json()

    pa_goal_detail_ids = []
    try:
        pa_goal_detail_ids = body_request["pa_goal_detail_ids"]
    except:
        return "pa goal detail ids not found", 400

    pa_goal_id = ""
    try:
        pa_goal_id = body_request["pa_goal_id"]
    except:
        return "pa goal id not found", 400

    if(type(pa_goal_detail_ids).__name__ != 'list'):
        return "pa goal detail ids is not array", 400

    if(len(pa_goal_detail_ids) != 0):
        try:
            sql = "SELECT * FROM pa_goal_detail WHERE PAGOALDETAIL_ID IN (" + ",".join(
                pa_goal_detail_ids) + ")"
            cursor.execute(sql)

            row_headers = [x[0] for x in cursor.description]
            data = cursor.fetchall()
            json_data = []
            for result in data:
                json_data.append(dict(zip(row_headers, result)))

            conn.commit()

            return jsonify({
                "data": json_data,
            })
        except:
            return "System error", 500

    else:
        try:

            cursor.execute(
                "SELECT * FROM pa_goal_detail WHERE PAGOAL_ID = %s", (pa_goal_id))

            row_headers = [x[0] for x in cursor.description]
            data = cursor.fetchall()
            json_data = []
            for result in data:
                json_data.append(dict(zip(row_headers, result)))

            conn.commit()

            return jsonify({
                "data": json_data,
            })
        except:
            return "System error", 500
