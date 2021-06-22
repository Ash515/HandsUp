import os
import base64
import io  
import PIL
from PIL import Image
from MySQLdb import connections
from flask import Flask,send_file, render_template,send_file,url_for,redirect,flash, request, redirect,session
from flask.wrappers import Response
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
app=Flask(__name__,template_folder='template')
app.secret_key="key"
app.config['MYSQL_HOST']="localhost"
app.config['MYSQL_USER']="root"
app.config['MYSQL_PASSWORD']=""
app.config['MYSQL_DB']="handsup"
mysql=MySQL(app)

@app.route('/')
def index():
  return render_template('/client/index.html')

@app.route('/userlogin',methods=['POST','GET'])
def userlogin():
    message="Please fill the login "
    if request.method=='POST':
        useremail=request.form['u_email']
        userpassword=request.form['u_psw']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (useremail, userpassword))
        user=cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['u_psw'] = user['password']
            session['u_email'] = user['email']
            return redirect(url_for('main'))
        else:
            # Account doesnt exist or username/password incorrect
             message = 'Incorrect username/password!'
    return render_template('/client/login.html', message='')
   
    
@app.route('/userregistration',methods=['POST','GET'])
def userregistration():
    msg = ''
    if request.method == 'POST':
        username = request.form['u_name']
        usermail = request.form['u_email']
        userpassword = request.form['u_psw']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (usermail,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', usermail):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not userpassword or not usermail:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO users VALUES (%s, %s, %s)', (username, usermail, userpassword))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            #after successfully inserted redirect to loginpage
            return render_template('/client/login.html') 
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('/client/signup.htm', msg=msg)

@app.route('/main')
def main():
     if 'loggedin' in session:
         email=session['u_email']
         cur=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cur.execute('SELECT * FROM replymessage where email=%s',(email,))
         adminreply=cur.fetchall()
         cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute('SELECT * FROM users WHERE email= %s ', (email,))
         user=cursor.fetchall()
         cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute('SELECT * FROM complains WHERE email= %s ', (email,))
         usercomplain=cursor.fetchall()
         cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute('SELECT * FROM complains')
         complainid=cursor.fetchall()
         cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute('SELECT * FROM replymessage WHERE email=%s',(email,))
         recieveid=cursor.fetchall()
         cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute('SELECT * FROM sentitems WHERE email= %s ', (email,))
         sentid=cursor.fetchall()
         return render_template('/client/main.html', usermail=session['u_email'],adminreply=adminreply,user=user,usercomplain=usercomplain,complainid=complainid,recieveid=recieveid,sentid=sentid)
     
    # User is not loggedin redirect to login page
     return render_template('userlogin.html')
    
    
@app.route('/userlogout')
def userlogout():
   session.pop('u_email')
   return redirect(url_for('index'))

@app.route('/profile')
def profile():
    return render_template('/client/profile.html') 

@app.route('/usersettings')
def usersettings():
    return render_template('/client/settings.html') 
    
@app.route('/complain',methods=['POST','GET'])
def complain():
    if request.method=='POST':
        studentid=request.form['complaint_id']
        studentemail=request.form['student_mail']
        studentregno=request.form['student_regno']
        complaintname=request.form['complaint_name']
        complaintmessage=request.form['complaint_msg']
        complaintdate=request.form['complaint_date']
        complaintfile=request.form['comp_file']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO complains VALUES(%s,%s,%s,%s,%s,%s,%s)',(studentid,studentemail,studentregno,complaintname,complaintmessage,complaintdate,complaintfile))
        mysql.connection.commit()
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO sentitems VALUES(%s,%s,%s,%s,%s,%s,%s)',(studentid,studentemail,studentregno,complaintname,complaintmessage,complaintdate,complaintfile))
        mysql.connection.commit()
    return redirect(url_for('main'))

@app.route('/recievelist/<id>')
def recievelist(id):
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM replymessage WHERE id= %s', (id,))
    recievedata=cursor.fetchall()
    return render_template('/client/recieved.html',recievedata=recievedata)

@app.route('/sentitems/<id>')
def sentitems(id):
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM sentitems WHERE id= %s', (id,))
    sentdata=cursor.fetchall()
    return render_template('/client/sentitems.html',sentdata=sentdata)

@app.route('/contact',methods=['POST','GET'])
def contact():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        subject=request.form['subject']
        message=request.form['message']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO contact VALUES(%s,%s,%s,%s)',(name,email,subject,message,))
        mysql.connection.commit()
    return render_template('/client/index.html') 


@app.route('/adminindex')
def adminindex():
    return render_template('/admin/admin.html')
    
@app.route('/adminlogin',methods=['POST','GET'])
def adminlogin():
    if request.method=='POST':
        message="Please fill the login "
        adminname=request.form['admin_email']
        adminpassword=request.form['admin_psw']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE email = %s AND password = %s', (adminname, adminpassword))
        admin=cursor.fetchone()

        if admin:
            session['loggedin'] = True
            session['admin_psw'] = admin['password']
            session['admin_email'] = admin['email']
            return redirect(url_for('adminworkspace'))
        else:
            # Account doesnt exist or username/password incorrect
            message = 'Incorrect username/password!'
    return render_template('/admin/adminlogin.html', message='')
     
@app.route('/adminregistration',methods=['POST','GET'])
def adminregistration():
    if request.method=='POST':
        msg=""
        adminname=request.form['admin_name']
        adminemail=request.form['admin_email']
        adminpassword=request.form['admin_psw']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        account=cursor.execute('SELECT * FROM admin WHERE email=%s',(adminemail,))
        if account :
             msg="Account already exists in this email Id"
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',adminemail):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', adminname):
            msg = 'Username must contain only characters and numbers!'
        elif not adminname or not adminpassword or not adminemail:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO admin VALUES (%s, %s, %s)', (adminname, adminemail, adminpassword))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            #after successfully inserted redirect to loginpage
            return render_template('/admin/adminlogin.html')
    elif request.method == 'POST':
     
        msg = 'Please fill out the form!'
        return render_template('admin/adminsignup.html', msg=msg)
    return render_template('admin/adminsignup.html')

@app.route('/workspace')
def adminworkspace():
    if 'loggedin' in session:
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM complains')
        complains=cursor.fetchall()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM complains')
        complaindata = cursor.fetchall() #data from database
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users')
        users=cursor.fetchall()
        return render_template('admin/adminworkspace.html',complaindata=complaindata,users=users, adminname=session['admin_email'],complains=complains)
    else:
        return render_template('admin/adminlogin.html')
  
@app.route('/complains/<id>',methods=['GET','POST'])
def complains(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM complains WHERE id= %s',(id,))
    complaindata = cursor.fetchall() #data from database
    cur=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM complains where id=%s',(id,))
    users=cur.fetchall()
    cur=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM complains where id=%s',(id,))
    des=cur.fetchall()
    return render_template('/client/complainbox.html',des=des,complaindata=complaindata,users=users)

@app.route('/replying',methods=['POST','GET'])
def replying():
    if request.method=='POST':
        adminreplydate=request.form['rep_date']
        adminreplyemail=request.form['rep_email']
        adminreplycomplainid=request.form['rep_complainid']
        adminreplysubject=request.form['rep_subject']
        adminreplymessage=request.form['rep_message']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO replymessage VALUES(%s,%s,%s,%s,%s)',(adminreplycomplainid,adminreplydate,adminreplyemail,adminreplysubject,adminreplymessage,))
        cursor.connection.commit()
    return redirect(url_for('sent'))

@app.route('/adminlogout')
def adminlogout():
   session.pop('admin_email')
   return redirect(url_for('index'))

@app.route('/sent')
def sent():
    return render_template('notification.html')
    
@app.route('/deletecomplain/<id>')
def deletecomplain(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM complains WHERE id=%s", (id,))
    de= cursor.fetchall()
    cursor.connection.commit()
    return render_template('/admin/adminworkspace.html',de=de)

@app.route('/deleterecieve/<id>')
def deleterecieve(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM replymessage WHERE id=%s", (id,))
    cursor.connection.commit()
    return redirect(url_for('main'))

@app.route('/deletesent/<id>')
def deletesent(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM sentitems WHERE id=%s", (id,))
    cursor.connection.commit()
    return redirect(url_for('main'))
   
if __name__=='__main__':
    app.debug=True
    app.run()

