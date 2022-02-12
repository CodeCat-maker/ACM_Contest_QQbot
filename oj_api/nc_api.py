from web_operation.operation import *

import time
import datetime
import asyncio
import pprint


async def get_contest():
    date = str(datetime.datetime.now().year) + '-' + str(datetime.datetime.now().month)
    url = "https://ac.nowcoder.com/acm/calendar/contest?token=&month=" + date + "&_=" + str(int(time.time()) * 1000)

    json_data = await get_json(url)

    if json_data['code'] != 0:
        return -1

    contest_data = json_data['data']

    lately_contest = dict()

    try_time = 0

    while try_time < 5:  # 重试五次，每次间隔20分钟
        for contest in contest_data:
            if contest['ojName'] == 'NowCoder' \
                    and contest['startTime'] >= int(time.time()) * 1000 \
                    and ("专题" not in contest['contestName']):
                lately_contest = contest
                break  # 只获取马上要举行的牛客比赛

        if lately_contest.__contains__('endTime') and lately_contest.__contains__('startTime'):
            durationSeconds = (int(lately_contest['endTime']) - int(lately_contest['startTime'])) // 1000
        else:
            try_time += 1

            print("获取牛客失败，正在重试")
            await asyncio.sleep(20 * 60)  # 休息20分钟再试
            # pprint.pprint(lately_contest)
            continue

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
