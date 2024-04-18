import pymysql

# database configure
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Zcy032619",
    "db": "web_transfer",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}


def create_database():
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    query = 'create database if not exists web_transfer'
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()


def create_table_images():
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    query = 'use web_transfer'
    cursor.execute(query)
    query2 = ('create table if not exists images (ImageID int AUTO_INCREMENT PRIMARY KEY, ImagePath varchar(255), '
              'UploadDate datetime, Email varchar(255))')
    cursor.execute(query2)
    connection.commit()
    cursor.close()
    connection.close()


def create_table_users():
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    query = 'use web_transfer'
    cursor.execute(query)
    query2 = ('create table if not exists users (UserID int AUTO_INCREMENT PRIMARY KEY, Email varchar(255), '
              'PasswordHash char(64), RegisterDate datetime, hometown varchar(100), name varchar(100))')
    cursor.execute(query2)
    connection.commit()
    cursor.close()
    connection.close()


create_database()
create_table_images()
create_table_users()
