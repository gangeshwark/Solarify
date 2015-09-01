import math

from flask import Flask, render_template, jsonify
import numpy

from utils import lt2a, lt3, ht2b, ht2a, ht4

application = Flask(__name__)


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


@application.route('/calculate', methods=['POST'])
def calculate():
    customer_type = 'R'  # residentaial-> R, commercial-> C, industrial -> I
    connection_type = 'LT'  # LT, HT
    rooftop_area = 200  # sqft
    # rooftop_type = 0  # 450
    # monthly_bill = 623000  # Rs.
    monthly_bill = 1000  # Rs.
    sanction_load = 3  # kVA
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
    for i in range(1, len(savings) + 1):
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
    return jsonify(response=res)


@application.route('/calculator')
def calculator():
    return render_template('calculator.html')


@application.route('/results')
def results():
    return render_template('results.html')


@application.route('/contact', methods=['POST'])
def contact():
    return render_template('faq.html')


if __name__ == '__main__':
    application.run(debug=True)
