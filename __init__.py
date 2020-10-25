import os
from flask import Flask

def create_app(test_config=None):
    print("\n----- New Instance -----")
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path,"flaskr.sqlite"),
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
        )

    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
    app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
    app.config['UPLOAD_PATH'] = os.path.join(app.instance_path, "uploads")

    if test_config is None:
        app.config.from_pyfile("config.py",silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from flaskr2 import db
    db.init_app(app)
    db.init_sql(app)

    from flaskr2 import auth
    app.register_blueprint(auth.bp)
    

    from flaskr2 import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule("/", endpoint="index")
    app.jinja_env.globals.update(check_if_liked=blog.check_if_liked)
    app.jinja_env.globals.update(check_if_disliked=blog.check_if_disliked)

    from flaskr2 import profile
    app.register_blueprint(profile.bp)
    app.add_url_rule("/", endpoint="profile")
    print(app.jinja_env.context_class)

    return app

print("hi")
print("sup")
print("asde")