import pymysql
from flask import Flask, render_template, request, session, redirect
import telebot
from config import db_config, settings

#Настройки
SECRET_KEY = settings['secret-key']
ROOT_USER = settings['root-user']

bot = telebot.TeleBot(settings['tg-bot'])

#Приложение
app = Flask(__name__)
app.config.from_object(__name__)

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
    #Преметы которые есть
    all_p = []
    #Словарь данных
    dic_data = []
    
    with conn.cursor() as cur:
        
        #Добавляю какие пары были в этот день
        cur.execute(f"SELECT p_name FROM attendance WHERE date(date_reg) = '{current_date}'")
        q = cur.fetchall()
        for p in q:
            if p[0] not in all_p:
                all_p.append(p[0])
                         
        #Люди которые есть в этот день
        # cur.execute(f"SELECT students.name, students.surname, schedule.p_name FROM ((attendance INNER JOIN students ON attendance.student_id = students.telegram_id) INNER JOIN schedule ON attendance.p_id = schedule.id) WHERE date_reg = '{current_date}'")
        for para in range(len(all_p)):
            cur.execute(f"SELECT name, surname FROM students INNER JOIN attendance ON telegram_id=student_id WHERE date(date_reg)='{current_date}' AND p_name='{all_p[para]}'")
            desc = cur.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row)) for row in cur.fetchall()]
            
            dic_data.append([all_p[para], [], []])
            
            for i in range(len(data)):
                full_name = data[i]['name']+' '+data[i]['surname']
                dic_data[para][1].append(full_name)
                    
        #Люди которых нет
        for para in range(len(all_p)):
            cur.execute(f"SELECT name, surname FROM students WHERE telegram_id NOT IN (SELECT student_id FROM attendance WHERE date(date_reg)='{current_date}' AND p_name='{all_p[para]}')")
            desc = cur.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row)) for row in cur.fetchall()]
            
            for i in range(len(data)):
                full_name = data[i]['name']+' '+data[i]['surname']
                dic_data[para][2].append(full_name)
    
    num = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten'] #Для bootstrap
    
    return render_template('list_users.html',dic=dic_data, date=current_date, num=num, logged=logged)

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect('/')

# if __name__ == '__main__':
#     app.run(debug=True)