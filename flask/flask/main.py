from flask import Flask, render_template
from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired
import searcher as sr


app = Flask(__name__)
app.config['SECRET_KEY'] = 'DontTellAnyone'

class LoginForm(Form):
	query = StringField('enter query', validators=[InputRequired()])

@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    print('hello world')
    if form.validate_on_submit():
        results=[format(form.query.data)]
        indexes = sr.search(format(form.query.data))
        return render_template('view.html',results = indexes)
    return render_template('index.html', form=form)

if __name__ == '__main__':
	app.run(debug=True)
