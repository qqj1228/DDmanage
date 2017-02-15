from flask import Flask
from flask import render_template
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('base.html', web_name='图纸管理程序')


@app.route('/hello')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)