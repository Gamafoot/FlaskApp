#!/usr/bin/python3
import sys
print(sys.version)
sys.path.insert(0,"/home/portream/web/flask.portream.ru/public_html/")
sys.path.insert(0,"/home/portream/web/flask.portream.ru/public_html/.venv/lib/python3.9/site-packages")
activate_this = '/home/portream/web/flask.portream.ru/public_html/.venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from app import app as application
