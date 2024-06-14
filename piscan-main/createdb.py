import mysql.connector

# connect to the database in the local server using housseine credential as a test
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="toor@44",
    database="piscan"
)

# create the cursor to parse and interact with the database
mycursor = mydb.cursor()

# try to create the table for storing data if it does not exist
try:
    mycursor.execute(
        "CREATE TABLE imagedata (id INT AUTO_INCREMENT PRIMARY KEY, info TEXT NOT NULL)")
except mysql.connector.errors.ProgrammingError:
    pass
