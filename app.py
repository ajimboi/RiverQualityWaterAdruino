from flask import Flask, render_template, url_for, request, session, redirect
import mysql.connector
from datetime import datetime, timedelta, date
from calendar import monthrange

app = Flask(__name__)
app.secret_key = b'\xe4\xad\x0c(!<\x1dhs\xcdG\xbc\xc8\x8c\xe3\xc8\xf1\xe2\xeb\x0f#\xac5\xab'


def connect_to_database():
    try:
        conn = mysql.connector.connect(user='jimboifyp', password='', host='localhost', port=2020, database='fypdbharith')
        print("Connection established successfully")
        return conn
    except mysql.connector.Error as error:
        print("Failed to connect to the database: {}".format(error))
        return None


@app.route('/all-graph', methods=['GET', 'POST'])
def allgraph():
    if 'username' in session:
        conn = connect_to_database()
        if conn is None:
            return "Failed to connect to the database. Check your database credentials."
        cursor = conn.cursor()

        # Get the selected month from the form data
        selected_month = request.form.get('month') or '1'

        # Get the number of days in the selected month
        _, num_days = monthrange(date.today().year, int(selected_month))

        temperature_data = []
        turbidity_data = []
        ph_value_data = []
        time_labels = []

        # Iterate over each day in the selected month
        for day in range(1, num_days + 1):
            query = f"SELECT DAY(date_time) AS day, AVG(temperature) AS avg_temperature, AVG(turbidity) AS avg_turbidity, AVG(phValue) AS avg_phValue FROM adruinodata WHERE MONTH(date_time) = {selected_month} AND DAY(date_time) = {day} GROUP BY DAY(date_time)"
            cursor.execute(query)
            data = cursor.fetchone()

            # Check if data is available for the day
            if data is not None:
                temperature_data.append(data[1])
                turbidity_data.append(data[2])
                ph_value_data.append(data[3])
                time_labels.append(data[0])

        conn.close()

        return render_template('linegraphall.html', temperature_data=temperature_data, turbidity_data=turbidity_data, ph_value_data=ph_value_data, time_labels=time_labels)
    else:
        return redirect('/login')

@app.route('/phvalue-graph')
def pHvalue_graph():
    if 'username' in session:
        conn = connect_to_database()

        if conn is None:
            return "Failed to connect to the database. Check your database credentials."

        cursor = conn.cursor()

        # Get the current date
        current_date = date.today().strftime('%Y-%m-%d')

        # Construct the query to retrieve pH value data for every 30 minutes of the day
        query = f"SELECT phValue, TIME(date_time) AS time FROM adruinodata WHERE TIMESTAMPDIFF(MINUTE, date_time, '{current_date}') % 30 = 0 AND DATE(date_time) = '{current_date}';"
        cursor.execute(query)
        data = cursor.fetchall()

        pHValue_data = [row[0] for row in data]
        phValueCric = [6.5 for row in data]
        time_labels = [(datetime.min + row[1]).time().strftime('%H:%M') for row in data]

        conn.close()

        return render_template('phvaluegraph.html', pHValue_data=pHValue_data, phValueCric=phValueCric, time_labels=time_labels)
    else:
        return redirect('/login')

@app.route('/turbidity-graph')
def turbidity_graph():
    if 'username' in session:
        conn = connect_to_database()

        if conn is None:
            return "Failed to connect to the database. Check your database credentials."

        cursor = conn.cursor()

        # Get the current date
        current_date = date.today().strftime('%Y-%m-%d')

        # Construct the query to retrieve turbidity data for every 30 minutes of the day
        query = f"SELECT turbidity, TIME(date_time) AS time FROM adruinodata WHERE TIMESTAMPDIFF(MINUTE, date_time, '{current_date}') % 30 = 0 AND DATE(date_time) = '{current_date}';"
        cursor.execute(query)
        data = cursor.fetchall()

        turbidity_data = [row[0] for row in data]
        turbidCric = [10 for row in data]
        time_labels = [(datetime.min + row[1]).time().strftime('%H:%M') for row in data]

        conn.close()

        return render_template('turbidgraph.html', turbidity_data=turbidity_data, turbidCric=turbidCric, time_labels=time_labels)
    else:
        return redirect('/login')

@app.route('/temperature-graph')
def temperature_graph():
    if 'username' in session:
        conn = connect_to_database()

        if conn is None:
            return "Failed to connect to the database. Check your database credentials."

        cursor = conn.cursor()

        # Get the current date
        current_date = date.today().strftime('%Y-%m-%d')

        # Construct the query to retrieve temperature data for every 30 minutes of the day
        query = f"SELECT temperature, TIME(date_time) AS time FROM adruinodata WHERE TIMESTAMPDIFF(MINUTE, date_time, '{current_date}') % 30 = 0 AND DATE(date_time) = '{current_date}';"
        cursor.execute(query)
        data = cursor.fetchall()

        temperature_data = [row[0] for row in data]
        tempCric = [28 for row in data]
        time_labels = [(datetime.min + row[1]).time().strftime('%H:%M') for row in data]

        conn.close()

        return render_template('tempgraph.html', temperature_data=temperature_data, tempCric=tempCric, time_labels=time_labels)
    else:
        return redirect('/login')

@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = connect_to_database()
        if conn is None:
            return "Failed to connect to the database. Check your database credentials."

        username = request.form['username']
        password = request.form['password']

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['username'] = user['username']
            return redirect('/admin')
        else:
            return render_template('index.html', error='Invalid username or password')

    return render_template('login.html')


@app.route('/admin')
def admin():
    if 'username' in session:
        conn = connect_to_database()

        if conn is None:
            return "Failed to connect to the database. Check your database credentials."

        cursor = conn.cursor()

        # Get the current date
        current_date = date.today().strftime('%Y-%m-%d')

        # Construct the query to retrieve data for the line graph
        query = f"SELECT temperature, turbidity, phValue, TIME(date_time) AS time FROM adruinodata WHERE TIMESTAMPDIFF(MINUTE, date_time, '{current_date}') % 30 = 0 AND DATE(date_time) = '{current_date}';"
        cursor.execute(query)
        data = cursor.fetchall()

        temperature_data = [row[0] for row in data]
        turbidity_data = [row[1] for row in data]
        ph_value_data = [row[2] for row in data]
        time_labels = [(datetime.min + row[3]).time().strftime('%H:%M') for row in data]

        conn.close()

        return render_template('linegraphall.html', temperature_data=temperature_data, turbidity_data=turbidity_data, ph_value_data=ph_value_data, time_labels=time_labels)
    else:
        return redirect('/login')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)