from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Index Page'


@app.route('/commercial')
def commercial():
    return 'Commercial page'


@app.route('/residential')
def residential():
    return 'Residential page'


@app.route('/industrial')
def industrial():
    return 'Industrial page'


@app.route('/calculate')
def calculate():
    result = '0'
    return 'result'


if __name__ == '__main__':
    app.run()
