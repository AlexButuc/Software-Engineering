from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

@app.route('/')
def index():
    conn = mysql.connector.connect(
        host="database-1.cv4842ms2b5l.eu-north-1.rds.amazonaws.com",
        user="admin",
        password="P*B&a33v+!7xj+*",
        database="my_bike_data"
    )
    cursor = conn.cursor(dictionary=True)  # This allows you to fetch rows as dictionaries
    cursor.execute("SELECT * FROM stations")
    stations = cursor.fetchall()  # This will now return a list of dictionaries
    conn.close()

    return render_template("index.html", stations=stations)

if __name__ == '__main__':
    app.run(debug=True)