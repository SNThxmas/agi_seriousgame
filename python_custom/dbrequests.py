import sqlite3 as lite

def _check_args(SQL_command, SQL_params):
    if SQL_command.count("?") != len(SQL_params):
        raise ValueError("The number of '?' in the SQL command must be equal to the number of parameters in the tuple.", SQL_command.count("?"), "? provided", len(SQL_params), "args given.")


def write_DB(SQL_command, SQL_params=()):
    _check_args(SQL_command, SQL_params)
    con = lite.connect("static/db/database.db")
    cur = con.cursor()
    cur.execute(SQL_command, SQL_params)
    con.commit()
    con.close()


def read_DB(SQL_command, SQL_params=()):
    _check_args(SQL_command, SQL_params)
    con = lite.connect("static/db/database.db")
    con.row_factory = lite.Row
    cur = con.cursor()
    result = cur.execute(SQL_command, SQL_params).fetchall()
    con.close()
    return result

def readone_DB(SQL_command, SQL_params=()):
    _check_args(SQL_command, SQL_params)
    con = lite.connect("static/db/database.db")
    con.row_factory = lite.Row
    cur = con.cursor()
    result = cur.execute(SQL_command, SQL_params).fetchone()[0]
    con.close()
    return result