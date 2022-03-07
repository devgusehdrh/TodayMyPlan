from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.miniProject

SECRET_KEY  = "secretkey"


@app.route('/')
def home():
    token_receive= request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        user_info = db.users.find_one({"id":payload["id"]})
        return render_template('index.html', nickname=user_info["nickName"])
    except jwt.ExpiredSignatureError:
        return  redirect(url_for("login",msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login",msg="로그인 정보가 존재하지 않습니다."))

@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/sign')
def signUp():
    return render_template('sign.html')

@app.route("/signup", methods=["POST"])
def signUp_post():
    id_receive = request.form['user_id']
    pw_receive = request.form['password']
    nickName_receive = request.form['nickName']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    doc = {
        'id': id_receive,
        'pw': pw_hash,
        'nickName': nickName_receive,
    }

    db.users.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})
@app.route("/login_check", methods=["POST"])
def web_login_post():
    id_receive = request.form['user_id']
    pw_receive = request.form['password']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.users.find({'id': id_receive,'pw':pw_hash}, {'_id': False})


    if result is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.utcnow() + timedelta(seconds=5)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success','token':token})
    return '', 401



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
