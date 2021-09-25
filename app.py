from project import create_app
from flask import Flask
from environment_variable import set_env
import os

app = create_app()
kkk = set_env()     #環境変数をset_envで設定するように変更
print(os.environ.get('FLASK_DEBUG'))

if __name__ == '__main__':
    app.run()

