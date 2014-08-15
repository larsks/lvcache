def human_format(num):
    if num < 1000:
        return '%d' % num
    elif num < 1000**2:
        return '%dK' % int(num/1000)
    elif num < 1000**3:
        return '%dM' % int(num/1000**2)
    elif num < 1000**4:
        return '%dG' % int(num/1000**3)
    elif num < 1000**5:
        return '%dT' % int(num/1000**4)
    elif num < 1000**6:
        return '%dP' % int(num/1000**5)
    else:
        return '%dE' % int(num/1000**6)
