from MySQLdb import connections
from flask import Flask, render_template,send_file,url_for,redirect,flash, request, redirect,session
from flask.wrappers import Response
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
app=Flask(__name__,template_folder='template')
app.secret_key="key"
app.config['MYSQL_HOST']="localhost"
app.config['MYSQL_USER']="root"
app.config['MYSQL_PASSWORD']=""
app.config['MYSQL_DB']="crimeportal"
mysql=MySQL(app)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/main')
def main():
     if 'loggedin' in session:
         return render_template('main.html', usermail=session['u_name'])
     
    # User is not loggedin redirect to login page
     return render_template('userlogin.html')

@app.route('/userlogin',methods=['POSt','GET'])
def userlogin():
   
    if request.method=='POST':
        message="Please fill the login "
        username=request.form['u_name']
        userpassword=request.form['u_psw']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE name = %s AND password = %s', (username, userpassword))
        user=cursor.fetchone()

        if user:
            session['loggedin'] = True
            session['u_psw'] = user['password']
            session['u_name'] = user['name']
            return redirect(url_for('main'))
        else:
            # Account doesnt exist or username/password incorrect
            message = 'Incorrect username/password!'
    return render_template('login.html', message='')
    


@app.route('/userregistration',methods=['POST','GET'])
def userregistration():
     msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
     if request.method == 'POST':       # Create variables for easy access
        username = request.form['u_name']
        usermail = request.form['u_email']
        userpassword = request.form['u_psw']
      
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (usermail,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
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
            return render_template('login.html')  
     elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
     return render_template('signup.htm', msg=msg)
@app.route('/userlogout')
def userlogut():
   session.pop('u_name')
   return redirect(url_for('index'))

@app.route('/profile')
def profile():
    return render_template('profile.html') 

@app.route('/usersettings')
def usersettings():
    return render_template('settings.html') 
    
   
@app.route('/aboutedit',methods=['POST','GET'])
def aboutedit():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        dept=request.form['dept']
        regno=request.form['regno']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO userprofile VALUES(%s,%s,%s,%s)',(email,name,dept,regno))
        mysql.connection.commit()
       

        return redirect(url_for('main'))
    return render_template('aboutedit.html')


@app.route('/complain',methods=['POST','GET'])
def complain():
    if request.method=='POST':
        studentemail=request.form['student_mail']
        complaintname=request.form['complaint_name']
        complaintmessage=request.form['complaint_msg']
        complaintdate=request.form['complaint_date']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO complains VALUES(%s,%s,%s,%s)',(studentemail,complaintname,complaintmessage,complaintdate))
        mysql.connection.commit()
    return redirect(url_for('main'))
    



@app.route('/adminindex')
def adminindex():
   
    return render_template('admin.html')
    

@app.route('/adminlogin',methods=['POST','GET'])
def adminlogin():
     if request.method=='POST':
        message="Please fill the login "
        adminname=request.form['admin_name']
        adminpassword=request.form['admin_psw']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE adminemail = %s AND adminpassword = %s', (adminname, adminpassword))
        admin=cursor.fetchone()

        if admin:
            session['loggedin'] = True
            session['admin_psw'] = admin['adminpassword']
            session['admin_email'] = admin['adminemail']
            return redirect(url_for('adminworkspace'))
        else:
            # Account doesnt exist or username/password incorrect
            message = 'Incorrect username/password!'
        return render_template('adminlogin.html', message='')
     

@app.route('/adminregistration',methods=['POST','GET'])
def adminregistration():
    if request.method=='POST':
        msg=""
        adminname=request.form['admin_uname']
        adminemail=request.form['admin_email']
        adminpassword=request.form['admin_psw']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        account=cursor.execute('SELECT * FROM admin WHERE adminemail=%s',(adminemail,))
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
            return render_template('adminlogin.html')  
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
        return render_template('adminsignup.html', msg=msg)
    return render_template('adminsignup.html')

@app.route('/workspace')
def adminworkspace():
    if 'loggedin' in session:
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM complains')
        complains=cursor.fetchall()
        return render_template('adminworkspace.html', adminname=session['admin_email'],complains=complains)
    else:
        return render_template('adminlogin.html')
  
  
@app.route('/adminreply',methods=['GET','POST'])
def adminreply():
    if request.method=='POST':
        replydate=request.form['rep_date']
        replymonth=request.form['rep_month']
        replyyear=request.form['rep_year']
        replysubject=request.form['rep_subject']
        replymessage=request.form['rep_message']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO adminreply VALUES(%s,%s,%s,%s,%s)',(replydate,replymonth,replyyear,replysubject,replymessage))
        cursor.connection.commit()
        return redirect(url_for('adminworkspace'))

    return render_template('adminreply.html')
    
    




   



if __name__=='__main__':
    app.debug=True
    app.run()

