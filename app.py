from flask import Flask,flash, render_template, request,url_for,redirect,Response,session,send_file,send_from_directory
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from functools import wraps

import os
import csv
import random

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'UPLOAD_FOLDER')

UPLOAD_FOLDER='static/images'
FILE_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app=Flask(__name__)
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='db_college'
app.config['MYSQL_CURSORCLASS']='DictCursor'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mysql=MySQL(app)

@app.route("/")
@app.route("/home",methods=['POST','GET'])
def home():
    return render_template("home.html")
    
@app.route("/admin",methods=['POST','GET'])
def admin():
    if request.method=='POST':
        if request.form["submit"]=="Login":
            a=request.form["uname"]
            b=request.form["upass"]
            cur=mysql.connection.cursor()
            cur.execute("select * from tbl_admin where aname=%s and apass=%s",(a,b))
            data=cur.fetchone()
            if data:
                session['logged_in']=True
                session['aid']=data["aid"]
                session['aname']=data["aname"]
                session['apass']=data["apass"]
                flash('Login Successfully','success')
                return redirect('adminlogin')
            else:
                flash('Invalid Login. Try Again','danger')
    return render_template("admin.html")
#check if user logged in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'logged_in' in session:
			return f(*args,**kwargs)
		else:
			flash('Unauthorized, Please Login','danger')
			return redirect(url_for('home'))
	return wrap
 
@app.route("/adminlogin",methods=['POST','GET'])
def adminlogin():	
    return render_template("adminlogin.html")
  
    
@app.route("/adddepartment",methods=['POST','GET'])
def adddepartment():
    if request.method=='POST':
        if request.form["submit"]=="Update":
            a=request.form["rname"]
            b=request.form["ryear"]
            c=request.form["rsem"]
            cur=mysql.connection.cursor()
            cur.execute("INSERT INTO tbl_department(dname,year,sem) values(%s,%s,%s)" ,(a,b,c))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('adddepartment'))
            
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_department")
    data=cur.fetchall()	
    cur.close()
    
    return render_template("adddepartment.html",datas=data) 
 
@app.route('/department_edit/<string:did>',methods=['POST','GET'])
def department_edit(did):
    if request.method=='POST':
        a=request.form["rname"]
        b=request.form["ryear"]
        c=request.form["rsem"]
        cur=mysql.connection.cursor()
        cur.execute("UPDATE tbl_department SET dname=%s,year=%s,sem=%s where did=%s",(a,b,c,did))
        mysql.connection.commit()
        cur.close()
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_department where did=%s",(did,))
    data=cur.fetchone()	
    return render_template("department_edit.html",datas=data)

@app.route('/departmentdelete/<string:did>',methods=["POST","GET"])
def departmentdelete(did):
    cur=mysql.connection.cursor()
    cur.execute("delete from tbl_department where did=%s",(did,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("adddepartment"))
   
        
@app.route("/addstudent",methods=["POST","GET"])
def addstudent():
    if request.method == 'POST':
        if request.form["submit"] == "Submit":
            a = request.form["sname"]
            b = request.form["semail"]
            c = request.form["did"]
            d = request.form["smobile"]
            e = request.form["sroll_no"]
            f = request.form["dyear"]
            file = request.files['file']
            if file and allowed_extensions(file.filename):
                filename, file_extension = os.path.splitext(file.filename)
                new_filename = secure_filename(str(random.randint(10000,99999))+"."+file_extension)
                file.save(os.path.join(UPLOAD_FOLDER, new_filename)) 
                cur=mysql.connection.cursor()
                cur.execute("INSERT INTO tbl_student(sname,email,did,mobile,roll_no,year,simage)Values(%s,%s,%s,%s,%s,%s,%s)",(a,b,c,d,e,f,new_filename))
                mysql.connection.commit()            
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_student")
    data = cur.fetchall()	
    cur.close()
    
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_department")
    dept = cur.fetchall()	
    cur.close()
    
    return render_template("addstudent.html",datas=data,data=dept)
    
def allowed_extensions(file_name):
    return '.' in file_name and file_name.rsplit('.',1)[1].lower() in FILE_EXTENSIONS
	

@app.route('/studentedit/<string:sid>',methods=['POST','GET'])
def studentedit(sid):
    if request.method=='POST':
        if request.form["submit"]=="Sumbit":
            a=request.form["sname"]
            b=request.form["semail"]
            c=request.form["dname"]
            d=request.form["sroll_no"]
            e=request.form["syear"]
            f=request.form["smobile"]
            cur=mysql.connection.cursor()
            cur.execute("UPDATE tbl_student SET sname=%s,year=%s,email=%s,roll_no=%s,mobile=%s,dname=%s where sid=%s",(a,b,c,d,e,f,sid))
            mysql.connection.commit()
            cur.close()
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_student where sid=%s",(sid,))
    data=cur.fetchone()	
    return render_template("studentedit.html",datas=data)
    

@app.route('/studentdelete/<string:sid>',methods=["POST","GET"])
def studentdelete(sid):
    cur=mysql.connection.cursor()
    cur.execute("delete from tbl_student where sid=%s",(sid,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("addstudent"))
 
@app.route("/viewstudent",methods=["POST","GET"])
def viewstudent():
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_student")
    data=cur.fetchall()	
    return render_template("viewstudent.html",datas=data)
    
@app.route("/addsubject",methods=["POST","GET"])
def addsubject():
    if request.method=='POST':
        if request.form["submit"]=="Update":
            a=request.form["sbjname"]
            b=request.form["dname"]
            c=request.form["sbjcode"]
            d=request.form["sem"]
            cur=mysql.connection.cursor()
            cur.execute("INSERT INTO tbl_subject(sbname,dname,sbcode,sem) values(%s,%s,%s,%s)" ,(a,b,c,d))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('addsubject'))
            
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_subject")
    data=cur.fetchall()	
    cur.close()
    
    return render_template("addsubject.html",datas=data)
    
@app.route('/subject_edit/<string:sbid>',methods=['POST','GET'])
def subject_edit(sbid):
    if request.method=='POST':
        a=request.form["dname"]
        b=request.form["sbjname"]
        c=request.form["sbjcode"]
        cur=mysql.connection.cursor()
        cur.execute("UPDATE tbl_subject SET dname=%s,sbname=%s,sbcode=%s where sbid=%s",(a,b,c,sbid))
        mysql.connection.commit()
        cur.close()
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_subject where sbid=%s",(sbid,))
    data=cur.fetchone()	
    return render_template("subject_edit.html",datas=data)
    
@app.route('/subject_delete/<string:sbid>',methods=["POST","GET"])
def subject_delete(sbid):
    cur=mysql.connection.cursor()
    cur.execute("delete from tbl_subject where sbid=%s",(sbid,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("addsubject"))
    
@app.route("/studentmarks",methods=["POST","GET"])
def studentmarks():
    return render_template("studentmarks.html")
    
@app.route("/addmark",methods=['POST','GET'])
@is_logged_in
def addmark():
    if request.method=='POST':
        if request.form["submit"]=="Submit":
            a=request.form["did"]
            b=request.form["sem"]
            file = request.files['file']
            filename, file_extension = os.path.splitext(file.filename)
            new_filename = "data.csv"
            file.save(os.path.join(UPLOAD_FOLDER, new_filename))
            cur = mysql.connection.cursor()

        with open(UPLOAD_FOLDER+'/data.csv',encoding="utf8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            i=0
            for row in csv_reader:
                if i>0:
                    cur.execute("insert into tbl_mark(did,sem,roll_no,s1,s2,s3,s4,s5,result) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(a,b,row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
                i+=1
        cur.close()
    mysql.connection.commit()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_department")
    dept = cur.fetchall()
    cur.close()
    return render_template("addmark.html",datas=dept)

@app.route('/addmark_view', methods=['POST', 'GET'])
def addmark_view():
    dept = []
 
    if request.method=='POST':
        if request.form["submit"]=="Submit":
            a = request.form["did"]
            b = request.form["sem"]
            cur = mysql.connection.cursor()
            cur.execute("select * from tbl_mark a inner join tbl_student s on a.roll_no=s.roll_no and a.did=s.did inner join tbl_department d on d.did=a.did where a.sem=%s and a.did=%s",(b,a))
            dept = cur.fetchall()
            cur.close()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_department")
    data1= cur.fetchall()
    cur.close()
    return render_template("addmark_view.html",status=dept,datas=data1)
    
@app.route("/student_login",methods=['POST','GET'])
def student_login():
    if request.method=='POST':
        if request.form["submit"]=="Login":
            a=request.form["sname"]
            b=request.form["roll_no"]
            cur=mysql.connection.cursor()
            cur.execute("select * from tbl_student where sname=%s and roll_no=%s",(a,b))
            data=cur.fetchone()
            if data:
                session['logged_in']=True
                session['sid']=data["sid"]
                session['sname']=data["sname"]
                session['roll_no']=data["roll_no"]
                flash('Login Successfully','success')
                return redirect('student_admin')
            else:
                flash('Invalid Login. Try Again','danger')
    return render_template("student_login.html")
#check if user logged in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'logged_in' in session:
			return f(*args,**kwargs)
		else:
			flash('Unauthorized, Please Login','danger')
			return redirect(url_for('student_admin'))
	return wrap

@app.route("/student_admin",methods=['POST','GET'])
def student_admin():	
    return render_template("student_admin.html")
    
@app.route("/view_profile",methods=["POST","GET"])
def view_profile():
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_student s inner join  tbl_department d on s.did=d.did where s.sid=%s",(session["sid"],))
    data=cur.fetchall()	
    return render_template("view_profile.html",datas=data)
    
@app.route("/view_result",methods=["POST","GET"])
def view_result(): 
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_mark m inner join tbl_subject s on m.sem=s.sem and m.did=s.did inner join tbl_department d inner join tbl_student t on d.did=t.did and t.roll_no=m.roll_no and d.did=m.did where t.sid=%s",(session["sid"],))
    data=cur.fetchall()
    return render_template("view_result.html",datas=data)
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("home"))
    
if  __name__=='__main__':
    app.secret_key='secret123'
    app.run(debug=True)
