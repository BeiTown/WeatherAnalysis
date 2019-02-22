import re
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.ticker import MultipleLocator,FuncFormatter
import math

ISTEST = True

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
df_PRCP = DataFrame(columns=['datetime', 'year', 'month', 'day', 'dayIndex', 'value', 'color'])
df_TAVG = DataFrame(columns=['datetime', 'year', 'month', 'day', 'dayIndex', 'value', 'color'])
df_TMAX = DataFrame(columns=['datetime', 'year', 'month', 'day', 'dayIndex', 'value'])
df_TMIN = DataFrame(columns=['datetime', 'year', 'month', 'day', 'dayIndex', 'value'])

tMax = 0
tMaxTime = ''
tMin = 0
tMinTime = ''

pMax = 0
pMaxTime = ''

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

        # 降雨记录
        if _type == 'PRCP':

            if _month == '01' and i == 1:
                pdi = 1
            else:
                pdi += 1

            _value = float(_date_res[i])  / 10

            if _value > pMax:
                pMax = _value
                pMaxTime = _year + '/' + _month + '/' + str(i)

            _color = '#FFFFFF'
            if _value != -999.9:
                _color = color(tuple(hsv2rgb(int(_value * 0.75) + 180, 1, 1)))

            _df = DataFrame({'datetime':[_datetime], 'year':[_year],'month':[_month],'day':[i], 'dayIndex':[pdi],'value':[_value],'color':[_color]})
            df_PRCP = df_PRCP.append(_df, ignore_index=True)

        # 平均气温记录
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

        # 最高气温记录
        elif _type == 'TMAX':

            _value = str(_date_res[i]).find('T') == True and 0 or float(_date_res[i]) / 10
            if _value > tMax and _value < 100:
                tMax = _value
                tMaxTime = _year + '/' + _month + '/' + str(i)

        # 最低气温记录
        elif _type == 'TMIN':

            _value = str(_date_res[i]).find('T') == True and 0 or float(_date_res[i]) / 10
            if _value < tMin and _value > -100:
                tMin = _value
                tMinTime = _year + '/' + _month + '/' + str(i)

    # 调试使用，避免数据加载时间过长
    if len(df_PRCP) and len(df_TAVG) > 1000:
        break

# 柱状图

# 年连续晴天最长时间段

# 年连续降雨最长时间段

# 年连续高温最长时间段

# 年连续低温最长时间段



# 年降雨天数统计
se_rainyD = (df_PRCP[df_PRCP['value'] > 0]).groupby('year')['value'].count()
# 年高温天数统计
se_LowT = (df_TAVG[df_TAVG['value'] < 10]).groupby('year')['value'].count()
# 年低温天数统计
se_HighT = (df_TAVG[df_TAVG['value'] > 30]).groupby('year')['value'].count()




df_YearCount = DataFrame()
df_YearCount['year'] = se_rainyD.index
df_YearCount = df_YearCount.set_index('year')
df_YearCount['rainyDays'] = se_rainyD.values
df_YearCount['coldDays'] = se_LowT.values
df_YearCount['hotDays'] = se_HighT.values

print(df_YearCount['year'])


df_YearCount.plot(kind='line')
plt.plot(df_YearCount.index, df_YearCount['rainyDays'], color='silver', label='rainyDays')
plt.plot(df_YearCount.index, df_YearCount['coldDays'], color='dodgerblue', label='coldDays')
plt.plot(df_YearCount.index, df_YearCount['hotDays'], color='orange', label='hotDays')



plt.gca().grid()# 网格
plt.xlabel("Year")
plt.title("Historical Weather Count")
plt.show()

#print(df_PRCP)
#df_TAVG.reset_index(drop=True)
#print(df_TAVG)
#print(df_PRCP)
df_PRCP = df_PRCP.set_index('datetime')
df_TAVG = df_TAVG.set_index('datetime')
#print(t)
# 365天的散点图


# 画布基础设置
if ISTEST == False:
    plt.rcParams['figure.figsize'] = (12.0, 8.0) # 设置figure_size尺寸
    plt.rcParams['image.interpolation'] = 'nearest' # 设置 interpolation style
    plt.rcParams['image.cmap'] = 'gray' # 设置 颜色 style

    plt.rcParams['savefig.dpi'] = 300 #图片像素
    plt.rcParams['figure.dpi'] = 300 #分辨率

# TAVG
plt.gca().xaxis.set_major_locator(MultipleLocator(31))
plt.gca().xaxis.set_major_formatter(FuncFormatter(month_formatter))

plt.gca().grid()# 网格
# plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
plt.scatter(df_TAVG['dayIndex'], df_TAVG['value'], s=80, c=df_TAVG['color'], marker='.', alpha=0.05)


plt.ylim(-30, 50)

plt.title('TAVG : 1951-2019')
plt.xlabel("Month")
plt.ylabel("Temperature C°")


if ISTEST == False:
    plt.savefig("./data/TAVG.png",dpi=300)

plt.show()
print('TMAX = '+ str(tMax) + 'C :' + tMaxTime)
print('TMIN = '+ str(tMin) + 'C :' + tMinTime)



# PRCP
plt.gca().xaxis.set_major_locator(MultipleLocator(31))
plt.gca().xaxis.set_major_formatter(FuncFormatter(month_formatter))
plt.gca().yaxis.set_major_locator(plt.MultipleLocator(10))
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, y: y * 10))

plt.gca().grid()# 网格
#plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
plt.scatter(df_PRCP['dayIndex'], df_PRCP['value'], s=40, c=df_PRCP['color'], marker='.', alpha=0.5)

plt.ylim(1, 250)

plt.title('PRCP : 1951-2019')
plt.xlabel("Month")
plt.ylabel("Precipitation mm")

if ISTEST == False:
    plt.savefig("./data/PRCP.png",dpi=300)

plt.show()

print('PMAX = '+ str(pMax) + 'mm :' + pMaxTime)

# PCRP补充雨季显示

plt.gca().xaxis.set_major_locator(MultipleLocator(31))
plt.gca().xaxis.set_major_formatter(FuncFormatter(month_formatter))
plt.gca().yaxis.set_major_locator(plt.MultipleLocator(5))
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, y: y * 5))

plt.gca().grid()# 网格
#plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
plt.scatter(df_PRCP['dayIndex'], df_PRCP['value'], s=40, c='#00CCFF', marker='.', alpha=0.1)

plt.ylim(1, 50)

plt.title('Rainy Season Show : 1951-2019')
plt.xlabel("Month")
plt.ylabel("Precipitation mm")

if ISTEST == False:
    plt.savefig("./data/PRCP_RAINDAY.png",dpi=300)

plt.show()


# 12 x 31 的3D散点图

# https://blog.csdn.net/sinat_35512245/article/details/79791190