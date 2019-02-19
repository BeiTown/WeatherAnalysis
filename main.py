import re

stationID = 'CHM00057679'

# 导入数据
with open('data/'+ stationID +'.dly', 'r') as f1:
    dataList = f1.readlines()

print(dataList[2])



# re.split() 对字符串进行分割操作
# res=re.split("\n|s|-| +",dataList[3])
res=re.split("\s+|s|-|s\s+",dataList[2])

print(res)