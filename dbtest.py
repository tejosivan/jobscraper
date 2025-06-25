import psycopg2
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

print("USER:", os.getenv("user"))
print("HOST:", os.getenv("host"))
print("PORT:", os.getenv("port"))
print("DBNAME:", os.getenv("dbname"))   
# Try to connect
try:
    connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )
    print("✅ Connection successful!")

    cursor = connection.cursor()
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print("🕒 Current DB time:", result)

    cursor.close()
    connection.close()
    print("✅ Connection closed.")

except Exception as e:
    print(f"❌ Failed to connect: {e}")
