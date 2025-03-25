import mysql.connector
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()

def connect_to_db():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            port=os.getenv("MYSQL_PORT")
        )
        print("Connection Success")
        return mydb
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    
def save_dataframe_to_db(df, connection, table_name):
    if connection is None:
        print("No database connection available.")
        return

    cursor = connection.cursor()

    try:
        cols = ",".join([f"`{col}`" for col in df.columns])

        placeholders = ",".join(["%s"] * len(df.columns))

        insert_query = f"INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders})"

        for row in df.itertuples(index=False):
            try:
                cursor.execute(insert_query, tuple(row))
            except mysql.connector.Error as err:
                print(f"Error inserting row: {err}")
                connection.rollback()
                return

        connection.commit()
        print(f"Successfully inserted {len(df)} rows into `{table_name}`")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        connection.rollback()

    finally:
        cursor.close()
        
def connect_to_sqlalchemy(host, user, password, database):
    try:
        engine = create_engine(f'mysql+pymysql://{user}:{password}@127.0.0.1/{database}')
        print("Successfully connected to MySQL database using SQLAlchemy")
        return engine
    except Exception as err:
        print(f"Error connecting to MySQL using SQLAlchemy: {err}")
        return None
