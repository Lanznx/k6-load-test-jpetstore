import re
import csv

# 從文本中提取數據
with open('./output/data.txt', 'r') as f:
    data = f.read()

results = re.findall(r'http_req_duration.+', data)
match_success = re.findall(r"✓ (\d+)", data)
match_fail = re.findall(r"✗ (\d+)", data) 
# 將數據寫入 CSV 文件
with open('./output/results.csv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter=',', lineterminator='')
    checker = csv.writer(f)
    writer.writerow(['error', 'avg', 'min', 'med', 'max', 'p(90)', 'p(95)\n'])


    rowCount = 0
    checkCount = 0
    for m in range(len(match_success)):
        if(int(match_fail[m]) == 0):
            writer.writerow([match_fail[m], ","])
        else:
            writer.writerow([str(int(match_fail[m]) / (int(match_success[m])+int(match_fail[m]) )), ","])


        for row in results:
            if(rowCount < checkCount):
                rowCount += 1
                continue
            values = re.findall(r'\d+\.\d+', row)
            writer.writerow(values)
            writer.writerow("\n")

            break
        rowCount = 0
        checkCount += 1