import mysql.connector

mydb = mysql.connector.connect(
  host="database-1.crosc2qqg17q.eu-north-1.rds.amazonaws.com",
  user="admin",
  password="P*B&a33v+!7xj+*"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE my_bike_data")