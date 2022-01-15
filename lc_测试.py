import requests
import retest
import json
import pprint
import os
import time
from lxml import etree


def get_html(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        'Connection': 'close',
        'origin': 'https://leetcode-cn.com',
        'referer': 'https://leetcode-cn.com/contest/'
    }

    r = requests.post(url=url, headers=headers)
    r.encoding = r.apparent_encoding
    time.sleep(1)
    return r.text


def get_json(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        'Connection': 'close'
    }

    response = requests.get(url=url, headers=headers)

    # print(response.status_code)

    try:
        url_text = response.content.decode()
        # print(url_text)
        json_data = json.loads(url_text)
        time.sleep(3)
        return json_data
    except:
        print('<Response [%s]>' % response.status_code)


def text_save(filename, text):  # filename为写入CSV文件的路径，data为要写入数据列表.
    file = open(filename, 'w', encoding='UTF-8')
    file.write(text)
    file.close()
    print("保存文件成功")


# TODO 获取力扣比赛列表
def get_contest():
    pass


# TODO 获取力扣分数
def get_usr_rank(name):
    pass



if __name__ == '__main__':
    pprint.pprint(get_html("https://leetcode-cn.com/contest/"))