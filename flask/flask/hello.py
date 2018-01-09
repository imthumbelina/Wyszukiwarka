from flask import Flask, render_template, request
from flask_wtf import Form
from wtforms import StringField, PasswordField
app = Flask(__name__)
app.config['SECRET KEY'] = 'DontTellAnyone'


class LoginForm(Form):
    username = StringField('username')
    password = PasswordField('password')

@app.route("/", methods=['GET','POST'])
def index():
    return render_template('test.html')

@app.route('/profile/<name>')
def profile(name):
    return render_template("index.html", name = name)

if __name__ == "__main__":
    app.run()
