from datetime import datetime
import os,random,string
from functools import wraps
from flask import render_template, abort, request, redirect, flash, url_for, make_response, session
from werkzeug.security import generate_password_hash, check_password_hash
from pkg import app 

from pkg.models import db, User, Level, Admin, Breakout

from pkg.forms import Breakoutform

@app.route("/admin/dashboard")
def admin_dashboard():
    return render_template("admin/dashboard.html")


@app.route("/admin/user")
def admin_user():
    return render_template("admin/admin_layout.html")



@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin/login.html')
    else: #retrieve form data
        email = request.form.get('email')
        pwd = request.form.get('pwd')

        admin = db.session.query(Admin).filter(Admin.admin_username == email).first()

        if admin != None: #check password
            saved_pwd = admin.admin_pwd
            check = check_password_hash(saved_pwd,pwd)
            if check:
                session['adminonline'] = admin.admin_id
                flash("Welcome", category="success")
                return redirect(url_for('admin_dashboard'))
            else:
                flash("Invalid credentials", category="error")
                return redirect('/admin/login')
        else:

            flash("Invalid credentials", category="error")
            return redirect('/admin/login')

@app.route('/admin/')
def admin_home():
    return "Welcome"

@app.route("/admin/breakouts")
def admin_breakouts():
    alltopics = db.session.query(Breakout).all()
    return render_template("admin/breakout.html", alltopics=alltopics)


@app.route("/admin/addtopic", methods=['Get', 'POST'])
def admin_addtopic():
    bform = Breakoutform()
    devs = db.session.query(Level).all()
    if request.method == 'GET':
        
        return render_template("admin/addtopic.html", bform=bform, devs=devs)
    else:
        if bform.validate_on_submit():
            title = bform.title.data
            # status = bform.status.data
            status =request.form.get('status')
            file = bform.image.data
            level = request.form.get('level')
            filename = bform.image.data.filename
            #you can set a new file name here if you wish
            file.save(f"pkg/static/uploads/{filename}")
            #insert into database, we redirect to url_for('breakouts)
            topic = Breakout(break_title=title, break_image=filename,break_status=status,break_level=level)
            db.session.add(topic)
            db.session.commit()
            return redirect('/admin/breakouts')
        else:
            return render_template("admin/addtopic.html", bform=bform, devs=devs)

