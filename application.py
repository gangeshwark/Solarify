from flask import Flask, render_template, jsonify
import math
import numpy
from utils import lt2b, lt2a, lt3, ht4, ht2b, ht2a

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


# , methods=['POST']
@application.route('/calculate')
def calculate():
    customer_type = 'R'  # residentaial-> R, commercial-> C, industrial -> I
    connection_type = 'LT'  # LT, HT
    rooftop_area = 2000  # sqft
    # rooftop_type = 0  # 450
    # monthly_bill = 623000  # Rs.
    monthly_bill = 10000  # Rs.
    sanction_load = 3  # kVA
    if (customer_type == 'R') & (connection_type == 'LT'):  # Residential and LT
        result = lt2a(monthly_bill)
        sys_type = 'grid-tie'

    elif (customer_type == 'C') & (connection_type == 'LT'):  # Commercial & LT
        result = lt3(monthly_bill)
        sys_type = 'grid-tie'

    elif (customer_type == 'I') & (connection_type == 'LT'):  # Industrial & LT
        result = lt3(monthly_bill)
        sys_type = 'grid-interactive'

    elif (customer_type == 'R') & (connection_type == 'HT'):  # Residential and HT
        result = ht4(monthly_bill)
        sys_type = 'grid-tie'

    elif (customer_type == 'C') & (connection_type == 'HT'):  # Commercial & HT
        result = ht2b(monthly_bill)
        sys_type = 'grid-interactive'

    elif (customer_type == 'I') & (connection_type == 'HT'):  # Industrial & HT
        result = ht2a(monthly_bill)
        sys_type = 'grid-interactive'

    elif (customer_type == 'R') & (connection_type == 0):  # Residential and -
        result = lt2a(monthly_bill)
        sys_type = 'grid-tie'

    elif (customer_type == 'C') & (connection_type == 0):  # Commercial & -
        result = lt3(monthly_bill)
        sys_type = 'grid-tie'

    elif (customer_type == 'I') & (connection_type == 0):  # Industrial & -
        result = ht2a(monthly_bill)
        sys_type = 'grid-interactive'

    else:
        return jsonify(response="Wrong Info!")

    size_of_rooftop_sys = ((result / 5) / 30)

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

    units_used_year = result * 12  # from grid

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
    # sum1 = sum1 - savings[i]
    i = i - 1

    print(sum1, i)
    savings_irr = []
    for j in range(i + 2):
        savings_irr.append(savings[j])

    print(yearly_bills)
    print(savings)
    print(savings_irr)
    # savings.pop(1)
    # savings.insert(1, 0)
    # print(savings)
    irr = round((numpy.irr(savings_irr) * 100.0), 2)
    print(irr)

    res = {
        'result': result,
        'sys_type': sys_type,
        'size_of_rooftop_sys': size_of_rooftop_sys,
        'system_size': system_size,
        'total_cost': total_cost,
        'units_prod_year': units_prod_year,
        'units_used_year': units_used_year,
        'net_units_consumed': net_units_consumed,
        'irr': irr
    }
    # response = json.dump({'result': result, 'sys_type': sys_type, 'size_of_rooftop_sys': size_of_rooftop_sys, 'system_size': system_size, 'total_cost': total_cost}, 200)
    return jsonify(response=res)
    # return render_template('result.html', result=result, sys_type=sys_type, size_of_rooftop_sys=size_of_rooftop_sys,
    # system_size=system_size, total_cost=total_cost)


@application.route('/calculator')
def calculator():
    return render_template('calc.html')


if __name__ == '__main__':
    application.run(debug=True)
