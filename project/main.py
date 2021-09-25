import os

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_login.utils import logout_user
from linebot import LineBotApi
from linebot.models import TextSendMessage

from . import db
from .models import User

# import re


main = Blueprint('main', __name__)
YOUR_CHANNEL_ACCESS_TOKEN = os.getenv("YOUR_CHANNEL_ACCESS_TOKEN", 'none')
YOUR_CHANNEL_SECRET = os.getenv("YOUR_CHANNEL_SECRET", 'none')
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.line_id)


@main.route('/option')
@login_required
def option():
    if current_user.manaba_id != 'default':
        return redirect(url_for('main.option_name', name=current_user.manaba_id))
    return render_template('option.html', manaba_id='')


@main.route('/option/')
@login_required
def option_slash():
    flash('IDは1文字以上8文字以内です & パスワードを入力してください。')
    return render_template('option.html', manaba_id='')


@main.route('/option/<string:name>')
@login_required
def option_name(name):
    if current_user.manaba_id == 'default':
        return render_template('option.html', manaba_id='')
    return render_template('option.html', manaba_id=name)


@main.route('/option', methods=['POST'])
@login_required
def option_post():
    name = request.form.get('manabaid')
    manabapass = request.form.get('manabapass')
    line_id = current_user.line_id
    manaba_id_pattern = '[A-Z][0-9]{2}[A-Z][0-9]{4}'

    # if re.match(manaba_id_pattern, name):
    #     name_correct_bool = True
    # else:
    #     name_correct_bool = False

    if name == '' or len(name) > 8:
        name_correct_bool = False
    else:
        name_correct_bool = True

    if not manabapass == '':
        manabapass_correct_bool = True
    else:
        manabapass_correct_bool = False

    if not name_correct_bool and not manabapass_correct_bool:
        flash('IDは1文字以上8文字以内です & パスワードを入力してください。')
    elif not manabapass_correct_bool:
        flash('パスワードを入力してください')
    elif not name_correct_bool:
        flash('IDは1文字以上8文字以内です')
    else:
        user = User.query.filter_by(line_id=line_id).first()
        if not user:
            # LINE IDが見つけられなかった場合の超例外的措置
            logout_user()
            flash('A serious error occured. Please Retry.')
            return redirect(url_for('line.index'))
        else:
            # ログイン情報書き換え
            user.manaba_id = name
            user.manaba_pass = manabapass
            db.session.commit()
            line_bot_api.push_message(
                user.line_id, messages=TextSendMessage(
                    text='情報が更新されました！'
                )
            )
            flash('Login info saved perfectly!')
            return redirect(url_for('main.option_name', name=user.manaba_id))

    return redirect(url_for('main.option_name', name=name))


@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('line.index'))


@main.route('/logout', methods=['POST'])
def logout_post():
    logout_user()
    return redirect(url_for('line.index'))


@main.route("/slide")
def slide():
    return redirect('https://docs.google.com/presentation/d/1_o-gU-dgIPcFfE4NC1aC5JUML3CbrGIk7e2-F93CJ4Q/edit?usp=sharing')
