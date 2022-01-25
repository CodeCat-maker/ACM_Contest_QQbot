import requests
import re
import json
import pprint
import os
import time
from lxml import etree
import asyncio
import httpx
from web_operation.operation import *


async def get_usr_rank(name):  # 返回一个列表，如果不存在用户则是空列表
    url = "https://atcoder.jp/users/" + name

    # 获取网页到本地
    html = await get_html(url)
    # text_save('./atc_usr.html', html)

    # 转化为能处理的对象
    # h5 = etree.parse("./atc_usr.html", etree.HTMLParser())
    # result = etree.tostring(h5)

    # 构建对应的xpath
    # rank_xpath = "/html/body/div[1]/div/div[1]/div[3]/table/tbody/tr[2]/td/span[0]"


    # 获取对应的属性值
    # rank = h5.xpath(rank_xpath)

    # -----xpath办法失败，不知道为什么获取的值都是空的，有没有懂的大佬可以解答一下qwq-------

    r = r'<th class="no-break">Rating<\/th><td><span class=\'user-gray\'>(.*?)<\/span>'
    results = re.findall(r, html, re.S)

    # print(results)
    try:
        return results[0]
    except:
        return -1

    # os.remove("./atc_usr.html")


async def get_contest_lately():
    url = "https://atcoder.jp/contests/"

    # 获取网页到本地
    html = await get_html(url)
    await(text_save('./atc_contest.html', html))

    # 转化为能处理的对象
    h5 = etree.parse("./atc_contest.html", etree.HTMLParser())
    # result = etree.tostring(h5)

    # 构建对应的xpath
    time_xpath = "//*[@id=\"contest-table-upcoming\"]/div/div/table/tbody/tr[1]/td[1]/a/time/text()"
    contest_xpath = "//*[@id=\"contest-table-upcoming\"]/div/div/table/tbody/tr[1]/td[2]/a/text()"
    during_time_xpath = "//*[@id=\"contest-table-upcoming\"]/div/div/table/tbody/tr[1]/td[3]/text()"
    contest_url_xpath = "//*[@id=\"contest-table-upcoming\"]/div/div/table/tbody/tr[1]/td[2]/a/@href"

    # 获取对应的信息
    contest_time = h5.xpath(time_xpath)[0]
    contest_name = h5.xpath(contest_xpath)[0]
    during_time = h5.xpath(during_time_xpath)[0]
    contest_url = h5.xpath(contest_url_xpath)[0]

    # debug
    pprint.pprint(contest_time)
    pprint.pprint(contest_name)
    pprint.pprint(during_time)
    pprint.pprint(url + str(contest_url[1:]))

    os.remove("./atc_contest.html")

    res = "下一场AtCoder比赛为：\n"
    res += "名称：{}\n开始时间：{}\n持续时间：{}\n比赛地址：{}\n".format(
        contest_name,
        contest_time,
        "{}小时{:02d}分钟".format(int(during_time[0:2]), int(during_time[3:])),
        url + str(contest_url[1:])
    )

    # print(res)
    return res

if __name__ == '__main__':
    # asyncio.run(get_contest_lately())
    print(asyncio.run(get_usr_rank("432423")))
    pass
