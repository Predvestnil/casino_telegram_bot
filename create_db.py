import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="LasVegas_casino_bot2022"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE db_cas;")
