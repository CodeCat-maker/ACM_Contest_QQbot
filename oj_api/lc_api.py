import requests
import re
import json
import pprint
import os
import time
from lxml import etree
from web_operation.operation import *


async def get_contest():
    url_data = "https://leetcode-cn.com/graphql"

    payload = {
        "operationName": "null",
        "query": "{\n  contestUpcomingContests {\n    containsPremium\n    title\n    cardImg\n    titleSlug\n    description\n    startTime\n    duration\n    originStartTime\n    isVirtual\n    isLightCardFontColor\n    company {\n      watermark\n      __typename\n    }\n    __typename\n  }\n}\n",
        "variables": {}
    }

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip,deflate,br",
        "accept-language": "zh,zh-TW;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6",
        "cache-control": "no-cache",
        # "content-length": "329",
        "content-type": "application/json",
        # "cookie": response.cookies,
        "origin": "https://leetcode-cn.com",
        "pragma": "no-cache",
        "referer": "https://leetcode-cn.com/contest/",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        # 'x-csrftoken': response.cookies
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url=url_data, data=json.dumps(payload), headers=headers)

    url_text = response.content.decode()
    # print(url_text)
    json_data = json.loads(url_text)

    # print(json_data)

    res = []

    try:
        contest_info = json_data['data']['contestUpcomingContests']

        # print(type(contest_info))

        for contest in contest_info:
            html = etree.HTML(contest['description'])
            company = html.xpath("/html/body/div/div/div/p[1]/text()")[0]

            start_time = contest['startTime']
            year = time.localtime(start_time).tm_year
            mon = time.localtime(start_time).tm_mon
            day = time.localtime(start_time).tm_mday
            hour = time.localtime(start_time).tm_hour
            minute = time.localtime(start_time).tm_min
            second = time.localtime(start_time).tm_sec

            info = "下一场力扣比赛为：\n" \
                   "比赛名称：{}\n" \
                   "赞助公司：{}\n" \
                   "开始时间：{}\n" \
                   "持续时间：{}\n" \
                   "比赛地址：{}".format(
                contest['title'],
                company,
                "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(year, mon, day, hour, minute, second),
                "{}小时{:02d}分钟".format(contest['duration'] // 3600, contest['duration'] % 3600 // 60),
                "https://leetcode-cn.com/contest/" + contest['titleSlug'])

            res.append([info, start_time])

        # print(res)
        res.sort(key=lambda x: x[1], reverse=False)
        return res, res[0][1]
    except:
        return -1


# TODO 获取力扣分数
def get_usr_rank(name):
    pass


if __name__ == '__main__':
    pprint.pprint(asyncio.run(get_contest()))
    # pprint.pprint(get_html("https://leetcode-cn.com/contest/"))
