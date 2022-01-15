import requests
import retest
import json
import pprint
import os
import time
from lxml import etree
import asyncio
import httpx


async def get_html(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        'Connection': 'close'
    }

    # r = requests.get(url=url, headers=headers)
    async with httpx.AsyncClient() as client:
        r = await client.get(url=url, headers=headers)

    # r.encoding = r.apparent_encoding
    time.sleep(5)
    return r.text


async def get_json(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        'Connection': 'close'
    }

    # response = requests.get(url=url, headers=headers)
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers)

    # print(response.status_code)

    try:
        # url_text = response.content.decode()
        # print(url_text)
        # json_data = json.loads(url_text)
        json_data = response.json()
        # time.sleep(3)
        return json_data
    except:
        return -1


async def text_save(filename, text):  # filename为写入CSV文件的路径，data为要写入数据列表.
    file = open(filename, 'w', encoding='UTF-8')
    file.write(text)
    file.close()
    print("保存文件成功")


async def get_usr_rank(name):
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
    results = retest.findall(r, html, retest.S)

    print(results)

    # os.remove("./atc_usr.html")


async def get_contest_lately():
    url = "https://atcoder.jp/contests/"

    # 获取网页到本地
    html = get_html(url)
    await text_save('./atc_contest.html', html)

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
    pprint.pprint(url + str(contest_url[0]))

    os.remove("./atc_contest.html")


if __name__ == '__main__':
    # get_contest_lately()
    get_usr_rank("ING__")
    pass
