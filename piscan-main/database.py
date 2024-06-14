import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="toor@44",
    database="piscan"
)

# Create a cursor object to interact and parse the database
mycursor = mydb.cursor()
try:
    # Create the imagedata table with a TEXT column(Text is used because of we don't know the size of the extracted text)
    mycursor.execute(
        "CREATE TABLE imagedata (id INT AUTO_INCREMENT PRIMARY KEY, info TEXT NOT NULL)")

except mysql.connector.errors.ProgrammingError:
    pass
