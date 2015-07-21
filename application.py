from flask import Flask

applicaion = Flask(__name__)


@applicaion.route('/')
def hello_world():
    return 'Index Page'


@applicaion.route('/commercial')
def commercial():
    return 'Commercial page'


@applicaion.route('/residential')
def residential():
    return 'Residential page'


@applicaion.route('/industrial')
def industrial():
    return 'Industrial page'


@applicaion.route('/calculate')
def calculate():
    result = '0'
    return 'result'


if __name__ == '__main__':
    applicaion.run()
