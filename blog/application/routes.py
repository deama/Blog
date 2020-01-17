from sqlalchemy import desc
from flask import render_template, redirect, url_for, request, jsonify, session
from application import app, db, bcrypt, login_manager, socketio, s3
from application.forms import RegistrationForm, LoginForm, AccountUpdateForm, BlogForm
from application.models import Account_details, Blog
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import SocketIO, emit
import boto3

#db.create_all()

sessionID = 0
gameSessions = {}
snakeBackgroundColor = "grey"


@app.route("/")
def home():
    return render_template("home.html", title="Blog")


@app.route("/account", methods=["GET","POST"])
def account():
    if current_user.is_authenticated:
        form = AccountUpdateForm()
        if form.validate_on_submit():
            if form.delete.data:
                player_name = Account_details.query.filter_by( player_id=current_user.get_id() ).first()
                db.session.delete(player_name)

                player_blog = Blog.query.filter_by( player_id=None )
                for deleted in player_blog:
                    db.session.delete(deleted)

                db.session.commit()
                return redirect(url_for("login"))

            else:
                current_user.login = form.new_login.data

                player_name = Account_details.query.filter_by( player_id=current_user.get_id() ).first()
                player_name.name = form.new_login.data
                
                s3.Bucket("app-blog-bucket-1295").put_object(Key="images/"+player_name.name+".jpg", Body=request.files["image"] )

                account_image_name = Account_details.query.filter_by( player_id=current_user.get_id() ).first()
                account_image_name.account_image_name = player_name.name+".jpg"

                db.session.commit()
                return redirect(url_for("account"))

        elif request.method == "GET":
            form.new_login.data = current_user.login

        return render_template("account.html", title = "Account update", form = form)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("postBlog"))

    form = LoginForm()
    if form.validate_on_submit():
        user = Account_details.query.filter_by( login=form.login.data ).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")

            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for("home"))

    return render_template("login.html", title="Login", form=form)

@app.route("/uploadImage", methods=["POST"])
def uploadImage():
    return "test"

@app.route("/register", methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegistrationForm()
    if form.validate_on_submit():
            hashed_pw = bcrypt.generate_password_hash( form.password.data )

            account = Account_details( login=form.login.data, password=hashed_pw, account_image_name="default.jpg" )

            db.session.add(account)
            db.session.commit()

            return redirect( url_for("home") )
    return render_template("register.html", title="Register", form=form)

@app.route("/postBlog", methods=["GET","POST"])
def postBlog():
    if current_user.is_authenticated:
        form = BlogForm()
        if form.validate_on_submit():
            post = Blog( player_id=current_user.get_id(), text=form.text.data )

            db.session.add(post)
            db.session.commit()
            return render_template("postBlog.html", title="Post to Blog", form=form, posted=True)

        return render_template("postBlog.html", title="Post to Blog", form=form, posted=False)

    return redirect( url_for("login") )

@app.route("/blog", methods=["GET","POST"])
def blog():
    if current_user.is_authenticated:
        blogPosts = Blog.query.all()
        posts = []

        for post in blogPosts:
            account = Account_details.query.filter_by( player_id=post.player_id ).first()
            posts.append( {"image":"https://app-blog-bucket-1295.s3-eu-west-1.amazonaws.com/images/"+account.account_image_name, "name":account.login, "post":post.text} )

        return render_template("viewBlog.html", title="Blog Posts", posts=posts)


    return redirect(url_for("login"))
