__author__ = 'Gangeshwar'


def lt2a(cost):  # done
    max1 = 81
    max2 = max1 + 280
    max3 = max2 + 540
    print(cost, max1, max2, max3)
    if cost <= max1:
        units = cost / 2.7
        # print(units)
        return units
    elif ((cost >= max1) & (cost <= max2)):
        units = (cost - max1) / 4.0
        units += 30
        # print(units)
        return units
    elif ((cost >= max2) & (cost <= max3)):
        units = (cost - max2) / 5.4
        units += 100
        # print(units)
        return units
    elif cost >= max3:
        units = (cost - max3) / 6.4
        units += 200
        # print(units)
        return units

    return -1


def lt2b(cost):
    max_ = 1200
    if cost >= max_:
        cost = cost - max_
        units = cost / 7.2
        units += 200
        return units
    else:
        units = cost / 6.0
        return units


def lt3(cost):  # done
    max_ = 347.5
    if cost >= max_:
        cost = cost - max_
        units = cost / 7.95
        units += 50
        return units
    else:
        units = cost / 6.95
        return units


def ht2a(cost):  # done
    max_ = 590000
    if cost >= max_:
        cost = cost - max_
        units = cost / 6.3
        units += 100000
        return units
    else:
        units = cost / 5.9
        return units


def ht2b(cost):
    max_ = 1510000
    if cost >= max_:
        cost = cost - max_
        units = cost / 7.85
        units += 200000
        return units
    else:
        units = cost / 7.55
        return units


def ht4(cost):
    units = cost / 5.5
    return units
