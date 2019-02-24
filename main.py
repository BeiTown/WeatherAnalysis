import math
import re

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MultipleLocator, FuncFormatter
from pandas import DataFrame

ISTEST = False


# hsv转rgb
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
    if hi == 0:
        r, g, b = v, t, p
    elif hi == 1:
        r, g, b = q, v, p
    elif hi == 2:
        r, g, b = p, v, t
    elif hi == 3:
        r, g, b = p, q, v
    elif hi == 4:
        r, g, b = t, p, v
    elif hi == 5:
        r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b


# rgb转16#
def color(value):
    digit = list(map(str, range(10))) + list("ABCDEF")
    if isinstance(value, tuple):
        string = '#'
        for i in value:
            a1 = i // 16
            a2 = i % 16
            string += digit[a1] + digit[a2]
        return string


# 月份格式
def month_formatter(x, pos):
    v = int(x / 31) + 1
    if v > 12:
        return '-'
    else:
        return str(v)


# 计算事件发生连续天数
def continue_count(_df):
    _count = 0
    _index = 0
    _maxCount = 0
    _maxDayIndex = 0
    _maxDesc = ''
    for i in _df['dayIndex']:
        if i - _index == 1:
            _count += 1
            if _count > _maxCount:
                _maxCount = _count
                _maxDayIndex = i - _maxCount + 1
                _maxDesc = _df[_df['dayIndex'] == _maxDayIndex].index
        else:
            _count = 1
        _index = i
    _tdf = DataFrame(
        {'year': [_df['year'][0]], 'maxCount': [_maxCount], 'maxDayIndex': [_maxDayIndex], 'maxDesc': _maxDesc[0]})
    return _tdf


stationID = 'CHM00057679'

df_PRCP = DataFrame(columns=['datetime', 'year', 'month', 'day', 'dayIndex', 'value', 'color'])  # 降雨数据
df_TAVG = DataFrame(columns=['datetime', 'year', 'month', 'day', 'dayIndex', 'value', 'color'])  # 平均气温数据
df_TMAX = DataFrame(columns=['datetime', 'year', 'month', 'day', 'dayIndex', 'value'])  # 最高气温数据
df_TMIN = DataFrame(columns=['datetime', 'year', 'month', 'day', 'dayIndex', 'value'])  # 最低气温数据

tMax = 0
tMaxTime = ''
tMin = 0
tMinTime = ''

pMax = 0
pMaxTime = ''

# 导入数据
with open('data/' + stationID + '.dly', 'r') as f1:
    dataList = f1.readlines()

pdi = 0  # 降雨天数索引
tdi = 0  # 气温天数索引

for _d in dataList:

    _res = re.split("\s+|s|S", _d)  # 使用正则对字符串进行分割
    _date_res = list(filter(lambda x: x != '', _res))  # 清除结果集中的空字符串

    _title = _date_res[0]  # 结果数组中的第一位为索引
    _year = _title.replace(stationID, '')[0:4]  # 获取年
    _month = _title.replace(stationID, '')[4:6]  # 获取月
    _type = _title.replace(stationID, '')[6:]  # 获取数据类型
    print('loding ' + str(_year) + str(_month))

    # 结果集中的后续内容为日数据值
    for i in range(1, len(_date_res)):
        _datetime = str(_year) + '-' + str(_month) + '-' + str(i)

        # 降雨记录
        if _type == 'PRCP':

            if _month == '01' and i == 1:
                pdi = 1
            else:
                pdi += 1

            _value = float(_date_res[i]) / 10  # 降雨量为 value / 10

            # 记录历史降雨量最高日期
            if _value > pMax:
                pMax = _value
                pMaxTime = _year + '/' + _month + '/' + str(i)

            _color = '#FFFFFF'
            if _value != -999.9:
                _color = color(tuple(hsv2rgb(int(_value * 0.75) + 180, 1, 1)))  # 设置数据颜色值

            _df = DataFrame({'datetime': [_datetime], 'year': [_year], 'month': [_month], 'day': [i], 'dayIndex': [pdi],
                             'value': [_value], 'color': [_color]})  #
            df_PRCP = df_PRCP.append(_df, ignore_index=True)  # 将单行数据添加至总DF中

        # 平均气温记录
        elif _type == 'TAVG':

            if _month == '01' and i == 1:
                tdi = 1
            else:
                tdi += 1

            _value = str(_date_res[i]).find('T') == True and -9999 or float(_date_res[i]) / 10  # 温度为 value / 10

            _color = '#FFFFFF'
            if _value != -999.9:
                _color = color(tuple(hsv2rgb(int(-7 * _value) + 240, 1, 1)))  # 设置数据颜色值
            _df = DataFrame({'datetime': [_datetime], 'year': [_year], 'month': [_month], 'day': [i], 'dayIndex': [tdi],
                             'value': [_value], 'color': [_color]})
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
    if len(df_PRCP) and len(df_TAVG) > 100000:
        break

df_PRCP = df_PRCP.set_index('datetime')
df_TAVG = df_TAVG.set_index('datetime')

# 画布基础设置
if ISTEST == True:
    plt.rcParams['figure.figsize'] = (12.0, 8.0)  # 设置figure_size尺寸

    plt.rcParams['image.cmap'] = 'gray'  # 设置 颜色 style

    plt.rcParams['savefig.dpi'] = 300  # 图片像素
    plt.rcParams['figure.dpi'] = 300  # 分辨率
plt.rcParams['image.interpolation'] = 'nearest'  # 设置 interpolation style
# 柱状图

# 年连续降雨最长时间段统计
df_stillRainyD = (df_PRCP[df_PRCP['value'] > 0]).groupby('year').apply(continue_count)  # 提交给自定义统计函数进行计算
df_stillRainyD = df_stillRainyD.set_index('year')

plt.xlabel("Month")
plt.ylabel("Year")
plt.title("Continuous Rainy Count : 1951-2019")
plt.barh(df_stillRainyD.index, df_stillRainyD['maxCount'], left=df_stillRainyD['maxDayIndex'],
         color=list(map(lambda v: color(tuple(hsv2rgb(int(6 * v) + 120, 1, 1))), df_stillRainyD['maxCount'])),
         align='edge') #  绘制横向柱状图

# 设置主刻度
plt.xlim(0, 365)
plt.gca().xaxis.set_major_locator(MultipleLocator(31))
plt.gca().xaxis.set_major_formatter(FuncFormatter(month_formatter))
plt.gca().yaxis.set_major_locator(MultipleLocator(5))
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, y: int(x + 1950)))
# 设置次刻度
plt.gca().xaxis.set_minor_locator(MultipleLocator(1))
plt.gca().yaxis.set_minor_locator(MultipleLocator(1))

# 打开网格
plt.gca().xaxis.grid(True, which='major')  # x坐标轴的网格使用主刻度
plt.gca().yaxis.grid(True, which='minor')  # y坐标轴的网格使用次刻度
if ISTEST == False:
    plt.savefig("./data/Continuous Rainy Count.png")  # 保存图片
plt.show()

# 年连续高温最长时间段
df_stillHotD = (df_TAVG[df_TAVG['value'] > 30]).groupby('year').apply(continue_count)
df_stillHotD = df_stillHotD.set_index('year')

plt.xlabel("Month")
plt.ylabel("Year")
plt.title("Continuous Hot Count : 1951-2019")
plt.barh(df_stillHotD.index, df_stillHotD['maxCount'], left=df_stillHotD['maxDayIndex'],
         color=list(map(lambda v: color(tuple(hsv2rgb(int(-1.2 * v) + 60, 1, 1))), df_stillHotD['maxCount'])),
         align='edge')
# plt.barh(df_stillRainyD.index, df_stillRainyD['maxDayIndex'] , color='#FFFFFF')
plt.xlim(0, 365)
plt.gca().xaxis.set_major_locator(MultipleLocator(31))
plt.gca().xaxis.set_major_formatter(FuncFormatter(month_formatter))
plt.gca().yaxis.set_major_locator(MultipleLocator(5))
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, y: int(x + 1950)))
# 修改次刻度
plt.gca().xaxis.set_minor_locator(MultipleLocator(1))
plt.gca().yaxis.set_minor_locator(MultipleLocator(1))

# 打开网格
plt.gca().xaxis.grid(True, which='major')  # x坐标轴的网格使用主刻度
plt.gca().yaxis.grid(True, which='minor')  # y坐标轴的网格使用次刻度
if ISTEST == False:
    plt.savefig("./data/Continuous Hot Count.png")  # 保存图片
plt.show()

# 年连续低温最长时间段
df_stillColdD = (df_TAVG[df_TAVG['value'] < 10]).groupby('year').apply(continue_count)
df_stillColdD = df_stillColdD.set_index('year')

plt.xlabel("Month")
plt.ylabel("Year")
plt.title("Continuous Cold Count : 1951-2019")
plt.barh(df_stillColdD.index, df_stillColdD['maxCount'], left=df_stillColdD['maxDayIndex'],
         color=list(map(lambda v: color(tuple(hsv2rgb(int(1 * v) + 180, 1, 1))), df_stillColdD['maxCount'])),
         align='edge')

# plt.xticks(range(1,13,1),range(1,13,1))
plt.xlim(0, 365)
plt.gca().xaxis.set_major_locator(MultipleLocator(31))
plt.gca().xaxis.set_major_formatter(FuncFormatter(month_formatter))
plt.gca().yaxis.set_major_locator(MultipleLocator(5))
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, y: int(x + 1950)))
# 修改次刻度
plt.gca().xaxis.set_minor_locator(MultipleLocator(1))
plt.gca().yaxis.set_minor_locator(MultipleLocator(1))

# 打开网格
plt.gca().xaxis.grid(True, which='major')  # x坐标轴的网格使用主刻度
plt.gca().yaxis.grid(True, which='minor')  # y坐标轴的网格使用次刻度
if ISTEST == False:
    plt.savefig("./data/Continuous Cold Count.png")  # 保存图片
plt.show()

# 年降雨天数统计
se_rainyD = (df_PRCP[df_PRCP['value'] > 0]).groupby('year')['value'].count()
df_rainyD = se_rainyD.to_frame('rainyDays')
# 年低温天数统计
se_LowT = (df_TAVG[(df_TAVG['value'] < 10) & (df_TAVG['value'] > -100)]).groupby('year')['value'].count()
df_LowT = se_LowT.to_frame('coldDays')
# 年高温天数统计
se_HighT = (df_TAVG[df_TAVG['value'] > 30]).groupby('year')['value'].count()
df_HighT = se_HighT.to_frame('hotDays')
# 汇总
df_YearCount = pd.concat([df_rainyD, df_LowT, df_HighT], axis=1, sort=False)

plt.plot(df_YearCount.index, df_YearCount['coldDays'], label='coldDays')
plt.plot(df_YearCount.index, df_YearCount['hotDays'], label='hotDays')
plt.plot(df_YearCount.index, df_YearCount['rainyDays'], label='rainyDays')
plt.gca().xaxis.set_major_locator(MultipleLocator(5))
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, y: int(x + 1950)))

plt.legend()  # 显示图例Tips
plt.gca().grid()  # 打开网格
plt.xlabel("Year")
plt.ylabel("Count Day")
plt.title("Historical Weather Count : 1951-2019")
if ISTEST == False:
    plt.savefig("./data/Historical Weather Count.png")  # 保存图片
plt.show()

# 历史同日降雨次数统计
se_HisRainyD = (df_PRCP[df_PRCP['value'] > 0]).groupby('dayIndex')['value'].count()

plt.xlabel("Month")
plt.ylabel("Probability %")
plt.title("Historical Same Day Rainy Count : 1951-2019")
plt.bar(se_HisRainyD.index, se_HisRainyD / len(df_PRCP.groupby('year')) * 100,
        color=list(map(lambda v: color(tuple(hsv2rgb(int(2.4 * v) + 120, 1, 1))), se_HisRainyD.values)))

plt.gca().xaxis.set_major_locator(MultipleLocator(31))
plt.gca().xaxis.set_major_formatter(FuncFormatter(month_formatter))
plt.gca().grid()  # 打开网格
plt.xlim(0, 365)
plt.ylim(0, 100)
plt.gca().yaxis.set_major_locator(plt.MultipleLocator(10))
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, y: str(y * 10 - 10) + '%'))
if ISTEST == False:
    plt.savefig("./data/Historical Same Day Rainy Count.png")  # 保存图片
plt.show()

# 历史同日冻雨次数统计
df_HisRainy = df_PRCP[df_PRCP['value'] > 0]
df_HisCold = pd.merge(df_TAVG[df_TAVG['value'] < 10], df_TAVG[df_TAVG['value'] > -100], how='inner',
                      on=['datetime', 'year', 'month', 'day', 'dayIndex', 'value', 'color'])
df_HisRainyCold = pd.merge(df_HisRainy, df_HisCold, left_on='datetime', right_index=True, how='inner')
se_HisRainyColdD = df_HisRainyCold.groupby('dayIndex_x')['value_x'].count()

plt.xlabel("Month")
plt.ylabel("Probability %")
plt.title("Historical Same Day Rainy and Cold Count : 1951-2019")
plt.bar(se_HisRainyColdD.index, se_HisRainyColdD / len(df_PRCP.groupby('year')) * 100,
        color=list(map(lambda v: color(tuple(hsv2rgb(int(2.4 * v) + 120, 1, 1))), se_HisRainyColdD.values)))
plt.gca().grid()  # 打开网格
plt.gca().xaxis.set_major_locator(MultipleLocator(31))
plt.gca().xaxis.set_major_formatter(FuncFormatter(month_formatter))
plt.xlim(0, 365)
plt.ylim(0, 100)
plt.gca().yaxis.set_major_locator(plt.MultipleLocator(10))
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, y: str(y * 10 - 10) + '%'))
if ISTEST == False:
    plt.savefig("./data/Historical Same Day Rainy and Cold Count.png")  # 保存图片
plt.show()

# 365天的散点图

# TAVG
plt.gca().xaxis.set_major_locator(MultipleLocator(31))
plt.gca().xaxis.set_major_formatter(FuncFormatter(month_formatter))
plt.gca().grid()  # 网格
# plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
plt.scatter(df_TAVG['dayIndex'], df_TAVG['value'], s=80, c=df_TAVG['color'], marker='.', alpha=0.05)
plt.xlim(0, 365)
plt.ylim(-30, 50)
plt.gca().yaxis.set_major_locator(plt.MultipleLocator(10))
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, y: str(x) + 'C°'))

plt.title('TAVG : 1951-2019')
plt.xlabel("Month")
plt.ylabel("Temperature C°")

if ISTEST == False:
    plt.savefig("./data/TAVG.png") # 保存图片

plt.show()

# PRCP散点图
plt.gca().xaxis.set_major_locator(MultipleLocator(31))  # 设置x轴的刻度间隔
plt.gca().xaxis.set_major_formatter(FuncFormatter(month_formatter))  # 设置x轴的显示数值
plt.gca().yaxis.set_major_locator(plt.MultipleLocator(10))  # 设置y轴的刻度间隔
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, y: str(y * 10) + 'mm'))  # 设置y轴的显示数值
plt.gca().grid()  # 开启网格

plt.scatter(df_PRCP['dayIndex'], df_PRCP['value'], s=40, c=df_PRCP['color'], marker='.', alpha=0.5)  # 散点图绘制
plt.xlim(0, 365)  # 设置x轴的坐标范围
plt.ylim(1, 250)  # 设置y轴的坐标范围

plt.title('PRCP : 1951-2019')
plt.xlabel("Month")
plt.ylabel("Precipitation mm")

if ISTEST == False:
    plt.savefig("./data/PRCP.png")  # 保存图片

plt.show()

print(df_stillRainyD[df_stillRainyD['maxCount'] == df_stillRainyD['maxCount'].max()])
print(df_stillHotD[df_stillHotD['maxCount'] == df_stillHotD['maxCount'].max()])
print(df_stillColdD[df_stillColdD['maxCount'] == df_stillColdD['maxCount'].max()])

print('TMAX = ' + str(tMax) + 'C°:' + tMaxTime)
print('TMIN = ' + str(tMin) + 'C°:' + tMinTime)
print('PMAX = ' + str(pMax) + 'mm :' + pMaxTime)

df_stillRainyD
# PCRP补充雨季显示 pass
'''
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
'''

# 12 x 31 的3D散点图

# 保存df

# color

# plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
