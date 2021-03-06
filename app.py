import pymysql
from flask import Flask, render_template, request, session, redirect
import telebot
from config import db_config

DATABASE = 'attendance.sqlite3'
SECRET_KEY = 'ad96e4f6c2a6ff454e6e63a8717a8726984e9230'
ROOT_USER = '402501778'

bot = telebot.TeleBot('2005932607:AAFAF_LCjBaM-Hkj_WDKnTUof0F0s0mJOlk')

app = Flask(__name__)
app.config.from_object(__name__)
# big dick boys club
#-----------------------Покдючение к базе данных-----------------------
def connection_db(db_host, user_name, user_password, db_name):
    db = None
    try:
        db = pymysql.connect(
            host = db_host,
            user = user_name,
            passwd = user_password,
            database = db_name
        )
        print('Подключился')
    except Exception as ex:
        print(f'Ошибка подключения к базе:\n {ex} \n')
    return db

conn = connection_db(db_config['host'],db_config['user'], db_config['passwd'], db_config['db']) #Переменная с подключённой базой
conn.cursor()
#-----------------------------Код сервера--------------------------------
@app.route('/', methods=['POST', 'GET'])
def main():
    logged = None
    if 'logged' in session:
        logged = True

    #-----------------------------Авторизация--------------------------------
    if request.method == 'POST':
        if 'logged' not in session and request.form['login'] == ROOT_USER:
            session['logged'] = 1
            return redirect('/')
    #------------------------------Получение списка из бд-------------------------------
    with conn.cursor() as cur:
        cur.execute("SELECT name, surname FROM students")
        list_users = cur.fetchall()
    
    return render_template('list_users.html', users=list_users, logged=logged)

date = ''

@app.route('/send_request', methods=['POST', 'GET'])
def send_request():
    if 'logged' in session:
        logged = True
        
    if request.method == 'POST':
        if request.form.get('date_send') == 'date':
            if len(request.form['date'].split('-')) > 2:
                href = request.form['date'].split('-')
                year = href[0]
                mouth = href[1]
                day = href[2]
                return redirect(f'{year}/{mouth}/{day}')
            return redirect('/')
        # Не удалять!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # if request.form.get('message_send') == 'msg':
        #     message = request.form.get('message')
        #     with conn.cursor() as cursore:
        #         cursore = conn.cursor()
        #         cursore.execute("SELECT telegram_id FROM students")
        #         students = cursore.fetchall()
        #         for student in range(len(students)):
        #             print(students[student])
        #             try:
        #                 bot.send_message(students[student][0], message)
        #             except Exception as ex:
        #                 print(f'Ошибка при отправки сообщения: {ex}')
            
    return render_template('base.html', logged=logged)
    
@app.route('/<year>/<mouth>/<day>', methods=['GET'])
def date_list(year,mouth,day):
    if 'logged' in session:
        logged = True
        
    current_date = f'{year}-{mouth}-{day}'
    print(current_date)
    #Преметы которые есть
    all_p = []
    #Словарь данных
    dic_data = []
    
    with conn.cursor() as cur:
        cur.execute(f"SELECT students.name, students.surname, schedule.p_name FROM ((attendance INNER JOIN students ON attendance.student_id = students.telegram_id) INNER JOIN schedule ON attendance.p_id = schedule.id) WHERE date_reg = '{current_date}'")
        desc = cur.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row)) for row in cur.fetchall()]
        
        for p in data:
            if p['p_name'] not in all_p:
                all_p.append(p['p_name'])
                
        for k in range(len(all_p)):
            dic_data.append([])
            dic_data[k].append(all_p[k])
            dic_data[k].append([])
            
        for i in range(len(data)):
            for j in range(len(dic_data)):
                if data[i]['p_name'] == dic_data[j][0]:
                    full_name = data[i]['name'] +" "+data[i]['surname']
                    dic_data[j][1].append(full_name)
    
    num = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten']
    
    return render_template('list_users.html',dic=dic_data, date=current_date, num=num, logged=logged)

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)