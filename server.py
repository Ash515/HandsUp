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
     return redirect(url_for('userlogin'))

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

@app.route('/adminindex')
def adminindex():
    return render_template('admin.html')
    
@app.route('/workspace')
def adminworkspace():
    if 'loggedin' in session:
         return render_template('adminworkspace.html', adminname=session['admin_email'])
    # User is not loggedin redirect to login page
    return redirect(url_for('adminlogin'))
  
    

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
        return render_template('login.html', message='')
     return render_template('adminlogin.html')

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

@app.route('/adminreply')
def adminreply():
    return render_template('adminreply.html')
    
    




   



if __name__=='__main__':
    app.debug=True
    app.run()

