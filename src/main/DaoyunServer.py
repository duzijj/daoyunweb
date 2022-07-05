import pymysql
from flask import Flask, jsonify, request
import json
from flask_cors import *
import datetime
import os
from werkzeug.utils import secure_filename
from flask import send_file
import random
from send_message import send_message
import jwt
# import pandas as pd
from pandas import read_sql

app = Flask(__name__)
CORS(app, supports_credentials=True)
# 连接数据库

token_algorithm='HS256'
# userName,userId,过期时间,签发时间


data = ''
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    port=3306,
    db='daoyunweb',
    charset='utf8',
)

#注册输入验证码
@app.route('/send_id_code', methods=["GET","POST"])
def regist_by_id_code():
    global data
    data = request.args.to_dict()
    tel = data.get('tel')
    global send_msg
    send_msg = str(random.randint(99999,999999))
    msg = send_message(send_msg, tel)
    returndata = dict()
    if msg.SendStatusSet[0].Message=="send success":
        returndata['send_state']='success'
    else:
        returndata['send_state']='fail'
    return jsonify(returndata)


#注册接口
@app.route('/regist', methods=["GET","POST"])  
def regist():
    global data
    data = request.args.to_dict()
    print(data)
    tel = data.get('tel')
    msg_code = data.get('msgCode')
    # 返回的数据字典
    returndata = dict()
    # 建立游标
    cur = conn.cursor()
    
    #判断手机号是否注册过
    selectsql = "select User_Id from user"
    cur.execute(selectsql)
    result = cur.fetchall()
    result1 = [i[0] for i in result]
    if tel in result1:
        returndata['status'] = 0  # 注册失败为0
        returndata['data'] = ''
        returndata['msg'] = '手机号码已注册'
        cur.close()
        return jsonify(returndata)
    
    if msg_code!=send_msg:
        returndata['status'] = 0  # 注册成功为1
        returndata['msg'] = '验证码错误'
        returndata['data'] = ''
        cur.close()
        return jsonify(returndata)
        
    pwd = data.get('pwd')
    username = data.get('username')
    
    school = data.get('school')
    college = data.get('college')
    sex = data.get('sex')
    identity = data.get('identity')
    username = str(username)
    sex = str(sex)
    identity = str(identity) if identity else '学生'
    tel = str(tel)
    pwd = str(pwd)
    print("手机：", tel)
    print("密码：", pwd)
    
    try:
        cur.execute("insert into user(User_ID,User_Name,Password,school,college,sex,identity) values (%s, %s, %s, %s, %s, %s,%s)",(tel, username, pwd, school, college, sex, identity))
    except Exception as e:
        returndata['status'] = 0  # 注册失败为0
        returndata['data'] = ''
        returndata['msg'] = ''
        print("插入数据失败:", e)
        cur.close()
    else:
        conn.commit()
        returndata['status'] = 1  # 注册成功为1
        returndata['msg'] = ''
        returndata['data'] = ''
        print("插入成功")
        # 关闭游标
        cur.close()

    return jsonify(returndata)  # 返回内容

#登录接口
@app.route('/login', methods=["GET","POST"])
def login():
    global data    
    data = request.args.to_dict()
    userid = data.get("username")
    pwd = data.get("pwd")
    tel = data.get('tel')
    msg_code = data.get('msgCode')
    # 建立游标
    cur = conn.cursor()
    # 返回的数据字典
    returndata = dict()
    if userid:
        selectsql = "select * from user where User_Name = \"%s\" and Password = \"%s\"" %(userid, pwd)
    elif tel:
        if msg_code == send_msg:
            selectsql = "select * from user where User_Id = \"%s\"" %(tel)
        else:
            print("验证码错误")
            returndata['status'] = 0
            returndata['msg'] = '验证码错误'
            returndata['data'] = ''
            cur.close()
    else:
            print("手机号或用户名为空")
            returndata['status'] = 0
            returndata['msg'] = '手机号或用户名为空'
            returndata['data'] = ''
            cur.close()
    cur.execute(selectsql)
    
    result = cur.fetchone()
    if result:
        print("登录成功")
        # 返回的用户信息
        info_data = dict()
        User_ID = result[0]
        User_Name = result[1]
        school = result[3]
        college = result[4]
        sex = result[5]
        identity = result[6]
        info_data['User_ID'] = User_ID
        info_data['User_Name'] = User_Name
        info_data['school'] = school
        info_data['college'] = college
        info_data['sex'] = sex
        info_data['identity'] = identity
        print("用户存在")
        returndata = info_data
        returndata['status'] = 1
        returndata['msg'] = ''
        # returndata['data'] =info_data
        cur.close()
    else:
        print("账号或密码错误")
        returndata['status'] = 0
        returndata['msg'] = '账号或密码错误'
        returndata['data'] = ''
        cur.close()

    return jsonify(returndata)

# 创建班课接口
@app.route('/construct_class', methods=["GET", "POST"])
def construct_class():
    global data
    data = request.args.to_dict()
    
    userid = data.get('userid')
    classname = data.get('class_name')
    classname=str(classname)
    print(classname)
    teachername = data.get('teacher_name')
    print(teachername)
    grade = data.get('grade')
    print(grade)
    grade = int(grade)
    comments = data.get('comments')
    print(comments)
    # 建立游标
    cur = conn.cursor()
    # 返回的数据字典
    returndata = dict()
    selectsql = "select count(*) from class_info"
    result=cur.execute(selectsql)
    count=cur.fetchall()
    class_id = count[0][0]+1
    print(class_id)
    
    # import pandas as pd
    # selectsql = "select * from class_info"
    # df=pd.read_sql(selectsql,con=conn)
    
    try:

        insertsql1 = 'insert into sign_state values (%d,%d)' % (class_id, 0)
        cur.execute("insert into class_info(class_id,class_name,userid,teacher_name,grade,comments) values (%s,%s,%s,%s,%s,%s)",(class_id,classname,userid,teachername,grade,comments))
        cur.execute("insert into class_member(class_id,user_id) values (%s,%s)" % (class_id, userid))
        cur.execute(insertsql1)

    except Exception as e:
        returndata['status'] = 0  # 创建课程失败为0
        returndata['msg'] = ''
        returndata['data'] = ''
        print("创建课程失败:", e)
        cur.close()
    else:
        conn.commit()
        returndata['status'] = 1  # 创建课程成功为1
        returndata['msg'] = ''
        returndata['data'] = ''
        print("创建课程成功")
        cur.close()

    return jsonify(returndata)

#获取班课列表接口
@app.route('/get_class', methods=["GET","POST"])
def get_class():
    userid = request.form.get('userid')
    print(userid)
    classType = request.form.get('class_type')
    classType = int(classType)
    print(classType)
    # 建立游标
    cur = conn.cursor()
    # 返回数据
    returndata = dict()
    if classType==1:  #为1代表创建的班级
        selectsql = "select * from class_info where userid = '%s'" % (userid)
        cur.execute(selectsql)
        contents = cur.fetchall()
        if contents is None:
            returndata['status'] = 0  #0表示没有创建的班级
            returndata['msg'] = ''
            returndata['data'] = ''
            return jsonify(returndata)
        else:
            # 创建列表
            dataList = []
            for row in contents:  # 遍历查询内容
                class_id = row[0]
                class_name = row[1]
                teacher_name = row[3]
                grade = row[4]
                comments = row[5]
                dataDic = dict()
                dataDic['class_id'] = class_id
                dataDic['class_name'] = class_name
                dataDic['teacher_name'] = teacher_name
                dataDic['grade'] = grade
                dataDic['comments'] = comments
                dataList.append(dataDic)
            returndata['status'] = 1  # 1表示有创建的班级
            returndata['msg'] = ''
            returndata['data'] = dataList
            cur.close()
            return jsonify(returndata)

    else:  #为0代表加入的课程
        selectsql  = "select * from class_info where class_id in (select class_id from class_member where user_id = %s)" %(userid)
        cur.execute(selectsql)
        contents = cur.fetchall()
        print(contents)
        if not contents:
            returndata['status'] = 0  # 0表示没有加入的班级
            returndata['msg'] = ''
            returndata['data'] = ''
            return jsonify(returndata)
        else:
            # 创建列表
            dataList = []
            for row in contents:  # 遍历查询内容
                class_id = row[0]
                class_name = row[1]
                teacher_name = row[3]
                grade = row[4]
                comments = row[5]
                dataDic = dict()
                dataDic['class_id'] = class_id
                dataDic['class_name'] = class_name
                dataDic['teacher_name'] = teacher_name
                dataDic['grade'] = grade
                dataDic['comments'] = comments
                dataList.append(dataDic)
            returndata['status'] = 1  # 1表示有创建的班级
            returndata['msg'] = ''
            returndata['data'] = dataList
            cur.close()
            return jsonify(returndata)

#加入班课接口
@app.route('/join_class',methods=["GET","POST"])
def join_class():
    my_Class_Id = request.form.get('classid')
    my_User_Id = request.form.get('userid')
    #建立游标
    cur = conn.cursor()
    #返回的数据字典
    returndata = dict()
    checkExistSql = "select * from class_info where class_id=%s"%(my_Class_Id)
    cur.execute(checkExistSql)
    contents = cur.fetchall()
    print(contents)
    if not contents:
        returndata['status'] = 0  # 加入失败
        returndata['msg'] = ''
        returndata['data'] = ''
        cur.close()
    else:
        try:
            insertsql = "insert into class_member(class_id,user_id) values (%s,%s)"%(my_Class_Id,my_User_Id)
            cur.execute(insertsql)
        except Exception as e:
            returndata['status']=0 #加入失败
            returndata['msg'] = ''
            returndata['data'] = ''
            print("插入数据失败:", e)
            cur.close()
        else:
            conn.commit()
            returndata['status'] = 1 #加入成功
            returndata['msg'] = ''
            returndata['data'] = ''
            print("插入成功")
            # 关闭游标
            cur.close()

    return jsonify(returndata)

#老师设置开始签到
@app.route('/begin_sign_in',methods=["GET","POST"])
def begin_sign_in():
    class_id = request.form.get('class_id')
    class_id=int(class_id)
    updatasql='update Sign_state set Is_sign = %d where class_id = %d'%(1,class_id)
    # 建立游标
    cur = conn.cursor()
    # 返回的数据字典
    returndata = dict()
    try:
        cur.execute(updatasql)
    except Exception as e:
        returndata['status']=0 #开启签到失败
        returndata['msg'] = ''
        returndata['data'] = ''
        print("开启签到失败:", e)
        cur.close()
    else:
        conn.commit()
        returndata['status'] = 1 #开启签到成功
        returndata['msg'] = ''
        returndata['data'] = ''
        print("开启签到成功")
        # 关闭游标
        cur.close()
    return jsonify(returndata)

#老师设置结束签到
@app.route('/cancel_sign_in',methods=["GET","POST"])
def cancel_sign_in():
    class_id = request.form.get('class_id')
    class_id = int(class_id)
    updatasql = 'update Sign_state set Is_sign = %d where class_id = %d' % (0, class_id)
    # 建立游标
    cur = conn.cursor()
    # 返回的数据字典
    returndata = dict()
    try:
        cur.execute(updatasql)
    except Exception as e:
        returndata['status'] = 0  # 结束签到失败
        returndata['msg'] = ''
        returndata['data'] = ''
        print("结束签到失败:", e)
        cur.close()
    else:
        conn.commit()
        returndata['status'] = 1  # 结束签到成功
        returndata['msg'] = ''
        returndata['data'] = ''
        print("结束签到成功")
        # 关闭游标
        cur.close()
    return jsonify(returndata)

#学生签到记录
@app.route('/sign_record',methods=["GET","POST"])
def sign_record():
    class_id=request.form.get('class_id')
    user_id=request.form.get('user_id')
    class_id=int(class_id)
    dateandtime = datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S")
    insertsql="insert into sign_in values (%s,%s,%s,%s)"%(class_id,user_id,1,dateandtime)
    # 建立游标
    cur = conn.cursor()
    # 返回的数据字典
    returndata = dict()
    selectsql='select Is_sign from sign_state where class_id = %s' %(class_id)
    cur.execute(selectsql)
    result=cur.fetchone()
    if result[0]==1:
        try:
            cur.execute("insert into sign_in values (%s,%s,%s,%s)",(class_id,user_id,1,dateandtime))
        except Exception as e:
            returndata['status'] = 0  # 签到失败
            returndata['msg'] = ''
            returndata['data'] = ''
            print("签到失败:", e)
            cur.close()
        else:
            conn.commit()
            returndata['status'] = 1  # 签到成功
            returndata['msg'] = ''
            returndata['data'] = ''
            print("签到成功")
            # 关闭游标
            cur.close()
    else:
        returndata['status'] = 0  # 签到失败
        returndata['msg'] = ''
        returndata['data'] = ''
        print("签到失败:")
        cur.close()

    return jsonify(returndata)

#判断用户名（即手机号）是否存在（使用手机验证码登录时使用到）
@app.route('/is_exist',methods=["GET","POST"])
def is_exist():
    tel=request.form.get('tel')
    selectsql = "select User_ID from user where User_ID = %s" %(tel)
    # 建立游标
    cur = conn.cursor()
    # 返回的数据字典
    returndata = dict()
    cur.execute(selectsql)
    result = cur.fetchone()
    if result:
        print("用户存在")
        returndata['status'] = 1
        returndata['msg'] = ''
        returndata['data'] = ''
        cur.close()
    else:
        print("用户不存在")
        returndata['status'] = 0
        returndata['msg'] = ''
        returndata['data'] = ''
        cur.close()

    return jsonify(returndata)

#根据手机号码，返回用户对象
@app.route('/get_user_by_phone',methods=["GET","POST"])
def get_user_by_phone():
    tel=request.form.get('tel')
    selectsql = "select User_ID, User_Name, school, college, sex, identity from user where User_ID = %s" % (tel)
    # 建立游标
    cur = conn.cursor()
    # 返回的数据字典
    returndata = dict()
    # 返回的用户信息
    info_data = dict()
    cur.execute(selectsql)
    result = cur.fetchone()
    if result:
        User_ID = result[0]
        User_Name = result[1]
        school = result[2]
        college = result[3]
        sex = result[4]
        identity = result[5]
        info_data['User_ID'] = User_ID
        info_data['User_Name'] = User_Name
        info_data['school'] = school
        info_data['college'] = college
        info_data['sex'] = sex
        info_data['identity'] = identity
        print("用户存在")
        returndata['status'] = 1 #用户存在
        returndata['msg'] = ''
        returndata['data'] = info_data
        cur.close()
    else:
        print("用户不存在")
        returndata['status'] = 0
        returndata['msg'] = ''
        returndata['data'] = ''
        cur.close()

    return jsonify(returndata)


##返回班课成员
@app.route('/get_class_member', methods=["GET", "POST"])
def get_class_member():
    class_id = request.form.get('class_id')
    class_id = int(class_id)
    selectsql = "select * from user where User_ID in (select user_id from class_member where class_id = %d)" % (class_id)
    # 建立游标
    cur = conn.cursor()
    # 返回的数据字典
    returndata = dict()
    # 返回的用户信息
    info_data = dict()
    cur.execute(selectsql)
    result = cur.fetchall()
    if result:
        # 创建列表
        dataList = []
        for row in result:
            info_data['userid'] = row[0]
            info_data['username'] = row[1]
            info_data['school'] = row[3]
            info_data['college'] = row[4]
            info_data['sex'] = row[5]
            info_data['identity'] = row[6]
            dataList.append(info_data)
        returndata['status'] = 1  # 返回成功
        returndata['msg'] = ''
        returndata['data'] = dataList
        cur.close()
    else:
        returndata['status'] = 0  # 返回成功
        returndata['msg'] = ''
        returndata['data'] = ''
        cur.close()
    return jsonify(returndata)


##返回作业列表
@app.route('/return_class_work', methods=["GET", "POST"])
def return_class_work():
    class_id = request.form.get('class_id')
    class_id = int(class_id)
    selectsql = "select work_name from wwork where class_id = %d" % (class_id)
    # 建立游标
    cur = conn.cursor()
    # 返回的数据字典
    returndata = dict()
    cur.execute(selectsql)
    result = cur.fetchall()
    if result:
        dataList = []
        for row in result:
            dataList.append(row[0])
        returndata['status'] = 1  # 返回成功
        returndata['msg'] = ''
        returndata['data'] = dataList
        cur.close()
    else:
        returndata['status'] = 0  # 返回成功
        returndata['msg'] = ''
        returndata['data'] = ''
        cur.close()
    return jsonify(returndata)

##接收上传ZIP文件
@app.route('/upload_work', methods=["GET", "POST"])
def upload_work():
    work_id=request.form.get('work_id')
    work_id=int(work_id)
    print(work_id)
    class_id = request.form.get('class_id')
    class_id=int(class_id)
    print(class_id)
    user_id = request.form.get('user_id')
    getfile = request.files.get('file')
    print(getfile)
    print('---')
    filename =secure_filename(getfile.filename) # 获取上传文件的文件名

    print(filename)
    dirname = "C:/Users/Administrator/Desktop/work"
    insersql = "insert into wwork values(%d,\"%s\",%d,%s)" % (class_id, filename,work_id,user_id)
    # 建立游标
    cur = conn.cursor()
    # 返回的数据字典
    returndata = dict()
    try:
        getfile.save(os.path.join(dirname, filename))  # 保存文件
        cur.execute(insersql)
    except Exception as e:
        returndata['status'] = 0  # 上传失败
        returndata['msg'] = ''
        returndata['data'] = ''
        cur.close()
        print(e)
    else:
        conn.commit()
        returndata['status'] = 1  # 上传成功
        returndata['msg'] = ''
        returndata['data'] = ''
        cur.close()
    return jsonify(returndata)

# 判断是否已经上传文件
@app.route('/checkup_loadfile',methods=["POST"])
def checkup_loadfile():
    workId = request.form.get('workId')
    workId = int(workId)
    print(workId)
    userId = request.form.get('userId')
    print(userId)

    classId = request.form.get('classId')
    classId = int(classId)
    print(classId)

    selectSQL = "select * from wwork where class_id=%d and work_id=%d and user_id=%s" % (classId, workId, userId)
    cur = conn.cursor()
    cur.execute(selectSQL)
    result = cur.fetchone()
    returndata = dict()
    if result:
        returndata['status'] = 1  # 已经上传
        returndata['msg'] = ''
        returndata['data'] = ''
    else :
        returndata['status'] = 0  # 还未上传
        returndata['msg'] = ''
        returndata['data'] = ''
    cur.close()
    return jsonify(returndata)

#下载课程作业
@app.route('/download_work',methods=["GET","POST"])
def download_work():
    filename=request.form.get('filename')
    dirname="C:/Users/Administrator/Desktop/work"
    file_path = os.path.join(dirname, filename)
     # 向api返回（图片）文件

    return send_file(file_path)

##退出班课
@app.route('/quit_class',methods=["GET","POST"])
def quit_class():
    class_id=request.form.get('class_id')
    class_id=int(class_id)
    user_id=request.form.get('user_id')
    selectSql = "select userid from class_info where class_id=%d"%(class_id)

    deletesql="delete from class_member where class_id=%d and user_id=%s"%(class_id,user_id)
    deletesql2="delete from class_info where class_id=%d"%(class_id)
    deletesql3="delete from class_member where class_id=%d"%(class_id)

    # 建立游标
    cur = conn.cursor()
    # 返回的数据字典
    returndata = dict()
    cur.execute(selectSql)
    result = cur.fetchone()
    print("---res:" + result[0])
    print("---userid:" + user_id)
    print(result[0] != user_id)
    if result[0] != user_id: #班课成员退出
        try:
            cur.execute(deletesql)
        except Exception as e:

            returndata['status'] = 0  # 删除失败
            returndata['msg'] = ''
            returndata['data'] = ''
            cur.close()
        else:
            conn.commit()
            returndata['status'] = 1  # 上传成功
            returndata['msg'] = ''
            returndata['data'] = ''
            cur.close()
    else:   #班课创建者退出
        try:
            cur.execute(deletesql2)
            cur.execute(deletesql3)
        except Exception as e:
            print(e)
            returndata['status'] = 0  # 删除失败
            returndata['msg'] = ''
            returndata['data'] = ''
            cur.close()
        else:
            conn.commit()
            returndata['status'] = 1  # 上传成功
            returndata['msg'] = ''
            returndata['data'] = ''
            cur.close()
    return jsonify(returndata)

##发布作业
@app.route('/publish_work',methods=["GET","POST"])
def publish_work():
    class_id=request.form.get('class_id')
    class_id = int(class_id)
    work_requirement=request.form.get('work_requirement')
    work_name=request.form.get('work_name')
    work_content=request.form.get('work_content')
    # 建立游标
    cur = conn.cursor()
    # 返回的数据字典
    returndata = dict()
    selectsql = "select count(*) from work_description"
    result = cur.execute(selectsql)
    count = cur.fetchall()
    work_id = count[0][0] + 1
    work_id=int(work_id)
    print(work_id)
    try:
        insertsql="insert into work_description(work_id,class_id,work_name,work_content,work_requirement) values(%d,%d,\"%s\",\"%s\",\"%s\")"%(work_id,class_id,work_name,work_content,work_requirement)
        cur.execute(insertsql)
    except Exception as e:
        returndata['status'] = 0  # 发布作业失败
        returndata['msg'] = ''
        returndata['data'] = ''
        cur.close()
        print(e)
    else:
        conn.commit()
        returndata['status'] = 1  # 发布作业成功
        returndata['msg'] = ''
        returndata['data'] = work_id
        cur.close()
    return jsonify(returndata)

##返回作业详情
@app.route('/query_work',methods=["GET","POST"])
def query_work():
    work_id=request.form.get('work_id')
    work_id=int(work_id)
    # 建立游标
    cur = conn.cursor()
    # 返回的数据字典
    returndata = dict()
    selecsql="select * from work_description where work_id=%d"%(work_id)
    cur.execute(selecsql)
    result=cur.fetchone()
    if result:
        info_data=dict()
        info_data['work_requirement']=result[1]
        info_data['work_cnotent']=result[2]
        returndata['status'] = 1  # 查询作业成功
        returndata['msg'] = ''
        returndata['data'] = info_data
        cur.close()
    else:
        returndata['status'] = 0  # 查询作业失败
        returndata['msg'] = ''
        returndata['data'] = ''
        cur.close()
    return jsonify(returndata)

##返回作业列表
@app.route('/get_homework', methods=["GET", "POST"])
def get_homework():
    class_id = request.form.get('class_id')
    class_id = int(class_id)
    selectsql = "select * from work_description where class_id = %d" % (class_id)
    # 建立游标
    cur = conn.cursor()
    # 返回的数据字典
    returndata = dict()
    # 返回的用户信息
    info_data = dict()
    cur.execute(selectsql)
    result = cur.fetchall()
    if result:
        # 创建列表
        dataList = []
        for row in result:
            info_data['workId'] = row[0]
            info_data['classId'] = row[1]
            info_data['workName'] = row[2]
            info_data['workContent'] = row[3]
            info_data['workRequirement'] = row[4]
            dataList.append(info_data)
            info_data = dict()
        print(dataList)
        returndata['status'] = 1  # 返回成功
        returndata['msg'] = ''
        returndata['data'] = dataList
        cur.close()
    else:
        returndata['status'] = 0  # 返回成功
        returndata['msg'] = ''
        returndata['data'] = ''
        cur.close()
    return jsonify(returndata)

#前端字典页面
@app.route('/data_dict', methods=["GET", "POST"])
def data_dict():
    # page是当前页数,pagesize是当前页数的数据数量,dictName字典名称
    global data
    data = request.args.to_dict()
    returndata = dict()
    dictName = data.get('dictName')
    dictDescription = data.get('dictDescription')
    delNameList = request.args.getlist('delNameList[]')
    deldictName = data.get('deldictName')
    command = data.get('command')
    
    # if command=='count':
    #     user_data = read_sql('Select * from %s'%dictName, con=conn)
    #     returndata['status'] = 1  # 返回成功
    #     returndata['msg'] = '当前已有用户数量为'
    #     returndata['data'] = str(len(user_data))
        
    if command=='query':
        page = int(data.get('Page'))
        size = int(data.get('pageSize'))
        
        if dictName:
            dict_df = read_sql('Select * from data_dict where name="%s"'%dictName, con=conn)
        else:
            dict_df = read_sql('Select * from data_dict', con=conn)
        selected_dict_df = dict_df.iloc[(page-1)*size : page*size]
        # selected_dict_df.columns = ['编号','字典','描述']
        if len(dict_df)==0:
            returndata['status'] = 0  # 失败
            returndata['msg'] = '用户数据为空'
            returndata['data'] = [dict_df.to_json()]
        elif len(selected_dict_df)==0:
            returndata['status'] = 0  # 失败
            returndata['msg'] = '超出页码范围'
            returndata['data'] = [selected_dict_df.to_json()]
        else:
            returndata['status'] = 1  # 返回成功
            returndata['msg'] = '查询成功'
            returndata['data'] = [selected_dict_df.to_json()]
            
    elif command in ['add_dict','update_dict']:
        selectsql = 'Select * from data_dict'
        items = read_sql(selectsql, con=conn)
        exist_items = items.name.tolist()
        if dictName in exist_items and command=='add_dict':
            returndata['status'] = 0  # 失败
            returndata['msg'] = '该字段已存在'
            returndata['data'] = ''
        else:
            cur = conn.cursor()
            if command=='add_dict':
                id_number = items.id.max() + 1
                cur.execute('insert into data_dict(id,name,description) values (%s,%s,%s);',(id_number,dictName,dictDescription))
            else:
                cur.execute('UPDATE data_dict SET description=%s WHERE name=%s;',(dictDescription,dictName))
            conn.commit()
            print("插入成功")
            cur.close()
            returndata['status'] = 1  # 成功
            returndata['msg'] = '插入成功'
            items = read_sql(selectsql, con=conn)
            # items.columns = ['编号','字典','描述']
            returndata['data'] = [items.to_json()]
        
    elif command == 'delete_dict':
        delete = delNameList if len(delNameList)>0 else [deldictName]
        cur = conn.cursor()
        for i in delete:
            cur.execute('delete from data_dict where name=%s;',(i))
        conn.commit()
        print('删除成功')
        cur.close()
        returndata['status'] = 1  # 成功
        returndata['msg'] = '删除成功'
        items = read_sql('Select * from data_dict', con=conn)
        # items.columns = ['编号','字典','描述']
        returndata['data'] = [items.to_json()]
        
    return jsonify(returndata)

#前端字典详情页面
@app.route('/dict_item', methods=["GET", "POST"])
def dict_item():
    # page是当前页数,pagesize是当前页数的数据数量,dictName字典名称
    global data, delItemNameList
    data = request.args.to_dict()
    returndata = dict()
    dictName = data.get('dictName')
    itemName = data.get('itemName')
    isDefault = data.get('isDefault')
    delItemNameList = request.args.getlist('delItemNameList[]')
    command = data.get('command')
    
    # if command=='count':
    #     user_data = read_sql('Select * from %s'%dictName, con=conn)
    #     returndata['status'] = 1  # 返回成功
    #     returndata['msg'] = '当前已有用户数量为'
    #     returndata['data'] = str(len(user_data))
        
    if command=='query':
        page = int(data.get('page'))
        size = int(data.get('pageSize'))
        
        if itemName:
            dict_df = read_sql('Select data_name,is_default from dict_set where data_name="%s" and from_dict="%s"'%(itemName,dictName), con=conn)
        else:
            dict_df = read_sql('Select data_name,is_default from dict_set where from_dict="%s"'%dictName, con=conn)
        selected_dict_df = dict_df.iloc[(page-1)*size : page*size]
        # selected_dict_df.columns=['数据名称','是否默认']
        if len(dict_df)==0:
            returndata['status'] = 0  # 失败
            returndata['msg'] = '用户数据为空'
            returndata['data'] = [dict_df.to_json()]
        elif len(selected_dict_df)==0:
            returndata['status'] = 0  # 失败
            returndata['msg'] = '超出页码范围'
            returndata['data'] = [selected_dict_df.to_json()]
        else:
            returndata['status'] = 1  # 返回成功
            returndata['msg'] = '查询成功'
            returndata['data'] = [selected_dict_df.to_json()]
            
    elif command in ['add_item','update_item']:
        selectsql = 'Select * from dict_set'
        items = read_sql(selectsql, con=conn)
        exist_items = items[items['from_dict']==dictName].data_name.tolist()
        if itemName in exist_items and command=='add_item':
            returndata['status'] = 0  # 失败
            returndata['msg'] = '该字段已存在'
            returndata['data'] = ''
        else:
            cur = conn.cursor()
            if command=='add_item':
                cur.execute('insert into dict_set(data_name,is_default,from_dict) values (%s,%s,%s);',(itemName,isDefault,dictName))
            else:
                cur.execute('UPDATE dict_set SET is_default=%s WHERE data_name=%s and from_dict=%s;',(isDefault,itemName,dictName))
            conn.commit()
            print("插入成功")
            cur.close()
            returndata['status'] = 1  # 成功
            returndata['msg'] = '插入成功'
            items = read_sql(selectsql, con=conn)
            # items.columns=['数据名称','是否默认']
            returndata['data'] = [items.to_json()]
        
    elif command == 'delete_item':
        delete = delItemNameList if len(delItemNameList)>0 else [itemName]
        cur = conn.cursor()
        for i in delete:
            cur.execute('delete from dict_set where data_name=%s and from_dict=%s;',(i,dictName))
        conn.commit()
        print('删除成功')
        cur.close()
        returndata['status'] = 1  # 成功
        returndata['msg'] = '删除成功'
        items = read_sql('Select * from dict_set', con=conn)
        # items.columns=['数据名称','是否默认']
        returndata['data'] = [items.to_json()]

    return jsonify(returndata)

#系统参数
@app.route('/system_parameter', methods=["GET", "POST"])
def system_parameter():
    global data
    data = request.args.to_dict()
    returndata = dict()
    
    tableName = data.get('tableName')
    item = data.get('item')
    value = data.get('value')
    if tableName=='table3':
        item = '签到范围'
    command = data.get('command')
    
    if command=='query':
        dict_df = read_sql('Select * from system_parameter', con=conn)
        dict_df1 = dict_df[dict_df.description=='table1'].values.tolist()
        dict_df2 = dict_df[dict_df.description=='table2'].values.tolist()
        dict_df3 = dict_df[dict_df.description=='table3'].values.tolist()
        returndata['data'] = [dict_df1, dict_df2, dict_df3]
        # selected_dict_df.columns = ['编号','字典','描述']
        
    elif command == 'update':
        cur = conn.cursor()
        cur.execute('UPDATE system_parameter SET value=%s WHERE item=%s and description=%s;',(value,item,tableName))
        conn.commit()
        print("插入成功")
        cur.close()
        returndata['status'] = 1  # 成功
        returndata['msg'] = '插入成功'
        returndata['data'] = ''
        
    
        
    return jsonify(returndata)
    
    
if __name__ == '__main__':
    # http://121.5.166.241:8080
    app.run(host='172.17.0.11', port='8080')  # 运行程序