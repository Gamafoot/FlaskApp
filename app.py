import mysql.connector
from flask import Flask, render_template, request, session, redirect

DATABASE = 'attendance.sqlite3'
SECRET_KEY = 'ad96e4f6c2a6ff454e6e63a8717a8726984e9230'

db_config = {
    'host':'localhost',
    'user':'root',
    'pass':'root',
}

app = Flask(__name__)
app.config.from_object(__name__)

#-----------------------Покдючение к базе данных-----------------------
def connection_db(db_host, user_name, user_password, db_name):
    db = None
    try:
        db = mysql.connector.connect(
            host = db_host,
            user = user_name,
            passwd = user_password,
            database = db_name
        )
        print('Подключился')
    except Exception as ex:
        print(f'Ошибка подключения к базе:\n {ex} \n')
    return db

conn = connection_db('localhost', 'root', '', 'test1') #Переменная с подключённой базой

#-----------------------------Код сервера--------------------------------
@app.route('/', methods=['POST', 'GET'])
def login():
    logged = None
    
    if 'logged' not in session:
        logged = True

    #-----------------------------Авторизация--------------------------------
    
    if request.method == 'POST':
        user = request.form['login']
        
        with conn.cursor() as cur:
            cur.execute("SELECT telegram_id FROM students")
            users = cur.fetchall()
            
        for i in users:
            if str(i[0]) == user:
                session['logged'] = 1
                return redirect('/')

    #------------------------------Получение списка из бд-------------------------------
    with conn.cursor() as cur:
        cur.execute("SELECT name, surname FROM students")
        list_users = cur.fetchall()
    
    return render_template('index.html', users=list_users, logged=logged)
    
        

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')