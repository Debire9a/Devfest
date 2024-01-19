from flask import Flask,render_template,flash, url_for, redirect,request,session
import requests,json
from sqlalchemy.sql import text
from pkg import app
import os,random,string
from functools import wraps
from sqlalchemy import and_,desc
from pkg.models import db,User,Level,Donation,Breakout,UserRegistration
from werkzeug.security import generate_password_hash,check_password_hash

def get_hotels():
  try:
    url = "http://127.0.0.1:3000/api/v1/listall"
    response = requests.get(url)
    data = response.json()

    return data
  except:
      None

def login_required(f):
    @wraps(f)
    def check_login(*args,**kwargs):
        if session.get("useronline") != None:
          return f(*args,**kwargs)

        else:
            flash("You Must be logged in to acess this page",category='error')
            return redirect(url_for("login"))
    return check_login





@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template ("user/register.html")
    else:
        state = request.form.get('state')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        pwd = request.form.get('pwd')
        LGa = request.form.get('lga')
        hashed_pwd = generate_password_hash(pwd)

        if state != "" and fname != "" and lname != "" and email != "":

            user=User(user_fname = fname, user_lname=lname, user_email=email,user_password= hashed_pwd , user_stateid = state, user_lgaid = LGa)
            db.session.add(user)
            db.session.commit()

            return "Done"
        
        else:
            flash ("Please fill a fields", category='error')
            return redirect(url_for())

@app.route("/")
def home():
     
     hotel = get_hotels()
     id = session.get('Useronline')
     if session.get("useronline") != None:
        deets = User.query.get(id)

     else:
        deets = None
     return render_template("user/home_layout.html",deets=deets,data=hotel)

@app.route("/home_edit")
def home_layout():
   
    return render_template("user/home.html",)

@app.route("/dashboard/")
@login_required
def user_dashboard():
    id = session.get('useronline')
    if id != None:
        deets = User.query.get(id)
        return render_template("user/dashboard.html", deets=deets)
    
        

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template("user/loginpage.html")
    else:
        email = request.form.get('email')
        pwd = request.form.get('pwd')

        record = db.session.query(User).filter(User.user_email == email).first()
        if record:
            hashed_pwd = record.user_password
            rsp = check_password_hash(hashed_pwd,pwd)
            if rsp:
                 id = record.user_id
                 session['useronline']=id
                 return redirect("/dashboard")
            else:
                flash("Incorrect password", category="error")
                return redirect("/login")
        else:
            flash("Incorrect email", category="error")
            return redirect("/login")
        

@app.route('/logout')
def logout():
    if session.get("useronline") != None:
        session.pop("useronline",None)

    return redirect("/")


@app.route('/profile',methods=["POST","GET"])
@login_required
def profile():
    id = session.get("useronline")
    if request.method == "GET":
        deets=User.query.get(id)
        devs = db.session.query(Level).all()
        return render_template("user/profile.html",devs=devs,deets=deets)
    else:
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        phone = request.form.get("phone")
        level = request.form.get("level")
        update = db.session.query(User).get(id)

        update.user_fname=fname
        update.user_lname=lname
        update.user_phone=phone
        update.user_levelid=level

        db.session.commit()
        return redirect("/dashboard/")


@app.route("/changedp",methods=["POST","GET"])
@login_required
def changedp():
    id = session.get("useronline")
    deets = User.query.get(id)
    if request.method == "GET":
        return render_template("user/changedp.html", deets=deets)
    else:
        dp = request.files.get("dp")
        filename=dp.filename   #Empty if no filetype was selected for upload
        if filename == "":
            flash("Please Select a File", category="error")
            return redirect("/chagedp")
        else:
            name,ext = os.path.splitext(filename)
            allowed = ['.jpg','.png','.jpeg']
        # ext = filename.split('.')
            if ext.lower() in allowed:
                # final_name = random.sample(string.ascii_lowercase,10)
                final_name = int(random.random() * 10000000000)
                final_name = str(final_name) + ext
                dp.save(f"pkg/static/profile/{final_name}")
                flash("Profile picture added", category="Success")
                user = db.session.query(User).get(id)
                user.user_pix = final_name
                db.session.commit()

                return redirect("/dashboard")
                # final_name = str(id)+filename
                # dp.save(f"pkg/static/profile/{final_name}")
                # return "Done"
            else:
                flash("Extension not allowed",category='error')
                return redirect("/changedp")
            

        
@app.route('/donations/',methods=['POST','GET'])
@login_required
def donations():
   id = session.get('useronline')
   if request.method == 'GET':
    deets = User.query.get(id)
    return render_template('user/donations.html', deets=deets)
   else:
       fullname = request.form.get('fullname')
       email = request.form.get('email')
       amt = request.form.get('amt')
       ref = int(random.random() * 10000000)
       custom = str(ref) + str(id)
       session['custom'] = custom

       if fullname != "" and email != "" and amt != "":
            donate = Donation(donate_donor = fullname,donate_amt = amt,donate_email=email,donate_status='Pending',donate_userid=id,donate_ref=custom)
            db.session.add(donate)
            db.session.commit()

            if donate.donate_id:
                return redirect('/confirm/payment')
       else:
           flash('Please complete the form')
           return redirect("/donations/")

@app.route('/confirm/payment')   
@login_required
def confirm():
    id = session.get('useronline')
    deets = User.query.get(id)

    ref = session.get('custom')

    if ref:
        donation_deets = Donation.query.filter(Donation.donate_ref == ref).first()
        return render_template("user/confirmpage.html",deets=deets,donation_deets=donation_deets)
    
    else:
        flash("Please start the transaction again")
        return redirect('/donations/')


@app.route("/topaystack", methods = ['POST'])
@login_required
def topaystack():
    id = session.get('useronline')
    custom = session.get('custom')
    if custom:
        url="https://api.paystack.co/transaction/initialize"

        headers = {"Content-Type": "application/json","Authorization": "Bearer sk_test_44dd1f5b176b92e54eadf26f1e62b2076d5332ea"}

        transaction_deets = Donation.query.filter(Donation.donate_ref == custom).first()

        data = {"email":transaction_deets.donate_email,"amount":transaction_deets.donate_amt * 100, "reference":custom}

        response = requests.post(url,headers=headers,data=json.dumps(data))
        rspjson = response.json()
        if rspjson and rspjson.get('status') == True:
            authurl = rspjson['data']['authorization_url']
            return redirect(authurl)
        else:
            flash("Start the payment process again")
            return redirect('/donations/')
        # return "We will connect to Paystack here"
    
    else:
        flash("Start the payment process again")
        return redirect('/donations/')
    

@app.route('/paylanding')
@login_required
def paylanding():
    id = session.get('useronline')
    
    trxref = request.args.get('trxref')

    if trxref == session.get('custom'):
        #!/bin/sh
        url="https://api.paystack.co/transaction/verify/"+session.get('custom')
        headers = {"Content-Type": "application/json","Authorization": "Bearer sk_test_44dd1f5b176b92e54eadf26f1e62b2076d5332ea"}

        response = requests.get(url,headers=headers)
        rsp = response.json()
        return rsp
    else:
        return "Start again"


@app.route('/breakout/', methods = ['POST','GET'])
@login_required
def breakout():
    id = session.get('useronline')
    deets = User.query.get(id)
    if request.method == 'GET':
        topics = Breakout.query.filter(Breakout.break_status == 1, Breakout.break_level == deets.user_levelid).all()

        regtopics = [x.break_id for x in deets.myregistrations]

        #Using query
        # regtopics = UserRegistration.query.filter(UserRegistration.user_id == id).all()

        #Using relationships
        # regtopics = deets.myregistrations

        return render_template('user/mybreakout.html', deets=deets, topics = topics,regtopics=regtopics)
    else:
        mytopics = request.form.getlist('topicid')
        if mytopics:
            # prev_reg=db.session.query(UserRegistration).filter(UserRegistration.userid == id).all()
            db.session.execute(db.text(f"DELETE FROM user_registration WHERE user_id={id}"))
            db.session.commit()
            for t in mytopics:
                user_reg = UserRegistration(user_id=id, break_id=t)
                db.session.add(user_reg)
            db.session.commit()
            flash('Your registration was Sucessful')
            return redirect('/dashboard/')
        else:
            flash('You must choosse a topic')
            return redirect('/breakout/')


       



    

        