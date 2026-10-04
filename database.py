import sqlite3
def get_connection():
  connection = sqlite3.connect("users_data.db", check_same_thread=False)
  connection.row_factory = sqlite3.Row
  return connection


def create_table():
    connection = get_connection()
    try:
        cursor = connection.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)

     )"""
        )

    

        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL)""")
#         cursor.execute("""
#     ALTER TABLE users
#     ADD COLUMN role TEXT NOT NULL DEFAULT 'user'
  
# """)
        
        connection.commit()

   
    finally:
        connection.close()
create_table()    



def get_all_tasks(user_id):
    connection=get_connection()
    try:
        cursor = connection.cursor()
    
        cursor.execute("SELECT * FROM tasks WHERE user_id = ?",
                   (user_id,))
        tasks = cursor.fetchall()
    
        return [dict(task) for task in tasks]
    finally:    
        connection.close()
def get_task(task_id,user_id):
    connection=get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
        "SELECT * FROM tasks WHERE id = ? and user_id = ?",
        (task_id,user_id)
         )
        task = cursor.fetchone()
        if task is None:
         return None
        return dict(task)
    finally:    
        connection.close()
def insert_task(name, status,user_id):
    connection=get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
        "INSERT INTO tasks (name, status , user_id) VALUES (?, ? , ?)",
        (name, status , user_id)
         )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def delete_task(task_id,user_id):
    connection=get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
        "DELETE FROM tasks WHERE id = ? and user_id = ?",
        (task_id,user_id)
         )
        connection.commit()
    finally:
        connection.close()

def update_task_db(task_id, name, status,user_id):
    connection=get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
        "UPDATE tasks SET name = ?, status = ? WHERE id = ? and user_id = ?",
        (name, status, task_id,user_id)
         )
        connection.commit()    
    finally:
        connection.close()

def create_user(username,password_hash):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""INSERT INTO users (username,password_hash) VALUES (?,?)""",(username,password_hash))
        connection.commit()
        user_id = cursor.lastrowid
        return user_id
    finally:
        connection.close()
def get_user_by_username(username):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM users WHERE username = ?""" , 
                   (username,))
        user = cursor.fetchone()
    

        if user is None :
            return None
        return dict(user)
    finally:
        connection.close()

def get_user_by_id(user_id):
   connection = get_connection()
   try:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?" , (user_id,))
    user = cursor.fetchone()

    if user is None :
        return None
    return dict(user) 

   finally:
       connection.close()
def get_all_users():
   connection = get_connection()
   try:
    cursor = connection.cursor()
    cursor.execute("SELECT user_id , username , role FROM users ")


    users = cursor.fetchall()

    
    
    return [dict(user) for user in users]
   finally:
    connection.close()
   
# connection = get_connection()
# cursor = connection.cursor()

# cursor.execute("SELECT * FROM users")

# for user in cursor.fetchall():
#     print(dict(user))

# connection.close()