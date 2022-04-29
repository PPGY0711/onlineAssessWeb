# -*- coding: utf-8 -*-
"""
@objective: application interface for Flask
@author: pengguanyan
@update date: 2022/04/21
"""
import sys
import os

# print('当前 Python 解释器目录：')
# print(os.path.dirname(sys.executable))
from flask import Flask, render_template, request, redirect, url_for, json, flash, send_from_directory, send_file, \
    make_response, session
from werkzeug.utils import secure_filename
from session import DBSession
from flask_wtf.csrf import CSRFProtect
from forms import *
from models import User, Building, BuildingData
from flask_login import login_user, login_required
from flask_login import LoginManager, current_user, AnonymousUserMixin
from flask_login import logout_user
import yaml
import json
from utils import LineFit, generateUUID, get_code, sendEmail
import datetime

# 读取全局配置文件
f = open('config.yaml', encoding='utf-8')
config = yaml.safe_load(f)
# print(config)
db_obj = config['mysql']
app_obj = config['app']
f.close()
ALLOWED_EXTENSIONS = app_obj['ALLOWED_EXTENSIONS']
csrf = CSRFProtect()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = app_obj['UPLOAD_FOLDER']
app.config['JSON_FOLDER'] = app_obj['JSON_FOLDER']
app.config['PIC_FOLDER'] = app_obj['PIC_FOLDER']
app.config['REPORT_FOLDER'] = app_obj['REPORT_FOLDER']
app.config['AVATAR_FOLDER'] = app_obj['AVATAR_FOLDER']
# 配置 SELECT_KEY
app.config['SECRET_KEY'] = '3c2d9d261a464e4e8814c5a39aa72f1c'
# 创建MySQL数据库连接
dbs = DBSession(db_obj=db_obj)
app.secret_key = os.urandom(24)
csrf.init_app(app=app)
# use login manager to manage session
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app=app)
bl = dict()
data_cnt = -1
start_index = 0


# 这个callback函数用于reload User object，根据session中存储的user id
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id, dbs)


@app.route('/home/<string:username>')
@login_required
def home(username):
    profile = current_user.profile
    return render_template('homepage.html', show_login_and_register_item=False, username=username, user_profile=profile)


@app.route('/')
def homepage():
    # 这里判断一下是否有session，不然还是需要返回home的
    if 'uname' in session:
        print('home')
        print(session['uname'])
        return redirect(url_for('home', username=session['uname']))
    else:
        return render_template('homepage.html', show_login_and_register_item=True, username="")


@csrf.exempt
@app.route('/reset-password', methods=['GET', 'POST'])
def reset():
    form = resetPwdForm()
    if request.method == 'GET':
        return render_template('forgot-password.html', form=form)
    else:
        # 有用户重置密码成功，跳转至登录页面
        return redirect(url_for('login'))


@csrf.exempt
@app.route('/sendValidCode', methods=["POST"])
def sendValidCode():
    data = json.loads(request.data)
    email = data['email']
    # 要查询一下当前的邮箱地址是否有效
    if User.get_id_static(email, dbs) is None:
        return json.dumps({'msg': 'error'})
    else:
        code = get_code()
        genTime = datetime.datetime.now()
        User.insert_code(email, code, genTime, dbs)
        mail_msg = """
        <p>欢迎使用HVAC-SIG空调系统能耗在线评估平台！</p>
        <p>验证码：{}</a></p>
        """.format(code)
        subject = 'HVAC-SIG密码重置验证码'
        while sendEmail(mail_msg, email, subject) == 1:
            sendEmail(mail_msg, email, subject)
        # "邮件发送成功","Error: 无法发送邮件"
        return json.dumps({'msg': 'success', "code": code,
                           "sendTime": genTime.strftime("%Y/%m/%d %H:%M:%S")})


@csrf.exempt
@app.route('/handleReset', methods=['POST'])
def handleReset():
    # 此时是用户发送重置密码，需要查询数据库
    # print('有用户要重置密码，查询数据库')
    data = json.loads(request.data)
    username = data.get('username', None)
    password = data.get('password', None)
    repeatPassword = data.get('repeatPassword', None)
    inputTime = data.get('inputTime', None)
    code = data.get('code', None)
    # print(username)
    # print(password)
    # print(repeatPassword)
    # print(inputTime)
    # 1. 查询该用户名是否已经被注册
    ret = User.verify_code(username, code, inputTime, dbs)
    if ret['msg'] == 'error':
        return "error: 验证码输入错误，请重试！"
    elif ret['msg'] == 'expired':
        return "error: 验证码已过期，请重试！"
    else:
        # 要改密码
        User.modify_password(username, password, dbs)
        return "Success!"


@csrf.exempt
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        if 'uname' in session:
            print(session['uname'])
            return redirect(url_for('index', username=session['uname']))
        else:
            # 没有登录，继续向下判断cookie
            if 'uname' in request.cookies:
                # 曾经记住过密码,取出值保存进session
                uname = request.cookies.get('uname')
                session['uname'] = uname
                return render_template('login.html', form=form, uname=uname)
            else:
                # 从home页面或者其他页面点击跳转到登录页面，直接返回登录页面
                current_user = AnonymousUserMixin()
                return render_template('login.html', form=form, uname="")
    else:
        # 此时是用户发送登录请求，需要查询数据库
        print('有用户要登录，查询数据库')
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        remember_me = request.form.get('ck', False)
        # print(remember_me)
        user = User(username, dbs)
        if user.verify_password(password):
            resp = redirect(url_for('index', username=username))
            if remember_me:
                resp.set_cookie('uname', username, 60*60*24*30)
            login_user(user, remember=True if remember_me is not False else False)
            return resp
        else:
            return redirect(url_for('login'))


@csrf.exempt
@app.route('/handleLogin', methods=['POST'])
def handleLogin():
    # 此时是用户发送登录请求，需要查询数据库
    # print('有用户要登录，查询数据库')
    data = json.loads(request.data)
    username = data.get('username', None)
    password = data.get('password', None)
    if User.isUsernameTaken(username, dbs) is False:
        return "error: 当前邮箱未被注册！"
    else:
        user = User(username, dbs)
        if user.verify_password(password) is False:
            return "error: 密码输入错误，请重试！"
        else:
            return "Success!"


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'GET':
        # 从home页面或者其他页面点击跳转到注册页面，直接返回注册页面
        return render_template('register.html', form=form)
    else:
        # 此时是用户发送登录请求，需要查询数据库
        # print('有新用户要注册，查询数据库')
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        User.register(username=username, password=password, dbs=dbs)
        return redirect(url_for('login'))


@csrf.exempt
@app.route('/handleRegister', methods=['POST'])
def handleRegister():
    # 此时是用户发送注册请求，需要查询数据库
    # print('有用户要注册，查询数据库')
    data = json.loads(request.data)
    username = data.get('username', None)
    password = data.get('password', None)
    repeatPassword = data.get('repeatPassword', None)
    # print(username)
    # print(password)
    # print(repeatPassword)
    # 1. 查询该用户名是否已经被注册
    if User.isUsernameTaken(username, dbs) is True:
        return "error: 当前用户名已被注册！"
    else:
        # 2. 当前用户名可用，继续查看两次密码输入是否正确
        if password != repeatPassword:
            return "error: 两次密码输入不一致，请重试！"
        else:
            return "Success!"


@app.route('/index/<string:username>')
@login_required
def index(username):
    return render_template('index.html', username=username, user_profile=current_user.profile)


@app.route('/profile/<string:username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    pform = personModifyForm()
    cbform = buildingForm()
    mbform = buildingForm()
    dbform = buildingSimpleForm()
    aform = avatarForm()
    global bl, data_cnt
    if request.method == 'GET':
        if data_cnt == -1:
            bl = dict()
            bl['data'], data_cnt = Building.getBuildingsOfUser(current_user.profile['user_id'], dbs)
        return render_template('profile.html', pform=pform, cbform=cbform, mbform=mbform,
                               dbform=dbform, aform=aform, username=username,
                               user_profile=current_user.profile, bl=bl, data_cnt=data_cnt)
    else:
        bl = dict()
        # 更新user_profile

        bl['data'], data_cnt = Building.getBuildingsOfUser(current_user.profile['user_id'], dbs)
        return render_template('profile.html', pform=pform, cbform=cbform, mbform=mbform,
                               dbform=dbform, aform=aform, username=username,
                               user_profile=current_user.profile, bl=bl, data_cnt=data_cnt)


@app.route('/buildingInfo/<string:username>', methods=['GET', 'POST'])
@login_required
def building(username):
    mbform = buildingForm()
    dform = dataForm()
    cform = dataDeleteForm()
    global bl, data_cnt, start_index
    if request.method == 'GET':
        if data_cnt == -1:
            bl = dict()
            bl['data'], data_cnt = Building.getBuildingsOfUser(current_user.profile['user_id'], dbs)
        return render_template('buildlingInfo.html', username=username, user_profile=current_user.profile, dform=dform,
                               mbform=mbform, cform=cform, bl=json.dumps(bl), data_cnt=data_cnt, startIndex=start_index)
    else:
        if data_cnt == -1:
            start_index = 0
        else:
            if 'startIndex' in request.form:
                start_index = int(request.form.get('startIndex', 0))
            elif 'uStartIndex' in request.form:
                # POST来自上传文件
                dataInfo = dict()
                start_index = int(request.form.get('uStartIndex', 0))
                dataInfo['building_id'] = request.form.get('fBId', None)
                dataInfo['case_id'] = request.form.get('newFileId', None)
                data, has_fix, data_type = LineFit.readFromJSON(os.path.join(app.config['JSON_FOLDER'],
                                                                             dataInfo['case_id'] + ".json"))
                dataInfo['has_fix'] = has_fix
                dataInfo['data_type'] = data_type
                dataInfo['data'] = {"records": data}
                BuildingData.insertData(dataInfo, dbs)
                bl = dict()
                bl['data'], data_cnt = Building.getBuildingsOfUser(current_user.profile['user_id'], dbs)
            else:
                # POST来自删除数据
                start_index = int(request.form.get('cStartIndex', 0))
                bl = dict()
                bl['data'], data_cnt = Building.getBuildingsOfUser(current_user.profile['user_id'], dbs)
    return render_template('buildlingInfo.html', username=username, user_profile=current_user.profile, dform=dform,
                           mbform=mbform, cform=cform, bl=json.dumps(bl), data_cnt=data_cnt, startIndex=start_index)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    resp = redirect(url_for('login'))
    resp.delete_cookie('uname')
    session.pop('uname', None)
    return resp


@csrf.exempt
@app.route('/modifyProfile', methods=['POST'])
def modifyProfile():
    data = json.loads(request.data)
    current_user.modify_profile(data)
    return "Success"


@csrf.exempt
@app.route('/modifyBuildingInfo', methods=['POST'])
def modifyBuildingInfo():
    data = json.loads(request.data)
    print(data)
    global start_index
    start_index = int(data['startIndex'])
    Building.modifyBuildingInfo(data, dbs)
    return "Success"


@csrf.exempt
@app.route('/createBuildingInfo', methods=['POST'])
def createBuildingInfo():
    data = json.loads(request.data)
    print(data)
    Building.createBuildingInfo(data, dbs)
    return "Success"


@csrf.exempt
@app.route('/deleteBuildingInfo', methods=['POST'])
def deleteBuildingInfo():
    data = json.loads(request.data)
    print(data)
    Building.deleteBuildingInfo(data, dbs)
    # 同时把相关的报告都删除
    return "Success"


@csrf.exempt
@app.route('/showBuildingInfo', methods=['POST'])
def showBuildingInfo():
    global start_index
    if request.data is not None:
        print(request.data)
        data = json.loads(request.data)
        start_index = int(data['startIndex'])
    return "Success"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@csrf.exempt
@app.route('/uploadDataFile', methods=['POST'])
def uploadDataFile():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        print(file.filename)
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        print('成功上传文件 %s ,保存至目录 %s' % (filename, app.config['UPLOAD_FOLDER']))
        # 生成新的文件名标识，用于之后建立标识
        fileId = generateUUID()
        filename = fileId + "." + ext
        filePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(filePath)
        file.save(filePath)
        if ext == 'csv':
            data = LineFit.readFromExcel(filePath, ext)
        else:
            data = LineFit.readFromExcel(filePath, ext)
        # print(data)
        # 文件仅在upload_folder暂存，读取数据后删除
        # 移除
        os.remove(filePath)
        if data.shape[1] != 2 and data.shape[1] != 3:
            return "error: 数据格式错误，可能存在数据列数过多或者缺失现象，请检查后重试！"
        else:
            if data.shape[1] == 2:
                data.columns = ['temperature', 'energy_consume']
            else:
                data.columns = ['temperature', 'energy_consume', 'fix_consume']
            with open(os.path.join(app.config['JSON_FOLDER'], fileId + ".json"), 'w') as jf:
                dj = data.to_json(orient='records')
                parsed = json.loads(dj)
                json.dump(parsed, jf, indent=4)
            data.to_excel(os.path.join(app.config['UPLOAD_FOLDER'], fileId + "_data.xlsx"))
            return fileId


@csrf.exempt
@app.route('/deleteDataInfo', methods=['POST'])
def deleteDataInfo():
    data = json.loads(request.data)
    # print(data)
    BuildingData.deleteData(data, dbs)
    return "Success"


@csrf.exempt
@app.route('/download', methods=['POST'])
def handleDownloadPost():
    # 实现文件下载功能
    # print('实现文件下载')
    # print(request.data)
    data = json.loads(request.data)
    return "/download/data/%s" % data.get("caseId")


@csrf.exempt
@app.route('/getReportData', methods=["POST"])
def calculateResult():
    data = json.loads(request.data)
    case_id = data.get("caseId")
    caseInfo = dict()
    caseInfo['caseId'] = case_id
    caseInfo['coldSource'] = data.get("coldSource")
    # 增加了返回值y30和e1_e0
    pics, y30, e1_e0, level, flag = LineFit.generateReportOfDataCase(caseInfo, os.path.join(app.config['JSON_FOLDER']),
                                                                     os.path.join(app.config['PIC_FOLDER']))
    # 在这里获取建筑信息
    ret_info = dict()
    ret_info['pics'] = pics
    if flag == "long":
        ret_info['y30'] = "%.4f" % y30
        ret_info['e1'] = "%.4f" % e1_e0[0]
        ret_info['e0'] = "%.4f" % e1_e0[1]
        ret_info['k'] = "%.4f" % e1_e0[2]
        ret_info['t0'] = "%.4f" % e1_e0[3]
        ret_info['e1_e0'] = "%.4f" % (e1_e0[0] + e1_e0[1])
    ret_info['level'] = level
    ret_info['type'] = flag
    # print(ret_info)
    return json.dumps(ret_info)


@app.route('/download/data/<path:filename>')
def sendDataFile(filename):
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename + "_data.xlsx")):
        # 版本2：如果./dataSheet文件夹下有数据文件，则直接返回
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']),
                                   path=filename + "_data.xlsx", as_attachment=True)
    else:
        # 版本1：上传文件删除后把json写成文件返回
        # 把json写成excel返回
        import pandas as pd
        import io
        import urllib
        df = pd.read_json(os.path.join(app.config['JSON_FOLDER'], filename + ".json"))
        out = io.BytesIO()
        writer = pd.ExcelWriter(out, engine='xlsxwriter')
        df.to_excel(excel_writer=writer, sheet_name='Sheet1', index=False)
        writer.save()
        out.seek(0)
        file_name = urllib.parse.quote(filename + "_data.xlsx")
        # 没有处理过的存成文件，下次访问直接发文件
        df.to_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename + "_data.xlsx"))
        return send_file(out, as_attachment=True, attachment_filename=file_name)


@app.route('/download/report/<path:filename>')
def sendReportFile(filename):
    # 调整：把长期数据的两张图画在了一起
    return send_from_directory(os.path.join(app.config['REPORT_FOLDER']),
                               path=filename + "_result.pdf", as_attachment=True)


@app.route('/guide/<string:username>')
@login_required
def guide(username):
    return render_template('guide.html', username=username, user_profile=current_user.profile)


# show photo
@app.route('/show/<string:filename>', methods=['GET'])
def show_photo(filename):
    file_dir = os.path.join(app.config['PIC_FOLDER'])
    if request.method == 'GET':
        if filename is None:
            pass
        else:
            image_data = open(os.path.join(file_dir, '%s' % filename), "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/png'
            return response
    else:
        pass


@csrf.exempt
@app.route('/uploadAvatarLocal/<string:username>', methods=['POST'])
def uploadAvatarLocal(username):
    print("upload send to backend")
    if 'file' not in request.files:
        return "Error"
    file = request.files['file']
    print(file)
    if file.filename == '':
        return "Error"
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        # username = request.files['username']
        print('成功上传文件 %s ,保存至目录 %s' % (filename, app.config['AVATAR_FOLDER']))
        # 生成新的文件名标识，用于之后建立标识
        fileId = generateUUID()
        filename = fileId + "." + ext
        filePath = os.path.join(app.config['AVATAR_FOLDER'], filename)
        print(filePath)
        file.save(filePath)
        current_user.modify_avatar(username, filename, dbs)
        # 修改数据库内容
        return {"state": 0}


@csrf.exempt
@app.route('/uploadAvatarSystem', methods=['POST'])
def uploadAvatarSystem():
    data = json.loads(request.data)
    print(data)
    # 修改数据库内容
    current_user.modify_avatar(data['username'], data['src'], dbs)
    return {"state": 0}


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000)
    app.run(host='127.0.0.1', port=5000)
    app.jinja_env.variable_start_string = '{{ '
    app.jinja_env.variable_end_string = ' }}'

# TODO
# 1.完善报告内容，需要加上结果页（函数拟合结果函数+ABCDE分区意义）done
# 2.调大原理页面字体（done）
# 3.数据拟合前先清洗，去掉离群点后拟合（done）
# 4.数据上传时做完整性检验和正确性检验，意见反馈给前台，得到前台的处理结果后再继续
# 5.数据存在后台，不做删除(done)
# 6.画图函数完善，E(30)的点加上横线指示且写上值(done)
# 7.写一个网站使用指南页面（网站主要功能，用途，数据上传规范、相关处理形式等）done
# 8.不紧要TODO：写一个忘记密码/修改密码页面（要改数据库结构啊，直接把用户名字段改成了email字段 done
# 9.三个图标加上学校网站跳转(done)，实验室那个link挂了，与我无关
# 10.完成上传头像，上次建筑物图片
