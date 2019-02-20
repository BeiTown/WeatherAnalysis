import re
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import matplotlib.dates as mdates





stationID = 'CHM00057679'
df_PRCP = DataFrame(columns=['datetime', 'year', 'month', 'day', 'dayIndex', 'value'])
df_TAVG = DataFrame(columns=['datetime', 'year', 'month', 'day', 'dayIndex', 'value'])


# 导入数据
with open('data/'+ stationID +'.dly', 'r') as f1:
    dataList = f1.readlines()
pdi = 0
tdi = 0
for _d in dataList:

    _res = re.split("\s+|s|s\s+", _d)
    _date_res = list(filter(lambda x:x != '' and x != '-9999', _res))

    _title = _date_res[0]
    _year = int(_title.replace(stationID,'')[0:4])
    _month = int(_title.replace(stationID,'')[4:6])
    _type = _title.replace(stationID,'')[6:]
    print('loding ' + str(_year) + str(_month))

    for i in range(1, len(_date_res)):
        _datetime = str(_year)+'-' + str(_month) + '-'+str(i)



        if _type == 'PRCP':

            if _month == 1 and i == 1:
                pdi = 1
            else:
                pdi += 1

            _value = str(_date_res[i]).find('T') == True and -9999 or _date_res[i]
            _df = DataFrame({'datetime':[_datetime], 'year':[_year],'month':[_month],'day':[i], 'dayIndex':[pdi],'value':[_value]})
            df_PRCP = df_PRCP.append(_df, ignore_index=True)


        elif _type == 'TAVG':

            if _month == 1 and i == 1:
                tdi = 1
            else:
                tdi += 1

            _value = str(_date_res[i]).find('T') == True and -9999 or float(_date_res[i])  / 10
            _df = DataFrame({'datetime':[_datetime], 'year':[_year],'month':[_month],'day':[i], 'dayIndex':[tdi],'value':[_value]})
            df_TAVG = df_TAVG.append(_df, ignore_index=True)


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


plt.setp(plt.gca().get_xticklabels(), rotation=30)

#plt.gca().grid # 网格
plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
plt.scatter(df_TAVG['dayIndex'], df_TAVG['value'], s=5, c="#ff1212", marker='.')

plt.axis()
plt.ylim(-30, 50)

plt.title('TAVG')
plt.xlabel("Month")
plt.ylabel("Temperature C°")
plt.show()


# 12 x 31 的3D散点图