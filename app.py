from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from functools import wraps
import sqlite3,os,smtplib,socket,base64,datetime,re,strgen,itertools
from flask_bcrypt import generate_password_hash
from flask_bcrypt import check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only
from flask_mail import Mail, Message
from flask import Blueprint
from flask_paginate import Pagination, get_page_parameter
import flask_restless

app=Flask(__name__, template_folder='./templates')
app.secret_key=os.urandom(1024)
#####################################
#######################################
mail=Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'mrpreskriber'
app.config['MAIL_PASSWORD'] = '#kunmi75020589'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
######################################
mod=Blueprint('users', __name__)
#####################################
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('index'))
    return wrap

#######################################################################################
def chunks(l, n):#####slicer
    for i in xrange(0, len(l), n):#use xrange-if using python 2, and range-for python3
        yield l[i:i + n]
#########################################################################################
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///Test.db'
app.config['SQLALCHEMY_ECHO']=True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
db=SQLAlchemy(app)
######################################
class Users(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer, primary_key=True)
    First_Name=db.Column(db.String(20), nullable=False)
    Middle_Name=db.Column(db.String(20), nullable=True)
    Last_Name=db.Column(db.String(20), nullable=False)
    Phone=db.Column(db.String(15), nullable=False)
    Email=db.Column(db.String(50), unique=True, nullable=False)
    Address=db.Column(db.String(250), nullable=True)
    Level=db.Column(db.String(15), nullable=False)
    Organisation=db.Column(db.String(15), nullable=False)
    Health_Code=db.Column(db.String(15), nullable=True)
    Password_Hash=db.Column(db.String(200), nullable=False)
    Status=db.Column(db.String(15), nullable=False)
    Created_By=db.Column(db.String(20), nullable=False)
    Date_Created=db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    #-$2b$10$xH.J64X4yWpwEy6j8NmWZ.xQ/eokxpYVPPxjpIiyaVqcup4YlIebe

class Patients(db.Model):
    __tablename__='patients'
    id=db.Column(db.Integer, primary_key=True)
    First_Name=db.Column(db.String(20), nullable=False)
    Middle_Name=db.Column(db.String(20), nullable=True)
    Last_Name=db.Column(db.String(20), nullable=False)
    Phone=db.Column(db.String(15), nullable=False)
    Email=db.Column(db.String(50), nullable=False)
    Preskriber_ID=db.Column(db.String(15), unique=True, nullable=False)
    Gender=db.Column(db.String(10), nullable=False)
    Created_By=db.Column(db.String(20), nullable=False)
    Date_Created=db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

class Checker(db.Model):#Checker for pharmacist, and physician
    __tablename__='checker'
    id=db.Column(db.Integer, primary_key=True)
    First_Name=db.Column(db.String(20), nullable=False)
    Middle_Name=db.Column(db.String(20), nullable=True)
    Last_Name=db.Column(db.String(20), nullable=False)
    Health_Code=db.Column(db.String(15), unique=True, nullable=False)
    Created_By=db.Column(db.String(20), nullable=False)
    Date_Created=db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

class Organisation(db.Model):
    __tablename__='Organisation'
    id=db.Column(db.Integer, primary_key=True)
    Acronym=db.Column(db.String(10), nullable=False)
    Organisation_Name=db.Column(db.String(15), nullable=False)
    Organisation_Type=db.Column(db.String(20), nullable=False)
    Created_By=db.Column(db.String(20), nullable=False)
    Date_Created=db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

class Prescriptions(db.Model):
    __tablename__='prescriptions'
    id=db.Column(db.Integer, primary_key=True)
    Preskriber_ID=db.Column(db.String(20), nullable=False)
    Prescription=db.Column(db.String(250), nullable=False)
    Expiry_Date=db.Column(db.DateTime, nullable=False)
    Code=db.Column(db.String(15), unique=True)
    Status=db.Column(db.String(15), nullable=False)
    Administed_By=db.Column(db.String(20), nullable=True)
    Date_administed=db.Column(db.DateTime, nullable=True)
    Created_By=db.Column(db.String(20), nullable=False)
    Date_Created=db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

class Request_Permission(db.Model):
    __tablename__='request_permission'
    id=db.Column(db.Integer, primary_key=True)
    Preskriber_ID=db.Column(db.String(20), nullable=False)
    Email=db.Column(db.String(50), nullable=False)
    Secret_Key=db.Column(db.String(15), unique=True, nullable=False)
    Date=db.Column(db.String(15), nullable=False)
    Created_By=db.Column(db.String(20), nullable=False)
    Date_Created=db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

class Banned_Drugs(db.Model):
    __tablename__='banned_drugs'
    id=db.Column(db.Integer, primary_key=True)
    Drug_Name=db.Column(db.String(50), unique=True, nullable=False)
    Manufacturer=db.Column(db.String(50), nullable=False)
    drug_description=db.Column(db.String(250), nullable=False)
    drug_effect=db.Column(db.String(250), nullable=False)
    Status=db.Column(db.String(15), nullable=False)
    Created_By=db.Column(db.String(20), nullable=False)
    Date_Created=db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
######################################
######rest api########################
#manager=flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
#user_blueprint=manager.create_api(Users, methods=['GET', 'POST', 'DELETE'])

######################################
@app.errorhandler(500)
@login_required
def page_not_found(e):
    return redirect(url_for('error'))
@app.errorhandler(404)
@login_required
def page_not_found(e):
    return redirect(url_for('error'))
@app.errorhandler(400)
@login_required
def page_not_found(e):
    return redirect(url_for('error'))
@app.errorhandler(403)
@login_required
def page_not_found(e):
    return redirect(url_for('error'))
############################################
@app.route('/error')
#@login_required
def error():  
    return render_template("error.html")
##################################################################################
##################################################################################
@app.route('/', methods=['GET', 'POST'])
def index():
    error=None
    return render_template('index.html', error=error)
###################
@app.route('/search/', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route('/search', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route('/search?page<int:page>/', methods=['GET', 'POST'])
@app.route('/search?page<int:page>', methods=['GET', 'POST'])
@login_required
def search(page):
    search=str(request.form['search']).strip()
    details=(session.get('username')).split("|")
    username=details[0].title()
    organisation=details[2].title()
    level=details[1]
    if level in ['admin']:
        users=Users.query.filter((Users.First_Name==search.title()) | (Users.Last_Name==search.title()) | (Users.Email==search.lower()) | (Users.Level==search.lower()) | (Users.Organisation==search.lower()) | (Users.Status==search.title())).all()
        size=len(users)
        if size==0:
            flash("NO RESULT FOUND!", 'info')
            return redirect(url_for('admin'))
        else:
            total=len(users)
            search=len(users)
            users=list(chunks(users, 10))###added
            index=page-1###added
            users=users[index]###added
            pagination=Pagination(page=page, per_page=10, total=total, bs_version=3, record_name="users")
            flash(total, 'info')
            return render_template('admin.html', users=users, per_page=10, pagination=pagination, username=username, level=level, active_url='users-page-url')
    elif level in ['official'] and organisation!="nafdac":
        users=Users.query.filter((Users.First_Name==search.title()) | (Users.Last_Name==search.title()) | (Users.Email==search.lower()) | (Users.Level==search.lower()) | (Users.Organisation==organisation.lower()) | (Users.Status==search.title())).filter(Users.Organisation==organisation).all()
        total=len(users)
        size=total
        if size==0:
            flash("NO RESULT FOUND!", 'info')
            return redirect(url_for('official'))
        else:
            users=list(chunks(users, 10))###added
            index=page-1###added
            users=users[index]###added 
            pagination=Pagination(page=page, per_page=10, total=total, bs_version=3, record_name="users")
            return render_template('official.html', users=users, per_page=10, pagination=pagination, username=username, level=level, active_url='users-page-url')
    elif organisation in ['nafdac'] and level=="official":
        drugs=Banned_Drugs.query.filter((Banned_Drugs.Drug_Name==search.title()) | (Banned_Drugs.Manufacturer==search.title())).all()
        total=len(drugs)
        size=total
        if size==0:
            flash("NO RESULT FOUND!", 'info')
            return redirect(url_for('official'))
        else:
            drugs=list(chunks(drugs, 10))###added
            index=page-1###added
            drugs=drugs[index]###added 
            pagination=Pagination(page=page, per_page=10, total=total, bs_version=3, record_name="drugs")
            return render_template('official.html', drugs=drugs, per_page=10, pagination=pagination, username=username, level=level, active_url='users-page-url')
    else:
        return redirect(url_for('home'))
##########################################
#users=Users.query.filter((Users.First_Name==search) | (Users.Last_Name==search) | (Users.Email==search) | (Users.Level==search) | (Users.Organisation==search) | (Users.Status==search)).all()
##################
@app.route('/admin/', defaults={'page': 1})
@app.route('/admin', defaults={'page': 1})
@app.route('/admin?page<int:page>/')
@app.route('/admin?page<int:page>')
#@app.route('/admin')
@login_required
#def admin(page):
def admin(page):
    details=(session.get('username')).split("|")
    username=details[0].title()
    level=details[1]
    if level in ['admin']:
        search=False
        q=request.args.get('q')
        if q:
            search=True
        users=Users.query.all()
        total=len(users)
        users=list(chunks(users, 10))
        index=page-1
        users=users[index]
        organisation=Organisation.query.all()
        pagination=Pagination(page=page, per_page=10, total=total, bs_version=3, search=search, record_name="users")
        return render_template('admin.html', users=users, per_page=10, pagination=pagination, username=username, level=level, active_url='users-page-url', organisation=organisation)
    elif level in ['official']:
        return redirect(url_for('official'))
    else:
        return redirect(url_for('home'))

###################
@app.route('/home', methods=['GET', 'POST'])#
@login_required
def home():
    error=None
    details=(session.get('username')).split("|")
    username=details[0].title()
    level=details[1]
    if level in ['pharmacist', 'affliate', 'physician']:
        if level=="pharmacist":
            pharmacist=Users.query.filter_by(Email=details[3]).first()
            health_code=pharmacist.Health_Code
            affliate=Users.query.filter_by(Level="affliate", Health_Code=health_code, Status="Green").all()
            affliate_size=len(affliate)
            return render_template('home.html', error=error, username=username, level=level, affliate=affliate, affliate_size=affliate_size)
        else:
            return render_template('home.html', error=error, username=username, level=level)

    elif level in ['official']:
        return redirect(url_for('official'))
    else:
        return redirect(url_for('admin'))
###################
@app.route('/official/', defaults={'page': 1})
@app.route('/official', defaults={'page': 1})
@app.route('/official?page<int:page>/')
@app.route('/official?page<int:page>')
@login_required
def official(page):
    error=None
    details=(session.get('username')).split("|")
    username=details[0].title()
    organisation=details[2]
    level=details[1]
    if level in ['pharmacist', 'affliate', 'physician', 'admin']:
        return redirect(url_for('home'))
    elif  organisation!="nafdac":
        search=False
        q=request.args.get('q')
        if q:
            search=True
        users=Users.query.filter_by(Organisation=organisation).all()
        size=len(users)
        pagination=Pagination(page=page, total=size, search=search, record_name='member(s)')
        return render_template('official.html', error=error, username=username, organisation=organisation, users=users, size=size, pagination=pagination)
    else:
        search=False
        q=request.args.get('q')
        if q:
            search=True
        drugs=Banned_Drugs.query.filter_by(Status="Black").all()
        size=len(drugs)
        total=size
        pagination=Pagination(page=page, total=total, search=search, record_name='member(s)')
        return render_template('official.html', error=error, username=username, organisation=organisation, drugs=drugs, size=size, pagination=pagination, level=level)

###################
###################
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error=None
    organisation=Organisation.query.all()
    return render_template('signup.html', error=error, organisation=organisation)
###################
@app.route('/terms', methods=['GET', 'POST'])
def terms():
    error=None
    return render_template('terms.html', error=error)
###################
@app.route('/ack', methods=['GET', 'POST'])
def ack():
    error=None
    return render_template('ack.html', error=error)
###################
@app.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    error=None
    details=(session.get('username')).split("|")
    username=details[0].title()
    level=details[1]
    size=0
    if level not in ['pharmacist', 'affliate', 'physician']:
        return redirect(url_for('home'))
    else:
        return render_template('report.html', error=error, username=username, level=level, size=size)
###################
@app.route('/check', methods=['GET', 'POST'])
def check():
    error=None
    return render_template('check.html', error=error)
###################
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    error=None
    return render_template('reset.html', error=error)
#####################################################
#################ACTIONS#########################
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$doctors$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
@app.route('/login', methods=['GET', 'POST'])#####(shared action-all user)
def login():########################################WORKING gOOD!
    error=None
    email=str(request.form['email']).strip()
    password=str(request.form['password'])
    try:
        user=Users.query.filter_by(Email=email).first()
        hash_password=user.Password_Hash
        status=user.Status
    except:
        flash("INVALID CREDENTIAL!", 'error')
        return redirect(url_for('index'))
    else:
        k=str(check_password_hash(hash_password, password))
        if status=="Black":
            flash("ACCOUNT SUSPENDED!", 'error')
            return redirect(url_for('index'))
        elif status=="Amber":
            flash("ACCOUNT HASN'T BEEN APPROVED!", 'error')
            return redirect(url_for('index'))
        else:
            if k=="True":
                session['username']=(user.First_Name+"|"+user.Level+"|"+user.Organisation+"|"+user.Email).lower()
                session['logged_in']=True
                if user.Level=="admin":
                    return redirect(url_for('admin'))
                elif user.Level=="official":
                    return redirect(url_for('official'))
                else:
                    return redirect(url_for('home'))
            else:
                flash("INVALID PASSWORD!".upper(), 'error')
                return redirect(url_for('index'))
    return render_template('home.html', error=error)
#####################################################
@app.route('/change_password', methods=['GET', 'POST'])#####(shared action-all user)
@login_required
def change_password():#######################################WORKING GOOD!
    error=None
    details=(session.get('username')).split("|")
    email=details[3]
    password=str(request.form['password'])
    confirm_password=str(request.form['confirm_password'])
    hash=str(generate_password_hash(confirm_password, 10))
    if password!=confirm_password:
        if details[1]=="admin":
            flash("PASSWORDS DON'T MATCH!", 'error')
            return redirect(url_for('admin'))
        elif details[1]=="official":
            flash("PASSWORDS DON'T MATCH!", 'error')
            return redirect(url_for('official'))
        else:
            flash("PASSWORDS DON'T MATCH!", 'error')
            return redirect(url_for('home'))
    else:
        user=Users.query.filter_by(Email=email).first()
        user.Password_Hash=hash
        db.session.commit()
        if details[1]=="admin":
            flash("PASSWORD SUCCESSFULLY CHANGED!", 'info')
            return redirect(url_for('admin'))
        elif details[1]=="official":
            flash("PASSWORD SUCCESSFULLY CHANGED!", 'info')
            return redirect(url_for('official'))
        else:
            flash("PASSWORD SUCCESSFULLY CHANGED!", 'info')
            return redirect(url_for('home'))
##################################################################################
@app.route('/logout')#WORKING GOOD!
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))
######################################################################################
##################################admin actions#######################################
@app.route('/add_official', methods=['GET', 'POST'])##working good!!
@login_required
def add_official():
    error=None
    details=(session.get('username')).split("|")
    if details[1]!="admin":
        return redirect(url_for('home'))
    else:
        first_name=str(request.form['first_name']).strip()
        middle_name=str(request.form['middle_name']).strip()
        last_name=str(request.form['last_name']).strip()
        phone=str(request.form['phone']).strip()
        email=str(request.form['email']).strip()
        option=str(request.form['option'])
        time=str(datetime.datetime.now())
        password=strgen.StringGenerator("[\d\w]{10}").render()
        password_hash=str(generate_password_hash(password, 10))
        try:
            add_official=Users(First_Name=first_name, Middle_Name=middle_name, Last_Name=last_name, Phone=phone, Email=email, Level="official", Organisation=option, Password_Hash=password_hash, Status="Green", Created_By=details[3])
            db.session.add(add_official)
            db.session.commit()
        except:
            flash("USER ALREADY EXIST ON PRESKRIBER!", 'error')
            return redirect(url_for('admin'))
        else:
            try:
                msg=Message('Preskriber-Welcome', sender='mrpreskriber@gmail.com', recipients=email)
                msg.body="Hello "+first_name+"! "+"Please use this code("+password+") to log into Preskriber. Please remember to change it immediately."  
                mail.send(msg)
            except:
                flash("EMAIL ERROR!", 'error')
                return redirect(url_for('admin'))
            else:
                flash("ACCOUNT WAS CREATED SUCCESSFULLY!", 'info')
                return redirect(url_for('admin'))
######################################################################################
@app.route('/add_organisation', methods=['GET', 'POST'])
@login_required
def add_organisation():
    error=None
    details=(session.get('username')).split("|")
    if details[1]!="admmrin":
        return redirect(url_for('home'))
    else:
        acronym=str(request.form['acronym']).strip().lower()
        organisation_name=str(request.form['organisation_name']).strip().title()
        organisation_type=str(request.form['organisation_type'])
        time=str(datetime.datetime.now())
        add_organisation=Organisation(Acronym=acronym, Organisation_Name=organisation_name, Organisation_Type=organisation_type, Created_By=details[3])
        db.session.add(add_organisation)
        db.session.commit().strip().title()
        flash("ORGANISATION WAS ADDED SUCCESSFULLY!", 'info')
        return redirect(url_for('admin'))
######################################################################################
@app.route('/reset_account', methods=['GET', 'POST'])
@login_required
def reset_account():
    error=None
    email=str(request.form['email']).strip().lower()
    try:
        email=Users.query.filter_by(Email=email).first()
    except:
        flash("ACCOUNT DOESN'T EXIST!", 'info')
        return redirect(url_for('reset'))
    else:
        try:
            name_0=email.First_Name
            password=strgen.StringGenerator("[\d\w]{10}").render()
            msg=Message('Preskriber', sender='mrpreskriber@gmail.com', recipients=email)
            msg.body="Hello "+name_0+", please use this code to access Preskriber."
            mail.send(msg)
        except:
            flash("EMAIL ERROR!", 'info')
            return redirect(url_for('reset'))
        else:
            password_hash=str(generate_password_hash(password, 10))
            user.Password_Hash=password_hash
            db.session.commit()
######################################################################################
######################################################################################
@app.route('/sign_up_now', methods=['GET', 'POST'])
def sign_up_now():
    error=None
    first_name=str(request.form['first_name']).strip().title()
    middle_name=str(request.form['middle_name']).strip().title()
    last_name=str(request.form['last_name']).strip().title()
    phone=str(request.form['phone']).strip()
    email=str(request.form['email']).strip()
    health_code=str(request.form['health_code']).strip()
    option=str(request.form['option'])
    organisation=str(request.form['organisation'])
    try:
        password=strgen.StringGenerator("[\d\w]{10}").render()
        password_hash=str(generate_password_hash(password, 10))
        users=Users(First_Name=first_name, Middle_Name=middle_name, Last_Name=last_name, Phone=phone, Email=email, Health_Code=health_code, Organisation=organisation, Level=option, Password_Hash=password_hash, Created_By="admin@preskriber.com", Status="Amber")
        db.session.add(users)
        db.session.commit()
    except Exception as e:
        flash("Account already exist!", 'error')
        return redirect(url_for('signup'))
    else:
        try:
            msg = Message('Preskriber', sender = 'mrpreskriber@gmail.com', recipients = [email])
            msg.body = "Your account has been created, please wait while we verify your account."
            mail.send(msg)
            flash("ACCOUNT CREATED!", 'info')
            return redirect(url_for('signup'))
        except:
            flash("Error B612!", 'error')
            return redirect(url_for('signup'))
######################################################################################

######################################################################################
@app.route('/revise_down/<email>/', methods=['GET', 'POST'])################admin&officialreset_account
@login_required
def revise_down(email):
    error=None
    details=(session.get('username')).split("|")
    user=Users.query.filter_by(Email=email).first()
    if details[1]=="admin":
        try:
            user.Status="Amber"
            organisation=user.Organisation
            db.session.commit()
        except:
            flash("Account Doesn't Exist!", 'error')
            return redirect(url_for('admin'))
        else:
            flash("ACCOUNT HAS BEEN SUSPENDED!", 'info')
            return redirect(url_for('admin'))
    elif details[1]=="official" and details[2]==user.Organisation:
        try:
            user.Status="Amber"
            db.session.commit()
        except:
            flash("ACCOUNT Doesn't exist!", 'error')
            return redirect(url_for('official'))
        else:
            flash("ACCOUNT HAS BEEN SUSPENDED!", 'info')
            return redirect(url_for('official'))
    else:
        flash("PERMISSION ERROR!", 'error')
        return redirect(url_for('home'))
######################################################################################
@app.route('/revise_up/<email>/', methods=['GET', 'POST'])################admin&official
@login_required
def revise_up(email):
    error=None
    details=(session.get('username')).split("|")
    user=Users.query.filter_by(Email=email).first()
    if details[1]=="admin":
        try:
            password=strgen.StringGenerator("[\d\w]{10}").render()
            password_hash=str(generate_password_hash(password, 10))
            user.Password_Hash=password_hash
            user.Status="Green"
            organisation=user.Organisation
            db.session.commit()
            talk="Your account has been approved, please use this to log in to preskriber:"+password
            msg = Message('Preskriber', sender = 'mrpreskriber@gmail.com', recipients = [email])
            msg.body = talk
            mail.send(msg)
        except:
            flash("Check Email Settings!", 'error')
            return redirect(url_for('admin'))
        else:
            flash("ACCOUNT HAS BEEN APPROVED!", 'info')
            return redirect(url_for('admin'))
    elif details[1]=="official" and details[2]==user.Organisation:
        try:
            password=strgen.StringGenerator("[\d\w]{10}").render()
            password_hash=str(generate_password_hash(password, 10))
            user.Password_Hash=password_hash
            user.Status="Green"
            db.session.commit()
            talk="Your account has been approved, please use this to log in to preskriber:"+password
            msg = Message('Preskriber', sender = 'mrpreskriber@gmail.com', recipients = [email])
            msg.body = talk
            mail.send(msg)
        except:
            flash("Check Email Settings!", 'error')
            return redirect(url_for('official'))
        else:
            flash("ACCOUNT HAS BEEN APPROVED!", 'info')
            return redirect(url_for('official'))
    else:
        flash("PERMISSION ERROR!", 'error')
        return redirect(url_for('home'))
######################################################################################
@app.route('/revise_ban/<email>/', methods=['GET', 'POST'])################admin&officialreset_account
@login_required
def revise_ban(email):
    error=None
    details=(session.get('username')).split("|")
    user=Users.query.filter_by(Email=email).first()
    if details[1]=="admin":
        try:
            user.Status="Black"
            organisation=user.Organisation
            db.session.commit()
        except:
            flash("Email Account Issue!", 'error')
            return redirect(url_for('admin'))
        else:
            flash("ACCOUNT HAS BEEN BANNED!", 'info')
            return redirect(url_for('admin'))
    elif details[1]=="official" and details[2]==user.Organisation:
        try:
            user.Status="Black"
            db.session.commit()
        except:
            flash("Email Account Issue!", 'error')
            return redirect(url_for('official'))
        else:
            flash("ACCOUNT HAS BEEN BANNED!", 'info')
            return redirect(url_for('official'))
    else:
        flash("PERMISSION ERROR!", 'error')
        return redirect(url_for('home'))
######################################################################################
@app.route('/check_drug', methods=['GET', 'POST'])
def check_drug():
    error=None
    drug_name=str(request.form['drug_name']).strip().title()
    try:
        drug=Banned_Drugs.query.filter_by(Drug_Name=drug_name).first()
    except:
        flash("DRUG ISN'T ON THE NAFDAC BANNED LIST!", 'error')
        return redirect(url_for('check'))
    else:
        if len(drug)==0:
            flash("DRUG ISN'T ON THE NAFDAC BANNED LIST!", 'error')
            return redirect(url_for('check'))
        else:
            drug=drug
            return render_template('check.html', error=error, drug=drug, result=result)
####################################################
@app.route('/ban_drug', methods=['GET', 'POST'])
def ban_drug():
    error=None
    details=(session.get('username')).split("|")
    if details[2]!="nafdac":
        return redirect(url_for('home'))
    else:
        drug_name=str(request.form['drug_name']).strip().upper().title()
        manufacturer=str(request.form['manufacturer']).strip().upper().title()
        description=str(request.form['description']).strip().upper().title()
        effect=str(request.form['effect']).strip().upper().title()
        try:
            add_drug=Banned_Drugs(Drug_Name=drug_name, Manufacturer=manufacturer, drug_description=description, drug_effect=effect, Status='Black', Created_By=details[3])
            db.session.add(add_drug)
            db.session.commit()
        except:
            flash("DRUG ADDED ALREADY!", 'error')
            return redirect(url_for('official'))
        else:
            flash("DRUG SUCCESSFULLY ADDED!", 'info')
            return redirect(url_for('official'))                              
######################################################################################
@app.route('/remove_ban/<name>/', methods=['GET', 'POST'])################admin&officialreset_account
@login_required
def remove_ban(name):
    error=None
    details=(session.get('username')).split("|")
    if details[2]=="nafdac":
        try:
            drug=Banned_Drugs.query.filter_by(Drug_Name=name).first()
            drug.Status="Green"
            db.session.commit()
        except:
            flash("ACTION FAILED!", 'error')
            return redirect(url_for('official'))
        else:
            flash("DRUG SUCCESSFULLY REMOVED FROM LIST!", 'info')
            return redirect(url_for('official'))
    else:
        return redirect(url_for('home'))
######################################################################################
@app.route('/make_prescription', methods=['GET', 'POST'])
@login_required
def make_prescription():
    error=None
    details=(session.get('username')).split("|")
    if details[1]!="physician":
        return redirect(url_for('home'))
    else:
        preskriber_id=str(request.form['preskriber_id']).strip()
        drug_prescription=str(request.form['drug_prescription']).strip()
        expiry_date=str(request.form['expiry_date']).strip()
        time=str(datetime.datetime.now())
        code=(hex(int(re.sub(r'[^\w\s]','',time).replace(" ",""))))[::-1]
        try:
            patient=Patients.query.filter_by(Preskriber_ID=preskriber_id).first()
            Email=patient.Email
        except:
            flash("INVALID PRESKRIBER ID!", 'error')
            return redirect(url_for('home'))
        else:
            try:
                msg=Message('Preskriber-Prescription', sender='mrpreskriber@gmail.com', recipients=Email)
                msg.body="Hello, Please use this code to '"+code+"' at the store to view drug prescription."
                mail.send(msg)
            except:
                flash("EMAIL ERROR!", 'error')
                return redirect(url_for('home'))
            else:
                make_prescription=Prescription(Preskriber_ID=preskriber_id, Prescription=drug_prescription, Expiry_Date=expiry_date, Code=code, Status='Green', Created_By=user[3])
                db.session.add(make_prescription)
                db.session.commit()
                flash("Successfully sent Prescription Code to patient's email!".upper(), 'info')
                return redirect(url_for('home'))
    return render_template('home.html', error=error)
######################################################################################
@app.route('/request_permission', methods=['GET', 'POST'])
@login_required
def request_permission():
    error=None
    details=(session.get('username')).split("|")
    if details[1]!="physician":
        return redirect(url_for('home'))
    else:
        preskriber_id=str(request.form['preskriber_id']).strip()
        time=datetime.datetime.now()
        time1=time.time()
        code=(hex(int(re.sub(r'[^\w\s]','',str(time1)).replace(" ",""))))[::-1]
        date=time.date()
        try:
            patient=Patients.query.filter_by(Preskriber_ID=preskriber_id).first()
            email=patient.Email
            name=patient.First_Name
        except:
            flash("USER DOESN'T EXIST!", 'error')
            return redirect(url_for('home'))
        else:
            try:
                msg=Message('Preskriber-Permission', sender='mrpreskriber@gmail.com', recipients=Email)
                msg.body="Hello "+name+", Please use this code to '"+code+"' to grant your physican access to view your previous prescriptions.."
                mail.send(msg)
            except:
                flash("EMAIL ERROR!", 'error')
                return redirect(url_for('home'))
            else:
                Request_Permission=Request_Permission(Preskriber_ID=preskriber_id, Email=email, Secret_Key=code, Date=date, Created_By=details[3])
                db.session.add(Request_Permission)
                db.session.commit()
                flash("SECURITY CODE SENT TO PATIENT'S EMAIL ADDRESS!", 'info')
                return redirect(url_for('home'))
######################################################################################
@app.route('/add_patient', methods=['GET', 'POST'])
@login_required
def add_patient():
    error=None
    details=(session.get('username')).split("|")
    if details[1]!="physician":
        return redirect(url_for('home'))
    else:
        first_name=str(request.form['first_name']).strip()
        middle_name=str(request.form['middle_name'])
        last_name=str(request.form['last_name']).strip()
        email=str(request.form['email']).strip()
        phone=str(request.form['phone']).strip()
        date_of_birth=str(request.form['date_of_birth']).strip()
        gender=str(request.form['gender'])
        time=datetime.datetime.now()
        code=(hex(int(re.sub(r'[^\w\s]','',str(time)).replace(" ",""))))[::-1]
        try:
            msg=Message('Preskriber-Permission', sender='mrpreskriber@gmail.com', recipients=email)
            msg.body="Hello "+first_name+", here's your preskriber id- '"+code+"'."
            mail.send(msg)
        except:
            flash("EMAIL ERROR!", 'error')
            return redirect(url_for('home'))
        else:
            try:
                add_patient=Patients(First_Name=first_name, Middle_Name=middle_name, Last_Name=last_name, Phone=phone, Email=email, Preskriber_ID=code,Gender=gender, Created_By=details[3])
                db.session.add(add_patient)
                db.session.commit()
                flash("SUCCESSFULLY ADDED PATIENT!", 'info')
                return redirect(url_for('home'))
            except:
                flash("DATA ERROR!", 'error')
                return redirect(url_for('home'))
######################################################################################
@app.route('/view_prescription', methods=['GET', 'POST'])
@login_required
def view_prescription():
    error=None
    details=(session.get('username')).split("|")
    secret_code=str(request.form['secret_code']).strip()
    if details[1]!="physician":
        return redirect(url_for('home'))
    else:
        secret_code=str(request.form['secret_code']).strip()
        time=datetime.datetime.now()
        date=time.date()
        try:
            permission=Request_Permission.query.filter_by(Secret_Key=secret_code, Date=date).first()
            permission=permission.Preskriber_ID
        except:
            flash("INVALID PERMISSION CODE!", 'error')
            return redirect(url_for('home'))
        else:
            try:
                prescriptions=Prescriptions.query.filter_by(Preskriber_ID=permission).limit(10)
            except:
                flash("PRESCRIPTION(S) NOT FOUND!", 'error')
                return redirect(url_for('home'))
            else:
                size=len(prescriptions)
                return render_template('report.html', error=error, prescriptions=prescriptions, size=size)
######################################################################################
@app.route('/verify_prescription', methods=['GET', 'POST'])
@login_required
def verify_prescription():
    error=None
    details=(session.get('username')).split("|")
    username=details[0]
    level=details[1]
    if level not in ['pharmacist', 'affliate']:
        return redirect(url_for('home'))
    try:
        prescription_code=str(request.form['prescription_code']).strip()
        prescription=Prescription.query.filter_by(Code=prescription_code).first()
        expiry_date=prescription.Expiry_Date
    except:
        flash("INVALID PRESCRIPTION CODE!", 'error')
        return redirect(url_for('home'))
    else:
        time0=datetime.datetime.now().strftime('%Y-%m-%d')
        if time0>expiry_date:
            flash("PRESCRIPTION HAS EXPIRED, CONTACT YOUR PHYSICIAN!", 'error')
            return redirect(url_for('home'))
        else:
            if prescription.Status=="Amber":
                flash("PRESCRIPTION WAS BE ADMINISTED BY "+prescription.Administed_By.upper()+"!", 'error')
                return redirect(url_for('home'))
            else:
                return render_template('report.html', error=error,level=level, username=username, prescription=prescription)
######################################################################################
@app.route('/add_affliate', methods=['GET', 'POST'])
@login_required
def add_affliate():
    error=None
    details=(session.get('username')).split("|")
    username=details[0]
    level=details[1]
    if level not in ['pharmacist']:
        return redirect(url_for('home'))
    else:
        first_name=str(request.form['first_name']).strip()
        middle_name=str(request.form['middle_name']).strip()
        last_name=str(request.form['last_name']).strip()
        email=str(request.form['email']).strip()
        phone=str(request.form['last_name']).strip()
        store_name=str(request.form['store_name']).strip()
        store_address=str(request.form['last_name']).strip()
        address=store_name+"- "+store_address
        user=Users.query.filter_by(Email=details[3]).first()
        code=user.Health_Code
        password=strgen.StringGenerator("[\d\w]{10}").render()
        password_hash=str(generate_password_hash(password, 10))
        try:
            msg=Message('Preskriber-Affliate', sender='mrpreskriber@gmail.com', recipients=email)
            msg.body="Hello "+first_name+"! "+"Please use this code("+password+") to log into Preskriber. Please remember to change it immediately."  
            mail.send(msg)
        except:
            flash("EMAIL ERROR!", 'error')
            return redirect(url_for('home'))
        else:
            try:
                add_affliate=Users(First_Name=first_name, Middle_Name=middle_name, Last_Name=last_name, Phone=phone, Email=email, Address=address, Level='affliate', Organisation=details[2], Health_Code=code, Password_Hash=password_hash, Status="Green", Created_By=details[3])
                db.session.add(add_affliate)
                db.session.commit()
            except:
                flash("EMAIL ERROR!", 'error')
                return redirect(url_for('home'))
            else:
                flash("SUCCESSFULLY ADDED AFFLIATE INTO CIRCLE!", 'info')
                return redirect(url_for('home'))
######################################################################################
@app.route('/remove/<email>/', methods=['GET', 'POST'])################admin&official
@login_required
def remove(email):
    error=None
    details=(session.get('username')).split("|")
    username=details[0]
    level=details[1]
    if level not in ['pharmacist']:
        return redirect(url_for('home'))
    else:
        affliate=Users.query.filter_by(Email=email).first()
        affliate.Status="removed"
        db.session.commit()
        flash("SUCCESSFULLY REMOVED AFFLIATE FROM CIRCLE!", 'info')
        return redirect(url_for('home'))
######################################################################################/admin?page=2
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
if __name__=='__main__':
    port = int(os.environ.get('PORT', 5555))
    app.run(host='0.0.0.0', port=port)

    # Create DB
    db.create_all()

    # Start app
#app.run()
app.run(debug=True)

######################################################################################

#if __name__=='__main__':
    #db.create_all()
    #app.run(host= '0.0.0.0',port=8899 , debug=False)
    #app.run(host= '0.0.0.0',port=8888 , debug=True)
