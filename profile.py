from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
    )
from werkzeug.exceptions import abort
import os
from werkzeug.utils import secure_filename

from flaskr.auth import login_required
from flaskr.db import get_db

ALLOWED_EXTENSIONS = {'jpg', 'jpeg',}

bp = Blueprint("profile", __name__,url_prefix="/profile")

@bp.route("/<int:userid>", methods=("GET","POST"))
@login_required
def profile(userid):
    
    user = get_user(userid)
    posts = get_user_posts(userid)
    print(user["joindate"])

    return render_template("profile/main.html", user=user, posts=posts)


@bp.route("/<int:userid>/bio/update", methods=("GET","POST"))
@login_required
def edit_bio(userid):
    
    bio = get_bio(userid)
    user = get_user(userid)
    

    
    if request.method == "POST":
        body = request.form["bio"]
        error = None
        db = get_db()
        db.execute("UPDATE user SET bio = ? WHERE id = ?", (body, userid))
        db.commit()
        return redirect(url_for("profile.profile", userid = userid))

    return render_template("profile/edit_bio.html", user=user)


def get_bio(userid, check_user=True):
    bio = get_db().execute(
        " SELECT bio from USER where id=?", (userid,)
    ).fetchone()

    if check_user and userid != g.user["id"]:
        abort(403)

    return bio

def get_user(userid):
    user = get_db().execute(
        " SELECT * from USER where id=?", (userid,)
    ).fetchone()
    return user

def get_user_posts(userid):
    posts = get_db().execute(
        "SELECT * from post WHERE author_id=?", (userid,)
        ).fetchall()
    return posts

def get_user_avatar(userid):
    pass

@bp.route("/<int:userid>/avatar/update", methods=["GET","POST"])
@login_required
def change_avatar(userid):
    
    user = get_user(userid)
    allowed_file("hi")

    if request.method == "POST":
        print(request.files.get("file"))

        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            file.save(os.path.join(current_app.config['UPLOAD_PATH'], filename))
            return redirect(url_for("profile.profile", userid=userid))

    return render_template("profile/change_avatar.html", user=user)

def allowed_file(filename):
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

print("asdasdasda")