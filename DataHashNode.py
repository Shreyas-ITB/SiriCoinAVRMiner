from flask import Flask, jsonify, render_template, request
import random
import json
from sqlite3 import connect as sqlconn
from os import path, mkdir

DATA_DIR = "data/"

WALLETS_DATABASE = DATA_DIR + '/Wallets.db'

if not path.exists(DATA_DIR): # if the folder data don`t exist, create it
    mkdir(DATA_DIR)

try: # if the database table don`t exist, create it
    with sqlconn(WALLETS_DATABASE, timeout=30) as conn:
        datab = conn.cursor()
        datab.execute(
            """CREATE TABLE IF NOT EXISTS wallets (address VARCHAR(255), balance REAL)""")
        conn.commit()
except Exception as e:
    print(e)

app = Flask(__name__)
Data =[]
Addr =[]

@app.route('/')
def main():  
    return render_template("index.html")

@app.route('/createData')
def createData():
    Hashlib = (
    "Hash1 05feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9",
    "Hash2 12cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
    "Hash3 2dcbf9fc03886e330869492a628f13774a0ca74b083e54a36a2876cef138bad30",
    "Hash4 34f4866995bcc400c9934134224addfa08c91544ba95ac674f0312e0687873aed",
    "Hash5 4559aead08264d5795d3909718cdd05abd49572e84fe55590eef31a88a08fdffd",
    "Hash6 5df7e70e5021544f4834bbee64a9e3789febc4be81470df629cad6ddb03320a5c",
    "Hash7 66b23c0d5f35d1b11f9b683f0b0a617355deb11277d91ae091d399c655b87940d",
    "Hash8 73f39d5c348e5b79d06e842c114e6cc571583bbf44e4b0ebfda1a01ec05745d43",
    "Hash9 8f67ab10ad4e4c53121b6a5fe4da9c10ddee905b978d3788d2723d7bfacbe28a9",
    "Hash10 9333e0a1e27815d0ceee55c473fe3dc93d56c63e3bee2b3b4aee8eed6d70191a3",
    "Hash11 1044bd7ae60f478fae1061e11a7739f4b94d1daf917982d33b6fc8a01a63f89c21",
    "Hash12 11a83dd0ccbffe39d071cc317ddf6e97f5c6b1c87af91919271f9fa140b0508c6c",
    "Hash13 126da43b944e494e885e69af021f93c6d9331c78aa228084711429160a5bbd15b5",
    "Hash14 1386be9a55762d316a3026c2836d044f5fc76e34da10e1b45feee5f18be7edb177",
    "Hash15 1472dfcfb0c470ac255cde83fb8fe38de8a128188e03ea5ba5b2a93adbea1062fa",
    "Hash16 1508f271887ce94707da822d5263bae19d5519cb3614e0daedc4c7ce5dab7473f1",
    "Hash17 168ce86a6ae65d3692e7305e2c58ac62eebd97d3d943e093f577da25c36988246b",
    "Hash18 175c62e091b8c0565f1bafad0dad5934276143ae2ccef7a5381e8ada5b1a8d26d2",
    "Hash19 184ae81572f06e1b88fd5ced7a1a000945432e83e1551e6f721ee9c00b8cc33260",
    "Hash20 198c2574892063f995fdf756bce07f46c1a5193e54cd52837ed91e32008ccf41ac",
    "Hash21 208de0b3c47f112c59745f717a626932264c422a7563954872e237b223af4ad643")
    HashData = random.choice(Hashlib)
    return HashData

@app.route('/acceptjob/<string:job>', methods=['POST'])
def JobSolved(job):
    if job is not None:
        try:
            json.loads(f'{job}')
        except ValueError as e:
            return "(ERROR) Share Rejected. {May Be The Hash is not valid to accept}"
        return "Share Accepted!! (Verified Hash) Moving on..."
    else:
        return "Share Rejected. {May Be The Hash is not valid to accept}"

def open_account(addr):
    try:
        with sqlconn(WALLETS_DATABASE, timeout=30) as conn:
            datab = conn.cursor()
            datab.execute(
                """SELECT * FROM wallets WHERE address = ?""", (addr,))
            conn.commit()
            if datab.fetchone() is None:
                datab.execute(
                    """INSERT INTO wallets (address, balance) VALUES (?, ?)""", (addr, 0))
                conn.commit()
                return True
    except Exception as e:
        print(e)
    return True

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

@app.route('/getaddr/<string:addr>', methods=['POST'])
def getAddr(addr):
    if addr is not None:
        Addr.append(addr)
        open_account(addr)
        update_bank(addr, 1)
        return addr
    else:
        return "Error"

@app.route('/api/getBalance', methods=['GET'])
def getBalance():
    try:
        addr = str(request.args.get('address'))
        if addr is not None:
            bal = 0
            try:
                with sqlconn(WALLETS_DATABASE, timeout=30) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        """SELECT * FROM wallets WHERE address = ?""", (addr,))
                    conn.commit()

                    user = datab.fetchone()

                    if user is None:
                        return jsonify(result = "Error: your account don`t exist")
                    else:
                        bal = user[1]
            except Exception as e:
                print(e)
            return jsonify(result = bal)
        else:
            return jsonify(result = "Error: your address isn`t valid")
    except Exception as e:
        print(e)
        return jsonify(result = "Error fetching the address")

if __name__ == '__main__':
    app.run(debug=True, host="localhost", port=10101)
