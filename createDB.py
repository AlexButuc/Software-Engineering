import mysql.connector

mydb = mysql.connector.connect(
  host="database-1.cv4842ms2b5l.eu-north-1.rds.amazonaws.com",
  user="admin",
  password="P*B&a33v+!7xj+*"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE my_bike_data")