from distutils.log import error
import re
from flask import Flask, jsonify, render_template, request
import uuid
import time
from sqlite3 import connect as sqlconn
from os import path, mkdir

BALERROR = "balance-error"
DATA_DIR = "data/"

WALLETS_DATABASE = DATA_DIR + '/Wallets.db'

if not path.exists(DATA_DIR): # if the folder data don`t exist, create it
    mkdir(DATA_DIR)

try: # if the database table don`t exist, create it
    with sqlconn(WALLETS_DATABASE, timeout=30) as conn:
        db = conn.cursor()
        db.execute("CREATE TABLE IF NOT EXISTS wallets (address varchar(255), balance integer, job varchar(46), time integer)")
        conn.commit()
except Exception as e:
    print(e)


def open_account(addr):
    try:
        with sqlconn(WALLETS_DATABASE, timeout=30) as conn:
            db = conn.cursor()
            db.execute("SELECT * FROM wallets WHERE address = (?)", (addr,))
            if db.fetchone() is None:
                db.execute("INSERT INTO wallets VALUES (?, 0, '', ?)", (addr, time.time(),))
                conn.commit()
                return True
            else:
                return None
    except Exception as e:
        print(e)
        return False

def update_bank(addr, bal=0):
    try:
        with sqlconn(WALLETS_DATABASE, timeout=30) as conn:
            datab = conn.cursor()

            datab.execute(
                """SELECT * FROM wallets WHERE address = ?""", (addr,))
            conn.commit()

            user = datab.fetchone()
            if user is not None:
                bal = user[1] + bal

            datab.execute(
                """UPDATE wallets SET balance = ? WHERE address = ?""", (bal, addr,))
            conn.commit()
    except Exception as e:
        print(e)
        try:
            with sqlconn(WALLETS_DATABASE, timeout=30) as conn:
                datab = conn.cursor()
                datab.execute(
                    """SELECT * FROM wallets WHERE address = ?""", (addr,))
                conn.commit()

                user = datab.fetchone()

                if user is None:
                    return False
                else:
                    bal = user[1]
        except Exception as e:
            print(e)
        return bal

app = Flask(__name__)

@app.route("/")
def main():  
    return render_template("index.html")

@app.route("/createData/<string:addr>")
def createData(addr):
    job = str(uuid.uuid4())
    account = open_account(addr)
    if account == False:
        return jsonify(success=False, error="unknown")
    try:
        with sqlconn(WALLETS_DATABASE, timeout=30) as conn:
            db = conn.cursor()
            db.execute("UPDATE wallets SET job = (?), time = (?) WHERE address = (?)", (job, time.time(), addr,))
            conn.commit()
            return jsonify(success=True, job=job)
    except Exception as e:
        print(e)
        return jsonify(success=False, error="unknown")
    

@app.route("/acceptjob/<string:job>/<string:addr>")
def acceptjob(job, addr):
    try:
        if job is not None and addr is not None:
            with sqlconn(WALLETS_DATABASE, timeout=30) as conn:
                    db = conn.cursor()
                    db.execute("SELECT job, time FROM wallets WHERE address = (?)", (addr,))
                    user = db.fetchone()
                    if user == None or user[0] == "":
                        return jsonify(success=False, error="nojob:account")
                    
                    if int(user[1]) + 25 < int(time.time()):
                        if user[0] == job:
                            db.execute("UPDATE wallets SET job = '' WHERE address = (?)", (addr,))
                            conn.commit()
                            update_bank(addr, 1)
                            return ("success=True Share Accepted! Moving On..")
                        else:
                            return jsonify(success=False, error="jobwrong")
                    else:
                        return jsonify(success=False, error="time")
        else:
            return jsonify(success=False, error="job:addrmissing")
    except Exception as e:
        print(e)
        return jsonify(success=False, error="unknown")


@app.route("/api/getBalance")
def getBalance():
    try:
        addr = str(request.args.get('address'))
        if addr is not None:
            with sqlconn(WALLETS_DATABASE, timeout=30) as conn:
                db = conn.cursor()
                db.execute("SELECT balance FROM wallets WHERE address = (?)", (addr,))
                conn.commit()

                user = db.fetchone()

                if user is None:
                    return jsonify(success=False, error="no user")

                return jsonify(success=True, balance=user[0])
        else:
            return jsonify(success=False, error="address")
    except Exception as e:
        print(e)
        return jsonify(success=False, error="unknown")

if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=10101)
