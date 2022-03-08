from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

import xml.etree.ElementTree as elemTree
tree = elemTree.parse("static/config.xml")
SECRET_KEY = tree.find('string[@name="SECRET_KEY"]').text


app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.miniProject



@app.route('/')
def home():
    token_receive= request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        user_info = db.users.find_one({"id":payload["id"]})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return  redirect(url_for("login",msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login",msg="로그인 정보가 존재하지 않습니다."))
#     닉네임으로 사용자 정보 조회
@app.route('/userinfo/<id>')
def getUser(id):
    # 토큰 가져오기

    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (id == payload["id"])
        user_info = db.users.find_one({"id": id},{"_id":False,"pw":False})
        return render_template('user.html', user_info=user_info, status=status)
    # return render_template('user.html')
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))



@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/signUp')
def signUp():
    return render_template('signUp.html')

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
        'profile_greeting':"",
        'profile_pic':'/static/img/profile/유튜브_기본프로필_파랑.jpg',
        "profile_pic_real": '/static/img/profile/유튜브_기본프로필_파랑.jpg'
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
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success','token':token})
    return '', 401

@app.route("/editInfo", methods=["POST"])
def editProfile():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        id = payload["id"]
        nickName = request.form["nickName"]
        greeting = request.form["greeting"]
        file = request.files["file"]

        new_doc = {
            "nickName": nickName,
            "profile_info": greeting
        }
        if file:
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"{id}.{jpg}"
            file.save("./static/img/profile/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.users.update_one({'id': payload['id']}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
