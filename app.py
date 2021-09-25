from project import create_app
from environment_variable import set_env

app = create_app()
kkk = set_env()     #環境変数をset_envで設定するように変更

if __name__ == '__main__':
    app.run()

