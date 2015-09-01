import math
import os

from flask import Flask, render_template, jsonify, request, flash, url_for, redirect
import numpy
from boto import dynamodb2
from boto.dynamodb2.table import Table
from boto.dynamodb2.items import Item
from boto.dynamodb2.exceptions import ConditionalCheckFailedException
from boto import sns

from utils import lt2a, lt3, ht2b, ht2a, ht4

application = Flask(__name__)

application.secret_key = 'this is secret of solrify!! :P !!'

# Load config values specified above
application.config.from_object(__name__)

# Load configuration values from a file
application.config.from_envvar('APP_CONFIG', silent=True)

FLASK_DEBUG = 'True' if os.environ.get('FLASK_DEBUG') is None else os.environ.get('FLASK_DEBUG')

# Connect to DynamoDB and get ref to Table
ddb_conn = dynamodb2.connect_to_region(application.config['AWS_REGION'])
ddb_table = Table(table_name=application.config['CONTACT_TABLE'],
                  connection=ddb_conn)

# Connect to SNS
sns_conn = sns.connect_to_region(application.config['AWS_REGION'])


class resultClass:
    system_size = 0
    sys_type = 0
    total_cost = 0
    irr = 0
    roi = 0
    average_savings = 0

    def __init__(self, system_size, sys_type, total_cost, irr, roi, average_savings):
        self.system_size = system_size
        self.sys_type = sys_type
        self.total_cost = total_cost
        self.irr = irr
        self.roi = roi
        self.average_savings = average_savings


@application.route('/index')
@application.route('/')
def index():
    return render_template('index.html')


@application.route('/commercial')
def commercial():
    return render_template('commercial.html')


@application.route('/residential')
def residential():
    return render_template('residential.html')


@application.route('/industrial')
def industrial():
    return render_template('industrial.html')


@application.route('/faq')
def faq():
    return render_template('faq.html')


@application.route('/results', methods=['POST', 'GET'])
def calculate():
    try:
        city = str(request.form['city'])
        customer_type = str(request.form['cust_type'])  # residentaial-> R, commercial-> C, industrial -> I
        connection_type = str(request.form['conn_type'])  # LT, HT
        rooftop_area = int(request.form['area'])  # sqft
        # rooftop_type = 0  # 450
        monthly_bill = int(request.form['bill'])  # Rs.
        sanction_load = int(request.form['load'])  # kVA
    except:
        flash('Wrong Information!')
        return redirect(url_for('calculator'))

    print(city, customer_type, connection_type, rooftop_area, monthly_bill, sanction_load)

    # customer_type = 'R'  # residentaial-> R, commercial-> C, industrial -> I
    # connection_type = 'LT'  # LT, HT
    # rooftop_area = 200  # sqft
    # rooftop_type = 0  # 450
    # monthly_bill = 1000  # Rs.
    # sanction_load = 3  # kVA
    if (customer_type == 'R') & (connection_type == 'LT'):  # Residential and LT
        total_units = lt2a(monthly_bill)
        sys_type = 'Grid-tie'

    elif (customer_type == 'C') & (connection_type == 'LT'):  # Commercial & LT
        total_units = lt3(monthly_bill)
        sys_type = 'Grid-tie'

    elif (customer_type == 'I') & (connection_type == 'LT'):  # Industrial & LT
        total_units = lt3(monthly_bill)
        sys_type = 'Grid-interactive'

    elif (customer_type == 'R') & (connection_type == 'HT'):  # Residential and HT
        total_units = ht4(monthly_bill)
        sys_type = 'Grid-tie'

    elif (customer_type == 'C') & (connection_type == 'HT'):  # Commercial & HT
        total_units = ht2b(monthly_bill)
        sys_type = 'Grid-interactive'

    elif (customer_type == 'I') & (connection_type == 'HT'):  # Industrial & HT
        total_units = ht2a(monthly_bill)
        sys_type = 'Grid-interactive'

    elif (customer_type == 'R') & (connection_type == 0):  # Residential and -
        total_units = lt2a(monthly_bill)
        sys_type = 'Grid-tie'

    elif (customer_type == 'C') & (connection_type == 0):  # Commercial & -
        total_units = lt3(monthly_bill)
        sys_type = 'Grid-tie'

    elif (customer_type == 'I') & (connection_type == 0):  # Industrial & -
        total_units = ht2a(monthly_bill)
        sys_type = 'Grid-interactive'

    else:
        flash('Wrong Information!')
        return redirect(url_for('index'))

    size_of_rooftop_sys = ((total_units / 5) / 30)

    if size_of_rooftop_sys <= (rooftop_area / 100):
        system_size = math.ceil(
            size_of_rooftop_sys * 10) / 10.0  # math.ceil(num * 100) / 100.0 returns roundup to a float
        # print(1, system_size)
    else:
        system_size = math.ceil((rooftop_area / 100) * 10) / 10.0
        # print(2)

    system_size = min(sanction_load, system_size)

    total_cost = system_size * 90000

    units_prod_year = system_size * 5 * 300  # produced from solar

    units_used_year = total_units * 12  # from grid

    net_units_consumed = units_used_year - units_prod_year

    if net_units_consumed > 0:
        net_yearly_bill = net_units_consumed * 5.25
    else:
        net_yearly_bill = net_units_consumed * 9.56

    fst_year_bill = 12 * monthly_bill
    yearly_bills = [0, fst_year_bill]
    savings = [-total_cost, round(fst_year_bill - net_yearly_bill)]  # round(fst_year_bill - net_yearly_bill)
    for i in range(2, 14):
        # print(i)
        yearly_bills.append(round(yearly_bills[i - 1] * 1.025))
        savings.append(round(yearly_bills[i] - net_yearly_bill))
    sum1 = 0
    for i in range(1, len(savings)):
        # print(i)
        if sum1 > total_cost:
            i -= 1
            break
        else:
            sum1 += savings[i]

    sum2 = sum1
    sum1 = sum1 - savings[i]
    i = i - 1

    months = (total_cost - sum1) / savings[i + 1]
    roi = math.ceil((i + months) * 10) / 10.0
    print(sum1, sum2, i, roi)
    savings_irr = []
    for j in range(i + 2):
        savings_irr.append(savings[j])

    print(yearly_bills)
    print(savings)
    print(savings_irr)
    average_savings = 0
    for i in range(1, 11):
        # print(i)
        average_savings += savings[i]

    average_savings = average_savings / 10

    irr = round((numpy.irr(savings_irr) * 100.0), 2)
    print(irr)

    temp = {
        'total_units': total_units,
        'sys_type': sys_type,
        'size_of_rooftop_sys': size_of_rooftop_sys,
        'system_size': system_size,
        'total_cost': total_cost,
        'units_prod_year': units_prod_year,
        'units_used_year': units_used_year,
        'net_units_consumed': net_units_consumed,
        'irr': irr,
        'roi': roi,
        'average_savings': average_savings
    }

    res = {
        'system_size': system_size,
        'sys_type': sys_type,
        'total_cost': total_cost,
        'irr': irr,
        'roi': roi,
        'average_savings': average_savings
    }
    result = resultClass(system_size, sys_type, total_cost, irr, roi, average_savings)
    return render_template('results.html', result=result)


@application.route('/calculator')
def calculator():
    return render_template('calculator.html')


@application.route('/results_test')
def calculate_test():
    customer_type = 'R'  # residentaial-> R, commercial-> C, industrial -> I
    connection_type = 'LT'  # LT, HT
    rooftop_area = 200  # sqft
    rooftop_type = 0  # 450
    monthly_bill = 1000  # Rs.
    sanction_load = 3  # kVA
    city = "Bangalore"
    print(city, customer_type, connection_type, rooftop_area, monthly_bill, sanction_load)
    if (customer_type == 'R') & (connection_type == 'LT'):  # Residential and LT
        total_units = lt2a(monthly_bill)
        sys_type = 'Grid-tie'

    elif (customer_type == 'C') & (connection_type == 'LT'):  # Commercial & LT
        total_units = lt3(monthly_bill)
        sys_type = 'Grid-tie'

    elif (customer_type == 'I') & (connection_type == 'LT'):  # Industrial & LT
        total_units = lt3(monthly_bill)
        sys_type = 'Grid-interactive'

    elif (customer_type == 'R') & (connection_type == 'HT'):  # Residential and HT
        total_units = ht4(monthly_bill)
        sys_type = 'Grid-tie'

    elif (customer_type == 'C') & (connection_type == 'HT'):  # Commercial & HT
        total_units = ht2b(monthly_bill)
        sys_type = 'Grid-interactive'

    elif (customer_type == 'I') & (connection_type == 'HT'):  # Industrial & HT
        total_units = ht2a(monthly_bill)
        sys_type = 'Grid-interactive'

    elif (customer_type == 'R') & (connection_type == 0):  # Residential and -
        total_units = lt2a(monthly_bill)
        sys_type = 'Grid-tie'

    elif (customer_type == 'C') & (connection_type == 0):  # Commercial & -
        total_units = lt3(monthly_bill)
        sys_type = 'Grid-tie'

    elif (customer_type == 'I') & (connection_type == 0):  # Industrial & -
        total_units = ht2a(monthly_bill)
        sys_type = 'Grid-interactive'

    else:
        return jsonify(response="Wrong Info!")

    size_of_rooftop_sys = ((total_units / 5) / 30)

    if size_of_rooftop_sys <= (rooftop_area / 100):
        system_size = math.ceil(
            size_of_rooftop_sys * 10) / 10.0  # math.ceil(num * 100) / 100.0 returns roundup to a float
        # print(1, system_size)
    else:
        system_size = math.ceil((rooftop_area / 100) * 10) / 10.0
        # print(2)

    system_size = min(sanction_load, system_size)

    total_cost = system_size * 90000

    units_prod_year = system_size * 5 * 300  # produced from solar

    units_used_year = total_units * 12  # from grid

    net_units_consumed = units_used_year - units_prod_year

    if net_units_consumed > 0:
        net_yearly_bill = net_units_consumed * 5.25
    else:
        net_yearly_bill = net_units_consumed * 9.56

    fst_year_bill = 12 * monthly_bill
    yearly_bills = [0, fst_year_bill]
    savings = [-total_cost, round(fst_year_bill - net_yearly_bill)]  # round(fst_year_bill - net_yearly_bill)
    for i in range(2, 14):
        # print(i)
        yearly_bills.append(round(yearly_bills[i - 1] * 1.025))
        savings.append(round(yearly_bills[i] - net_yearly_bill))
    sum1 = 0
    for i in range(1, len(savings)):
        # print(i)
        if sum1 > total_cost:
            i -= 1
            break
        else:
            sum1 += savings[i]

    sum2 = sum1
    sum1 = sum1 - savings[i]
    i = i - 1

    months = (total_cost - sum1) / savings[i + 1]
    roi = math.ceil((i + months) * 10) / 10.0
    print(sum1, sum2, i, roi)
    savings_irr = []
    for j in range(i + 2):
        savings_irr.append(savings[j])

    print(yearly_bills)
    print(savings)
    print(savings_irr)
    average_savings = 0
    for i in range(1, 11):
        # print(i)
        average_savings += savings[i]

    average_savings = average_savings / 10

    irr = round((numpy.irr(savings_irr) * 100.0), 2)
    print(irr)

    temp = {
        'total_units': total_units,
        'sys_type': sys_type,
        'size_of_rooftop_sys': size_of_rooftop_sys,
        'system_size': system_size,
        'total_cost': total_cost,
        'units_prod_year': units_prod_year,
        'units_used_year': units_used_year,
        'net_units_consumed': net_units_consumed,
        'irr': irr,
        'roi': roi,
        'average_savings': average_savings
    }

    res = {
        'system_size': system_size,
        'sys_type': sys_type,
        'total_cost': total_cost,
        'irr': irr,
        'roi': roi,
        'average_savings': average_savings
    }
    return jsonify(result=res)


@application.route('/contact', methods=['POST'])
def contact():
    try:
        name = str(request.form['name'])
        email = str(request.form['email'])
        phone = str(request.form['phone'])
    except:
        flash('Wrong Information!')
        print("Error")
        return redirect(url_for('index'))
    body = "%s Tried to contact you through Solarify.in. Check details below.\nName: %s\nPhone: %s\nEmail: %s" % (
        name, name, phone, email)
    print(body)
    contact_data = dict()
    for item in request.form:
        contact_data[item] = request.form[item]

    try:
        store_in_dynamo(contact_data)
        publish_to_sns(body, email)
    except ConditionalCheckFailedException as ex:
        print("Mail not sent : " + ex.message)
        return redirect(url_for('index'))
    return render_template('index.html')


def store_in_dynamo(signup_data):
    signup_item = Item(ddb_table, data=signup_data)
    signup_item.save()
    print "Data stored in DDB"


def publish_to_sns(body, email):
    try:
        sns_conn.add_permission(application.config['NEW_CONTACT_TOPIC'], "permission")
        sns_conn.publish(application.config['NEW_CONTACT_TOPIC'], body,
                         "New Contact: %s" % email)
        print("Mail Sent")
    except Exception as ex:
        print("Error publishing subscription message to SNS: %s" % ex.message)
        print(ex)
        print("Mail Not Sent!")


if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=FLASK_DEBUG)
