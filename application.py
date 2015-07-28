from flask import Flask, render_template

application = Flask(__name__)


@application.route('/')
@application.route('/index')
def hello_world():
    return render_template('index.html')


@application.route('/commercial')
def commercial():
    return 'Commercial page'


@application.route('/residential')
def residential():
    return 'Residential page'


@application.route('/industrial')
def industrial():
    return 'Industrial page'


@application.route('/calculate')
def calculate():
    result = '0'
    return 'result'


@application.route('/calculator')
def calculator():
    return render_template('calc.html')


if __name__ == '__main__':
    application.run(debug=True)
