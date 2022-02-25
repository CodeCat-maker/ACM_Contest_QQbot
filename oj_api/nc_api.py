from web_operation.operation import *

import time
import datetime
import asyncio
import pprint
from dateutil.relativedelta import relativedelta


async def get_contest():
    now = datetime.datetime.now()

    date = str(now.year) + '-' + str(now.month)
    url = "https://ac.nowcoder.com/acm/calendar/contest?token=&month=" + date + "&_=" + str(int(time.time()) * 1000)

    json_data = await get_json(url)

    if json_data['code'] != 0:
        return -1

    contest_data = json_data['data']

    next = now + relativedelta(months=1)
    next_date = str(next.year) + '-' + str(next.month)
    next_url = "https://ac.nowcoder.com/acm/calendar/contest?token=&month=" + next_date + "&_=" + str(
        int(time.time()) * 1000)
    json_next_data = await get_json(next_url)
    
    if json_next_data['code'] == 0:
        contest_data += json_next_data['data']

    for contest in contest_data:
        if contest['ojName'] == 'NowCoder' \
                and contest['startTime'] >= int(time.time()) * 1000 \
                and ("专题" not in contest['contestName']):
            lately_contest = contest
            if lately_contest.__contains__('endTime') and lately_contest.__contains__('startTime'):
                durationSeconds = (int(lately_contest['endTime']) - int(lately_contest['startTime'])) // 1000
                break  # 只获取马上要举行的牛客比赛
    else:
        return -1

    res = "下一场牛客比赛为：\n" \
          "比赛名称：{}\n" \
          "开始时间：{}\n" \
          "持续时间：{}\n" \
          "比赛地址：{}".format(
        lately_contest['contestName'],
        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(lately_contest['startTime']) // 1000)),
        "{}小时{:02d}分钟".format(durationSeconds // 3600, durationSeconds % 3600 // 60),
        lately_contest['link']
    )

    return res, int(lately_contest['startTime'] // 1000)



if __name__ == '__main__':
    pprint.pprint(asyncio.run(get_contest()))
