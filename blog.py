from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
    )
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("blog", __name__)

@bp.route("/")
def index():

    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username, likes"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
        ).fetchall()
    return render_template("blog/index.html", posts=posts)

@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None
        print("test")

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id)"
                " VALUES (?, ?, ?)",
                (title, body, g.user["id"])
            )
            db.commit()
            return redirect(url_for("blog.index"))
    return render_template("blog/create.html")

def get_post(id, check_author=True):
    post = get_db().execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " WHERE p.id = ?",
        (id,)
        ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    
    return post

def get_user(id):
    user = get_db().execute(
        "SELECT * FROM User"
    )


@bp.route("/<int:id>/update", methods=("GET","POST"))
@login_required
def update(id):
    
    post = get_post(id)
    

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)


        else:
            db=get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ?"
                "WHERE id = ?",
                (title, body, id)
                )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>delete", methods=("POST",))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))


@bp.route("/like/<int:postid>/<int:userid>?<string:page>", methods=("GET","POST", "UPDATE"))
@login_required
def likePost(postid, userid, page="index"):

    print("Likepost Running. Called by page: ", page)

    post = get_post(postid, False)
    user = get_user(userid)
    likeresult = check_if_liked(postid, userid)
    dislikeresult = check_if_disliked(postid, userid)

    db = get_db()

    if likeresult:
        print("Unliking")
        db.execute("UPDATE post set likes = likes-1 WHERE id = ?",(postid,))
        db.execute("DELETE FROM likes where post_id=? and user_id = ?;",(postid,userid))
        db.commit()
        

    if likeresult == None:
        if dislikeresult == None:
            db.execute("UPDATE post set likes = likes+1 WHERE id = ?",(postid,))
            db.execute("INSERT INTO likes (post_id, user_id) VALUES (?,?)",(postid,userid))
            db.commit()
        else:
            db.execute("UPDATE post set likes = likes+2 WHERE id = ?",(postid,))
            db.execute("INSERT INTO likes (post_id, user_id) VALUES (?,?)",(postid,userid))
            db.execute("DELETE FROM dislikes where post_id=? and user_id = ?;",(postid,userid))
            db.commit()

    if page== "index":
        print("running index")
        return redirect(url_for("blog.index"))

    if page== "profile":
        print("running profile")
        return redirect(url_for("profile.profile", userid=post['author_id']))

def get_like(postid, userid):
    user = get_db().execute(
        "SELECT * FROM likes where "
    )


@bp.route("/dislike/<int:postid>/<userid>?<string:page>", methods=("GET","POST"))
@login_required
def dislikePost(postid, userid, page="index"):
    post = get_post(postid, False)
    user = get_user(userid)
    db = get_db()
    likeresult = check_if_liked(postid, userid)
    dislikeresult = check_if_disliked(postid, userid)

    if dislikeresult:
        print("Undisliking")
        db.execute("UPDATE post set likes = likes+1 WHERE id = ?",(postid,))
        db.execute("DELETE FROM dislikes where post_id=? and user_id = ?;",(postid,userid))
        db.commit()
    
    if dislikeresult == None:
        if likeresult == None:
            db.execute("UPDATE post set likes = likes-1 WHERE id = ?",(postid,))
            db.execute("INSERT INTO dislikes (post_id, user_id) VALUES (?,?)",(postid,userid))
            db.commit()
        else:
            db.execute("UPDATE post set likes = likes-2 WHERE id = ?",(postid,))
            db.execute("INSERT INTO dislikes (post_id, user_id) VALUES (?,?)",(postid,userid))
            db.execute("DELETE FROM likes where post_id=? and user_id = ?;",(postid,userid))
            db.commit()
    

    if page == "index":
        return redirect(url_for("blog.index"))

    if page == "profile":
        return redirect(url_for("profile.profile", userid=post['author_id']))   

def check_if_liked(postid, userid):
    db = get_db()
    result = db.execute("SELECT * from likes where post_id=? AND user_id=?", (postid, userid)).fetchone()
    return result



def check_if_disliked(postid, userid):
    db = get_db()
    result = db.execute("SELECT * from dislikes where post_id=? AND user_id=?", (postid, userid)).fetchone()
    return result



# ----------- SEARCH FEATURE -----------

@bp.route("/search/", methods=("GET", "POST"))
def search_posts():
    
    searchterm = request.args.get("keyword")
    print(searchterm)
    category = request.args.get("category")
    print(category)
    db = get_db()
    
    if category == "body":
        posts = db.execute("SELECT p.id, title, body, created, author_id, username, likes"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " WHERE body LIKE ?"
        " ORDER BY created DESC",("%" + searchterm + "%",)).fetchall()
        print(posts)
    

    if category == "title":
        posts = db.execute("SELECT p.id, title, body, created, author_id, username, likes"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " WHERE title LIKE ?"
        " ORDER BY created DESC",("%" + searchterm + "%",)).fetchall()
        print(posts)
        

    if category == "user":
        posts = db.execute("SELECT * from post WHERE title LIKE ?", ("%" + searchterm + "%",)).fetchall()
        
    
    for x in posts: (print(x["id"]))
    print(len(posts))
    return render_template("blog/search.html", posts=posts, amount=len(posts))

















        





