from flask import Flask, jsonify,request, json
import base64
from io import BytesIO
import image
import pymysql as mysql
import smtplib
from email.mime.text import MIMEText
import string
import random

app = Flask(__name__) 
@app.route('/signup',methods=['POST','GET']) 
def signup(): 
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()
    
    if request.method == 'POST':
        u_id = request.values['u_id']
        u_passwd = request.values['u_passwd']
        u_name = request.values['u_name']
        u_email = request.values['u_email']   
        sql ="insert into user values('"+str(u_id)+"','"+str(u_passwd)+"','"+str(u_name)+"','"+str(u_email)+"',1,True)"
        result = cur.execute(sql)
        con.commit()
        con.close()
        if result == 1:
            return "Success"
        else:
            return "Failed"
    else:
        return "Error"

@app.route('/signin',methods = ['POST','GET'])
def signin():
      con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
      cur = con.cursor()
    
      if request.method == 'POST':
            u_id = request.values['u_id']
            u_passwd = request.values['u_passwd']
 
            sql ="select * from user where u_id ='"+str(u_id)+"' and u_passwd ='"+str(u_passwd)+"'"
            result = cur.execute(sql)
            con.close()
            if result == 1:
                return "Success"
            else:
                return "Failed"
      else:
            return "Error"


@app.route('/getuser',methods = ['POST','GET'])
def getuser():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        u_id = request.values['u_id']
        sql = "select * from user where u_id ='"+str(u_id)+"'"
        result = cur.execute(sql)
        userinfo = cur.fetchall()
        userdata = {"u_id" : userinfo[0][0], "u_name":userinfo[0][2], "u_email" : userinfo[0][3],"u_permission" : userinfo[0][4], "push" : userinfo[0][5],"u_photo" :userinfo[0][6]}
        cur.execute("select team.t_num, team.t_name, team.t_logo, team.t_info,team.t_facebook,team.t_youtube from team where t_num = (select t_num from bookmark where u_id = '"+str(u_id)+"')")
        bookmarkdata = cur.fetchall()
        bookmarklist = []
        for data in bookmarkdata:
            teamdata = {"t_num":data[0], "t_name":data[1],"t_logo":data[2], "t_info":data[3], "t_facebook":data[4],"t_youtube":data[5]}
            bookmarklist.append(teamdata)
        if userinfo[0][4]==2:
            cur.execute("select team.t_name, team.t_logo, team.t_info,team.t_facebook,team.t_youtube, team.t_num from team where t_num = (select t_num from team_user where u_id='"+str(u_id)+"')")
            teaminfo = cur.fetchall()
            teamdata = {"t_name":teaminfo[0][0],"t_logo":teaminfo[0][1], "t_info":teaminfo[0][2], "t_facebook":teaminfo[0][3],"t_youtube":teaminfo[0][4], "t_num":teaminfo[0][5]}

            return jsonify(user = userdata, team = teamdata, bookmark = bookmarklist)
        else:
        
            return jsonify(user = userdata, bookmark = bookmarklist)

    else:
        return jsonify(result="Error")
        
@app.route('/getuserid', methods = ['POST','GET'])
def getuserid():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()
     
    if request.method == 'GET':
        u_email = request.values['u_email']
        sql = "select u_id from user where u_email = '"+str(u_email)+"'"
        result = cur.execute(sql)
               
        if result != 0 :
            myid = cur.fetchall()
            realid = str(myid[0][0])
            return realid
        else :
            return "Failed"
    else:
        return "Failed"

@app.route('/findpassword', methods = ['POST','GET'])
def findpassword():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        u_email = request.values['u_email']
        u_id = request.values['u_id']
        sql = "select u_email from user where u_id = '"+str(u_id)+"' and u_email = '"+str(u_email)+"'"
        result = cur.execute(sql)

        # -*- coding: 949 -*-
        if result != 0:
            myuser = cur.fetchall()

            smtpserver = 'smtp.gmail.com'
            smtpport = 587
            smtpuser = 'hangang.manager@gmail.com'
            smtppw = 'zxcv1245'
            recipients = str(myuser[0][0])
           
            tempPW = ''
            for i in range(0,8,1):
                randValue = random.randint(0,10)
                tempPW += str(randValue)
            
                                    
            msg = MIMEText("안녕하세요? 임시비밀번호는 '"+str(tempPW)+"'입니다.'", _charset = 'utf-8')
            msg['Subject'] = '한강에서 놀자 임시 비밀번호입니다.'
            msg['From'] = smtpuser
            msg['To'] = recipients  #
                             
            session = smtplib.SMTP(smtpserver, smtpport)
            session.ehlo()
            session.starttls()
            session.ehlo()

            session.login(smtpuser, smtppw)
            smtpresult = session.sendmail(smtpuser, recipients, msg.as_string())

            if smtpresult:
                errstr = ''
                for recip in smtpresult.keys():
                    errstr = """Could not delivery mail to: %s

            Server said: %s
            %s
                    
            %s""" % (recip, smtpresult[recip][0], smtpresult[recip][1], errstr)
                raise smtplib.SMTPException(errstr)

            session.close()
            return "Success"
        else :
            return "Failed"
    else:
        return "Failed"

@app.route('/getteaminfo', methods = ['POST','GET'])
def getteaminfo():
      con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
      cur = con.cursor()

      if request.method == 'GET':
          sql = "select * from team order by t_name"
          result = cur.execute(sql)
          
          if result != 0:
              teamdata = cur.fetchall()
              teamlist = []
              for data in teamdata:
                  teamdict = {"t_num":data[0], "t_name":data[1],"t_logo":data[2], "t_info":data[3], "t_facebook":data[4],"t_youtube":data[5]}
                  teamlist.append(teamdict)
              resultdata = jsonify(team = teamlist, result="Success")
              return resultdata
          else:
              return jsonify(result="Failed")

      else:
          return jsonify(result="Failed")
          
  @app.route('/')

@app.route('/d')
def test():
     con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
     cur = con.cursor()

     cur.execute("select * from team where t_num = 1")
     temp = cur.fetchone()
     teamdata = {"t_name":temp[0],"t_logo":temp[1], "t_info":temp[2], 
                  "t_facebook":temp[3],"t_youtube":temp[4]}
     return teamdata

if __name__ == '__main__': 
    app.debug = True
    app.run(host='203.252.166.213', port = 3000)
