for i in range(10000):
    t = (i * 3 + 3) * 3
    tSTR = str(t)
    sum = 0
    for j in tSTR:
        sum += int(j)
    if sum != 9:
        print('Загадано: '+ str(i)+ ', Результат вычислений:'+str(t)+ ', Сумма результата: '+ str(sum))
