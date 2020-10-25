import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
            )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


# INITIALIZING THE DATABASE COMMAND
def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))

@click.command("init-db")
@with_appcontext
def init_db_command():
    init_db()
    click.echo("Initialized the database.")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


"""

EXECUTING SQL COMMAND
This let's me execute SQL Files using the execute.sql in the project folder

USAGE
First, register the command in the __init__.py file by using the followign code:
  from . import db
  db.init_sql(app)

Second, make an execute.sql file in your project folder. This is where you write the SQL code that
you want executed

"""

def execute_sql():
    db = get_db()
    with current_app.open_resource("execute.sql") as f:
        db.executescript(f.read().decode("utf8"))

@click.command("sqlexecute")
@with_appcontext
def execute_sql_command():
    execute_sql()
    click.echo("SQL executed.")

def init_sql(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(execute_sql_command)
    
    



