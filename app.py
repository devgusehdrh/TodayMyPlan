from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

# 정규식 표현식 불러오기
import re

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# 비밀키 설정
SECRET_KEY = 'SPARTA'

# 몽고DB 연결
client = MongoClient('mongodb://127.0.0.1', 27017)
db = client.todaymyplan


@app.route('/')
def home():
    # 토큰 가져오기
    token_receive = request.cookies.get('mytoken')
    try:
        # 토큰 복호화
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 복호화한 페이로드에서 사용자 아이디 획득
        user_info = db.users.find_one({"username": payload["id"]})
        # 오늘 날짜에 해당하는 계획들을 데이터베이스에서 검색
        today_plans = db.plans.find({'today': datetime.now().strftime('%Y-%m-%d')})
        # 오늘 날짜에 현재 접속한 유저가 업로드 한 계획만 따로 검색
        my_plan = db.plans.find_one({'today': datetime.now().strftime('%Y-%m-%d'), 'username': user_info['username']})

        # 메인 페이지를 돌려주며 사용자 정보, 오늘 날짜에 해당하는 계획들을 함께 넘겨준다.
        return render_template('index.html', user_info=user_info, today_plans=today_plans, my_plan=my_plan)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 로그인 페이지
@app.route('/login')
def login():
    # 만약 토큰 값을 가지고 있을 경우 home 함수를 호출
    if request.cookies.get('mytoken'):
        return home()

    msg = request.args.get("msg")
    # 로그인 페이지로 이동
    return render_template('login.html', msg=msg)


# 로그인
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 아이디
    username_receive = request.form['username_give']
    # 패스워드
    password_receive = request.form['password_give']

    # 패스워드 암호화(해시함수)
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # 아이디, 패스워드 값을 이용하여 데이터베이스에서 검색
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    # 아이디 및 패스워드 일치하는 사용자가 있을 경우
    if result:
        # 페이로드에 아이디 및 토큰 파기 시간 저장
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24),  # 로그인 24시간 유지
        }
        # 토큰 생성(암호화)
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        # 토큰 반환
        return jsonify({'result': 'success', 'token': token})
    # 해당 정보가 없을 경우
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 회원가입
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    # 아이디
    username_receive = request.form['username_give']
    # 패스워드
    password_receive = request.form['password_give']
    # 닉네임
    nickname_receive = request.form['nickname_give']
    # 패스워드 해시값 획득
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # 데이터베이스에 저장
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "nickname": nickname_receive,  # 닉네임
        'profile_greeting': "",  # 기본 인사말
        "profile_pic_real": '유튜브_기본프로필_파랑.jpg'  # 프로필 이미지 경로

    }
    db.users.insert_one(doc)
    # 회원가입 성공 반환
    return jsonify({'result': 'success'})


# 회원가입 시 아이디 중복 확인
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    # 사용자 아이디 존재여부 확인
    exists = bool(db.users.find_one({"username": username_receive}))
    # 사용자 아이디 존재여부 반환
    return jsonify({'result': 'success', 'exists': exists})


# 회원가입 시 닉네임 중복 확인 - ( 현재 미작동 )
def check_dup_nick():
    nickname_receive = request.form['nickname_give']
    exists = bool(db.users.find_one({"nickname": nickname_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# 프로필 페이지
@app.route('/userinfo/<id>')
def userInfo(id):
    # 토큰 가져오기
    token_receive = request.cookies.get('mytoken')

    try:
        # 토큰 복호화
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # 복호화한 페이로드에서 사용자 아이디 획득
        user_info = db.users.find_one({"username": id}, {"_id": False})

        if user_info != None:
            # myPlan DB에 유저의 계획 변경

            # 오늘 날짜에 현재 접속한 유저가 업로드 한 계획만 따로 검색
            my_plan = db.plans.find_one({'today': datetime.now().strftime('%Y-%m-%d'), 'username': user_info['username']})

            status = (id == payload["id"])

            # user 페이지를 돌려주며 사용자 정보, 오늘 날짜에 해당하는 계획들을 함께 넘겨준다.
            return render_template('user.html', user_info=user_info, status=status, my_plan=my_plan)
        return redirect(url_for("home"))
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# 오늘 나의 계획을 등록하는 API입니다. (메인 페이지의 ajax가 콜합니다.)
@app.route('/POST/plan', methods=['POST'])
def post_plan():
    # 토큰 가져오기
    token_receive = request.cookies.get('mytoken')
    # 토큰이 유효한 경우에만 아래 처리 실행
    try:
        # 토큰을 복호화
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 유저DB에서 토큰["id"]를 키로 유저검색
        user_info = db.users.find_one({"username": payload["id"]})

        my_plan_receive = request.form['myPlan_give']  # 계획
        registration_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 등록시간 (초단위까지)
        today = datetime.now().strftime('%Y-%m-%d')  # 등록시간 (년월일)

        # [플랜 고유번호 부여]
        # plans DB에서 오늘 날짜로 등록된 전체 데이터 조회
        today_all_plans = list(db.plans.find({'today': today}, {'_id': False}))

        # 현재 로그인한 유저가 오늘 등록한 계획이 이미 있다면 알림을 띄우고 포스팅을 등록을 취소합니다.
        if len(list(db.plans.find({'today': today, 'username': user_info['username']}, {'_id': False}))) > 0:
            return jsonify({'result': 'fail', 'msg': '이미 계획이 등록 되었습니다.'})

        # 오늘 등록된 플랜이 하나도 없는 경우
        if len(today_all_plans) == 0:
            # 플랜 번호 1을 부여
            plan_no = 1
        # 등록된 플랜이 한 개라도 있는 경우
        else:
            # 람다함수를 이용, 플랜 번호를 key로 오름차순 정률 후 [-1]로 마지막 요소 추출
            last_plan = sorted(today_all_plans, key=lambda k: k['plan_no'])[-1]
            # 최근 등록된 플랜 번호에 1을 더해 플랜 번호 부여
            plan_no = last_plan['plan_no'] + 1

        doc = {
            'plan_no': plan_no,  # 고유번호
            'username': user_info['username'],  # 유저 아이디
            'nickname': user_info['nickname'],  # 유저 닉네임
            'my_plan': my_plan_receive,  # 계획
            'registration_time': registration_time,  # 등록시간 (초단위까지)
            'today': today  # 오늘 날짜
        }
        # myPlan DB에 유저의 계획 등록
        db.plans.insert_one(doc)
        # json형태로 response 반환
        return jsonify({'result': 'success', 'msg': '오늘의 계획이 등록되었습니다!'})

    except jwt.ExpiredSignatureError:
        return redirect(url_for("/"))


# 세부 페이지에 인덱스 없이 접속할 경우 home() 함수를 호출
@app.route('/detail')
def detail_none():
    return home()


# 오늘 계획 삭제
@app.route('/DELETE/plan', methods=['DELETE'])
def delete_plan():
    # 토큰 가져오기
    token_receive = request.cookies.get('mytoken')
    try:
        # 토큰 복호화
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 복호화한 페이로드에서 사용자 아이디 획득
        user_info = db.users.find_one({"username": payload["id"]})
        today = datetime.now().strftime('%Y-%m-%d')  # 오늘 날짜
        # 포스트 번호 획득
        plan_no = str(db.plans.find_one({'today': today, 'username': user_info['username']})['plan_no'])
        # 포스트 삭제 시 해당 포스트에 달린 코멘트 모두 삭제
        db.comments.delete_many({'today': today, 'plan_no': plan_no})
        # 포스트 삭제
        db.plans.delete_one({'today': today, 'username': user_info['username']})


        # 메인 페이지를 돌려주며 사용자 정보, 오늘 날짜에 해당하는 계획들을 함께 넘겨준다.
        return jsonify({'result': 'success', 'msg': '계획을 삭제 했어요.'})

    except jwt.ExpiredSignatureError:
        return redirect(url_for('/'))
    except jwt.exceptions.DecodeError:
        return redirect(url_for('/'))


# 프로필 변경
@app.route("/editInfo", methods=["POST"])
def editProfile():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        id = payload["id"]
        nickName = request.form["nickName"]
        greeting = request.form["greeting"]

        registration_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 등록시간 (초단위까지)
        today = datetime.now().strftime('%Y-%m-%d')  # 오늘 날짜

        new_doc = {
            "nickname": nickName,
            "profile_greeting": greeting
        }

        if 'file' in request.files:
            file = request.files["file"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"{id}.jpg"
            file.save("./static/img/profile/" + file_path)

            new_doc["profile_pic_real"] = file_path

        db.users.update_one({'username': payload['id']}, {'$set': new_doc})
        db.plans.update_one({'username': payload['id'], 'today': today},
                            {'$set': {'nickname': nickName, 'registration_time': registration_time}})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# 비밀번호 변경
@app.route("/editPw", methods=["POST"])
def changePw():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        password = request.form.get('password')
        pw_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        new_doc = {
            "password": pw_hash,
        }

        db.users.update_one({'username': payload['id']}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '비밀번호 변경 완료했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# 오늘 계획 수정
@app.route('/PUT/plan', methods=["PUT"])
def put_plan():
    # 토큰 가져오기
    token_receive = request.cookies.get('mytoken')
    # 토큰이 유효한 경우에만 아래 처리 실행
    try:
        # 토큰을 복호화
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 유저DB에서 토큰["id"]를 키로 유저검색
        user_info = db.users.find_one({"username": payload["id"]})

        my_plan_receive = request.form['myPlan_give']  # 계획
        registration_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 등록시간 (초단위까지)
        today = datetime.now().strftime('%Y-%m-%d')  # 오늘 날짜

        # myPlan DB에 유저의 계획 변경
        db.plans.update_one({'username': user_info['username'], 'today': today},
                            {'$set': {'my_plan': my_plan_receive, 'registration_time': registration_time}})

        # json형태로 response 반환
        return jsonify({'result': 'success', 'msg': '오늘의 계획을 수정 했어요!'})

    except jwt.ExpiredSignatureError:
        return redirect(url_for("/"))


# 세부 페이지 계획 포스팅 인덱스별 접속
@app.route('/detail/<plan_no>')
def detail(plan_no):
    # 토큰 가져오기
    token_receive = request.cookies.get('mytoken')
    # plan_no에서 숫자만 남기고 다른 문자를 지운다
    plan_no = re.sub('[^0-9]', ' ', plan_no).strip()
    try:
        # 토큰 복호화
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 복호화한 페이로드에서 사용자 아이디 획득
        user_info = db.users.find_one({"username": payload["id"]})
        # 사용자가 계획 클릭시 해당 계획 번호를 이용하여 포스트 정보 획득

        user_plan = db.plans.find_one({'today': datetime.now().strftime('%Y-%m-%d'),"plan_no": int(plan_no)},{'_id':False})

        # 오늘 날짜의 댓글 입력 닉네임과 코멘트, 페이지 넘버 획득
        comments = list(db.comments.find({'today': datetime.now().strftime('%Y-%m-%d')}, {'_id': False}))


        # 세부 페이지를 돌려주며 사용자 정보, 포스팅 정보, 포스팅 번호, 댓글 정보를 함께 넘겨준다.
        return render_template('detail.html', user_info=user_info, user_plan=user_plan, plan_no=plan_no,
                               comments=comments)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/detail/comment-registration', methods=['POST'])
def save_comment():
    # 토큰 가져오기
    token_receive = request.cookies.get('mytoken')
    try:
        # 토큰이 유효한 경우에만 아래 처리 실행
        # 토큰을 복호화
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 유저DB에서 토큰["id"]를 키로 유저검색
        user_info = db.users.find_one({"username": payload["id"]})

        registration_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 등록시간 (초단위까지)
        today = datetime.now().strftime('%Y-%m-%d')  # 등록시간 (년월일)

        # [코멘트 고유번호 부여]
        # plans DB에서 오늘 날짜로 등록된 전체 데이터 조회
        today_all_comments = list(db.comments.find({'today': today}, {'_id': False}))

        # 오늘 등록된 댓글이 하나도 없는 경우
        if len(today_all_comments) == 0:
            # 플랜 번호 1을 부여
            comment_no = 1
        # 등록된 댓글이 한 개라도 있는 경우
        else:
            # 람다함수를 이용, 플랜 번호를 key로 오름차순 정률 후 [-1]로 마지막 요소 추출
            last_comment = sorted(today_all_comments, key=lambda k: k['comment_no'])[-1]
            # 최근 등록된 댓글 번호에 1을 더해 플랜 번호 부여
            comment_no = last_comment['comment_no'] + 1

        comment_receive = request.form['comment_give']
        plan_no_receive = request.form['plan_no_give']

        doc = {
            'nickname': user_info['nickname'],
            'username': user_info['username'],
            'comment': comment_receive,
            'plan_no': plan_no_receive,
            'comment_no': comment_no,
            'today': today,
            'registration_time': registration_time
        }
        db.comments.insert_one(doc)

        return jsonify({'result': 'success', 'msg': '댓글을 등록 하였습니다!'})

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))


@app.route('/detail/comment-delete', methods=['DELETE'])
def delete_comment():
    # 토큰 가져오기
    token_receive = request.cookies.get('mytoken')
    try:
        # 토큰 복호화
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 복호화한 페이로드에서 사용자 아이디 획득
        user_info = db.users.find_one({"username": payload["id"]})
        today = datetime.now().strftime('%Y-%m-%d')  # 오늘 날짜
        plan_no = db.comments.find_one({'username': user_info['username']})

        # 날짜와 유저정보가 일치하는 댓글 데이터 삭제
        db.comments.delete_one({'today': today, 'username': user_info['username'], 'plan_no': plan_no['plan_no']})

        # 메인 페이지를 돌려주며 사용자 정보, 오늘 날짜에 해당하는 계획들을 함께 넘겨준다.
        return jsonify({'result': 'success', 'msg': '댓글을 삭제 했어요.'})

    except jwt.ExpiredSignatureError:
        return redirect(url_for('/'))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
