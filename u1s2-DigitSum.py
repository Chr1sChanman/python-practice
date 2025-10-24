def sum_of_digits(num):
    num = str(num)
    res = 0
    for i in num:
        res += int(i)
    return print(res)

num = 423
sum_of_digits(num)

num = 4
sum_of_digits(num)