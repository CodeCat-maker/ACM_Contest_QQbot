from web_operation.operation import *

import time
import datetime
import asyncio
import pprint
from lxml import etree
import requests
from dateutil.relativedelta import relativedelta

async def get_nc_rating(uname):
    url = "https://ac.nowcoder.com/acm/contest/rating-index?searchUserName=" + uname
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
    }
    resp = requests.get(url=url, headers=headers)
    text = resp.text
    zm = text.encode(resp.encoding).decode('utf-8')
    xx = etree.fromstring(zm, parser=etree.HTMLParser())
    rating = xx.xpath('/html/body/div/div[2]/div/div/div[2]/table/tbody/tr/td[5]/span/text()')
    return "“{}”当前牛客rating为：{}".format(uname, rating[0])

async def get_contest():
    async def find():
        now = datetime.datetime.now()

        try:
            for _ in range(12):
                now = now + relativedelta(months=1)
                date = str(now.year) + '-' + str(now.month)
                url = "https://ac.nowcoder.com/acm/calendar/contest?token=&month=" + date + "&_=" + str(int(time.time()) * 1000)

                json_data = await get_json(url)

                contest_data = json_data['data']

                for contest in contest_data:
                    if contest['ojName'] == 'NowCoder' \
                            and contest['startTime'] >= int(time.time()) * 1000 \
                            and ("专题" not in contest['contestName']):
                        lately_contest = contest
                        if lately_contest.__contains__('endTime') and lately_contest.__contains__('startTime'):
                            durationSeconds = (int(lately_contest['endTime']) - int(lately_contest['startTime'])) // 1000
                            return lately_contest, durationSeconds  # 只获取马上要举行的牛客比赛
        except:
            return -1

    lately_contest, durationSeconds = await find()

    if lately_contest == -1:
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
