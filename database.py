import pymysql

def get_db_connection():
    return pymysql.connect(
        host="localhost",       # Change if your DB host is different
        user="root",            # Your MySQL username
        password="1234",        # Your MySQL password
        database="epl_prediction",  # Your database name
        cursorclass=pymysql.cursors.DictCursor  # Return results as dictionaries
    )
