from flask import Flask

app = Flask(__name__)


from airline.routes import homepage