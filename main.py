import re
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.ticker import MultipleLocator,FuncFormatter
import math


def hsv2rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b

def color(value):
    digit = list(map(str, range(10))) + list("ABCDEF")
    if isinstance(value, tuple):
        string = '#'
        for i in value:
            a1 = i // 16
            a2 = i % 16
            string += digit[a1] + digit[a2]
        return string

def month_formatter(x,pos):
    v = int(x / 31) + 1
    if v > 12:
        return '-'
    else:
        return v

stationID = 'CHM00057679'
df_PRCP = DataFrame(columns=['datetime', 'year', 'month', 'day', 'dayIndex', 'value'])
df_TAVG = DataFrame(columns=['datetime', 'year', 'month', 'day', 'dayIndex', 'value', 'color'])
df_TMAX = DataFrame(columns=['datetime', 'year', 'month', 'day', 'dayIndex', 'value'])
df_TMIN = DataFrame(columns=['datetime', 'year', 'month', 'day', 'dayIndex', 'value'])

tMax = 0
tMaxTime = ''
tMin = 0
tMinTime = ''


# 导入数据
with open('data/'+ stationID +'.dly', 'r') as f1:
    dataList = f1.readlines()
pdi = 0
tdi = 0
for _d in dataList:

    _res = re.split("\s+|s|S", _d)
    _date_res = list(filter(lambda x:x != '', _res))

    _title = _date_res[0]
    _year = _title.replace(stationID,'')[0:4]
    _month = _title.replace(stationID,'')[4:6]
    _type = _title.replace(stationID,'')[6:]
    print('loding ' + str(_year) + str(_month))

    for i in range(1, len(_date_res)):
        _datetime = str(_year)+'-' + str(_month) + '-'+str(i)



        if _type == 'PRCP':

            if _month == '01' and i == 1:
                pdi = 1
            else:
                pdi += 1

            _value = str(_date_res[i]).find('T') == True and -9999 or _date_res[i]
            _df = DataFrame({'datetime':[_datetime], 'year':[_year],'month':[_month],'day':[i], 'dayIndex':[pdi],'value':[_value]})
            df_PRCP = df_PRCP.append(_df, ignore_index=True)


        elif _type == 'TAVG':

            if _month == '01' and i == 1:
                tdi = 1
            else:
                tdi += 1

            _value = str(_date_res[i]).find('T') == True and -9999 or float(_date_res[i])  / 10

            _color = '#FFFFFF'
            if _value != -999.9:

                _color = color(tuple(hsv2rgb(int(-7 * _value) + 240, 1, 1)))



            _df = DataFrame({'datetime':[_datetime], 'year':[_year],'month':[_month],'day':[i], 'dayIndex':[tdi],'value':[_value],'color':[_color]})
            df_TAVG = df_TAVG.append(_df, ignore_index=True)

        elif _type == 'TMAX':

            _value = str(_date_res[i]).find('T') == True and 0 or float(_date_res[i]) / 10
            if _value > tMax and _value < 100:
                tMax = _value
                tMaxTime = _year + '/' + _month + '/' + str(i)

        elif _type == 'TMIN':

            _value = str(_date_res[i]).find('T') == True and 0 or float(_date_res[i]) / 10
            if _value < tMin and _value > -100:
                tMin = _value
                tMinTime = _year + '/' + _month + '/' + str(i)


    # 调试使用，避免数据加载时间过长
    if len(df_PRCP) and len(df_TAVG) > 100000:
        break


#print(df_PRCP)
df_TAVG.reset_index(drop=True)
print(df_TAVG)

# 365天的散点图

#plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  #設置x軸主刻度顯示格式（日期）
#plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))  #設置x軸主刻度間距
#plt.gca().xaxis.set_minor_locator(mdates.DayLocator())

# T = np.arctan2(df_TAVG['dayIndex'], df_TAVG['value']) # for color value


plt.gca().xaxis.set_major_locator(MultipleLocator(31))
plt.gca().xaxis.set_major_formatter(FuncFormatter(month_formatter))

plt.gca().grid()# 网格
# plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
plt.scatter(df_TAVG['dayIndex'], df_TAVG['value'], s=80, c=df_TAVG['color'], marker='.', alpha=0.05)

plt.axis()
plt.ylim(-30, 50)

plt.title('TAVG')
plt.xlabel("Month")
plt.ylabel("Temperature C°")
plt.show()

print('TMAX = '+ str(tMax) + 'C :' + tMaxTime)
print('TMIN = '+ str(tMin) + 'C :' + tMinTime)

# 12 x 31 的3D散点图