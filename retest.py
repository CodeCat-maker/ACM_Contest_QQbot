import re

s = "查询CF比赛"

m = re.match(r'查询CF比赛', s.strip())

print(m)