from flask import Flask , jsonify, request
from random import choice

app = Flask(__name__)     
ip = ("138.197.181.206:8000/")

@app.route('/')
def main():
   return ip

if __name__ == '__main__':
    app.run(debug=True, host="localhost", port=10101)