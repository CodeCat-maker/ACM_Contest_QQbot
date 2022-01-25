import httpx
import requests
import re
import json
import pprint
import time
import asyncio
from web_operation.operation import *


async def get_usr_rating(name):
    def pd_color(ratting):
        if ratting < 1200:
            return "灰名隐藏大佬"
        if ratting < 1400:
            return '绿名'
        if ratting < 1600:
            return '青名'
        if ratting < 1900:
            return '蓝名大佬'
        if ratting < 2100:
            return '紫名巨巨'
        if ratting < 2300:
            return '橙名'
        if ratting < 2400:
            return '橙名'
        if ratting < 2600:
            return '红名巨佬'
        else:
            return '黑红名神犇'

    url = "https://codeforces.com/api/user.rating?handle=" + name

    try:
        json_data = await get_json(url)
        # pprint.pprint(json_data)
        json_data = dict(json_data)

        if json_data['status'] == "OK":
            json_data = json_data['result']

            if len(json_data) == 0:
                return "该用户还未进行过比赛"

            # pprint.pprint(json_data[-1])

            final_contest = json_data[-1]
            # print(
            s = "“{}”是{}，当前ratting为：{}".format(name, pd_color(int(final_contest['newRating'])), final_contest['newRating'])
            # )
            return s
        else:
            pprint.pprint(json_data)
            return -1  # 表示请求失败
    except:
        return "程序出错，请稍后再试"


async def get_contest():
    url = "https://codeforces.com/api/contest.list?gym=false"
    contest_url = "https://codeforces.com/contest/"

    json_data = await get_json(url)
    if json_data == -1:
        return -1
    json_data = dict(json_data)

    if json_data['status'] == "OK":
        contest_list_all = list(json_data['result'])
        contest_list_lately = []

        for contest in contest_list_all:
            if contest['relativeTimeSeconds'] < 0:
                contest_list_lately.append(contest)
            else:
                break

        if len(contest_list_lately) == 0:
            # print("最近没有比赛~")
            return "最近没有比赛~", 0, 0
        else:
            contest_list_lately.sort(key=lambda x: x['relativeTimeSeconds'], reverse=True)

            contest = contest_list_lately[0]
            res = "下一场Codeforces比赛为：\n"
            res += "比赛名称：{}\n开始时间：{}\n持续时间：{}\n比赛地址：{}".format(
                contest['name'],
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(contest['startTimeSeconds']))),
                "{}小时{:02d}分钟".format(contest['durationSeconds'] // 3600, contest['durationSeconds'] % 3600 // 60),
                contest_url + str(contest['id'])
            )
            return res, int(contest['startTimeSeconds']), int(contest['durationSeconds'])




if __name__ == '__main__':
    # name = input()
    name = "ING__"

    # asyncio.run(get_usr_rating(name))
    # while True:
    #     name = input()
    #     print(asyncio.run(get_usr_rating(name)))

    pprint.pprint(asyncio.run(get_contest()))
    # get_contest()
