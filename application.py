from flask import Flask

application = Flask(__name__)




@application.route('/')
def hello_world():
    return 'Index Page'


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


if __name__ == '__main__':
    application.run()
